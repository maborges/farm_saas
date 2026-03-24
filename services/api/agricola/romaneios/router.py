from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.romaneios.schemas import RomaneioColheitaCreate, RomaneioColheitaResponse
from agricola.romaneios.service import RomaneioService

router = APIRouter(prefix="/romaneios", tags=["Romaneios de Colheita"])

@router.post("/", response_model=RomaneioColheitaResponse, status_code=status.HTTP_201_CREATED)
async def criar_romaneio(
    dados: RomaneioColheitaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = RomaneioService(session, tenant_id)
    romaneio = await svc.criar(dados)
    return RomaneioColheitaResponse.model_validate(romaneio)

@router.get("/", response_model=List[RomaneioColheitaResponse])
async def listar_romaneios(
    safra_id: UUID | None = None,
    talhao_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = RomaneioService(session, tenant_id)
    filters = {}
    if safra_id: filters["safra_id"] = safra_id
    if talhao_id: filters["talhao_id"] = talhao_id
    
    romaneios = await svc.list_all(**filters)
    return [RomaneioColheitaResponse.model_validate(r) for r in romaneios]

@router.get("/{id}", response_model=RomaneioColheitaResponse)
async def detalhar_romaneio(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = RomaneioService(session, tenant_id)
    romaneio = await svc.get_or_fail(id)
    return RomaneioColheitaResponse.model_validate(romaneio)
