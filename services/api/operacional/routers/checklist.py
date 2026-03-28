import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id, require_module
from core.exceptions import EntityNotFoundError
from operacional.models.checklist import ChecklistModelo, ChecklistRealizado
from operacional.schemas.checklist import (
    ChecklistModeloCreate, ChecklistModeloUpdate, ChecklistModeloResponse,
    ChecklistRealizadoCreate, ChecklistRealizadoResponse,
)

router = APIRouter(
    prefix="/frota/checklists",
    tags=["Frota — Checklists"],
    dependencies=[Depends(require_module("O1"))],
)


# ─── Modelos / Templates ─────────────────────────────────────────────────────

@router.get("/modelos", response_model=list[ChecklistModeloResponse])
async def listar_modelos(
    tipo_equipamento: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ChecklistModelo).where(
        ChecklistModelo.tenant_id == tenant_id,
        ChecklistModelo.ativo == True,
    )
    if tipo_equipamento:
        stmt = stmt.where(ChecklistModelo.tipo_equipamento == tipo_equipamento)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/modelos", response_model=ChecklistModeloResponse, status_code=201)
async def criar_modelo(
    data: ChecklistModeloCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    payload = data.model_dump()
    payload["itens"] = [i.model_dump() for i in data.itens]
    obj = ChecklistModelo(tenant_id=tenant_id, **payload)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.patch("/modelos/{modelo_id}", response_model=ChecklistModeloResponse)
async def atualizar_modelo(
    modelo_id: uuid.UUID,
    data: ChecklistModeloUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(ChecklistModelo).where(
            ChecklistModelo.id == modelo_id, ChecklistModelo.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Modelo de checklist não encontrado")
    updates = data.model_dump(exclude_none=True)
    if "itens" in updates:
        updates["itens"] = [i.model_dump() for i in data.itens]
    for k, v in updates.items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


# ─── Realizados ──────────────────────────────────────────────────────────────

@router.get("/realizados", response_model=list[ChecklistRealizadoResponse])
async def listar_realizados(
    equipamento_id: Optional[uuid.UUID] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ChecklistRealizado).where(ChecklistRealizado.tenant_id == tenant_id)
    if equipamento_id:
        stmt = stmt.where(ChecklistRealizado.equipamento_id == equipamento_id)
    stmt = stmt.order_by(ChecklistRealizado.data_hora.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/realizados", response_model=ChecklistRealizadoResponse, status_code=201)
async def realizar_checklist(
    data: ChecklistRealizadoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    # Valida modelo existe no tenant
    modelo = await session.get(ChecklistModelo, data.modelo_id)
    if not modelo or modelo.tenant_id != tenant_id:
        raise EntityNotFoundError("Modelo de checklist não encontrado")

    respostas = [r.model_dump() for r in data.respostas]

    # Determina liberação: qualquer item obrigatório NOK → bloqueia
    itens_obrigatorios = {i["ordem"] for i in modelo.itens if i.get("obrigatorio", True)}
    liberado = all(
        r["status"] != "NOK"
        for r in respostas
        if r["ordem"] in itens_obrigatorios
    )

    obj = ChecklistRealizado(
        tenant_id=tenant_id,
        equipamento_id=data.equipamento_id,
        modelo_id=data.modelo_id,
        operador_id=data.operador_id,
        respostas=respostas,
        liberado_para_uso=liberado,
        observacoes_gerais=data.observacoes_gerais,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/realizados/{check_id}", response_model=ChecklistRealizadoResponse)
async def obter_realizado(
    check_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(ChecklistRealizado).where(
            ChecklistRealizado.id == check_id, ChecklistRealizado.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Checklist não encontrado")
    return obj
