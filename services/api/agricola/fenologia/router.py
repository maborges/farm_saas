from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role, get_session_with_tenant
from agricola.fenologia.schemas import (
    FenologiaEscalaCreate, FenologiaEscalaUpdate, FenologiaEscalaResponse,
    FenologiaRegistroCreate, FenologiaRegistroGrupoCreate, FenologiaRegistroResponse,
    GrupoTalhaoCreate, GrupoTalhaoUpdate, GrupoTalhaoResponse,
    GrupoSincronizarTalhoes, CopiarGruposDeSafra,
)
from agricola.fenologia.service import FenologiaEscalaService, FenologiaRegistroService
from agricola.fenologia.grupos_service import SafraTalhaoGrupoService

router = APIRouter(tags=["Fenologia Agrícola"])


# ─── Escalas ─────────────────────────────────────────────────────────────────

@router.get("/fenologia/escalas", response_model=list[FenologiaEscalaResponse])
async def listar_escalas(
    cultura: str | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    return await FenologiaEscalaService(session, tenant_id).listar(cultura=cultura)


@router.post("/fenologia/escalas", response_model=FenologiaEscalaResponse, status_code=status.HTTP_201_CREATED)
async def criar_escala(
    dados: FenologiaEscalaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    return await FenologiaEscalaService(session, tenant_id).criar(dados)


@router.patch("/fenologia/escalas/{escala_id}", response_model=FenologiaEscalaResponse)
async def atualizar_escala(
    escala_id: UUID,
    dados: FenologiaEscalaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    return await FenologiaEscalaService(session, tenant_id).atualizar(escala_id, dados)


# ─── Grupos de talhões ────────────────────────────────────────────────────────

@router.get("/safras/{safra_id}/grupos-talhoes", response_model=list[GrupoTalhaoResponse])
async def listar_grupos(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    return await SafraTalhaoGrupoService(session, tenant_id).listar(safra_id)


@router.post("/safras/{safra_id}/grupos-talhoes", response_model=GrupoTalhaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_grupo(
    safra_id: UUID,
    dados: GrupoTalhaoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    return await SafraTalhaoGrupoService(session, tenant_id).criar(safra_id, dados.nome, dados.cor, dados.ordem)


@router.patch("/safras/{safra_id}/grupos-talhoes/{grupo_id}", response_model=GrupoTalhaoResponse)
async def atualizar_grupo(
    safra_id: UUID,
    grupo_id: UUID,
    dados: GrupoTalhaoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    return await SafraTalhaoGrupoService(session, tenant_id).atualizar(
        grupo_id, dados.nome, dados.cor, dados.ordem
    )


@router.put(
    "/safras/{safra_id}/grupos-talhoes/{grupo_id}/talhoes",
    response_model=GrupoTalhaoResponse,
    summary="Sincroniza talhões do grupo (drag & drop)",
)
async def sincronizar_talhoes_grupo(
    safra_id: UUID,
    grupo_id: UUID,
    dados: GrupoSincronizarTalhoes,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    return await SafraTalhaoGrupoService(session, tenant_id).sincronizar_talhoes(grupo_id, dados.talhao_ids)


@router.delete("/safras/{safra_id}/grupos-talhoes/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_grupo(
    safra_id: UUID,
    grupo_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    await SafraTalhaoGrupoService(session, tenant_id).excluir(grupo_id)


@router.post(
    "/safras/{safra_id}/grupos-talhoes/copiar",
    response_model=list[GrupoTalhaoResponse],
    summary="Copia grupos de uma safra anterior",
)
async def copiar_grupos_de_safra(
    safra_id: UUID,
    dados: CopiarGruposDeSafra,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    return await SafraTalhaoGrupoService(session, tenant_id).copiar_de_safra(dados.safra_origem_id, safra_id)


# ─── Registros fenológicos ────────────────────────────────────────────────────

@router.post(
    "/safras/{safra_id}/talhoes/{talhao_id}/fenologia",
    response_model=FenologiaRegistroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra fenologia em um talhão específico",
)
async def registrar_fenologia_talhao(
    safra_id: UUID,
    talhao_id: UUID,
    dados: FenologiaRegistroCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = FenologiaRegistroService(session, tenant_id)
    usuario_id = UUID(user["sub"]) if user.get("sub") else None
    r = await svc.registrar_por_talhao(safra_id, talhao_id, dados, usuario_id)
    return svc._to_response(r)


@router.post(
    "/safras/{safra_id}/grupos-talhoes/{grupo_id}/fenologia",
    response_model=list[FenologiaRegistroResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Registra fenologia em todos os talhões de um grupo",
)
async def registrar_fenologia_grupo(
    safra_id: UUID,
    grupo_id: UUID,
    dados: FenologiaRegistroCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = FenologiaRegistroService(session, tenant_id)
    usuario_id = UUID(user["sub"]) if user.get("sub") else None
    registros = await svc.registrar_por_grupo(safra_id, grupo_id, dados, usuario_id)
    return [svc._to_response(r) for r in registros]


@router.get(
    "/safras/{safra_id}/talhoes/{talhao_id}/fenologia",
    response_model=list[FenologiaRegistroResponse],
    summary="Histórico fenológico de um talhão",
)
async def historico_fenologia_talhao(
    safra_id: UUID,
    talhao_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = FenologiaRegistroService(session, tenant_id)
    return [svc._to_response(r) for r in await svc.listar_por_talhao(safra_id, talhao_id)]


@router.get(
    "/safras/{safra_id}/fenologia",
    response_model=list[FenologiaRegistroResponse],
    summary="Histórico fenológico de todos os talhões da safra",
)
async def historico_fenologia_safra(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = FenologiaRegistroService(session, tenant_id)
    return [svc._to_response(r) for r in await svc.listar_por_safra(safra_id)]
