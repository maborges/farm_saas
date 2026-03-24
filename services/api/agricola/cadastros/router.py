from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.cadastros.schemas import CulturaCreate, CulturaUpdate, CulturaResponse
from agricola.cadastros.service import CulturaService

router = APIRouter(prefix="/culturas", tags=["Cadastros Agrícolas"])

@router.post("/", response_model=CulturaResponse, status_code=status.HTTP_201_CREATED)
async def criar_cultura(
    dados: CulturaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = CulturaService(session, tenant_id)
    cultura = await svc.create(dados)
    return CulturaResponse.model_validate(cultura)

@router.get("/", response_model=List[CulturaResponse])
async def listar_culturas(
    ativo: bool | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = CulturaService(session, tenant_id)
    filters = {}
    if ativo is not None:
        filters["ativa"] = ativo
    culturas = await svc.list_all(**filters)
    return [CulturaResponse.model_validate(c) for c in culturas]

@router.get("/{id}", response_model=CulturaResponse)
async def detalhar_cultura(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = CulturaService(session, tenant_id)
    cultura = await svc.get_or_fail(id)
    return CulturaResponse.model_validate(cultura)

@router.patch("/{id}", response_model=CulturaResponse)
async def atualizar_cultura(
    id: UUID,
    dados: CulturaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = CulturaService(session, tenant_id)
    cultura = await svc.update(id, dados)
    return CulturaResponse.model_validate(cultura)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_cultura(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = CulturaService(session, tenant_id)
    await svc.hard_delete(id)
