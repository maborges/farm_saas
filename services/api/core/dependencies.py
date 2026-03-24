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

# Simulating OAuth2 scheme locally or extracting from headers (Bearer)
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
        # Aqui o payload teria algo como: 
        # { "sub": "userid", "tenant_id": "xyz", "modules": ["CORE", "A1", "F1"], "fazendas": [{...}] }
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tokens invádilo ou expirado",
        )

# -- TIER 1 de Segurança: Tenant
async def get_tenant_id(
    request: Request,
    claims: dict = Depends(get_current_user_claims)
) -> uuid.UUID:
    """
    Recupera e garante que o usuário pertence ao Tenant que ele está tentando operar.
    Isso é alimentado para o BaseService e pro Database Session RLS.
    """
    # Exemplo: Lemos do token
    tenant_id_str = claims.get("tenant_id")
    if not tenant_id_str:
        logger.warning(f"Tentativa de requisição sem tenant no JWT. UserId: {claims.get('sub')}")
        raise HTTPException(status_code=403, detail="Tenant context missing")
    
    return uuid.UUID(tenant_id_str)

# -- TIER 2 de Segurança: Feature Flags Componiveis
def require_module(required_module: str):
    """
    Feature Gate Dinâmico - Valida se o Tenant tem o módulo contratado.

    Estratégia de validação em 2 níveis:
    1. Verifica no JWT (cache rápido) - claims["modules"]
    2. Se não estiver no JWT, consulta banco de dados (source of truth)

    Args:
        required_module: ID do módulo (ex: "A1_PLANEJAMENTO", "P1_REBANHO")

    Raises:
        HTTPException 402: Módulo não contratado
        HTTPException 403: Sem licença base
    """
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

        # Estratégia 1: Verificar cache do JWT (rápido)
        allowed_modules = claims.get("modules", [])

        # Estratégia 2: Se não estiver no cache, consultar banco (source of truth)
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

            # Log para debug - módulos carregados do banco
            logger.debug(f"Módulos carregados do DB para tenant {tenant_id}: {allowed_modules}")

        # Validação: Todo tenant precisa ter CORE
        if Modulos.CORE not in allowed_modules:
            logger.error(f"CRITICAL: Tenant {tenant_id} sem módulo CORE")
            raise HTTPException(
                status_code=403,
                detail="Licença base inválida. Contate o suporte."
            )

        # Validação: Módulo específico contratado?
        if required_module not in allowed_modules:
            logger.info(
                f"ACCESS_DENIED - Tenant {tenant_id} tentou acessar módulo {required_module}. "
                f"Módulos contratados: {allowed_modules}"
            )
            from core.constants import ModuloMetadata
            modulo_info = ModuloMetadata.get_modulo_info(required_module)
            modulo_nome = modulo_info.get("nome", required_module)

            raise HTTPException(
                status_code=402,  # Payment Required
                detail=f"Módulo '{modulo_nome}' não contratado. Faça upgrade do seu plano.",
                headers={"X-Module-Required": required_module}
            )

        return True

    return _dependency


