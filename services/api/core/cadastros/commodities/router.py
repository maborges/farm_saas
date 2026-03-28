import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id
from core.exceptions import EntityNotFoundError
from .models import Commodity
from .schemas import CommodityCreate, CommodityUpdate, CommodityResponse

router = APIRouter(prefix="/cadastros/commodities", tags=["Cadastros — Commodities"])


@router.get("/", response_model=list[CommodityResponse])
@router.get("", response_model=list[CommodityResponse])
async def listar(
    tipo: Optional[str] = Query(None),
    apenas_ativos: bool = Query(True),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(Commodity).where(Commodity.tenant_id == tenant_id)
    if apenas_ativos:
        stmt = stmt.where(Commodity.ativo == True)
    if tipo:
        stmt = stmt.where(Commodity.tipo == tipo)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=CommodityResponse, status_code=201)
@router.post("", response_model=CommodityResponse, status_code=201)
async def criar(
    data: CommodityCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    obj = Commodity(tenant_id=tenant_id, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/{commodity_id}", response_model=CommodityResponse)
async def obter(
    commodity_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Commodity).where(Commodity.id == commodity_id, Commodity.tenant_id == tenant_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Commodity não encontrada")
    return obj


@router.patch("/{commodity_id}", response_model=CommodityResponse)
async def atualizar(
    commodity_id: uuid.UUID,
    data: CommodityUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Commodity).where(Commodity.id == commodity_id, Commodity.tenant_id == tenant_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Commodity não encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/{commodity_id}", status_code=204)
async def remover(
    commodity_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Commodity).where(Commodity.id == commodity_id, Commodity.tenant_id == tenant_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Commodity não encontrada")
    obj.ativo = False
    await session.commit()
