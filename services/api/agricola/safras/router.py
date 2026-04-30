from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import List
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.safras.schemas import (
    SafraCreate, SafraResponse, SafraUpdate,
    SafraAvancarFase, SafraFaseHistoricoResponse,
    SafraTalhaoResponse, SafraTalhoesSincronizar,
    EstoqueResumoResponse, MovimentacaoSafraResponse,
    LotesResponse,
)
from agricola.cultivos.schemas import CultivoResponse
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
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.criar(dados)
    await session.commit()
    return SafraResponse.model_validate(safra)


@router.get(
    "/",
    response_model=List[SafraResponse],
    summary="Lista safras com cultivos",
)
async def listar_safras(
    talhao_id: UUID | None = None,
    ano_safra: str | None = None,
    cultura: str | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    svc = SafraService(session, tenant_id)
    filters = {}
    if talhao_id: filters["talhao_id"] = talhao_id
    if ano_safra: filters["ano_safra"] = ano_safra
    if cultura: filters["cultura"] = cultura
    if status: filters["status"] = status

    safras = await svc.list_with_cultivos(**filters)
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
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.get_or_fail(id)
    return SafraResponse.model_validate(safra)


@router.get(
    "/{id}/cultivos",
    response_model=List[CultivoResponse],
    summary="Lista cultivos de uma safra com áreas",
)
async def listar_cultivos_safra(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    from agricola.cultivos.service import CultivoService
    svc = CultivoService(session, tenant_id)
    cultivos = await svc.listar_por_safra(id)
    return [CultivoResponse.model_validate(c) for c in cultivos]

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
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.atualizar(id, dados)
    await session.commit()
    return SafraResponse.model_validate(safra)

@router.get(
    "/{id}/resumo",
    summary="Planejado vs realizado da safra",
)
async def resumo_safra(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
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
    dados: SafraAvancarFase,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    if dados.novo_status and dados.novo_status.upper() != nova_fase.upper():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="novo_status no corpo diverge da fase informada na URL.",
        )
    svc = SafraService(session, tenant_id)
    usuario_id = UUID(user["sub"]) if user.get("sub") else None
    safra = await svc.avancar_fase(
        id,
        nova_fase.upper(),
        usuario_id=usuario_id,
        observacao=dados.observacao,
        dados_fase=dados.dados_fase,
    )
    await session.commit()
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
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
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
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    """Retorna todos os talhões associados à safra."""
    svc = SafraService(session, tenant_id)
    talhoes = await svc.listar_talhoes(id)
    # Se ainda não foi populado via sincronizar, retorna o talhao_id legado
    if not talhoes:
        safra = await svc.get_or_fail(id)
        if not safra.talhao_id:
            return []
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
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
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


# ─── Estoque (Inventory) ──────────────────────────────────────────────────────

@router.get(
    "/{id}/estoque/saldo",
    summary="Saldo atual de estoque para a safra",
)
async def get_estoque_saldo(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    """
    Retorna saldo atual de estoque agrupado por depósito e produto.
    Útil para a aba de estoque no detalhe da safra.
    """
    svc = SafraService(session, tenant_id)
    return await svc.get_saldo_safra(id)


@router.get(
    "/{id}/estoque/movimentacoes",
    summary="Histórico de movimentações de estoque para a safra",
)
async def get_estoque_historico(
    id: UUID,
    tipo: str | None = Query(None, description="Tipo de movimentação: ENTRADA, SAIDA, AJUSTE, TRANSFERENCIA"),
    deposito_id: UUID | None = Query(None, description="Filtrar por depósito"),
    data_inicio: date | None = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: date | None = Query(None, description="Data final (YYYY-MM-DD)"),
    numero_lote: str | None = Query(None, description="Número do lote (busca parcial)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    """
    Retorna histórico de movimentações de estoque para a safra,
    com filtros por tipo, depósito, período e lote.
    Inclui informações da operação agrícola associada.
    """
    svc = SafraService(session, tenant_id)
    return await svc.get_movimentacoes_safra(
        id,
        tipo=tipo,
        deposito_id=deposito_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        numero_lote=numero_lote,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{id}/estoque/lotes",
    response_model=LotesResponse,
    summary="Lotes consumidos em operações da safra",
)
async def get_estoque_lotes(
    id: UUID,
    deposito_id: UUID | None = Query(None, description="Filtrar por depósito"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    """
    Retorna lotes (batches) consumidos em operações agrícolas da safra.
    Mostra o status de cada lote (quantidade restante, se esgotado, etc).
    Útil para rastreabilidade de fornecedores e custo histórico.
    """
    svc = SafraService(session, tenant_id)
    return await svc.get_lotes_safra(id, deposito_id=deposito_id)
