from fastapi import APIRouter, Depends, status
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session_with_tenant, get_tenant_id, require_module
from pecuaria.schemas.manejo_schema import ManejoLoteCreate, ManejoLoteResponse
from pecuaria.services.manejo_service import ManejoLoteService

router = APIRouter(
    prefix="/pecuaria/manejos",
    tags=["Pecuária - Manejo (P1)"],
    dependencies=[Depends(require_module("P1_REBANHO"))],
)


@router.get("/", response_model=List[ManejoLoteResponse])
async def listar_manejos(
    lote_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session_with_tenant),
):
    """Lista eventos de manejo. Filtra por lote quando `lote_id` for fornecido."""
    svc = ManejoLoteService(tenant_id)
    svc.session = db
    if lote_id:
        return await svc.listar_por_lote(db, lote_id=lote_id)
    return await svc.listar_todos(db)


@router.post("/", response_model=ManejoLoteResponse, status_code=status.HTTP_201_CREATED)
async def registrar_evento(
    payload: ManejoLoteCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session_with_tenant),
):
    """Registra um evento de manejo: nascimento, morte, pesagem, vacinação ou transferência."""
    svc = ManejoLoteService(tenant_id)
    svc.session = db
    evento = await svc.registrar_evento(db, obj_in=payload)
    await db.commit()
    return evento
