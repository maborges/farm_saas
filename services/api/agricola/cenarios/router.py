from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import PlanTier
from core.dependencies import get_tenant_id, get_session_with_tenant, require_module, require_tier
from agricola.cenarios.schemas import (
    CenarioCreate,
    CenarioListItem,
    CenarioResponse,
    CenarioUpdate,
    ComparativoResponse,
    DuplicarCenarioRequest,
)
from agricola.cenarios.service import CenariosService

router = APIRouter(prefix="/safras/{safra_id}/cenarios", tags=["Cenários Econômicos — Step 20"])

MODULE = "A1_PLANEJAMENTO"


@router.get("", response_model=List[CenarioListItem])
async def list_cenarios(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = CenariosService(session, tenant_id)
    cenarios = await svc.list_cenarios(safra_id)
    await session.commit()
    return cenarios


@router.post("", response_model=CenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_cenario(
    safra_id: UUID,
    data: CenarioCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _module: None = Depends(require_module(MODULE)),
    _tier: None = Depends(require_tier(PlanTier.PROFISSIONAL)),
):
    svc = CenariosService(session, tenant_id)
    cenario = await svc.create_cenario(safra_id, data)
    await session.commit()
    await session.refresh(cenario, attribute_names=["unidades"])
    return cenario


@router.get("/comparativo", response_model=ComparativoResponse)
async def get_comparativo(
    safra_id: UUID,
    ids: List[UUID] = Query(..., description="IDs dos cenários a comparar"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _module: None = Depends(require_module(MODULE)),
    _tier: None = Depends(require_tier(PlanTier.PROFISSIONAL)),
):
    svc = CenariosService(session, tenant_id)
    return await svc.get_comparativo(safra_id, ids)


@router.post("/base/recalcular", response_model=CenarioResponse)
async def recalcular_base(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = CenariosService(session, tenant_id)
    cenario = await svc.recalcular_base(safra_id)
    await session.commit()
    await session.refresh(cenario, attribute_names=["unidades"])
    return cenario


@router.get("/{cenario_id}", response_model=CenarioResponse)
async def get_cenario(
    safra_id: UUID,
    cenario_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = CenariosService(session, tenant_id)
    return await svc.get_cenario(safra_id, cenario_id)


@router.patch("/{cenario_id}", response_model=CenarioResponse)
async def update_cenario(
    safra_id: UUID,
    cenario_id: UUID,
    data: CenarioUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = CenariosService(session, tenant_id)
    cenario = await svc.update_cenario(safra_id, cenario_id, data)
    await session.commit()
    await session.refresh(cenario, attribute_names=["unidades"])
    return cenario


@router.delete("/{cenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cenario(
    safra_id: UUID,
    cenario_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = CenariosService(session, tenant_id)
    await svc.delete_cenario(safra_id, cenario_id)
    await session.commit()


@router.post("/{cenario_id}/duplicar", response_model=CenarioResponse, status_code=status.HTTP_201_CREATED)
async def duplicar_cenario(
    safra_id: UUID,
    cenario_id: UUID,
    data: DuplicarCenarioRequest,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _module: None = Depends(require_module(MODULE)),
    _tier: None = Depends(require_tier(PlanTier.PROFISSIONAL)),
):
    svc = CenariosService(session, tenant_id)
    cenario = await svc.duplicar(safra_id, cenario_id, data)
    await session.commit()
    await session.refresh(cenario, attribute_names=["unidades"])
    return cenario