def require_tier(minimum_tier: "PlanTier"):
    """
    Feature Gate de Tier — valida se o tenant tem o tier mínimo exigido.

    Governa a profundidade de funcionalidades financeiras em qualquer módulo.
    Complementa require_module(): módulo ativo E tier suficiente.

    Estratégia em 2 níveis:
    1. JWT claim "plan_tier" (cache rápido)
    2. DB via AssinaturaTenant → PlanoAssinatura (source of truth)

    Args:
        minimum_tier: Tier mínimo exigido (PlanTier.BASICO / PROFISSIONAL / PREMIUM)

    Raises:
        HTTPException 402: Tier insuficiente — sugere upgrade

    Exemplo:
        @router.post("/rateio", dependencies=[
            Depends(require_module("A1_PLANEJAMENTO")),
            Depends(require_tier(PlanTier.PROFISSIONAL)),
        ])
    """
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

        # Estratégia 1: JWT cache (rápido)
        tier_str = claims.get("plan_tier")

        # Estratégia 2: banco de dados (source of truth)
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
            logger.error(f"CRITICAL: Tenant {tenant_id} sem plano ativo")
            raise HTTPException(status_code=402, detail="Sem assinatura ativa. Contate o suporte.")

        try:
            tenant_tier = PlanTier(tier_str)
        except ValueError:
            logger.error(f"plan_tier inválido '{tier_str}' para tenant {tenant_id}")
            raise HTTPException(status_code=402, detail="Configuração de plano inválida.")

        if tenant_tier < minimum_tier:
            logger.info(
                f"TIER_DENIED - Tenant {tenant_id} (tier={tenant_tier.value}) "
                f"tentou acessar recurso que exige {minimum_tier.value}"
            )
            raise HTTPException(
                status_code=402,
                detail=f"Esta funcionalidade requer o plano {minimum_tier.value}. Faça upgrade.",
                headers={"X-Tier-Required": minimum_tier.value, "X-Tier-Current": tenant_tier.value},
            )

        return tenant_tier

    return _dependency


