from fastapi import APIRouter, Depends, status
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session_with_tenant, get_tenant_id, require_module
from pecuaria.schemas.piquete_schema import PiqueteCreate, PiqueteResponse
from pecuaria.services.piquete_service import PiqueteService

router = APIRouter(
    prefix="/pecuaria/piquetes",
    tags=["Pecuária - Piquetes (P1)"],
    dependencies=[Depends(require_module("P1_REBANHO"))],
)


@router.get("/", response_model=List[PiqueteResponse])
async def listar_piquetes(
    unidade_produtiva_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session_with_tenant),
):
    """Lista piquetes do tenant. Filtra por fazenda quando `unidade_produtiva_id` fornecido."""
    svc = PiqueteService(tenant_id)
    svc.session = db
    if unidade_produtiva_id:
        return await svc.listar_por_fazenda(db, unidade_produtiva_id=unidade_produtiva_id)
    return await svc.list_all()


@router.post("/", response_model=PiqueteResponse, status_code=status.HTTP_201_CREATED)
async def criar_piquete(
    payload: PiqueteCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session_with_tenant),
):
    """Cadastra um novo piquete/pastagem na fazenda."""
    svc = PiqueteService(tenant_id)
    svc.session = db
    return await svc.criar_piquete(db, obj_in=payload)
