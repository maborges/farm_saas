from __future__ import annotations

from fastapi import Depends, HTTPException, status, Request
from loguru import logger
from jose import JWTError, jwt
from core.config import settings
from typing import TYPE_CHECKING, List, Optional, AsyncGenerator
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from core.database import async_session_maker, DB_URL

if TYPE_CHECKING:
    from core.constants import PlanTier

# ==============================================================================
# CORE DEPENDENCIES (Top-level)
# ==============================================================================

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para injeção comum de Sessão (sem forçar tenant, ex: login livre)"""
    async with async_session_maker() as session:
        yield session

def get_token(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    return authorization.split(" ")[1]

async def get_current_user_claims(token: str = Depends(get_token)) -> dict:
    """Extrai as claims do JWT."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tokens invádilo ou expirado",
        )

async def get_tenant_id(
    request: Request,
    claims: dict = Depends(get_current_user_claims)
) -> uuid.UUID:
    """Recupera e garante que o usuário pertence ao Tenant que ele está tentando operar."""
    tenant_id_str = claims.get("tenant_id")
    if not tenant_id_str:
        logger.warning(f"Tentativa de requisição sem tenant no JWT. UserId: {claims.get('sub')}")
        raise HTTPException(status_code=403, detail="Tenant context missing")
    
    return uuid.UUID(tenant_id_str)

async def get_session_with_tenant(
    tenant_id: uuid.UUID = Depends(get_tenant_id)
) -> AsyncGenerator[AsyncSession, None]:
    """Dependency que abre conexão com postgres injetando a claim local para o RLS."""
    async with async_session_maker() as session:
        session.info["tenant_id"] = tenant_id
        if "postgresql" in DB_URL:
            await session.execute(
                text(f"SET LOCAL app.current_tenant_id = '{tenant_id}';")
            )
        yield session

