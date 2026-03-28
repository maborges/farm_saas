import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id, require_module
from core.exceptions import EntityNotFoundError
from core.cadastros.equipamentos.models import Equipamento
from operacional.models.abastecimento import Abastecimento
from operacional.schemas.abastecimento import (
    AbastecimentoCreate, AbastecimentoUpdate, AbastecimentoResponse
)

router = APIRouter(
    prefix="/frota/abastecimentos",
    tags=["Frota — Abastecimentos"],
    dependencies=[Depends(require_module("O1"))],
)


@router.get("/", response_model=list[AbastecimentoResponse])
@router.get("", response_model=list[AbastecimentoResponse])
async def listar(
    equipamento_id: Optional[uuid.UUID] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(Abastecimento).where(Abastecimento.tenant_id == tenant_id)
    if equipamento_id:
        stmt = stmt.where(Abastecimento.equipamento_id == equipamento_id)
    if data_inicio:
        stmt = stmt.where(Abastecimento.data >= data_inicio)
    if data_fim:
        stmt = stmt.where(Abastecimento.data <= data_fim)
    stmt = stmt.order_by(Abastecimento.data.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=AbastecimentoResponse, status_code=201)
@router.post("", response_model=AbastecimentoResponse, status_code=201)
async def criar(
    data: AbastecimentoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    eq = await session.get(Equipamento, data.equipamento_id)
    if not eq or eq.tenant_id != tenant_id:
        raise EntityNotFoundError("Equipamento não encontrado")

    custo_total = round(data.litros * data.preco_litro, 2)
    payload = data.model_dump()
    payload["custo_total"] = custo_total

    ab = Abastecimento(tenant_id=tenant_id, **payload)
    session.add(ab)

    # Atualiza horímetro/km do equipamento
    if data.horimetro_na_data > eq.horimetro_atual:
        eq.horimetro_atual = data.horimetro_na_data
    if data.km_na_data and data.km_na_data > eq.km_atual:
        eq.km_atual = data.km_na_data

    await session.commit()
    await session.refresh(ab)
    return ab


@router.get("/{ab_id}", response_model=AbastecimentoResponse)
async def obter(
    ab_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Abastecimento).where(
            Abastecimento.id == ab_id, Abastecimento.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Abastecimento não encontrado")
    return obj


@router.patch("/{ab_id}", response_model=AbastecimentoResponse)
async def atualizar(
    ab_id: uuid.UUID,
    data: AbastecimentoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Abastecimento).where(
            Abastecimento.id == ab_id, Abastecimento.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Abastecimento não encontrado")
    updates = data.model_dump(exclude_none=True)
    for k, v in updates.items():
        setattr(obj, k, v)
    # Recalcula custo se litros ou preco_litro foram alterados
    if "litros" in updates or "preco_litro" in updates:
        obj.custo_total = round(obj.litros * obj.preco_litro, 2)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/{ab_id}", status_code=204)
async def remover(
    ab_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Abastecimento).where(
            Abastecimento.id == ab_id, Abastecimento.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Abastecimento não encontrado")
    await session.delete(obj)
    await session.commit()
