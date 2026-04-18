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

from core.models.auth import Usuario, TenantUsuario, PerfilAcesso, UnidadeProdutivaUsuario as FazendaUsuario, TokenRecuperacaoSenha
from core.models.tenant import Tenant
from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda
from core.models.billing import AssinaturaTenant, PlanoAssinatura, Fatura
from core.schemas.auth_schemas import LoginRequest, UserCreateRequest, TenantAcessoResponse, UnidadeProdutivaAcessoResponse as FazendaAcessoResponse, PerfilSimplesResponse, UsuarioMeResponse
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
        grupos_jwt = []
        perfil = None

        # Superadministradores não entram vinculados a nenhum tenant por padrão.
        # Eles entram no contexto de Gestão Global.
        if not user.is_superuser and tenant_usuarios:
            first_tu = tenant_usuarios[0]
            default_tenant_id = str(first_tu.tenant_id)
            
            # Fetch profile to get roles
            perfil_stmt = select(PerfilAcesso).where(PerfilAcesso.id == first_tu.perfil_id)
            perfil = (await self.session.execute(perfil_stmt)).scalar_one_or_none()
            role_name = perfil.nome.lower() if perfil else "operador"
            
            # Fetch allowed unidades produtivas
            fazenda_usu_stmt = select(FazendaUsuario).where(
                FazendaUsuario.usuario_id == user.id,
                FazendaUsuario.tenant_id == first_tu.tenant_id
            )
            f_usuarios = (await self.session.execute(fazenda_usu_stmt)).scalars().all()
            for fu in f_usuarios:
                fazendas_auth.append({"id": str(fu.unidade_produtiva_id), "role": role_name})

            # Fetch subscription info for the tenant
            assin_stmt = (
                select(PlanoAssinatura.modulos_inclusos, PlanoAssinatura.plan_tier,
                       PlanoAssinatura.max_fazendas, AssinaturaTenant.usuarios_contratados)
                .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                .where(
                    AssinaturaTenant.tenant_id == first_tu.tenant_id,
                    AssinaturaTenant.status.in_(["ATIVA", "TRIAL"]),
                )
                .limit(1)
            )
            assin_row = (await self.session.execute(assin_stmt)).first()
            tenant_modules = (assin_row[0] if assin_row and assin_row[0] else ["CORE"])
            tenant_tier = (assin_row[1] if assin_row and assin_row[1] else "BASICO")
            tenant_max_fazendas = (assin_row[2] if assin_row and assin_row[2] else 1)
            tenant_max_usuarios = (assin_row[3] if assin_row and assin_row[3] else 2)

            # All unidades produtivas the user can access
            faz_stmt = select(Fazenda.id, Fazenda.nome).where(
                Fazenda.tenant_id == first_tu.tenant_id,
                Fazenda.ativo == True,
            )
            faz_rows = (await self.session.execute(faz_stmt)).all()
            all_fazendas = [{"id": str(r[0]), "nome": r[1]} for r in faz_rows]

            grupos_jwt = [{
                "id": str(first_tu.tenant_id),
                "nome": "default",
                "modules": tenant_modules,
                "plan_tier": tenant_tier,
                "max_fazendas": tenant_max_fazendas,
                "max_usuarios": tenant_max_usuarios,
                "fazendas": all_fazendas,
            }]
            modulos = list(set(modulos) | set(tenant_modules))
            for faz in all_fazendas:
                if not any(f["id"] == faz["id"] for f in fazendas_auth):
                    fazendas_auth.append({"id": faz["id"], "role": role_name})

        # plan_tier do tenant (ou BASICO)
        plan_tier = grupos_jwt[0]["plan_tier"] if grupos_jwt else "BASICO"

        # Role do tenant (owner/admin) para acesso implícito
        tenant_role = perfil.nome.lower() if (not user.is_superuser and perfil) else None

        # Generate token payload
        claims = {
            "sub": str(user.id),
            "tenant_id": default_tenant_id,
            "role": tenant_role,
            "modules": modulos,
            "fazendas_auth": fazendas_auth,
            "grupos": grupos_jwt,
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
        # grupos_fazendas removed

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

        grupos_auth = []
        modulos: list[str] = ["CORE"]
        fazendas_auth: list[dict] = []
        grupos_jwt: list[dict] = []

        # Fetch subscription info for the tenant
        assin_row = (await self.session.execute(
            select(PlanoAssinatura.modulos_inclusos, PlanoAssinatura.plan_tier,
                   PlanoAssinatura.max_fazendas, AssinaturaTenant.usuarios_contratados)
            .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
            .where(
                AssinaturaTenant.tenant_id == tenant_id,
                AssinaturaTenant.status.in_(["ATIVA", "TRIAL"]),
            )
            .limit(1)
        )).first()

        tenant_modules = (assin_row[0] if assin_row and assin_row[0] else ["CORE"])
        tenant_tier = (assin_row[1] if assin_row and assin_row[1] else "BASICO")
        tenant_max_fazendas = (assin_row[2] if assin_row and assin_row[2] else 1)
        tenant_max_usuarios = (assin_row[3] if assin_row and assin_row[3] else 2)

        faz_rows = (await self.session.execute(
            select(Fazenda.id, Fazenda.nome).where(
                Fazenda.tenant_id == tenant_id,
                Fazenda.ativo == True,
            )
        )).all()
        all_fazendas = [{"id": str(r[0]), "nome": r[1]} for r in faz_rows]

        grupos_jwt = [{
            "id": str(tenant_id),
            "nome": "default",
            "modules": tenant_modules,
            "plan_tier": tenant_tier,
            "max_fazendas": tenant_max_fazendas,
            "max_usuarios": tenant_max_usuarios,
            "fazendas": all_fazendas,
        }]
        modulos = list(set(modulos) | set(tenant_modules))
        fazendas_auth = [{"id": faz["id"], "role": role_name} for faz in all_fazendas]

        plan_tier = tenant_tier

        claims = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "modules": modulos,
            "fazendas_auth": fazendas_auth,
            "grupos": grupos_jwt,
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
        """Deprecated: grupos removed. Delegates to generate_token_for_tenant."""
        return await self.generate_token_for_tenant(user_id, tenant_id, ip_address, user_agent)

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
                f_stmt = select(Fazenda).where(Fazenda.id == fl.unidade_produtiva_id)
                fazenda_obj = (await self.session.execute(f_stmt)).scalar_one_or_none()
                if fazenda_obj:
                    fazendas_resp.append(FazendaAcessoResponse(unidade_produtiva_id=fazenda_obj.id, nome=fazenda_obj.nome))
                    
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

    # ==================== CRIAÇÃO DE NOVA ASSINATURA ====================

    async def create_tenant_for_user(
        self,
        user_id: uuid.UUID,
        nome: str,
        plano_id: uuid.UUID,
        ciclo: str = "MENSAL",
        cpf_cnpj: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        """
        Cria um novo tenant (assinatura/produtor) para um usuário já autenticado.
        Retorna um novo JWT no contexto do tenant recém-criado.
        """
        # Verificar plano
        plano = (await self.session.execute(
            select(PlanoAssinatura).where(PlanoAssinatura.id == plano_id, PlanoAssinatura.ativo == True)
        )).scalar_one_or_none()
        if not plano:
            raise HTTPException(status_code=404, detail="Plano não encontrado")

        agora = datetime.now(timezone.utc)

        # 1. Criar Tenant
        tenant = Tenant(nome=nome, documento=cpf_cnpj or "", slug="", ativo=True)
        self.session.add(tenant)
        await self.session.flush()  # gera tenant.id

        # 2. Vincular usuário como owner
        tu = TenantUsuario(
            tenant_id=tenant.id,
            usuario_id=user_id,
            is_owner=True,
            status="ATIVO",
        )
        self.session.add(tu)

        # 3. Criar assinatura
        is_trial = not plano.is_free and plano.tem_trial
        if plano.is_free:
            status_assin = "ATIVA"
            trial_expira_em = None
            primeiro_vencimento = None
        else:
            status_assin = "TRIAL" if is_trial else "ATIVA"
            trial_expira_em = agora + timedelta(days=plano.dias_trial) if is_trial else None
            # Vencimento = dia seguinte ao fim do trial
            primeiro_vencimento = (trial_expira_em + timedelta(days=1)).date() if trial_expira_em else None

        assin = AssinaturaTenant(
            tenant_id=tenant.id,
            plano_id=plano.id,
            tipo_assinatura="TENANT",
            ciclo_pagamento=ciclo,
            status=status_assin,
            data_inicio=agora,
            data_proxima_renovacao=trial_expira_em,
        )
        self.session.add(assin)
        await self.session.flush()  # gera assin.id

        # 6. Criar Fatura (APENAS se plano pago e tem trial)
        if not plano.is_free and is_trial and primeiro_vencimento:
            from decimal import Decimal
            valor_fatura = Decimal(str(plano.preco_anual)) if ciclo == "ANUAL" else Decimal(str(plano.preco_mensal))
            vencimento_datetime = datetime.combine(primeiro_vencimento, datetime.min.time(), tzinfo=timezone.utc)
            fatura = Fatura(
                tenant_id=tenant.id,
                assinatura_id=assin.id,
                valor=valor_fatura,
                data_vencimento=vencimento_datetime,
                status="ABERTA",
            )
            self.session.add(fatura)
            logger.info(f"Fatura criada para assinatura {assin.id}: R${valor_fatura} vence em {primeiro_vencimento}")

        await self.session.commit()

        # 7. Buscar usuário para email
        usuario = (await self.session.execute(select(Usuario).where(Usuario.id == user_id))).scalar_one_or_none()

        # 8. Enviar email com aviso de trial (background, sem bloquear)
        if usuario and not plano.is_free and is_trial:
            from core.services.email_service import email_service
            try:
                dias_trial = plano.dias_trial
                await email_service.send_trial_notice(
                    email=usuario.email,
                    nome=usuario.nome_completo or usuario.username,
                    nome_produtor=nome,
                    nome_plano=plano.nome,
                    dias_trial=dias_trial,
                    data_vencimento=primeiro_vencimento,
                    tenant_id=tenant.id,
                )
                logger.info(f"Email de trial enviado para {usuario.email}")
            except Exception as e:
                logger.error(f"Erro ao enviar email de trial: {e}")

        # 9. Gerar token no contexto do novo tenant
        token = await self.generate_token_for_tenant(user_id, tenant.id, ip_address, user_agent)

        return {
            "access_token": token,
            "tenant_id": tenant.id,
            "nome_tenant": nome,
            "is_trial": is_trial,
            "trial_expira_em": trial_expira_em,
            "data_primeiro_vencimento": primeiro_vencimento,
        }

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