async def get_current_user(
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session)
):
    """Retorna o objeto Usuario completo do banco de dados."""
    from core.models.auth import Usuario
    user_id_str = claims.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido: sem identificador de usuário.")
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido: ID de usuário malformado.")

    result = await session.execute(select(Usuario).where(Usuario.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado ou inativo.")
    return user

async def get_current_tenant(
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session)
):
    """Retorna o objeto Tenant completo do banco."""
    from core.models.tenant import Tenant
    tenant_id_str = claims.get("tenant_id")
    if not tenant_id_str:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contexto de tenant ausente no token.")
    try:
        tenant_id = uuid.UUID(tenant_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token inválido: tenant ID malformado.")

    result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant or not tenant.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant não encontrado ou inativo.")
    return tenant

async def get_current_admin(claims: dict = Depends(get_current_user_claims)) -> dict:
    """Garante que o usuário é um administrador global do SaaS."""
    if not claims.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito ao Backoffice administrativo."
        )
    return claims

# ==============================================================================
# SECURITY GATES (RBAC / Feature Flags)
# ==============================================================================

def require_module(required_module: str):
    """Feature Gate Dinâmico - Valida se o Tenant tem o módulo contratado."""
    async def _dependency(
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.billing import AssinaturaTenant, PlanoAssinatura
        from core.constants import Modulos

        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")

        tenant_id = uuid.UUID(tenant_id_str)
        allowed_modules = claims.get("modules", [])

        if not allowed_modules:
            stmt = (
                select(PlanoAssinatura.modulos_inclusos)
                .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                .where(
                    AssinaturaTenant.tenant_id == tenant_id,
                    AssinaturaTenant.status == "ATIVA"
                )
            )
            result = await session.execute(stmt)
            modulos_db = result.scalar_one_or_none()
            allowed_modules = modulos_db if modulos_db else []

        if Modulos.CORE not in allowed_modules:
            logger.error(f"CRITICAL: Tenant {tenant_id} sem módulo CORE")
            raise HTTPException(status_code=403, detail="Licença base inválida. Contate o suporte.")

        if required_module not in allowed_modules:
            from core.constants import ModuloMetadata
            modulo_info = ModuloMetadata.get_modulo_info(required_module)
            modulo_nome = modulo_info.get("nome", required_module)
            raise HTTPException(
                status_code=402,
                detail=f"Módulo '{modulo_nome}' não contratado. Faça upgrade do seu plano.",
                headers={"X-Module-Required": required_module}
            )
        return True
    return _dependency

def require_tier(minimum_tier: "PlanTier"):
    """Feature Gate de Tier — valida se o tenant tem o tier mínimo exigido."""
    async def _dependency(
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.billing import AssinaturaTenant, PlanoAssinatura
        from core.constants import PlanTier

        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")

        tenant_id = uuid.UUID(tenant_id_str)
        tier_str = claims.get("plan_tier")

        if not tier_str:
            stmt = (
                select(PlanoAssinatura.plan_tier)
                .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                .where(
                    AssinaturaTenant.tenant_id == tenant_id,
                    AssinaturaTenant.status == "ATIVA",
                    AssinaturaTenant.tipo_assinatura == "PRINCIPAL",
                )
                .limit(1)
            )
            result = await session.execute(stmt)
            tier_str = result.scalar_one_or_none()

        if not tier_str:
            raise HTTPException(status_code=402, detail="Sem assinatura ativa. Contate o suporte.")

        try:
            tenant_tier = PlanTier(tier_str)
        except ValueError:
            raise HTTPException(status_code=402, detail="Configuração de plano inválida.")

        if tenant_tier < minimum_tier:
            raise HTTPException(
                status_code=402,
                detail=f"Esta funcionalidade requer o plano {minimum_tier.value}. Faça upgrade.",
                headers={"X-Tier-Required": minimum_tier.value, "X-Tier-Current": tenant_tier.value},
            )
        return tenant_tier
    return _dependency

def require_any_module(*required_modules: str):
    """Feature Gate que permite acesso se o tenant tiver QUALQUER UM dos módulos listados."""
    async def _dependency(
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.billing import AssinaturaTenant, PlanoAssinatura
        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")
        tenant_id = uuid.UUID(tenant_id_str)
        allowed_modules = claims.get("modules", [])
        if not allowed_modules:
            stmt = (
                select(PlanoAssinatura.modulos_inclusos)
                .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                .where(AssinaturaTenant.tenant_id == tenant_id, AssinaturaTenant.status == "ATIVA")
            )
            result = await session.execute(stmt)
            modulos_db = result.scalar_one_or_none()
            allowed_modules = modulos_db if modulos_db else []
        if not any(mod in allowed_modules for mod in required_modules):
            raise HTTPException(
                status_code=402,
                detail=f"Acesso negado. É necessário contratar um dos módulos: {', '.join(required_modules)}",
            )
        return True
    return _dependency

def require_all_modules(*required_modules: str):
    """Feature Gate que permite acesso APENAS se o tenant tiver TODOS os módulos listados."""
    async def _dependency(
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.billing import AssinaturaTenant, PlanoAssinatura
        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")
        tenant_id = uuid.UUID(tenant_id_str)
        allowed_modules = claims.get("modules", [])
        if not allowed_modules:
            stmt = (
                select(PlanoAssinatura.modulos_inclusos)
                .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                .where(AssinaturaTenant.tenant_id == tenant_id, AssinaturaTenant.status == "ATIVA")
            )
            result = await session.execute(stmt)
            modulos_db = result.scalar_one_or_none()
            allowed_modules = modulos_db if modulos_db else []
        missing = [mod for mod in required_modules if mod not in allowed_modules]
        if missing:
            raise HTTPException(
                status_code=402,
                detail=f"Acesso negado. Você precisa dos módulos: {', '.join(missing)}",
            )
        return True
    return _dependency

def require_role(roles_allowed: List[str]):
    async def _dependency(
        request: Request,
        claims: dict = Depends(get_current_user_claims)
    ):
        target_fazenda_id = request.headers.get("x-fazenda-id")
        fazendas_auth = claims.get("fazendas_auth", [])
        role = next((f.get("role") for f in fazendas_auth if f.get("id") == target_fazenda_id), None)
        if not role or role not in roles_allowed:
            raise HTTPException(status_code=403, detail="Role insuficiente nesta Fazenda de trabalho")
        return claims
    return _dependency

def require_permission(permissao: str):
    """Dependency para verificar permissão específica do admin do backoffice."""
    async def dependency(
        claims: dict = Depends(get_current_admin),
        session: AsyncSession = Depends(get_session)
    ):
        from core.constants import BackofficePermissions
        from core.models.admin_user import AdminUser
        if claims.get("is_superuser"):
            return claims
        user_id_str = claims.get("sub")
        if user_id_str:
            try:
                admin_id = uuid.UUID(user_id_str)
                result = await session.execute(
                    select(AdminUser).where(AdminUser.id == admin_id, AdminUser.ativo == True)
                )
                admin_user = result.scalar_one_or_none()
                if admin_user and (admin_user.tem_permissao(permissao) or BackofficePermissions.has_permission(admin_user.role, permissao)):
                    return claims
            except ValueError:
                pass
        role = claims.get("role", "admin")
        if BackofficePermissions.has_permission(role, permissao):
            return claims
        raise HTTPException(status_code=403, detail=f"Permissão negada: {permissao}")
    return dependency

def require_tenant_permission(permission: str):
    """Dependency para verificar permissão específica no contexto do tenant."""
    async def _dependency(
        request: Request,
        tenant_id: uuid.UUID = Depends(get_tenant_id),
        user: "Usuario" = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
    ):
        from core.constants import TenantPermissions, TenantRoles
        from core.models.auth import TenantUsuario, PerfilAcesso, FazendaUsuario
        stmt = (
            select(TenantUsuario, PerfilAcesso)
            .outerjoin(PerfilAcesso, TenantUsuario.perfil_id == PerfilAcesso.id)
            .where(TenantUsuario.tenant_id == tenant_id, TenantUsuario.usuario_id == user.id, TenantUsuario.status == "ATIVO")
        )
        result = await session.execute(stmt)
        row = result.first()
        if not row:
            raise HTTPException(status_code=403, detail="Usuário não tem acesso a este tenant")
        tenant_usuario, perfil_acesso = row
        if tenant_usuario.is_owner:
            return True
        fazenda_id_header = request.headers.get("x-fazenda-id")
        if fazenda_id_header:
            try:
                fazenda_id = uuid.UUID(fazenda_id_header)
                stmt_f = select(FazendaUsuario, PerfilAcesso).outerjoin(PerfilAcesso, FazendaUsuario.perfil_fazenda_id == PerfilAcesso.id).where(FazendaUsuario.tenant_id == tenant_id, FazendaUsuario.usuario_id == user.id, FazendaUsuario.fazenda_id == fazenda_id)
                res_f = await session.execute(stmt_f)
                row_f = res_f.first()
                if row_f and row_f[1]: perfil_acesso = row_f[1]
            except ValueError: pass
        if perfil_acesso:
            if TenantPermissions.has_permission(perfil_acesso.nome.lower(), permission, perfil_acesso.permissoes if perfil_acesso.is_custom else None):
                return True
        raise HTTPException(status_code=403, detail=f"Permissão negada: {permission}")
    return _dependency
