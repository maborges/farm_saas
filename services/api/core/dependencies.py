from __future__ import annotations

from fastapi import Depends, HTTPException, status, Request
from loguru import logger
from jose import JWTError, jwt
from core.config import settings
from typing import TYPE_CHECKING, List, Optional, AsyncGenerator
import uuid
import hashlib
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from core.database import async_session_maker, DB_URL

# ---------------------------------------------------------------------------
# Cache simples TTL para validação de sessão (evita query por request)
# ---------------------------------------------------------------------------
_SESSION_CACHE: dict[str, tuple[bool, float]] = {}  # token_hash -> (is_valid, expires_at)
_SESSION_CACHE_TTL = 30  # segundos
_SESSION_CACHE_MAX = 2000

def _cache_get(token_hash: str) -> bool | None:
    entry = _SESSION_CACHE.get(token_hash)
    if entry and time.monotonic() < entry[1]:
        return entry[0]
    _SESSION_CACHE.pop(token_hash, None)
    return None

def _cache_set(token_hash: str, is_valid: bool) -> None:
    if len(_SESSION_CACHE) >= _SESSION_CACHE_MAX:
        # Evict oldest ~10%
        to_remove = sorted(_SESSION_CACHE, key=lambda k: _SESSION_CACHE[k][1])[:200]
        for k in to_remove:
            _SESSION_CACHE.pop(k, None)
    _SESSION_CACHE[token_hash] = (is_valid, time.monotonic() + _SESSION_CACHE_TTL)

def invalidate_session_cache(token_hash: str) -> None:
    """Invalida o cache de uma sessão específica (chamar ao revogar)."""
    _SESSION_CACHE.pop(token_hash, None)

if TYPE_CHECKING:
    from core.constants import PlanTier

# ==============================================================================
# CORE DEPENDENCIES (Top-level)
# ==============================================================================

