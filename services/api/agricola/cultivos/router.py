from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, get_session, require_tenant_permission
from core.exceptions import EntityNotFoundError
from agricola.cultivos.service import CultivoService
from agricola.cultivos.schemas import (
    CultivoCreate,
    CultivoUpdate,
    CultivoResponse,
    CultivoAreaCreate,
)

router = APIRouter(prefix="/safras", tags=["Cultivos"])


@router.get("/{safra_id}/cultivos", response_model=list[CultivoResponse])
async def listar_cultivos(
    safra_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    service = CultivoService(session, tenant_id)
    cultivos = await service.listar_por_safra(safra_id)
    return [CultivoResponse.model_validate(c) for c in cultivos]


@router.post("/{safra_id}/cultivos", response_model=CultivoResponse, status_code=status.HTTP_201_CREATED)
async def criar_cultivo(
    safra_id: UUID,
    cultivo_in: CultivoCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(require_tenant_permission("agricola:cultivo:criar")),
):
    service = CultivoService(session, tenant_id)
    cultivo = await service.criar_com_areas(safra_id, cultivo_in)
    return CultivoResponse.model_validate(cultivo)


@router.get("/{safra_id}/cultivos/{cultivo_id}", response_model=CultivoResponse)
async def get_cultivo(
    safra_id: UUID,
    cultivo_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    service = CultivoService(session, tenant_id)
    try:
        cultivo = await service.get_or_fail(cultivo_id)
        return CultivoResponse.model_validate(cultivo)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo não encontrado.")


@router.patch("/{safra_id}/cultivos/{cultivo_id}", response_model=CultivoResponse)
async def atualizar_cultivo(
    safra_id: UUID,
    cultivo_id: UUID,
    cultivo_in: CultivoUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(require_tenant_permission("agricola:cultivo:editar")),
):
    service = CultivoService(session, tenant_id)
    try:
        updates = cultivo_in.model_dump(exclude_unset=True)
        cultivo = await service.update(cultivo_id, updates)
        return CultivoResponse.model_validate(cultivo)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo não encontrado.")


@router.delete("/{safra_id}/cultivos/{cultivo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_cultivo(
    safra_id: UUID,
    cultivo_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(require_tenant_permission("agricola:cultivo:deletar")),
):
    service = CultivoService(session, tenant_id)
    try:
        await service.hard_delete(cultivo_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo não encontrado.")


@router.put("/{safra_id}/cultivos/{cultivo_id}/areas")
async def sincronizar_areas(
    safra_id: UUID,
    cultivo_id: UUID,
    areas_in: list[CultivoAreaCreate],
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(require_tenant_permission("agricola:cultivo:editar")),
):
    service = CultivoService(session, tenant_id)
    try:
        cultivo = await service.sincronizar_areas(cultivo_id, areas_in)
        return CultivoResponse.model_validate(cultivo)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo não encontrado.")
