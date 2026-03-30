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

from operacional.services.abastecimento_service import AbastecimentoService

router = APIRouter(
    prefix="/frota/abastecimentos",
    tags=["Frota — Abastecimentos"],
    dependencies=[Depends(require_module("O1"))],
)

@router.get("/", response_model=list[AbastecimentoResponse])
@router.get("", response_model=list[AbastecimentoResponse])
async def listar(
    equipamento_id: Optional[uuid.UUID] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = AbastecimentoService(session, tenant_id)
    if equipamento_id:
        return await service.listar_por_equipamento(equipamento_id)
    return await service.listar()

@router.post("/", response_model=AbastecimentoResponse, status_code=201)
@router.post("", response_model=AbastecimentoResponse, status_code=201)
async def criar(
    data: AbastecimentoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = AbastecimentoService(session, tenant_id)
    return await service.registrar(data)

@router.get("/{id}", response_model=AbastecimentoResponse)
async def obter(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = AbastecimentoService(session, tenant_id)
    return await service.obter(id)

@router.patch("/{id}", response_model=AbastecimentoResponse)
async def atualizar(
    id: uuid.UUID,
    data: AbastecimentoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = AbastecimentoService(session, tenant_id)
    return await service.atualizar(id, data)

@router.delete("/{id}", status_code=204)
async def remover(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = AbastecimentoService(session, tenant_id)
    await service.remover(id)
