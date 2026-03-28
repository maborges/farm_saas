from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.safras.schemas import (
    SafraCreate, SafraResponse, SafraUpdate,
    SafraAvancarFase, SafraFaseHistoricoResponse,
    SafraTalhaoResponse, SafraTalhoesSincronizar,
)
from agricola.safras.models import SAFRA_FASES_ORDEM, SAFRA_TRANSICOES
from agricola.safras.service import SafraService

router = APIRouter(prefix="/safras", tags=["Safras"])

@router.post(
    "/",
    response_model=SafraResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova safra",
)
async def criar_safra(
    dados: SafraCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.criar(dados)
    return SafraResponse.model_validate(safra)


@router.get(
    "/",
    response_model=List[SafraResponse],
    summary="Lista safras de um talhão",
)
async def listar_safras(
    talhao_id: UUID | None = None,
    ano_safra: str | None = None,
    cultura: str | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraService(session, tenant_id)
    filters = {}
    if talhao_id: filters["talhao_id"] = talhao_id
    if ano_safra: filters["ano_safra"] = ano_safra
    if cultura: filters["cultura"] = cultura
    if status: filters["status"] = status
    
    safras = await svc.list_all(**filters)
    return [SafraResponse.model_validate(s) for s in safras]


@router.get(
    "/{id}",
    response_model=SafraResponse,
    summary="Detalhes de uma safra",
)
async def detalhar_safra(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.get_or_fail(id)
    return SafraResponse.model_validate(safra)

@router.patch(
    "/{id}",
    response_model=SafraResponse,
    summary="Atualiza dados da safra",
)
async def atualizar_safra(
    id: UUID,
    dados: SafraUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.atualizar(id, dados)
    return SafraResponse.model_validate(safra)

@router.get(
    "/{id}/resumo",
    summary="Planejado vs realizado da safra",
)
async def resumo_safra(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    """
    Retorna comparativo planejado vs realizado:
    custo, produtividade (sc/ha), receita e resultado líquido.
    """
    svc = SafraService(session, tenant_id)
    return await svc.resumo_planejado_realizado(id)


@router.post(
    "/{id}/avancar-fase/{nova_fase}",
    response_model=SafraResponse,
    summary="Avança o ciclo de vida da safra para a próxima fase",
)
async def avancar_fase_safra(
    id: UUID,
    nova_fase: str,
    dados: SafraAvancarFase = SafraAvancarFase(),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = SafraService(session, tenant_id)
    usuario_id = UUID(user["sub"]) if user.get("sub") else None
    safra = await svc.avancar_fase(
        id,
        nova_fase.upper(),
        usuario_id=usuario_id,
        observacao=dados.observacao,
        dados_fase=dados.dados_fase,
    )
    return SafraResponse.model_validate(safra)


@router.get(
    "/{id}/historico-fases",
    response_model=list[SafraFaseHistoricoResponse],
    summary="Histórico de transições de fase da safra",
)
async def historico_fases_safra(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraService(session, tenant_id)
    return [SafraFaseHistoricoResponse.model_validate(h) for h in await svc.listar_historico(id)]


@router.get(
    "/meta/fases",
    summary="Retorna as fases válidas e transições permitidas",
)
async def meta_fases():
    return {
        "fases_ordem": SAFRA_FASES_ORDEM,
        "transicoes": SAFRA_TRANSICOES,
    }


# ─── Talhões da Safra ─────────────────────────────────────────────────────────

@router.get("/{id}/talhoes", response_model=list[SafraTalhaoResponse])
async def listar_talhoes_safra(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    """Retorna todos os talhões associados à safra."""
    svc = SafraService(session, tenant_id)
    talhoes = await svc.listar_talhoes(id)
    # Se ainda não foi populado via sincronizar, retorna o talhao_id legado
    if not talhoes:
        safra = await svc.get_or_fail(id)
        from agricola.safras.models import SafraTalhao
        import uuid as _uuid
        placeholder = SafraTalhao()
        placeholder.id = _uuid.uuid4()
        placeholder.safra_id = safra.id
        placeholder.area_id = safra.talhao_id
        placeholder.principal = True
        placeholder.area_ha = safra.area_plantada_ha
        return [SafraTalhaoResponse.model_validate(placeholder)]
    return [SafraTalhaoResponse.model_validate(t) for t in talhoes]


@router.put("/{id}/talhoes", response_model=list[SafraTalhaoResponse])
async def sincronizar_talhoes_safra(
    id: UUID,
    dados: SafraTalhoesSincronizar,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    """Substitui a lista de talhões da safra. O primeiro ID é o principal."""
    svc = SafraService(session, tenant_id)
    talhoes = await svc.sincronizar_talhoes(
        id,
        dados.talhao_ids,
        areas_ha=dados.areas_ha,
    )
    await session.commit()
    for t in talhoes:
        await session.refresh(t)
    return [SafraTalhaoResponse.model_validate(t) for t in talhoes]
