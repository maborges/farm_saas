import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id
from core.exceptions import EntityNotFoundError
from .models import Equipamento
from .schemas import EquipamentoCreate, EquipamentoUpdate, EquipamentoResponse

router = APIRouter(prefix="/cadastros/equipamentos", tags=["Cadastros — Equipamentos"])


def _q(session: AsyncSession, tenant_id: uuid.UUID):
    return session, tenant_id


@router.get("/", response_model=list[EquipamentoResponse])
@router.get("", response_model=list[EquipamentoResponse])
async def listar(
    tipo: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(Equipamento).where(Equipamento.tenant_id == tenant_id)
    if tipo:
        stmt = stmt.where(Equipamento.tipo == tipo)
    if status:
        stmt = stmt.where(Equipamento.status == status)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=EquipamentoResponse, status_code=201)
@router.post("", response_model=EquipamentoResponse, status_code=201)
async def criar(
    data: EquipamentoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    eq = Equipamento(tenant_id=tenant_id, **data.model_dump())
    session.add(eq)
    await session.commit()
    await session.refresh(eq)
    return eq


@router.get("/{eq_id}", response_model=EquipamentoResponse)
async def obter(
    eq_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Equipamento).where(Equipamento.id == eq_id, Equipamento.tenant_id == tenant_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Equipamento não encontrado")
    return obj


@router.patch("/{eq_id}", response_model=EquipamentoResponse)
async def atualizar(
    eq_id: uuid.UUID,
    data: EquipamentoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Equipamento).where(Equipamento.id == eq_id, Equipamento.tenant_id == tenant_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Equipamento não encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/{eq_id}", status_code=204)
async def remover(
    eq_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Equipamento).where(Equipamento.id == eq_id, Equipamento.tenant_id == tenant_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Equipamento não encontrado")
    obj.status = "INATIVO"
    await session.commit()
