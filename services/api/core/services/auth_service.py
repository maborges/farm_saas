from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Request
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from typing import Optional
import uuid
import secrets
from loguru import logger

from core.models.auth import Usuario, TenantUsuario, PerfilAcesso, FazendaUsuario, TokenRecuperacaoSenha
from core.models.grupo_fazendas import GrupoUsuario
from core.models.tenant import Tenant
from core.models.fazenda import Fazenda
from core.models.billing import AssinaturaTenant, PlanoAssinatura
from core.schemas.auth_schemas import LoginRequest, UserCreateRequest, TenantAcessoResponse, FazendaAcessoResponse, PerfilSimplesResponse, UsuarioMeResponse
from core.config import settings
from core.services.login_rate_limit_service import LoginRateLimitService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)
        
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    async def register_user(self, user_data: UserCreateRequest) -> Usuario:
        # Check if email or username exists
        stmt = select(Usuario).where((Usuario.email == user_data.email) | (Usuario.username == user_data.username))
        result = await self.session.execute(stmt)
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Email ou Username já cadastrado")
            
        hashed_pw = self.get_password_hash(user_data.senha)
        db_user = Usuario(
            email=user_data.email,
            username=user_data.username,
            nome_completo=user_data.nome_completo,
            senha_hash=hashed_pw
        )
        self.session.add(db_user)
        # Note: A real app usually creates a default Tenant here if the user is a new "Produtor"
        # For now, let's just create the user.
        await self.session.commit()
        return db_user

    async def authenticate_user(
        self,
        login_data: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> tuple[Usuario, str]:
        """
        Autentica usuário com rate limiting configurável por tenant.

        Args:
            login_data: Dados de login (email, senha)
            ip_address: IP do cliente para auditoria
            user_agent: User agent do cliente para auditoria

        Returns:
            tuple[Usuario, str]: Usuário autenticado e token de acesso

        Raises:
            HTTPException 423: Conta bloqueada temporariamente
            HTTPException 401: Credenciais inválidas
            HTTPException 403: Usuário inativo
        """
        from core.services.configuracoes_service import ConfiguracoesService

        # Busca usuário primeiro para descobrir o tenant
        stmt = select(Usuario).where(Usuario.email == login_data.email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        # Descobre tenant do usuário para pegar config de segurança
        seguranca_config = None
        if user:
            tenant_usuario_stmt = select(TenantUsuario).where(
                TenantUsuario.usuario_id == user.id,
                TenantUsuario.status == "ATIVO"
            ).limit(1)
            tenant_usuario_result = await self.session.execute(tenant_usuario_stmt)
            tenant_usuario = tenant_usuario_result.scalar_one_or_none()

            if tenant_usuario and not user.is_superuser:
                svc = ConfiguracoesService(self.session, tenant_usuario.tenant_id)
                seguranca_config = await svc.get_seguranca_config()

        # Inicializa serviço de rate limiting com config do tenant
        rate_limit_svc = LoginRateLimitService(self.session, seguranca_config=seguranca_config)

        # Verifica se está bloqueado
        bloqueado, data_desbloqueio = await rate_limit_svc.verificar_bloqueio(login_data.email)

        if bloqueado:
            minutos_restantes = max(1, int((data_desbloqueio - datetime.now(timezone.utc)).total_seconds() / 60))
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Conta bloqueada por segurança. Tente novamente em {minutos_restantes} minuto(s).",
                headers={"Retry-After": str(minutos_restantes * 60)}
            )

        logger.debug(f"🔍 Tentativa de autenticação para: {login_data.email}")
        
        # Usuário não encontrado
        if not user:
            logger.warning(f"❌ Usuário não encontrado: {login_data.email}")
            await rate_limit_svc.registrar_tentativa_falha(
                email=login_data.email,
                motivo="USUARIO_NAO_ENCONTRADO",
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")

        if not user.senha_hash:
            logger.warning(f"❌ Usuário sem senha (SSO?): {login_data.email}")
            await rate_limit_svc.registrar_tentativa_falha(
                email=login_data.email,
                motivo="USUARIO_SEM_HASH",
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login via senha não habilitado para este usuário")

        # Senha inválida
        if not self.verify_password(login_data.senha, user.senha_hash):
            logger.warning(f"❌ Senha incorreta para: {login_data.email}")
            await rate_limit_svc.registrar_tentativa_falha(
                email=login_data.email,
                motivo="SENHA_INVALIDA",
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")

        # Usuário inativo
        if not user.ativo:
            await rate_limit_svc.registrar_tentativa_falha(
                email=login_data.email,
                motivo="USUARIO_INATIVO",
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")

        # Login bem-sucedido - registra e reseta contador
        await rate_limit_svc.registrar_tentativa_sucesso(login_data.email)
            
        # Build the dynamic token claims based on the first tenant or default structure
        # A good SaaS token only holds current "active" tenant context, not ALL tenants.
        # But our old mock injected all. Let's find first active tenant to inject as default context.
        
        tenant_usuario_stmt = select(TenantUsuario).where(TenantUsuario.usuario_id == user.id, TenantUsuario.status == "ATIVO")
        tenant_usuarios = (await self.session.execute(tenant_usuario_stmt)).scalars().all()
        
        default_tenant_id = None
        modulos = ["CORE"]
        fazendas_auth = []
        grupos_auth = []
        grupos_jwt = []
        
        # Superadministradores não entram vinculados a nenhum tenant por padrão.
        # Eles entram no contexto de Gestão Global.
        if not user.is_superuser and tenant_usuarios:
            first_tu = tenant_usuarios[0]
            default_tenant_id = str(first_tu.tenant_id)
            
            # Fetch tenant to get modules
            tenant_stmt = select(Tenant).where(Tenant.id == first_tu.tenant_id)
            tenant = (await self.session.execute(tenant_stmt)).scalar_one_or_none()
            if tenant:
                modulos = tenant.modulos_ativos or ["CORE"]
                
            # Fetch profile to get roles
            perfil_stmt = select(PerfilAcesso).where(PerfilAcesso.id == first_tu.perfil_id)
            perfil = (await self.session.execute(perfil_stmt)).scalar_one_or_none()
            role_name = perfil.nome.lower() if perfil else "operador"
            
            # Fetch allowed fazendas
            fazenda_usu_stmt = select(FazendaUsuario).where(
                FazendaUsuario.usuario_id == user.id,
                FazendaUsuario.tenant_id == first_tu.tenant_id
            )
            f_usuarios = (await self.session.execute(fazenda_usu_stmt)).scalars().all()
            for fu in f_usuarios:
                fazendas_auth.append({"id": str(fu.fazenda_id), "role": role_name})

            # Fetch grupos do usuário com assinatura e fazendas
            grupo_usu_stmt = select(GrupoUsuario).where(
                GrupoUsuario.user_id == user.id,
                GrupoUsuario.tenant_id == first_tu.tenant_id
            )
            g_usuarios = (await self.session.execute(grupo_usu_stmt)).scalars().all()
            grupos_auth = [str(gu.grupo_id) for gu in g_usuarios]

            # Monta grupos[] com assinatura e fazendas para o JWT
            grupos_jwt = []
            for gu in g_usuarios:
                from core.models.grupo_fazendas import GrupoFazendas
                grupo_stmt = select(GrupoFazendas).where(GrupoFazendas.id == gu.grupo_id)
                grupo_obj = (await self.session.execute(grupo_stmt)).scalar_one_or_none()
                if not grupo_obj or not grupo_obj.ativo:
                    continue

                assin_stmt = (
                    select(PlanoAssinatura.modulos_inclusos, PlanoAssinatura.plan_tier,
                           PlanoAssinatura.max_fazendas, AssinaturaTenant.usuarios_contratados)
                    .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                    .where(
                        AssinaturaTenant.grupo_fazendas_id == gu.grupo_id,
                        AssinaturaTenant.tenant_id == first_tu.tenant_id,
                        AssinaturaTenant.tipo_assinatura == "GRUPO",
                        AssinaturaTenant.status == "ATIVA",
                    )
                    .limit(1)
                )
                assin_row = (await self.session.execute(assin_stmt)).first()
                grupo_modules = (assin_row[0] if assin_row and assin_row[0] else ["CORE"])
                grupo_tier = (assin_row[1] if assin_row and assin_row[1] else "BASICO")
                grupo_max_fazendas = (assin_row[2] if assin_row and assin_row[2] else 1)
                grupo_max_usuarios = (assin_row[3] if assin_row and assin_row[3] else 2)

                # Fazendas do grupo que o usuário tem acesso
                from core.models.fazenda import Fazenda as FazendaModel
                faz_grupo_stmt = select(FazendaModel.id, FazendaModel.nome).where(
                    FazendaModel.grupo_id == gu.grupo_id,
                    FazendaModel.tenant_id == first_tu.tenant_id,
                    FazendaModel.ativo == True,
                )
                faz_rows = (await self.session.execute(faz_grupo_stmt)).all()
                fazendas_do_grupo = [{"id": str(r[0]), "nome": r[1]} for r in faz_rows]

                grupos_jwt.append({
                    "id": str(gu.grupo_id),
                    "nome": grupo_obj.nome,
                    "modules": grupo_modules,
                    "plan_tier": grupo_tier,
                    "max_fazendas": grupo_max_fazendas,
                    "max_usuarios": grupo_max_usuarios,
                    "fazendas": fazendas_do_grupo,
                })
                # Atualiza modulos (union de todos os grupos) e fazendas_auth
                modulos = list(set(modulos) | set(grupo_modules))
                for faz in fazendas_do_grupo:
                    if not any(f["id"] == faz["id"] for f in fazendas_auth):
                        fazendas_auth.append({"id": faz["id"], "role": role_name})

        # plan_tier do primeiro grupo (ou BASICO)
        plan_tier = grupos_jwt[0]["plan_tier"] if grupos_jwt else "BASICO"

        # Generate token payload
        claims = {
            "sub": str(user.id),
            "tenant_id": default_tenant_id,
            "modules": modulos,          # union — mantido para compatibilidade
            "fazendas_auth": fazendas_auth,
            "grupos_auth": grupos_auth,
            "grupos": grupos_jwt,        # novo: por grupo com módulos e fazendas
            "is_superuser": user.is_superuser,
            "plan_tier": plan_tier,
        }
        
        access_token = self.create_access_token(data=claims)
        
        # Cria registro da sessão ativa no banco de dados
        from core.models.sessao import SessaoAtiva
        import hashlib
        from datetime import datetime, timezone, timedelta
        
        token_hash = hashlib.sha256(access_token.encode()).hexdigest()
        agora = datetime.now(timezone.utc)
        
        sessao_ativa = SessaoAtiva(
            tenant_id=uuid.UUID(default_tenant_id) if default_tenant_id else None,
            usuario_id=user.id,
            token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            inicio=agora,
            ultimo_heartbeat=agora,
            expira_em=agora + timedelta(minutes=30),
            status="ATIVA",
            grupo_fazendas_id=None,
            fazenda_id=None,
        )
        self.session.add(sessao_ativa)
        await self.session.commit()
        
        return user, access_token

    async def generate_token_for_tenant(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> str:
        """
        Gera um novo JWT com grupos[] do tenant selecionado.
        Usado pelo endpoint /auth/switch-tenant.
        """
        from core.models.grupo_fazendas import GrupoFazendas

        user = (await self.session.execute(select(Usuario).where(Usuario.id == user_id))).scalar_one_or_none()
        if not user or not user.ativo:
            raise HTTPException(status_code=403, detail="Usuário inativo")

        first_tu = (await self.session.execute(
            select(TenantUsuario).where(
                TenantUsuario.tenant_id == tenant_id,
                TenantUsuario.usuario_id == user_id,
                TenantUsuario.status == "ATIVO"
            )
        )).scalar_one_or_none()
        if not first_tu:
            raise HTTPException(status_code=403, detail="Sem acesso ao tenant")

        perfil = None
        if first_tu.perfil_id:
            perfil = (await self.session.execute(
                select(PerfilAcesso).where(PerfilAcesso.id == first_tu.perfil_id)
            )).scalar_one_or_none()
        role_name = perfil.nome.lower() if perfil else "operador"

        # Reutiliza a lógica de montagem de grupos do authenticate_user
        g_usuarios = (await self.session.execute(
            select(GrupoUsuario).where(
                GrupoUsuario.user_id == user_id,
                GrupoUsuario.tenant_id == tenant_id
            )
        )).scalars().all()

        grupos_auth = [str(gu.grupo_id) for gu in g_usuarios]
        modulos: list[str] = ["CORE"]
        fazendas_auth: list[dict] = []
        grupos_jwt: list[dict] = []

        for gu in g_usuarios:
            grupo_obj = (await self.session.execute(
                select(GrupoFazendas).where(GrupoFazendas.id == gu.grupo_id)
            )).scalar_one_or_none()
            if not grupo_obj or not grupo_obj.ativo:
                continue

            assin_row = (await self.session.execute(
                select(PlanoAssinatura.modulos_inclusos, PlanoAssinatura.plan_tier,
                       PlanoAssinatura.max_fazendas, AssinaturaTenant.usuarios_contratados)
                .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                .where(
                    AssinaturaTenant.grupo_fazendas_id == gu.grupo_id,
                    AssinaturaTenant.tenant_id == tenant_id,
                    AssinaturaTenant.tipo_assinatura == "GRUPO",
                    AssinaturaTenant.status == "ATIVA",
                )
                .limit(1)
            )).first()

            grupo_modules = (assin_row[0] if assin_row and assin_row[0] else ["CORE"])
            grupo_tier = (assin_row[1] if assin_row and assin_row[1] else "BASICO")
            grupo_max_fazendas = (assin_row[2] if assin_row and assin_row[2] else 1)
            grupo_max_usuarios = (assin_row[3] if assin_row and assin_row[3] else 2)

            faz_rows = (await self.session.execute(
                select(Fazenda.id, Fazenda.nome).where(
                    Fazenda.grupo_id == gu.grupo_id,
                    Fazenda.tenant_id == tenant_id,
                    Fazenda.ativo == True,
                )
            )).all()
            fazendas_do_grupo = [{"id": str(r[0]), "nome": r[1]} for r in faz_rows]

            grupos_jwt.append({
                "id": str(gu.grupo_id),
                "nome": grupo_obj.nome,
                "modules": grupo_modules,
                "plan_tier": grupo_tier,
                "max_fazendas": grupo_max_fazendas,
                "max_usuarios": grupo_max_usuarios,
                "fazendas": fazendas_do_grupo,
            })
            modulos = list(set(modulos) | set(grupo_modules))
            for faz in fazendas_do_grupo:
                if not any(f["id"] == faz["id"] for f in fazendas_auth):
                    fazendas_auth.append({"id": faz["id"], "role": role_name})

        plan_tier = grupos_jwt[0]["plan_tier"] if grupos_jwt else "BASICO"
        active_grupo_id = grupos_jwt[0]["id"] if len(grupos_jwt) == 1 else None

        claims = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "modules": modulos,
            "fazendas_auth": fazendas_auth,
            "grupos_auth": grupos_auth,
            "grupos": grupos_jwt,
            "active_grupo_id": active_grupo_id,
            "is_superuser": user.is_superuser,
            "plan_tier": plan_tier,
        }

        access_token = self.create_access_token(data=claims)

        # Registrar nova sessão
        from core.models.sessao import SessaoAtiva
        import hashlib
        token_hash = hashlib.sha256(access_token.encode()).hexdigest()
        agora = datetime.now(timezone.utc)
        self.session.add(SessaoAtiva(
            tenant_id=tenant_id,
            usuario_id=user_id,
            token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            inicio=agora,
            ultimo_heartbeat=agora,
            expira_em=agora + timedelta(minutes=30),
            status="ATIVA",
            grupo_fazendas_id=uuid.UUID(active_grupo_id) if active_grupo_id else None,
            fazenda_id=None,
        ))
        await self.session.commit()
        return access_token

    async def generate_token_for_grupo(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        grupo_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> str:
        """
        Gera um novo JWT com o grupo de fazendas selecionado como contexto ativo.
        Usado pelo endpoint /auth/switch-grupo.
        """
        from core.models.grupo_fazendas import GrupoFazendas

        user = (await self.session.execute(select(Usuario).where(Usuario.id == user_id))).scalar_one_or_none()
        if not user or not user.ativo:
            raise HTTPException(status_code=403, detail="Usuário inativo")

        # Verificar acesso ao tenant
        first_tu = (await self.session.execute(
            select(TenantUsuario).where(
                TenantUsuario.tenant_id == tenant_id,
                TenantUsuario.usuario_id == user_id,
                TenantUsuario.status == "ATIVO"
            )
        )).scalar_one_or_none()
        if not first_tu:
            raise HTTPException(status_code=403, detail="Sem acesso ao tenant")

        perfil = None
        if first_tu.perfil_id:
            perfil = (await self.session.execute(
                select(PerfilAcesso).where(PerfilAcesso.id == first_tu.perfil_id)
            )).scalar_one_or_none()
        role_name = perfil.nome.lower() if perfil else "operador"

        # Buscar o grupo específico
        g_usuario = (await self.session.execute(
            select(GrupoUsuario).where(
                GrupoUsuario.user_id == user_id,
                GrupoUsuario.tenant_id == tenant_id,
                GrupoUsuario.grupo_id == grupo_id
            )
        )).scalar_one_or_none()

        if not g_usuario:
            raise HTTPException(status_code=403, detail="Usuário não tem acesso ao grupo selecionado")

        grupo_obj = (await self.session.execute(
            select(GrupoFazendas).where(GrupoFazendas.id == grupo_id, GrupoFazendas.ativo == True)
        )).scalar_one_or_none()

        if not grupo_obj:
            raise HTTPException(status_code=404, detail="Grupo não encontrado ou inativo")

        # Buscar assinatura do grupo
        assin_row = (await self.session.execute(
            select(PlanoAssinatura.modulos_inclusos, PlanoAssinatura.plan_tier,
                   PlanoAssinatura.max_fazendas, AssinaturaTenant.usuarios_contratados)
            .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
            .where(
                AssinaturaTenant.grupo_fazendas_id == grupo_id,
                AssinaturaTenant.tenant_id == tenant_id,
                AssinaturaTenant.tipo_assinatura == "GRUPO",
                AssinaturaTenant.status == "ATIVA",
            )
            .limit(1)
        )).first()

        grupo_modules = (assin_row[0] if assin_row and assin_row[0] else ["CORE"])
        grupo_tier = (assin_row[1] if assin_row and assin_row[1] else "BASICO")
        grupo_max_fazendas = (assin_row[2] if assin_row and assin_row[2] else 1)
        grupo_max_usuarios = (assin_row[3] if assin_row and assin_row[3] else 2)

        # Buscar fazendas do grupo
        faz_rows = (await self.session.execute(
            select(Fazenda.id, Fazenda.nome).where(
                Fazenda.grupo_id == grupo_id,
                Fazenda.tenant_id == tenant_id,
                Fazenda.ativo == True,
            )
        )).all()
        fazendas_do_grupo = [{"id": str(r[0]), "nome": r[1]} for r in faz_rows]

        grupos_jwt = [{
            "id": str(grupo_id),
            "nome": grupo_obj.nome,
            "modules": grupo_modules,
            "plan_tier": grupo_tier,
            "max_fazendas": grupo_max_fazendas,
            "max_usuarios": grupo_max_usuarios,
            "fazendas": fazendas_do_grupo,
        }]

        fazendas_auth = [{"id": faz["id"], "role": role_name} for faz in fazendas_do_grupo]

        claims = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "modules": grupo_modules,
            "fazendas_auth": fazendas_auth,
            "grupos_auth": [str(grupo_id)],
            "grupos": grupos_jwt,
            "active_grupo_id": str(grupo_id),
            "is_superuser": user.is_superuser,
            "plan_tier": grupo_tier,
        }

        access_token = self.create_access_token(data=claims)

        # Registrar nova sessão
        from core.models.sessao import SessaoAtiva
        import hashlib
        token_hash = hashlib.sha256(access_token.encode()).hexdigest()
        agora = datetime.now(timezone.utc)
        self.session.add(SessaoAtiva(
            tenant_id=tenant_id,
            usuario_id=user_id,
            token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            inicio=agora,
            ultimo_heartbeat=agora,
            expira_em=agora + timedelta(minutes=30),
            status="ATIVA",
            grupo_fazendas_id=grupo_id,
            fazenda_id=None,
        ))
        await self.session.commit()
        return access_token

    async def get_user_me(self, user_id: uuid.UUID) -> UsuarioMeResponse:
        stmt = select(Usuario).where(Usuario.id == user_id)
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
        # Get all tenants
        tu_stmt = select(TenantUsuario).where(TenantUsuario.usuario_id == user.id, TenantUsuario.status == "ATIVO")
        tenant_links = (await self.session.execute(tu_stmt)).scalars().all()
        
        tenants_response = []
        for tu in tenant_links:
            # get tenant
            t_stmt = select(Tenant).where(Tenant.id == tu.tenant_id)
            tenant = (await self.session.execute(t_stmt)).scalar_one()
            
            # get perfil
            perfil = None
            if tu.perfil_id:
                p_stmt = select(PerfilAcesso).where(PerfilAcesso.id == tu.perfil_id)
                perfil = (await self.session.execute(p_stmt)).scalar_one_or_none()
            
            # get fazendas
            fu_stmt = select(FazendaUsuario).where(FazendaUsuario.usuario_id == user.id, FazendaUsuario.tenant_id == tenant.id)
            f_links = (await self.session.execute(fu_stmt)).scalars().all()
            fazendas_resp = []
            for fl in f_links:
                f_stmt = select(Fazenda).where(Fazenda.id == fl.fazenda_id)
                fazenda_obj = (await self.session.execute(f_stmt)).scalar_one_or_none()
                if fazenda_obj:
                    fazendas_resp.append(FazendaAcessoResponse(fazenda_id=fazenda_obj.id, nome=fazenda_obj.nome))
                    
            # Query plan info — agrega todos os grupos do tenant (union de módulos)
            plan_stmt = (
                select(
                    PlanoAssinatura.plan_tier,
                    PlanoAssinatura.max_fazendas,
                    PlanoAssinatura.modulos_inclusos,
                    AssinaturaTenant.usuarios_contratados,
                )
                .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                .where(
                    AssinaturaTenant.tenant_id == tenant.id,
                    AssinaturaTenant.tipo_assinatura == "GRUPO",
                    AssinaturaTenant.status.in_(["ATIVA", "PENDENTE_PAGAMENTO", "TRIAL"]),
                )
            )
            plan_rows = (await self.session.execute(plan_stmt)).all()
            if plan_rows:
                t_plan_tier = plan_rows[0][0] or "BASICO"
                t_max_fazendas = max((r[1] or 1) for r in plan_rows)
                t_modulos = list({m for r in plan_rows if r[2] for m in r[2]})
                t_max_usuarios = max((r[3] or 2) for r in plan_rows)
            else:
                t_plan_tier = "BASICO"
                t_max_fazendas = 1
                t_modulos = ["CORE"]
                t_max_usuarios = 2

            tenants_response.append(TenantAcessoResponse(
                tenant_id=tenant.id,
                nome_tenant=tenant.nome,
                is_owner=tu.is_owner,
                perfil=PerfilSimplesResponse(id=perfil.id, nome=perfil.nome, permissoes=perfil.permissoes) if perfil else None,
                fazendas=fazendas_resp,
                plan_tier=t_plan_tier,
                max_fazendas=t_max_fazendas,
                max_usuarios=t_max_usuarios,
                modulos=t_modulos,
            ))

        response = UsuarioMeResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            nome_completo=user.nome_completo,
            foto_perfil_url=user.foto_perfil_url,
            is_superuser=user.is_superuser,
            tenants=tenants_response
        )
        return response

    # ==================== RECUPERAÇÃO DE SENHA ====================

    async def create_password_reset_token(self, email: str, ip_address: Optional[str] = None) -> dict:
        """
        Cria um token de recuperação de senha e envia por e-mail.
        
        Args:
            email: E-mail do usuário
            ip_address: IP de origem da solicitação
            
        Returns:
            dict: Informações sobre o resultado da operação
        """
        from core.services.email_service import email_service

        # Busca usuário pelo email
        stmt = select(Usuario).where(Usuario.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        # Sempre retorna sucesso para evitar enumeração de usuários
        if not user:
            return {
                "sucesso": True,
                "mensagem": "Se o e-mail estiver cadastrado, você receberá as instruções para recuperação de senha.",
                "email": None
            }

        # Invalida tokens anteriores não utilizados deste usuário
        invalidate_stmt = select(TokenRecuperacaoSenha).where(
            TokenRecuperacaoSenha.usuario_id == user.id,
            TokenRecuperacaoSenha.utilizado == False
        )
        invalidate_result = await self.session.execute(invalidate_stmt)
        tokens_anteriores = invalidate_result.scalars().all()
        
        for token in tokens_anteriores:
            token.utilizado = True  # Marca como utilizado para invalidar

        # Gera token seguro
        token_value = secrets.token_urlsafe(48)  # 64 caracteres
        data_expiracao = datetime.now(timezone.utc) + timedelta(hours=1)

        # Cria registro do token
        token_record = TokenRecuperacaoSenha(
            usuario_id=user.id,
            token=token_value,
            data_expiracao=data_expiracao,
            ip_origem=ip_address
        )
        
        self.session.add(token_record)
        await self.session.commit()

        # Obtém tenant_id do usuário para configuração SMTP correta
        tenant_id = None
        tenant_usuario_stmt = select(TenantUsuario).where(
            TenantUsuario.usuario_id == user.id,
            TenantUsuario.status == "ATIVO"
        ).limit(1)
        tenant_usuario_result = await self.session.execute(tenant_usuario_stmt)
        tenant_usuario = tenant_usuario_result.scalar_one_or_none()
        
        if tenant_usuario:
            tenant_id = tenant_usuario.tenant_id

        # Envia e-mail de recuperação
        nome_usuario = user.nome_completo or user.username
        await email_service.send_password_recovery(
            email=user.email,
            nome_usuario=nome_usuario,
            token=token_value,
            tenant_id=tenant_id
        )

        return {
            "sucesso": True,
            "mensagem": "Se o e-mail estiver cadastrado, você receberá as instruções para recuperação de senha.",
            "email": user.email
        }

    async def verify_reset_token(self, token: str) -> dict:
        """
        Verifica se um token de recuperação é válido.
        
        Args:
            token: Token de recuperação
            
        Returns:
            dict: Informações sobre a validade do token
        """
        # Busca token não utilizado
        stmt = select(TokenRecuperacaoSenha).where(
            TokenRecuperacaoSenha.token == token,
            TokenRecuperacaoSenha.utilizado == False
        )
        result = await self.session.execute(stmt)
        token_record = result.scalar_one_or_none()
        if not token_record:
            return {
                "valido": False,
                "mensagem": "Token inválido ou já utilizado.",
                "email": None,
                "expira_em": None
            }

        # Verifica se expirou
        agora = datetime.now(timezone.utc)
        if agora > token_record.data_expiracao:
            return {
                "valido": False,
                "mensagem": "Token expirado. Solicite um novo link de recuperação.",
                "email": None,
                "expira_em": None
            }

        # Busca informações do usuário
        usuario = await self.session.get(Usuario, token_record.usuario_id)
        if not usuario:
            return {
                "valido": False,
                "mensagem": "Usuário não encontrado.",
                "email": None,
                "expira_em": None
            }

        minutos_restantes = int((token_record.data_expiracao - agora).total_seconds() / 60)
        
        return {
            "valido": True,
            "mensagem": "Token válido.",
            "email": usuario.email,
            "expira_em": f"{minutos_restantes} minutos"
        }

    async def reset_password(self, token: str, nova_senha: str, ip_address: Optional[str] = None) -> dict:
        """
        Redefine a senha do usuário usando um token válido.
        
        Args:
            token: Token de recuperação
            nova_senha: Nova senha
            ip_address: IP de origem da solicitação
            
        Returns:
            dict: Resultado da operação
        """
        # Busca token não utilizado
        stmt = select(TokenRecuperacaoSenha).where(
            TokenRecuperacaoSenha.token == token,
            TokenRecuperacaoSenha.utilizado == False
        )
        result = await self.session.execute(stmt)
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou já utilizado."
            )

        # Verifica se expirou
        agora = datetime.now(timezone.utc)
        if agora > token_record.data_expiracao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expirado. Solicite um novo link de recuperação."
            )

        # Busca usuário
        usuario = await self.session.get(Usuario, token_record.usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )

        # Verifica se a senha é diferente da atual
        if usuario.senha_hash and self.verify_password(nova_senha, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A nova senha deve ser diferente da senha atual."
            )

        # Atualiza a senha
        usuario.senha_hash = self.get_password_hash(nova_senha)
        usuario.updated_at = datetime.now(timezone.utc)

        # Marca o token como utilizado
        token_record.utilizado = True
        token_record.data_utilizacao = agora
        token_record.ip_utilizacao = ip_address

        await self.session.commit()

        return {
            "sucesso": True,
            "mensagem": "Senha redefinida com sucesso. Você já pode fazer login com a nova senha."
        }
