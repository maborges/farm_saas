from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.talhoes.schemas import TalhaoCreate, TalhaoResponse, TalhaoUpdate
from agricola.talhoes.service import TalhaoService

router = APIRouter(prefix="/talhoes", tags=["Talhões"])

@router.post(
    "/",
    response_model=TalhaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra um novo talhão",
)
async def criar_talhao(
    dados: TalhaoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = TalhaoService(session, tenant_id)
    talhao = await svc.criar(dados)
    return await svc.serializar_com_geojson(talhao)


@router.get(
    "/",
    response_model=List[TalhaoResponse],
    summary="Lista talhões da fazenda",
)
async def listar_talhoes(
    fazenda_id: UUID,
    ativo: bool = True,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = TalhaoService(session, tenant_id)
    talhoes = await svc.list_all(fazenda_id=fazenda_id, ativo=ativo)
    # Serialize all to include GeoJSON
    return [await svc.serializar_com_geojson(t) for t in talhoes]


@router.get(
    "/{id}",
    response_model=TalhaoResponse,
    summary="Detalhes de um talhão",
)
async def detalhar_talhao(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = TalhaoService(session, tenant_id)
    talhao = await svc.get_or_fail(id)
    return await svc.serializar_com_geojson(talhao)


@router.patch(
    "/{id}",
    response_model=TalhaoResponse,
    summary="Atualiza dados do talhão",
)
async def atualizar_talhao(
    id: UUID,
    dados: TalhaoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = TalhaoService(session, tenant_id)
    talhao = await svc.atualizar(id, dados)
    return await svc.serializar_com_geojson(talhao)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativa o talhão (soft delete)",
)
async def deletar_talhao(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = TalhaoService(session, tenant_id)
    await svc.delete(id)