def require_any_module(*required_modules: str):
    """
    Feature Gate que permite acesso se o tenant tiver QUALQUER UM dos módulos listados.
    Útil para funcionalidades compartilhadas entre módulos.

    Exemplo:
        # Relatórios financeiros podem ser acessados por quem tem F1 OU F2
        @router.get("/", dependencies=[Depends(require_any_module("F1_TESOURARIA", "F2_CUSTOS_ABC"))])

    Args:
        *required_modules: Lista de IDs de módulos aceitos

    Raises:
        HTTPException 402: Nenhum dos módulos necessários contratado
    """
    async def _dependency(
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.billing import AssinaturaTenant, PlanoAssinatura

        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")

        tenant_id = uuid.UUID(tenant_id_str)

        # Carregar módulos (cache ou DB)
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

        # Verificar se TEM PELO MENOS UM dos módulos necessários
        has_any = any(mod in allowed_modules for mod in required_modules)

        if not has_any:
            logger.info(
                f"ACCESS_DENIED - Tenant {tenant_id} tentou acessar recurso que requer "
                f"qualquer um de {required_modules}. Módulos contratados: {allowed_modules}"
            )
            raise HTTPException(
                status_code=402,
                detail=f"Acesso negado. É necessário contratar um dos módulos: {', '.join(required_modules)}",
            )

        return True

    return _dependency


def require_all_modules(*required_modules: str):
    """
    Feature Gate que permite acesso APENAS se o tenant tiver TODOS os módulos listados.
    Útil para funcionalidades avançadas que integram múltiplos módulos.

    Exemplo:
        # Rateio de custos agrícolas requer tanto planejamento quanto financeiro
        @router.get("/", dependencies=[Depends(require_all_modules("A1_PLANEJAMENTO", "F2_CUSTOS_ABC"))])

    Args:
        *required_modules: Lista de IDs de módulos obrigatórios

    Raises:
        HTTPException 402: Algum módulo necessário não contratado
    """
    async def _dependency(
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.billing import AssinaturaTenant, PlanoAssinatura

        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")

        tenant_id = uuid.UUID(tenant_id_str)

        # Carregar módulos (cache ou DB)
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

        # Verificar se TEM TODOS os módulos necessários
        missing_modules = [mod for mod in required_modules if mod not in allowed_modules]

        if missing_modules:
            logger.info(
                f"ACCESS_DENIED - Tenant {tenant_id} tentou acessar recurso que requer "
                f"TODOS os módulos {required_modules}. Faltam: {missing_modules}"
            )
            raise HTTPException(
                status_code=402,
                detail=f"Acesso negado. Você precisa dos módulos: {', '.join(missing_modules)}",
            )

        return True

    return _dependency

# -- TIER 3 de Segurança: RBAC Local da Fazenda 
def require_role(roles_allowed: List[str]):
    async def _dependency(
        request: Request,
        claims: dict = Depends(get_current_user_claims)
    ):
        # Lê de qual Fazenda ele está reportando do Header customizado front-end
        target_fazenda_id = request.headers.get("x-fazenda-id")
        
        # Array simulando "fazendas_auth": [{"id":"f1", "role":"gerente"}, {"id":"f2", "role":"peao"}]
        fazendas_auth = claims.get("fazendas_auth", [])
        
        role_nesta_fazenda = None
        for f in fazendas_auth:
            if f.get("id") == target_fazenda_id:
                role_nesta_fazenda = f.get("role")
                break
                
        if not role_nesta_fazenda or role_nesta_fazenda not in roles_allowed:
            raise HTTPException(status_code=403, detail="Role insuficiente nesta Fazenda de trabalho")
            
        return role_nesta_fazenda
    return _dependency


# DEPRECATED: Usar BackofficePermissions de core.constants
# Mantido por compatibilidade temporária
ADMIN_PERMISSIONS = {
    "super_admin": ["*"],
    "admin": [
        "dashboard:view",
        "assinantes:*",
        "assinaturas:*",
        "suporte:*",
        "pacotes:*",
        "cupons:*",
        "emails:*",
        "financeiro:view"
    ],
    "suporte": [
        "dashboard:view",
        "assinantes:view",
        "suporte:*"
    ],
    "financeiro": [
        "dashboard:view",
        "financeiro:*",
        "assinantes:view"
    ],
    "comercial": [
        "dashboard:view",
        "pacotes:*",
        "cupons:*",
        "assinaturas:*"
    ]
}


def require_permission(permissao: str):
    """
    Dependency para verificar permissão específica do admin do backoffice.

    Uso:
        @router.get("/tenants", dependencies=[Depends(require_permission("backoffice:tenants:view"))])
        @router.post("/plans", dependencies=[Depends(require_permission("backoffice:plans:create"))])
    """
    async def dependency(
        claims: dict = Depends(get_current_admin),
        session: AsyncSession = Depends(get_session)
    ):
        from core.constants import BackofficePermissions
        from core.models.admin_user import AdminUser

        # Se é superuser, permite tudo
        if claims.get("is_superuser"):
            return claims

        # Buscar AdminUser do banco para obter role atualizada
        user_id_str = claims.get("sub")
        if user_id_str:
            try:
                admin_id = uuid.UUID(user_id_str)
                result = await session.execute(
                    select(AdminUser).where(AdminUser.id == admin_id, AdminUser.ativo == True)
                )
                admin_user = result.scalar_one_or_none()

                if admin_user:
                    # Usar método do AdminUser
                    if admin_user.tem_permissao(permissao):
                        return claims

                    # Se não tem permissão, verificar usando novo sistema
                    if BackofficePermissions.has_permission(admin_user.role, permissao):
                        return claims

            except ValueError:
                pass

        # Fallback: verificar usando role do JWT
        role = claims.get("role", "admin")
        if BackofficePermissions.has_permission(role, permissao):
            return claims

        logger.warning(
            f"ACCESS_DENIED - Admin {user_id_str} (role={role}) tentou acessar: {permissao}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permissão negada: {permissao}"
        )

    return dependency

async def get_current_admin(claims: dict = Depends(get_current_user_claims)) -> dict:
    """Garante que o usuário é um administrador global do SaaS."""
    if not claims.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito ao Backoffice administrativo."
        )
    return claims

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para injeção comum de Sessão (sem forçar tenant, ex: login livre)"""
    async with async_session_maker() as session:
        yield session

async def get_session_with_tenant(
    tenant_id: uuid.UUID = Depends(get_tenant_id)
) -> AsyncGenerator[AsyncSession, None]:
    """Dependency que abre conexão com postgres injetando a claim local para o RLS."""
    async with async_session_maker() as session:
        session.info["tenant_id"] = tenant_id
        # Ignora flag de Postgres caso usando fallback sqlite local
        if "postgresql" in DB_URL:
            await session.execute(
                text(f"SET LOCAL app.current_tenant_id = '{tenant_id}';")
            )
        yield session


async def get_current_user(
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna o objeto Usuario completo do banco de dados a partir das claims do JWT.

    Args:
        claims: payload do JWT decodificado
        session: sessão de banco de dados
    Returns:
        Usuario: objeto de usuário autenticado
    Raises:
        HTTPException 401: se o usuário não existir ou estiver inativo
    """
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
    """
    Retorna o objeto Tenant completo do banco a partir das claims do JWT.

    Args:
        claims: payload do JWT decodificado
        session: sessão de banco de dados
    Returns:
        Tenant: objeto do tenant autenticado
    Raises:
        HTTPException 403: se o tenant não existir ou estiver inativo
    """
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


def require_tenant_permission(permission: str):
    """
    Dependency para verificar permissão específica no contexto do tenant.

    Verifica permissões baseado no perfil do usuário no tenant (TenantUsuario.perfil_id).
    Suporta perfis customizados e override por fazenda.

    Uso:
        @router.get("/team/users", dependencies=[Depends(require_tenant_permission("tenant:users:view"))])
        @router.post("/team/invite", dependencies=[Depends(require_tenant_permission("tenant:users:invite"))])

    Hierarquia de permissões:
        1. Owner do tenant → acesso total
        2. Perfil customizado (PerfilAcesso.permissoes JSON)
        3. Perfil padrão (TenantPermissions)
        4. Override por fazenda (FazendaUsuario.perfil_fazenda_id)
    """
    async def _dependency(
        request: Request,
        tenant_id: uuid.UUID = Depends(get_tenant_id),
        user: "Usuario" = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
    ):
        from core.constants import TenantPermissions, TenantRoles
        from core.models.auth import TenantUsuario, PerfilAcesso, FazendaUsuario

        # Buscar vínculo do usuário com o tenant
        stmt = (
            select(TenantUsuario, PerfilAcesso)
            .outerjoin(PerfilAcesso, TenantUsuario.perfil_id == PerfilAcesso.id)
            .where(
                TenantUsuario.tenant_id == tenant_id,
                TenantUsuario.usuario_id == user.id,
                TenantUsuario.status == "ATIVO"
            )
        )
        result = await session.execute(stmt)
        row = result.first()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não tem acesso a este tenant"
            )

        tenant_usuario, perfil_acesso = row

        # Owner tem acesso total
        if tenant_usuario.is_owner:
            return True

        # Verificar se há override por fazenda específica
        fazenda_id_header = request.headers.get("x-fazenda-id")
        if fazenda_id_header:
            try:
                fazenda_id = uuid.UUID(fazenda_id_header)
                stmt_fazenda = (
                    select(FazendaUsuario, PerfilAcesso)
                    .outerjoin(PerfilAcesso, FazendaUsuario.perfil_fazenda_id == PerfilAcesso.id)
                    .where(
                        FazendaUsuario.tenant_id == tenant_id,
                        FazendaUsuario.usuario_id == user.id,
                        FazendaUsuario.fazenda_id == fazenda_id
                    )
                )
                result_fazenda = await session.execute(stmt_fazenda)
                row_fazenda = result_fazenda.first()

                if row_fazenda and row_fazenda[1]:  # Tem perfil específico da fazenda
                    perfil_acesso = row_fazenda[1]  # Sobrescreve o perfil do tenant

            except ValueError:
                pass  # Ignora fazenda_id inválido

        # Verificar permissão
        if perfil_acesso:
            # Perfil customizado ou padrão
            role_nome = perfil_acesso.nome.lower()
            custom_perms = perfil_acesso.permissoes if perfil_acesso.is_custom else None

            has_perm = TenantPermissions.has_permission(
                role=role_nome,
                permission=permission,
                custom_permissions=custom_perms
            )

            if has_perm:
                return True

        logger.warning(
            f"ACCESS_DENIED - User {user.id} (tenant={tenant_id}) "
            f"tentou acessar: {permission} (perfil={perfil_acesso.nome if perfil_acesso else 'NONE'})"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permissão negada: {permission}"
        )

    return _dependency
