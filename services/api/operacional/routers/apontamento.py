import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id, require_module
from core.exceptions import EntityNotFoundError, BusinessRuleError
from core.cadastros.equipamentos.models import Equipamento
from operacional.models.apontamento import ApontamentoUso
from operacional.schemas.apontamento import (
    ApontamentoUsoCreate, ApontamentoUsoUpdate, ApontamentoUsoResponse
)

router = APIRouter(
    prefix="/frota/apontamentos",
    tags=["Frota — Apontamentos de Uso"],
    dependencies=[Depends(require_module("O1"))],
)


@router.get("/", response_model=list[ApontamentoUsoResponse])
@router.get("", response_model=list[ApontamentoUsoResponse])
async def listar(
    equipamento_id: Optional[uuid.UUID] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ApontamentoUso).where(ApontamentoUso.tenant_id == tenant_id)
    if equipamento_id:
        stmt = stmt.where(ApontamentoUso.equipamento_id == equipamento_id)
    if data_inicio:
        stmt = stmt.where(ApontamentoUso.data >= data_inicio)
    if data_fim:
        stmt = stmt.where(ApontamentoUso.data <= data_fim)
    stmt = stmt.order_by(ApontamentoUso.data.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=ApontamentoUsoResponse, status_code=201)
@router.post("", response_model=ApontamentoUsoResponse, status_code=201)
async def criar(
    data: ApontamentoUsoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    # Valida equipamento pertence ao tenant
    eq = await session.get(Equipamento, data.equipamento_id)
    if not eq or eq.tenant_id != tenant_id:
        raise EntityNotFoundError("Equipamento não encontrado")
    if eq.status == "EM_MANUTENCAO":
        raise BusinessRuleError("Equipamento está em manutenção e não pode ser apontado")

    apontamento = ApontamentoUso(tenant_id=tenant_id, **data.model_dump())
    session.add(apontamento)

    # Atualiza horímetro/km do equipamento se maior que o atual
    if data.horimetro_fim > eq.horimetro_atual:
        eq.horimetro_atual = data.horimetro_fim
    if data.km_fim and data.km_fim > eq.km_atual:
        eq.km_atual = data.km_fim

    await session.commit()
    await session.refresh(apontamento)
    return apontamento


@router.get("/{ap_id}", response_model=ApontamentoUsoResponse)
async def obter(
    ap_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(ApontamentoUso).where(
            ApontamentoUso.id == ap_id, ApontamentoUso.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Apontamento não encontrado")
    return obj


@router.patch("/{ap_id}", response_model=ApontamentoUsoResponse)
async def atualizar(
    ap_id: uuid.UUID,
    data: ApontamentoUsoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(ApontamentoUso).where(
            ApontamentoUso.id == ap_id, ApontamentoUso.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Apontamento não encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/{ap_id}", status_code=204)
async def remover(
    ap_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(ApontamentoUso).where(
            ApontamentoUso.id == ap_id, ApontamentoUso.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Apontamento não encontrado")
    await session.delete(obj)
    await session.commit()
