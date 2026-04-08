from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.beneficiamento.schemas import (
    LoteBeneficiamentoCreate,
    LoteBeneficiamentoUpdate,
    LoteBeneficiamentoResponse,
    BeneficiamentoKPIs,
)
from agricola.beneficiamento.service import BeneficiamentoService

router = APIRouter(prefix="/beneficiamento", tags=["Beneficiamento de Café"])


@router.post("/", response_model=LoteBeneficiamentoResponse, status_code=status.HTTP_201_CREATED)
async def criar_lote(
    dados: LoteBeneficiamentoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = BeneficiamentoService(session, tenant_id)
    lote = await svc.criar(dados)
    return LoteBeneficiamentoResponse.model_validate(lote)


@router.get("/kpis", response_model=BeneficiamentoKPIs)
async def kpis_beneficiamento(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
):
    svc = BeneficiamentoService(session, tenant_id)
    return await svc.kpis_safra(safra_id)


@router.get("/", response_model=List[LoteBeneficiamentoResponse])
async def listar_lotes(
    safra_id: UUID | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
):
    svc = BeneficiamentoService(session, tenant_id)
    filters = {}
    if safra_id:
        filters["safra_id"] = safra_id
    if status:
        filters["status"] = status
    lotes = await svc.list_all(**filters)
    return [LoteBeneficiamentoResponse.model_validate(l) for l in lotes]


@router.get("/{id}", response_model=LoteBeneficiamentoResponse)
async def detalhar_lote(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
):
    svc = BeneficiamentoService(session, tenant_id)
    lote = await svc.get_or_fail(id)
    return LoteBeneficiamentoResponse.model_validate(lote)


@router.patch("/{id}", response_model=LoteBeneficiamentoResponse)
async def atualizar_lote(
    id: UUID,
    dados: LoteBeneficiamentoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = BeneficiamentoService(session, tenant_id)
    lote = await svc.atualizar(id, dados)
    return LoteBeneficiamentoResponse.model_validate(lote)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_lote(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
    user: dict = Depends(require_role(["admin"])),
):
    svc = BeneficiamentoService(session, tenant_id)
    await svc.hard_delete(id)
