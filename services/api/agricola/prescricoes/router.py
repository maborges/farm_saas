from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, get_session_with_tenant
from agricola.prescricoes.schemas import PrescricaoVRACreate, PrescricaoVRAResponse
from agricola.prescricoes.service import PrescricaoService

router = APIRouter(prefix="/prescricoes", tags=["Mapas de Prescrição (VRA)"])

@router.post("/", response_model=PrescricaoVRAResponse, status_code=status.HTTP_201_CREATED)
async def criar_prescricao(
    dados: PrescricaoVRACreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = PrescricaoService(session, tenant_id)
    obj = await svc.create(dados.model_dump())
    await session.commit()
    return obj

@router.get("/", response_model=List[PrescricaoVRAResponse])
async def listar_prescricoes(
    talhao_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = PrescricaoService(session, tenant_id)
    filters = {}
    if talhao_id: filters["talhao_id"] = talhao_id
    return await svc.list_all(**filters)

@router.get("/{id}", response_model=PrescricaoVRAResponse)
async def detalhar_prescricao(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = PrescricaoService(session, tenant_id)
    return await svc.get_or_fail(id)
