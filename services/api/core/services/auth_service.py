from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from typing import Optional
import uuid

from core.models.auth import Usuario, TenantUsuario, PerfilAcesso, FazendaUsuario
from core.models.tenant import Tenant
from core.models.fazenda import Fazenda
from core.models.billing import AssinaturaTenant, PlanoAssinatura
from core.schemas.auth_schemas import LoginRequest, UserCreateRequest, TenantAcessoResponse, FazendaAcessoResponse, PerfilSimplesResponse, UsuarioMeResponse
from core.config import settings

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

    async def authenticate_user(self, login_data: LoginRequest) -> tuple[Usuario, str]:
        stmt = select(Usuario).where(Usuario.email == login_data.email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.senha_hash:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")
            
        if not self.verify_password(login_data.senha, user.senha_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")
            
        if not user.ativo:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
            
        # Build the dynamic token claims based on the first tenant or default structure
        # A good SaaS token only holds current "active" tenant context, not ALL tenants.
        # But our old mock injected all. Let's find first active tenant to inject as default context.
        
        tenant_usuario_stmt = select(TenantUsuario).where(TenantUsuario.usuario_id == user.id, TenantUsuario.status == "ATIVO")
        tenant_usuarios = (await self.session.execute(tenant_usuario_stmt)).scalars().all()
        
        default_tenant_id = None
        modulos = ["CORE"]
        fazendas_auth = []
        
        # Superadministradores não entram vinculados a nenhum tenant por padrão.
        # Eles entram no contexto de Gestão Global.
        if not user.is_superuser and tenant_usuarios:
            first_tu = tenant_usuarios[0]
            default_tenant_id = str(first_tu.tenant_id)
            
            # Fetch tenant to get modules
            tenant_stmt = select(Tenant).where(Tenant.id == first_tu.tenant_id)
            tenant = (await self.session.execute(tenant_stmt)).scalar_one_or_none()
            if tenant:
                modulos = tenant.modulos_ativos
                
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

        # Resolve plan_tier da assinatura PRINCIPAL ativa do tenant
        plan_tier = "BASICO"
        if default_tenant_id:
            tier_stmt = (
                select(PlanoAssinatura.plan_tier)
                .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                .where(
                    AssinaturaTenant.tenant_id == first_tu.tenant_id,
                    AssinaturaTenant.tipo_assinatura == "PRINCIPAL",
                    AssinaturaTenant.status == "ATIVA",
                )
                .limit(1)
            )
            plan_tier = (await self.session.execute(tier_stmt)).scalar_one_or_none() or "BASICO"

        # Generate token payload
        claims = {
            "sub": str(user.id),
            "tenant_id": default_tenant_id,
            "modules": modulos,
            "fazendas_auth": fazendas_auth,
            "is_superuser": user.is_superuser,
            "plan_tier": plan_tier,
        }
        
        access_token = self.create_access_token(data=claims)
        return user, access_token

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
            p_stmt = select(PerfilAcesso).where(PerfilAcesso.id == tu.perfil_id)
            perfil = (await self.session.execute(p_stmt)).scalar_one()
            
            # get fazendas
            fu_stmt = select(FazendaUsuario).where(FazendaUsuario.usuario_id == user.id, FazendaUsuario.tenant_id == tenant.id)
            f_links = (await self.session.execute(fu_stmt)).scalars().all()
            fazendas_resp = []
            for fl in f_links:
                f_stmt = select(Fazenda).where(Fazenda.id == fl.fazenda_id)
                fazenda_obj = (await self.session.execute(f_stmt)).scalar_one_or_none()
                if fazenda_obj:
                    fazendas_resp.append(FazendaAcessoResponse(fazenda_id=fazenda_obj.id, nome=fazenda_obj.nome))
                    
            # Query plan info (tier, limits, modules) for this tenant
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
                    AssinaturaTenant.tipo_assinatura == "PRINCIPAL",
                    AssinaturaTenant.status == "ATIVA",
                )
                .limit(1)
            )
            plan_row = (await self.session.execute(plan_stmt)).first()
            t_plan_tier = plan_row[0] if plan_row else "BASICO"
            t_max_fazendas = plan_row[1] if plan_row else 1
            t_modulos = plan_row[2] if plan_row else ["CORE"]
            t_max_usuarios = plan_row[3] if plan_row else 2

            tenants_response.append(TenantAcessoResponse(
                tenant_id=tenant.id,
                nome_tenant=tenant.nome,
                is_owner=tu.is_owner,
                perfil=PerfilSimplesResponse(id=perfil.id, nome=perfil.nome, permissoes=perfil.permissoes),
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
