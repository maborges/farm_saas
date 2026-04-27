from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from agricola.production_units.schemas import (
    ProductionUnitCreate,
    ProductionUnitUpdate,
)
from agricola.production_units.service import ProductionUnitService
from core.dependencies import get_session_with_tenant, get_tenant_id, require_module

router = APIRouter(
    prefix="/safras/{safra_id}/production-units",
    tags=["Production Units — Step 24"],
)

MODULE = "A1_PLANEJAMENTO"


@router.get("", response_model=list[dict[str, Any]])
async def listar(
    safra_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
    _: None = Depends(require_module(MODULE)),
):
    svc = ProductionUnitService(session, tenant_id)
    return await svc.listar_por_safra(safra_id)


@router.post("", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def criar(
    safra_id: uuid.UUID,
    data: ProductionUnitCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
    _: None = Depends(require_module(MODULE)),
):
    svc = ProductionUnitService(session, tenant_id)
    result = await svc.criar(safra_id, data)
    await session.commit()
    return result


@router.get("/status-consorcio", response_model=list[dict[str, Any]])
async def status_consorcio(
    safra_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
    _: None = Depends(require_module(MODULE)),
):
    svc = ProductionUnitService(session, tenant_id)
    return await svc.status_consorcio(safra_id)


@router.get("/{pu_id}", response_model=dict[str, Any])
async def obter(
    safra_id: uuid.UUID,
    pu_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
    _: None = Depends(require_module(MODULE)),
):
    svc = ProductionUnitService(session, tenant_id)
    return await svc.obter(pu_id)


@router.patch("/{pu_id}", response_model=dict[str, Any])
async def atualizar(
    safra_id: uuid.UUID,
    pu_id: uuid.UUID,
    data: ProductionUnitUpdate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
    _: None = Depends(require_module(MODULE)),
):
    svc = ProductionUnitService(session, tenant_id)
    result = await svc.atualizar(pu_id, data)
    await session.commit()
    return result


@router.post("/{pu_id}/encerrar", response_model=dict[str, Any])
async def encerrar(
    safra_id: uuid.UUID,
    pu_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
    _: None = Depends(require_module(MODULE)),
):
    svc = ProductionUnitService(session, tenant_id)
    result = await svc.encerrar(pu_id)
    await session.commit()
    return result
