import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session_with_tenant, get_tenant_id
from core.exceptions import EntityNotFoundError, EntityAlreadyExistsError
from .schemas import (
    CommodityCreate, CommodityUpdate, CommodityResponse, CommodityDetalhadaResponse,
    CommodityClassificacaoCreate, CommodityClassificacaoUpdate, CommodityClassificacaoResponse,
    CotacaoCommodityCreate, CotacaoCommodityUpdate, CotacaoCommodityResponse,
)
from .service import CommodityService
from .cotacao_service import CotacaoService

router = APIRouter(prefix="/cadastros/commodities", tags=["Cadastros — Commodities"])


# ===========================================================================
# Commodity — CRUD
# ===========================================================================

@router.get("/", response_model=list[CommodityResponse])
@router.get("", response_model=list[CommodityResponse])
async def listar(
    tipo: Optional[str] = Query(None),
    apenas_ativos: bool = Query(True),
    incluir_sistema: bool = Query(True),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await CommodityService(session, tenant_id).listar(tipo=tipo, apenas_ativos=apenas_ativos, incluir_sistema=incluir_sistema)


@router.post("/", response_model=CommodityResponse, status_code=201)
@router.post("", response_model=CommodityResponse, status_code=201)
async def criar(
    data: CommodityCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await CommodityService(session, tenant_id).criar(data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityAlreadyExistsError as e:
        raise HTTPException(409, str(e))


@router.get("/{commodity_id}", response_model=CommodityDetalhadaResponse)
async def obter(
    commodity_id: uuid.UUID,
    incluir_classificacoes: bool = Query(True),
    incluir_cotacao: bool = Query(True),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await CommodityService(session, tenant_id).obter(commodity_id, incluir_classificacoes=incluir_classificacoes, incluir_cotacao=incluir_cotacao)
    except EntityNotFoundError:
        raise HTTPException(404, "Commodity não encontrada")


@router.patch("/{commodity_id}", response_model=CommodityResponse)
async def atualizar(
    commodity_id: uuid.UUID,
    data: CommodityUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await CommodityService(session, tenant_id).atualizar(commodity_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError:
        raise HTTPException(404, "Commodity não encontrada")


@router.delete("/{commodity_id}", status_code=204)
async def remover(
    commodity_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        await CommodityService(session, tenant_id).remover(commodity_id)
        await session.commit()
    except EntityNotFoundError:
        raise HTTPException(404, "Commodity não encontrada")


@router.post("/cotacoes/atualizar")
async def atualizar_cotacoes(
    fonte: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = CotacaoService(session, tenant_id)
    try:
        return await svc.atualizar_todas(fonte=fonte)
    finally:
        await svc.close()


# ===========================================================================
# CommodityClassificacao
# ===========================================================================

classif_router = APIRouter(
    prefix="/cadastros/commodities/{commodity_id}/classificacoes",
    tags=["Cadastros — Commodities — Classificações"],
)


@classif_router.get("/", response_model=list[CommodityClassificacaoResponse])
async def listar_classificacoes(
    commodity_id: uuid.UUID,
    apenas_ativas: bool = Query(True),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await CommodityService(session, tenant_id).listar_classificacoes(commodity_id, apenas_ativas=apenas_ativas)
    except EntityNotFoundError:
        raise HTTPException(404, "Commodity não encontrada")


@classif_router.post("/", response_model=CommodityClassificacaoResponse, status_code=201)
async def criar_classificacao(
    commodity_id: uuid.UUID,
    data: CommodityClassificacaoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await CommodityService(session, tenant_id).criar_classificacao(commodity_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@classif_router.get("/{classificacao_id}", response_model=CommodityClassificacaoResponse)
async def obter_classificacao(
    commodity_id: uuid.UUID,
    classificacao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await CommodityService(session, tenant_id)._get_classificacao(commodity_id, classificacao_id)
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@classif_router.patch("/{classificacao_id}", response_model=CommodityClassificacaoResponse)
async def atualizar_classificacao(
    commodity_id: uuid.UUID,
    classificacao_id: uuid.UUID,
    data: CommodityClassificacaoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await CommodityService(session, tenant_id).atualizar_classificacao(commodity_id, classificacao_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@classif_router.delete("/{classificacao_id}", status_code=204)
async def remover_classificacao(
    commodity_id: uuid.UUID,
    classificacao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        await CommodityService(session, tenant_id).remover_classificacao(commodity_id, classificacao_id)
        await session.commit()
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


# ===========================================================================
# CotacaoCommodity
# ===========================================================================

cotacao_router = APIRouter(
    prefix="/cadastros/commodities/{commodity_id}/cotacoes",
    tags=["Cadastros — Commodities — Cotações"],
)


@cotacao_router.get("/", response_model=list[CotacaoCommodityResponse])
async def listar_cotacoes(
    commodity_id: uuid.UUID,
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    fonte: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await CommodityService(session, tenant_id).listar_cotacoes(commodity_id, data_inicio=data_inicio, data_fim=data_fim, fonte=fonte)
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@cotacao_router.post("/", response_model=CotacaoCommodityResponse, status_code=201)
async def criar_cotacao(
    commodity_id: uuid.UUID,
    data: CotacaoCommodityCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await CommodityService(session, tenant_id).criar_cotacao(commodity_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@cotacao_router.get("/ultima", response_model=CotacaoCommodityResponse)
async def ultima_cotacao(
    commodity_id: uuid.UUID,
    fonte: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await CommodityService(session, tenant_id).ultima_cotacao(commodity_id, fonte=fonte)
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@cotacao_router.delete("/{cotacao_id}", status_code=204)
async def remover_cotacao(
    commodity_id: uuid.UUID,
    cotacao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        await CommodityService(session, tenant_id).remover_cotacao(commodity_id, cotacao_id)
        await session.commit()
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


# ===========================================================================
# ConversaoUnidade
# ===========================================================================

conversao_router = APIRouter(
    prefix="/cadastros/commodities/{commodity_id}/conversoes",
    tags=["Cadastros — Commodities — Conversões de Unidade"],
)


@conversao_router.get("/")
async def listar_conversoes(
    commodity_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await CommodityService(session, tenant_id).listar_conversoes(commodity_id)
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@conversao_router.post("/")
async def criar_conversao(
    commodity_id: uuid.UUID,
    data: dict,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        result = await CommodityService(session, tenant_id).criar_conversao(commodity_id, data)
        await session.commit()
        return result
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@conversao_router.post("/calcular")
async def calcular_conversao(
    commodity_id: uuid.UUID,
    data: dict,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await CommodityService(session, tenant_id).calcular_conversao(
            commodity_id, data["quantidade"], data["origem"], data["destino"]
        )
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))