async def get_session(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency de sessão. Se o middleware TenantRLSMiddleware tiver extraído
    um tenant_id do JWT, ativa RLS automaticamente — mesmo em routers que
    usam get_session em vez de get_session_with_tenant (fail-safe).
    """
    async with async_session_maker() as session:
        tenant_id = getattr(request.state, "rls_tenant_id", None) if request else None
        if tenant_id and "postgresql" in DB_URL:
            await session.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant_id}';"))
            session.info["tenant_id"] = tenant_id
        yield session

def get_token(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    return authorization.split(" ")[1]

async def get_current_user_claims(
    token: str = Depends(get_token),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Extrai as claims do JWT e valida se a sessão está ativa no banco."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    cached = _cache_get(token_hash)

    if cached is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão encerrada ou revogada")

    if cached is None:
        from core.models.sessao import SessaoAtiva
        result = await db.execute(
            select(SessaoAtiva.status).where(SessaoAtiva.token_hash == token_hash)
        )
        sessao_status = result.scalar_one_or_none()

        if sessao_status is not None and sessao_status != "ATIVA":
            _cache_set(token_hash, False)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão encerrada ou revogada")

        _cache_set(token_hash, True)

    return payload

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

async def get_user_id(
    claims: dict = Depends(get_current_user_claims)
) -> uuid.UUID | None:
    """Extrai o user_id (sub) do JWT para uso em audit logs."""
    sub = claims.get("sub")
    if sub:
        try:
            return uuid.UUID(sub)
        except (ValueError, AttributeError):
            pass
    return None

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

async def _resolve_grupo_id(
    request: Request,
    tenant_id: uuid.UUID,
    session: AsyncSession,
) -> uuid.UUID | None:
    """
    Compatibilidade temporária.

    O sistema não usa mais agrupamento por grupo. O tenant é a raiz de
    autorização e assinatura, então esta função existe apenas para não quebrar
    imports antigos.
    """
    return None


def _assinatura_ativa_filter():
    """
    Retorna a cláusula de status para assinaturas consideradas ativas.

    PENDENTE_PAGAMENTO é excluído intencionalmente: inadimplentes não passam nos
    feature gates. A carência (grace_period_days) é verificada separadamente pelo
    job de suspensão — não abre acesso a recursos durante a carência.
    """
    from core.models.billing import AssinaturaTenant
    from datetime import datetime, timezone
    return AssinaturaTenant.status.in_(["ATIVA", "TRIAL"])


async def _get_modulos_do_tenant(
    tenant_id: uuid.UUID,
    session: AsyncSession,
) -> list[str]:
    """Retorna módulos ativos das assinaturas do tenant."""
    from core.models.billing import AssinaturaTenant, PlanoAssinatura

    stmt = (
        select(PlanoAssinatura.modulos_inclusos)
        .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .where(
            AssinaturaTenant.tenant_id == tenant_id,
            _assinatura_ativa_filter(),
            AssinaturaTenant.tipo_assinatura == "TENANT",
        )
    )

    results = await session.execute(stmt)
    rows = results.scalars().all()

    # União de módulos de todas as assinaturas encontradas
    modulos: set[str] = set()
    for row in rows:
        if row:
            modulos.update(row)
    return list(modulos)


def require_module(required_module: str):
    """Feature Gate Dinâmico — valida se o tenant tem o módulo contratado."""
    async def _dependency(
        request: Request,
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.constants import Modulos

        # SaaS admin tem acesso irrestrito a todos os módulos
        if claims.get("is_superuser"):
            return

        tenant_id_str = claims.get("tenant_id")
        request_path = str(getattr(getattr(request, "url", None), "path", "")) if request else ""
        request_method = getattr(request, "method", "")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")

        tenant_id = uuid.UUID(tenant_id_str)
        allowed_modules = await _get_modulos_do_tenant(tenant_id, session)

        if Modulos.CORE not in allowed_modules:
            logger.error(f"CRITICAL: Tenant {tenant_id} sem módulo CORE")
            raise HTTPException(status_code=403, detail="Licença base inválida. Contate o suporte.")

        if required_module not in allowed_modules:
            from core.constants import ModuloMetadata
            modulo_info = ModuloMetadata.get_modulo_info(required_module)
            modulo_nome = modulo_info.get("nome", required_module)
            raise HTTPException(
                status_code=402,
                detail=f"Módulo '{modulo_nome}' não contratado neste tenant. Faça upgrade do plano.",
                headers={"X-Module-Required": required_module}
            )

        # Telemetria: incrementa contador diário de uso em background
        try:
            from core.services.module_usage_service import increment_module_usage
            from datetime import date
            await increment_module_usage(session, tenant_id, required_module, date.today())
            await session.commit()
        except Exception:
            pass  # Telemetria nunca deve bloquear a requisição

        return True
    return _dependency

def require_tier(minimum_tier: "PlanTier"):
    """Feature Gate de Tier — valida se o tenant tem o tier mínimo exigido."""
    async def _dependency(
        request: Request,
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.billing import AssinaturaTenant, PlanoAssinatura
        from core.constants import PlanTier

        tenant_id_str = claims.get("tenant_id")
        request_path = str(getattr(getattr(request, "url", None), "path", "")) if request else ""
        request_method = getattr(request, "method", "")
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
                    _assinatura_ativa_filter(),
                    AssinaturaTenant.tipo_assinatura == "TENANT",
                )
            )
            stmt = stmt.limit(1)
            result = await session.execute(stmt)
            tier_str = result.scalar_one_or_none()

        if not tier_str:
            logger.bind(
                event="monetization_blocked",
                surface="backend.require_tier",
                feature="tier_gate",
                tenant_id=str(tenant_id),
                required_tier=minimum_tier.value,
                current_tier=None,
                path=request_path,
                method=request_method,
                reason="missing_active_subscription",
            ).info("monetization_blocked")
            raise HTTPException(status_code=402, detail="Sem assinatura ativa. Contate o suporte.")

        try:
            tenant_tier = PlanTier(tier_str)
        except ValueError:
            logger.bind(
                event="monetization_blocked",
                surface="backend.require_tier",
                feature="tier_gate",
                tenant_id=str(tenant_id),
                required_tier=minimum_tier.value,
                current_tier=tier_str,
                path=request_path,
                method=request_method,
                reason="invalid_tier_configuration",
            ).info("monetization_blocked")
            raise HTTPException(status_code=402, detail="Configuração de plano inválida.")

        if tenant_tier < minimum_tier:
            logger.bind(
                event="monetization_blocked",
                surface="backend.require_tier",
                feature="tier_gate",
                tenant_id=str(tenant_id),
                required_tier=minimum_tier.value,
                current_tier=tenant_tier.value,
                path=request_path,
                method=request_method,
                reason="insufficient_tier",
            ).info("monetization_blocked")
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
        request: Request,
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")
        tenant_id = uuid.UUID(tenant_id_str)
        allowed_modules = await _get_modulos_do_tenant(tenant_id, session)
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
        request: Request,
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")
        tenant_id = uuid.UUID(tenant_id_str)
        allowed_modules = await _get_modulos_do_tenant(tenant_id, session)
        missing = [mod for mod in required_modules if mod not in allowed_modules]
        if missing:
            raise HTTPException(
                status_code=402,
                detail=f"Acesso negado. Você precisa dos módulos: {', '.join(missing)}",
            )
        return True
    return _dependency

def get_grupos_auth(claims: dict) -> list[str]:
    """Extrai a lista de grupo UUIDs autorizados do JWT."""
    return claims.get("grupos_auth", [])


def require_grupo_access():
    """
    Compatibilidade para endpoints que ainda enviam x-fazenda-id.

    O modelo atual não usa grupo. Então validamos apenas se o usuário é owner
    do tenant ou possui vínculo explícito à fazenda informada.
    """
    async def _dependency(
        request: Request,
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda
        from core.models.auth import TenantUsuario

        # is_owner bypasses group check
        tenant_id_str = claims.get("tenant_id")
        user_id_str = claims.get("sub")
        if not tenant_id_str or not user_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant/usuário ausente")

        tenant_id = uuid.UUID(tenant_id_str)
        user_id = uuid.UUID(user_id_str)

        tu_stmt = select(TenantUsuario).where(
            TenantUsuario.tenant_id == tenant_id,
            TenantUsuario.usuario_id == user_id,
            TenantUsuario.status == "ATIVO"
        )
        tu = (await session.execute(tu_stmt)).scalar_one_or_none()
        if tu and tu.is_owner:
            return True

        fazenda_id_header = request.headers.get("x-fazenda-id")
        if not fazenda_id_header:
            return True  # No fazenda context — skip group check

        try:
            unidade_produtiva_id = uuid.UUID(fazenda_id_header)
        except ValueError:
            raise HTTPException(status_code=400, detail="x-fazenda-id inválido")

        fazenda_stmt = select(Fazenda).where(
            Fazenda.id == unidade_produtiva_id,
            Fazenda.tenant_id == tenant_id
        )
        fazenda = (await session.execute(fazenda_stmt)).scalar_one_or_none()
        if not fazenda:
            raise HTTPException(status_code=404, detail="Fazenda não encontrada")

        from core.models.auth import FazendaUsuario
        fu_stmt = select(FazendaUsuario).where(
            FazendaUsuario.tenant_id == tenant_id,
            FazendaUsuario.usuario_id == user_id,
            FazendaUsuario.unidade_produtiva_id == unidade_produtiva_id
        )
        fu = (await session.execute(fu_stmt)).scalar_one_or_none()
        if not fu:
            from loguru import logger
            logger.warning(
                f"TenantViolationError: user {user_id} tentou acessar fazenda {unidade_produtiva_id} sem autorização"
            )
            raise HTTPException(status_code=403, detail="Acesso negado: você não tem acesso a esta fazenda")
        return True
    return _dependency


def require_role(roles_allowed: List[str]):
    async def _dependency(
        request: Request,
        claims: dict = Depends(get_current_user_claims)
    ):
        from loguru import logger
        target_fazenda_id = request.headers.get("x-fazenda-id")
        fazendas_auth = claims.get("fazendas_auth", [])
        role = next((f.get("role") for f in fazendas_auth if f.get("id") == target_fazenda_id), None)

        # Admin/Owner do tenant tem acesso implícito a todas as fazendas
        tenant_role = claims.get("role")
        is_superuser = claims.get("is_superuser", False)
        logger.debug(f"require_role: fazenda={target_fazenda_id}, role_from_db={role}, tenant_role={tenant_role}, is_superuser={is_superuser}")

        # Owner e admin do tenant são tratados como 'admin' para permissão
        if is_superuser or tenant_role in ("owner", "admin"):
            role = "admin"

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
                unidade_produtiva_id = uuid.UUID(fazenda_id_header)
                stmt_f = select(FazendaUsuario, PerfilAcesso).outerjoin(PerfilAcesso, FazendaUsuario.perfil_fazenda_id == PerfilAcesso.id).where(FazendaUsuario.tenant_id == tenant_id, FazendaUsuario.usuario_id == user.id, FazendaUsuario.unidade_produtiva_id == unidade_produtiva_id)
                res_f = await session.execute(stmt_f)
                row_f = res_f.first()
                if row_f and row_f[1]: perfil_acesso = row_f[1]
            except ValueError: pass
        if perfil_acesso:
            if TenantPermissions.has_permission(perfil_acesso.nome.lower(), permission, perfil_acesso.permissoes if perfil_acesso.is_custom else None):
                return True
        raise HTTPException(status_code=403, detail=f"Permissão negada: {permission}")
    return _dependency


# ==============================================================================
# DECORATOR COMPOSTO — módulo + permissão em uma só chamada
# ==============================================================================

def require_module_and_permission(module: str, permission: str):
    """
    Decorator que combina require_module + require_tenant_permission em uma única
    dependência — impossível usar um sem o outro.

    Substitui o padrão propenso a erro:
        @require_module("AGRICOLA")
        @require_tenant_permission("agricola:safra:criar")

    Uso:
        @router.post("/")
        async def create(
            _=Depends(require_module_and_permission("AGRICOLA", "agricola:safra:criar")),
            ...
        ):
    """
    _mod_dep = require_module(module)
    _perm_dep = require_tenant_permission(permission)

    async def _combined(
        _mod=Depends(_mod_dep),
        _perm=Depends(_perm_dep),
    ):
        return True

    return _combined


# ==============================================================================
# LIMIT VALIDATION GATES
# ==============================================================================

def require_limit(limit_type: str):
    """
    Feature Gate de Limites — valida se o tenant não ultrapassou o limite contratado.

    Tipos de limite suportados:
    - "max_fazendas": Número máximo de fazendas no tenant
    - "max_usuarios": Número máximo de usuários simultâneos
    - "max_categorias_plano": Categorias customizáveis no plano de contas
    - "storage_limite_mb": Limite de armazenamento em MB

    Uso em router:
        @router.post("/", dependencies=[Depends(require_limit("max_fazendas"))])
    """
    async def _dependency(
        request: Request,
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.billing import AssinaturaTenant, PlanoAssinatura
        from core.models.tenant import Tenant
        from sqlalchemy import func

        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant ausente")

        tenant_id = uuid.UUID(tenant_id_str)

        # Buscar assinatura ativa do tenant
        stmt = (
            select(PlanoAssinatura)
            .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
            .where(
                AssinaturaTenant.tenant_id == tenant_id,
                _assinatura_ativa_filter(),
                AssinaturaTenant.tipo_assinatura == "TENANT",
            )
        )
        stmt = stmt.limit(1)
        result = await session.execute(stmt)
        plano = result.scalar_one_or_none()

        if not plano:
            # Sem assinatura ativa — usar limites padrão ou bloquear
            logger.warning(f"Tenant {tenant_id} sem assinatura ativa para validação de limites")
            raise HTTPException(
                status_code=402,
                detail="Assinatura não encontrada. Por favor, contrate um plano.",
            )

        # Validar limite conforme tipo
        if limit_type == "max_fazendas":
            limite = plano.max_fazendas
            if limite == -1:
                return True  # Ilimitado

            # Contar fazendas atuais do tenant
            from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda
            count_stmt = select(func.count(Fazenda.id)).where(Fazenda.tenant_id == tenant_id, Fazenda.ativo == True)
            count_result = await session.execute(count_stmt)
            atual = count_result.scalar_one() or 0

            if atual >= limite:
                raise HTTPException(
                    status_code=402,
                    detail=f"Limite de {limite} fazendas atingido. Você tem {atual} fazenda(s) ativas. Faça upgrade do plano para adicionar mais.",
                    headers={"X-Limit-Type": "max_fazendas", "X-Limit-Max": str(limite), "X-Limit-Current": str(atual)},
                )

        elif limit_type == "max_usuarios":
            # Verificar primeiro o limite do plano
            limite = plano.limite_usuarios_maximo
            if limite is None:
                return True  # Ilimitado

            # Contar usuários ativos do tenant
            from core.models.auth import TenantUsuario
            count_stmt = select(func.count(TenantUsuario.id)).where(
                TenantUsuario.tenant_id == tenant_id,
                TenantUsuario.status == "ATIVO",
            )
            count_result = await session.execute(count_stmt)
            atual = count_result.scalar_one() or 0

            if atual >= limite:
                raise HTTPException(
                    status_code=402,
                    detail=f"Limite de {limite} usuários atingido. Você tem {atual} usuário(s) ativo(s). Faça upgrade do plano para adicionar mais.",
                    headers={"X-Limit-Type": "max_usuarios", "X-Limit-Max": str(limite), "X-Limit-Current": str(atual)},
                )

        elif limit_type == "max_categorias_plano":
            limite = plano.max_categorias_plano
            if limite == -1:
                return True  # Ilimitado

            # Contar categorias do plano de contas
            from financeiro.models.plano_conta import PlanoConta
            count_stmt = select(func.count(PlanoConta.id)).where(
                PlanoConta.tenant_id == tenant_id,
                PlanoConta.ativo == True,
            )
            count_result = await session.execute(count_stmt)
            atual = count_result.scalar_one() or 0

            if atual >= limite:
                raise HTTPException(
                    status_code=402,
                    detail=f"Limite de {limite} categorias atingido. Você tem {atual} categoria(s). Faça upgrade do plano para adicionar mais.",
                    headers={"X-Limit-Type": "max_categorias_plano", "X-Limit-Max": str(limite), "X-Limit-Current": str(atual)},
                )

        elif limit_type == "storage_limite_mb":
            # Buscar tenant para verificar storage
            tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
            tenant_result = await session.execute(tenant_stmt)
            tenant = tenant_result.scalar_one()

            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant não encontrado")

            limite = tenant.storage_limite_mb
            atual = tenant.storage_usado_mb

            if atual >= limite:
                raise HTTPException(
                    status_code=402,
                    detail=f"Limite de armazenamento atingido ({atual}/{limite} MB). Libere espaço ou faça upgrade do plano.",
                    headers={"X-Limit-Type": "storage_limite_mb", "X-Limit-Max": str(limite), "X-Limit-Current": str(atual)},
                )

        else:
            logger.error(f"Tipo de limite desconhecido: {limit_type}")
            raise HTTPException(status_code=500, detail="Tipo de limite não configurado")

        return True
    return _dependency


def check_limit_soft(limit_type: str) -> dict:
    """
    Verificação suave de limite — retorna status sem bloquear.

    Retorna: {"atual": int, "limite": int | None, "porcentagem": float, "atingido": bool}
    """
    async def _dependency(
        request: Request,
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session)
    ):
        from core.models.billing import AssinaturaTenant, PlanoAssinatura
        from core.models.tenant import Tenant
        from sqlalchemy import func

        tenant_id_str = claims.get("tenant_id")
        if not tenant_id_str:
            return {"atual": 0, "limite": 0, "porcentagem": 0.0, "atingido": False}

        tenant_id = uuid.UUID(tenant_id_str)

        # Buscar assinatura ativa do tenant
        stmt = (
            select(PlanoAssinatura)
            .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
            .where(
                AssinaturaTenant.tenant_id == tenant_id,
                _assinatura_ativa_filter(),
                AssinaturaTenant.tipo_assinatura == "TENANT",
            )
        )
        stmt = stmt.limit(1)
        result = await session.execute(stmt)
        plano = result.scalar_one_or_none()

        if not plano:
            return {"atual": 0, "limite": 0, "porcentagem": 0.0, "atingido": False}

        atual = 0
        limite = None

        if limit_type == "max_fazendas":
            limite = plano.max_fazendas
            if limite == -1:
                return {"atual": 0, "limite": None, "porcentagem": 0.0, "atingido": False}

            from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda
            count_stmt = select(func.count(Fazenda.id)).where(Fazenda.tenant_id == tenant_id, Fazenda.ativo == True)
            count_result = await session.execute(count_stmt)
            atual = count_result.scalar_one() or 0

        elif limit_type == "max_usuarios":
            limite = plano.limite_usuarios_maximo
            if limite is None:
                return {"atual": 0, "limite": None, "porcentagem": 0.0, "atingido": False}

            from core.models.auth import TenantUsuario
            count_stmt = select(func.count(TenantUsuario.id)).where(
                TenantUsuario.tenant_id == tenant_id,
                TenantUsuario.status == "ATIVO",
            )
            count_result = await session.execute(count_stmt)
            atual = count_result.scalar_one() or 0

        elif limit_type == "storage_limite_mb":
            tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
            tenant_result = await session.execute(tenant_stmt)
            tenant = tenant_result.scalar_one()

            if tenant:
                limite = tenant.storage_limite_mb
                atual = tenant.storage_usado_mb

        porcentagem = (atual / limite * 100) if limite and limite > 0 else 0.0
        atingido = atual >= limite if limite else False

        return {
            "atual": atual,
            "limite": limite,
            "porcentagem": round(porcentagem, 2),
            "atingido": atingido,
        }


# ==============================================================================
# ACESSO EXPLÍCITO POR FAZENDA (BL-03)
# ==============================================================================

def require_fazenda_access(fazenda_id_param: str = "unidade_produtiva_id"):
    """
    Dependency que verifica se o usuário tem acesso explícito à fazenda.

    Regras:
    - is_owner (TenantUsuario) → acesso irrestrito
    - FazendaUsuario existe com vigencia_fim NULL ou >= hoje → acesso permitido
    - Caso contrário → 403

    Uso:
        @router.get("/{unidade_produtiva_id}/dados")
        async def endpoint(
            unidade_produtiva_id: uuid.UUID,
            _: bool = Depends(require_fazenda_access("unidade_produtiva_id")),
            ...
        )
    """
    async def _dependency(
        request: Request,
        claims: dict = Depends(get_current_user_claims),
        session: AsyncSession = Depends(get_session),
    ) -> bool:
        from core.models.auth import TenantUsuario, FazendaUsuario
        from datetime import date as date_type

        tenant_id_str = claims.get("tenant_id")
        user_id_str = claims.get("sub")
        if not tenant_id_str or not user_id_str:
            raise HTTPException(status_code=403, detail="Contexto de tenant/usuário ausente")

        tenant_id = uuid.UUID(tenant_id_str)
        user_id = uuid.UUID(user_id_str)

        # Resolve unidade_produtiva_id do path param ou header
        fazenda_id_value = request.path_params.get(fazenda_id_param) or request.headers.get("x-fazenda-id")
        if not fazenda_id_value:
            return True  # Sem contexto de fazenda — deixa passar (outro gate cuida)

        try:
            unidade_produtiva_id = uuid.UUID(str(fazenda_id_value))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Parâmetro '{fazenda_id_param}' inválido")

        # is_owner → acesso total
        tu_result = await session.execute(
            select(TenantUsuario).where(
                TenantUsuario.tenant_id == tenant_id,
                TenantUsuario.usuario_id == user_id,
                TenantUsuario.status == "ATIVO",
                TenantUsuario.is_owner == True,
            )
        )
        if tu_result.scalar_one_or_none():
            return True

        # Verificar FazendaUsuario com vigência válida
        hoje = date_type.today()
        fu_result = await session.execute(
            select(FazendaUsuario).where(
                FazendaUsuario.tenant_id == tenant_id,
                FazendaUsuario.usuario_id == user_id,
                FazendaUsuario.unidade_produtiva_id == unidade_produtiva_id,
            )
        )
        fu = fu_result.scalar_one_or_none()

        if not fu:
            logger.warning(
                f"require_fazenda_access: user {user_id} tentou acessar fazenda {unidade_produtiva_id} "
                f"sem FazendaUsuario. tenant={tenant_id}"
            )
            raise HTTPException(status_code=403, detail="Acesso negado: sem permissão para esta propriedade")

        # Verificar vigência em runtime (não depende do JWT)
        if fu.vigencia_fim and fu.vigencia_fim < hoje:
            logger.warning(
                f"require_fazenda_access: acesso expirado — user {user_id} fazenda {unidade_produtiva_id} "
                f"vigencia_fim={fu.vigencia_fim}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Acesso expirado em {fu.vigencia_fim.strftime('%d/%m/%Y')}. "
                       "Contate o gestor da assinatura para renovar."
            )

        if fu.vigencia_inicio and fu.vigencia_inicio > hoje:
            raise HTTPException(
                status_code=403,
                detail=f"Acesso liberado apenas a partir de {fu.vigencia_inicio.strftime('%d/%m/%Y')}."
            )

        return True
    return _dependency

    return _dependency
