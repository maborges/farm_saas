from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_session_with_tenant
from core.dependencies import get_tenant_id, require_module, require_role
from core.schemas.fazenda_input import FazendaCreate, FazendaUpdate
from core.schemas.fazenda_output import FazendaResponse
from core.services.fazenda_service import FazendaService

router = APIRouter(prefix="/fazendas", tags=["Core — Fazendas"])

@router.get(
    "/",
    response_model=List[FazendaResponse],
    summary="Lista todas as fazendas do Tenant logado",
)
async def listar_fazendas(
    # Dependencies
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("CORE")), 
    # Sem require_role pois quem tem modulo CORE no tenant pode ver suas fazendas globais
):
    svc = FazendaService(session, tenant_id)
    fazendas = await svc.list_all()
    return fazendas

@router.post(
    "/",
    response_model=FazendaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra uma nova fazenda rural atrelada ao tenant",
)
async def criar_fazenda(
    dados: FazendaCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("CORE")),
):
    svc = FazendaService(session, tenant_id)
    fazenda = await svc.create_fazenda(dados)
    # Importante: Como SQLAlchemy não auto-comita logo que se adiciona para permitir rollbacks:
    await session.commit()
    return fazenda

@router.get(
    "/{fazenda_id}",
    response_model=FazendaResponse,
    summary="Obtém detalhes de uma fazenda específica",
)
async def obter_fazenda(
    fazenda_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = FazendaService(session, tenant_id)
    # Se id não existir OU não pertencer ao tenant logado, levanta EntityNotFoundError
    fazenda = await svc.get_or_fail(fazenda_id)
    return fazenda

@router.put(
    "/{fazenda_id}",
    response_model=FazendaResponse,
    summary="Atualiza dados da fazenda",
)
async def atualizar_fazenda(
    fazenda_id: uuid.UUID,
    dados: FazendaUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = FazendaService(session, tenant_id)
    fazenda = await svc.update(fazenda_id, dados)
    await session.commit()
    return fazenda
