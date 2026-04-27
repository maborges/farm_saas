from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, get_session_with_tenant, require_tenant_permission
from core.exceptions import EntityNotFoundError
from agricola.cultivos.service import CultivoService
from agricola.cultivos.schemas import (
    CultivoCreate,
    CultivoUpdate,
    CultivoResponse,
    CultivoAreaCreate,
    CultivoAreaAnalisePatch,
    CultivoAreaResponse,
    TarefaSoloGerada,
)

router = APIRouter(prefix="/safras", tags=["Cultivos"])


@router.get("/{safra_id}/cultivos", response_model=list[CultivoResponse])
async def listar_cultivos(
    safra_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
):
    service = CultivoService(session, tenant_id)
    cultivos = await service.listar_por_safra(safra_id)
    return [CultivoResponse.model_validate(c) for c in cultivos]


@router.post("/{safra_id}/cultivos", response_model=CultivoResponse, status_code=status.HTTP_201_CREATED)
async def criar_cultivo(
    safra_id: UUID,
    cultivo_in: CultivoCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
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
    session: AsyncSession = Depends(get_session_with_tenant),
):
    service = CultivoService(session, tenant_id)
    try:
        cultivo = await service.get_com_areas(cultivo_id)
        return CultivoResponse.model_validate(cultivo)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo não encontrado.")


@router.patch("/{safra_id}/cultivos/{cultivo_id}", response_model=CultivoResponse)
async def atualizar_cultivo(
    safra_id: UUID,
    cultivo_id: UUID,
    cultivo_in: CultivoUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
    _: bool = Depends(require_tenant_permission("agricola:cultivo:editar")),
):
    service = CultivoService(session, tenant_id)
    try:
        cultivo = await service.atualizar_com_areas(cultivo_id, cultivo_in.model_dump(exclude_unset=True))
        await session.commit()
        return CultivoResponse.model_validate(cultivo)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo não encontrado.")


@router.delete("/{safra_id}/cultivos/{cultivo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_cultivo(
    safra_id: UUID,
    cultivo_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
    _: bool = Depends(require_tenant_permission("agricola:cultivo:deletar")),
):
    service = CultivoService(session, tenant_id)
    try:
        await service.hard_delete(cultivo_id)
        await session.commit()
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo não encontrado.")


@router.patch(
    "/{safra_id}/cultivos/{cultivo_id}/areas/{area_id}/analise",
    response_model=CultivoAreaResponse,
    tags=["Análise Solo"],
)
async def vincular_analise_area(
    safra_id: UUID,
    cultivo_id: UUID,
    area_id: UUID,
    dados: CultivoAreaAnalisePatch,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
):
    """Vincula ou rejeita uma análise de solo para este talhão/cultivo."""
    service = CultivoService(session, tenant_id)
    try:
        area = await service.vincular_analise(area_id, dados)
        return CultivoAreaResponse.model_validate(area)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CultivoArea não encontrado.")


@router.get(
    "/{safra_id}/cultivos/{cultivo_id}/areas/{area_id}/tarefas-solo",
    response_model=list[TarefaSoloGerada],
    tags=["Análise Solo"],
)
async def preview_tarefas_solo(
    safra_id: UUID,
    cultivo_id: UUID,
    area_id: UUID,
    analise_id: UUID | None = None,
    regiao: str | None = None,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
):
    """Retorna preview das tarefas. analise_id e regiao sobrepõem o vínculo salvo no banco."""
    from core.exceptions import BusinessRuleError
    service = CultivoService(session, tenant_id)
    try:
        return await service.gerar_tarefas_solo(area_id, analise_id=analise_id, regiao=regiao)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CultivoArea não encontrado.")
    except BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.put("/{safra_id}/cultivos/{cultivo_id}/areas")
async def sincronizar_areas(
    safra_id: UUID,
    cultivo_id: UUID,
    areas_in: list[CultivoAreaCreate],
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
    _: bool = Depends(require_tenant_permission("agricola:cultivo:editar")),
):
    service = CultivoService(session, tenant_id)
    try:
        cultivo = await service.sincronizar_areas(cultivo_id, areas_in)
        return CultivoResponse.model_validate(cultivo)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo não encontrado.")
