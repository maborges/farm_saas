from fastapi import APIRouter, Depends, status
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session
from core.dependencies import get_session_with_tenant
from core.dependencies import get_tenant_id, require_module

from pecuaria.schemas.lote_schema import LoteBovinoCreate, LoteBovinoResponse
from pecuaria.services.lote_service import LoteBovinoService

# A Trava impeditiva "P1" - Licença do Módulo Pecuária
router = APIRouter(
    prefix="/lotes-bovinos",
    tags=["Pecuária - Rebanho (P1)"],
    dependencies=[Depends(require_module("P1"))]
)

@router.get("/", response_model=List[LoteBovinoResponse])
async def listar_lotes(
    fazenda_id: uuid.UUID | None = None,
    categoria: str | None = None,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session_with_tenant),
):
    """Lista Lotes de Animais na propriedade, filtrado por fazenda e/ou categoria."""
    svc = LoteBovinoService(tenant_id)
    filters: dict = {}
    if fazenda_id:
        filters["fazenda_id"] = fazenda_id
    if categoria:
        filters["categoria"] = categoria
    svc.session = db
    return await svc.list_all(**filters)


@router.post("/", response_model=LoteBovinoResponse, status_code=status.HTTP_201_CREATED)
async def criar_lote(
    payload: LoteBovinoCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session_with_tenant),
):
    """Registra a fundação de um novo Lote na fazenda (Compra ou Nascimento)."""
    svc = LoteBovinoService(tenant_id)
    return await svc.create_lote(db, obj_in=payload)
