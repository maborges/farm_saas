from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module
from core.dependencies import get_session_with_tenant
from operacional.schemas.frota import (
    MaquinarioCreate, MaquinarioResponse, MaquinarioUpdate,
    PlanoManutencaoCreate, PlanoManutencaoResponse,
    OrdemServicoCreate, OrdemServicoResponse, OrdemServicoUpdate,
    ItemOrdemServicoCreate, ItemOrdemServicoResponse
)
from operacional.services.frota_service import FrotaService

router = APIRouter(prefix="/frota", tags=["Frota — Maquinários"])

@router.post("/", response_model=MaquinarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_maquinario(
    dados: MaquinarioCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("O1_FROTA"))
):
    svc = FrotaService(session, tenant_id)
    maq = await svc.create(dados)
    await session.commit()
    await session.refresh(maq)
    return maq

@router.get("/", response_model=List[MaquinarioResponse])
async def listar_maquinarios(
    fazenda_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("O1_FROTA"))
):
    svc = FrotaService(session, tenant_id)
    filters = {}
    if fazenda_id: filters["fazenda_id"] = fazenda_id
    return await svc.list_all(**filters)

@router.get("/{id}", response_model=MaquinarioResponse)
async def detalhar_maquinario(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("O1_FROTA"))
):
    svc = FrotaService(session, tenant_id)
    return await svc.get_or_fail(id)

@router.patch("/{id}", response_model=MaquinarioResponse)
async def atualizar_maquinario(
    id: UUID,
    dados: MaquinarioUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("O1_FROTA"))
):
    svc = FrotaService(session, tenant_id)
    maq = await svc.update(id, dados)
    await session.commit()
    await session.refresh(maq)
    return maq

# --- Planos de Manutenção ---

@router.post("/planos/", response_model=PlanoManutencaoResponse)
async def criar_plano(
    dados: PlanoManutencaoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("O1_FROTA"))
):
    svc = FrotaService(session, tenant_id)
    return await svc.criar_plano_manutencao(dados)

@router.get("/{maquinario_id}/planos", response_model=List[PlanoManutencaoResponse])
async def listar_planos(
    maquinario_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("O1_FROTA"))
):
    svc = FrotaService(session, tenant_id)
    return await svc.listar_planos(maquinario_id)

# --- Ordens de Serviço ---

@router.post("/os/", response_model=OrdemServicoResponse)
async def abrir_ordem_servico(
    dados: OrdemServicoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("O1_FROTA"))
):
    svc = FrotaService(session, tenant_id)
    return await svc.abrir_os(dados)

@router.post("/os/{os_id}/itens", response_model=ItemOrdemServicoResponse)
async def adicionar_peça_os(
    os_id: UUID,
    dados: ItemOrdemServicoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("O1_FROTA"))
):
    svc = FrotaService(session, tenant_id)
    return await svc.adicionar_item_os(os_id, dados)

@router.patch("/os/{os_id}/fechar", response_model=OrdemServicoResponse)
async def fechar_ordem_servico(
    os_id: UUID,
    dados: OrdemServicoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("O1_FROTA"))
):
    svc = FrotaService(session, tenant_id)
    return await svc.fechar_os(os_id, dados)
