import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session_with_tenant, get_tenant_id
from core.exceptions import EntityNotFoundError
from .service import EquipamentoService
from .schemas import EquipamentoCreate, EquipamentoUpdate, EquipamentoResponse

router = APIRouter(prefix="/cadastros/equipamentos", tags=["Cadastros — Equipamentos"])


@router.get("/", response_model=list[EquipamentoResponse])
@router.get("", response_model=list[EquipamentoResponse])
async def listar(
    tipo: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = EquipamentoService(session, tenant_id)
    return await svc.listar(tipo=tipo, status=status_filter)


@router.post("/", response_model=EquipamentoResponse, status_code=201)
@router.post("", response_model=EquipamentoResponse, status_code=201)
async def criar(
    data: EquipamentoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = EquipamentoService(session, tenant_id)
    eq = await svc.criar(data)
    await session.commit()
    await session.refresh(eq)
    return eq


@router.get("/{eq_id}", response_model=EquipamentoResponse)
async def obter(
    eq_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = EquipamentoService(session, tenant_id)
    try:
        return await svc.obter(eq_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento não encontrado")


@router.patch("/{eq_id}", response_model=EquipamentoResponse)
async def atualizar(
    eq_id: uuid.UUID,
    data: EquipamentoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = EquipamentoService(session, tenant_id)
    try:
        obj = await svc.atualizar(eq_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento não encontrado")


@router.delete("/{eq_id}", status_code=204)
async def remover(
    eq_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = EquipamentoService(session, tenant_id)
    try:
        await svc.desativar(eq_id)
        await session.commit()
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento não encontrado")
