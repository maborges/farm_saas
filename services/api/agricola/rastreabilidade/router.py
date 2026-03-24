from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role, get_session_with_tenant
from agricola.rastreabilidade.schemas import (
    LoteRastreabilidadeCreate, LoteRastreabilidadeResponse,
    CertificacaoCreate, CertificacaoResponse
)
from agricola.rastreabilidade.service import RastreabilidadeService, CertificacaoService

router = APIRouter(prefix="/rastreabilidade", tags=["Rastreabilidade e Certificações"])

@router.post("/lotes", response_model=LoteRastreabilidadeResponse, status_code=status.HTTP_201_CREATED)
async def criar_lote(
    dados: LoteRastreabilidadeCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = RastreabilidadeService(session, tenant_id)
    return await svc.criar_lote(dados)

@router.get("/lotes/{lote_id}/cadeia")
async def cadeia_rastreabilidade(
    lote_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    """Retorna a cadeia completa: lote → safra → talhão → operações + insumos → romaneios."""
    svc = RastreabilidadeService(session, tenant_id)
    return await svc.cadeia_rastreabilidade(lote_id)


@router.get("/lotes", response_model=List[LoteRastreabilidadeResponse])
async def listar_lotes(
    safra_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = RastreabilidadeService(session, tenant_id)
    filters = {}
    if safra_id: filters["safra_id"] = safra_id
    return await svc.list_all(**filters)

@router.post("/certificacoes", response_model=CertificacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_certificacao(
    dados: CertificacaoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = CertificacaoService(session, tenant_id)
    return await svc.create(dados.model_dump())

@router.get("/certificacoes", response_model=List[CertificacaoResponse])
async def listar_certificacoes(
    fazenda_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = CertificacaoService(session, tenant_id)
    filters = {}
    if fazenda_id: filters["fazenda_id"] = fazenda_id
    return await svc.list_all(**filters)
