from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.safras.schemas import SafraCreate, SafraResponse, SafraUpdate
from agricola.safras.service import SafraService

router = APIRouter(prefix="/safras", tags=["Safras"])

@router.post(
    "/",
    response_model=SafraResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova safra",
)
async def criar_safra(
    dados: SafraCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.criar(dados)
    return SafraResponse.model_validate(safra)


@router.get(
    "/",
    response_model=List[SafraResponse],
    summary="Lista safras de um talhão",
)
async def listar_safras(
    talhao_id: UUID | None = None,
    ano_safra: str | None = None,
    cultura: str | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraService(session, tenant_id)
    filters = {}
    if talhao_id: filters["talhao_id"] = talhao_id
    if ano_safra: filters["ano_safra"] = ano_safra
    if cultura: filters["cultura"] = cultura
    if status: filters["status"] = status
    
    safras = await svc.list_all(**filters)
    return [SafraResponse.model_validate(s) for s in safras]


@router.get(
    "/{id}",
    response_model=SafraResponse,
    summary="Detalhes de uma safra",
)
async def detalhar_safra(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.get_or_fail(id)
    return SafraResponse.model_validate(safra)

@router.patch(
    "/{id}",
    response_model=SafraResponse,
    summary="Atualiza dados da safra",
)
async def atualizar_safra(
    id: UUID,
    dados: SafraUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.atualizar(id, dados)
    return SafraResponse.model_validate(safra)

@router.get(
    "/{id}/resumo",
    summary="Planejado vs realizado da safra",
)
async def resumo_safra(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    """
    Retorna comparativo planejado vs realizado:
    custo, produtividade (sc/ha), receita e resultado líquido.
    """
    svc = SafraService(session, tenant_id)
    return await svc.resumo_planejado_realizado(id)


class StatusUpdate(BaseModel):
    novo_status: str

@router.patch(
    "/{id}/status",
    response_model=SafraResponse,
    summary="Transição de status da safra",
)
async def atualizar_status_safra(
    id: UUID,
    dados: StatusUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = SafraService(session, tenant_id)
    safra = await svc.atualizar_status(id, dados.novo_status)
    return SafraResponse.model_validate(safra)
