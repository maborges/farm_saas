from fastapi import APIRouter, Depends, status
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, get_session_with_tenant, require_module
from rh.models import ColaboradorRH, LancamentoDiaria, Empreitada
from rh.schemas import (
    ColaboradorCreate, ColaboradorResponse,
    DiarariaCreate, DiariaResponse, PagarDiariasRequest,
    EmpreitadaCreate, EmpreitadaResponse, ConcluirEmpreitadaRequest,
    DashboardRHResponse,
)
from rh.service import ColaboradorService, DiariaService, EmpreitadaService, get_dashboard_rh

router = APIRouter(prefix="/rh", tags=["RH — Recursos Humanos"])


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardRHResponse)
async def dashboard_rh(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    return await get_dashboard_rh(session, tenant_id)


# ── Colaboradores ─────────────────────────────────────────────────────────────

@router.get("/colaboradores", response_model=List[ColaboradorResponse])
async def listar_colaboradores(
    ativo: Optional[bool] = True,
    tipo_contrato: Optional[str] = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = ColaboradorService(session, tenant_id)
    filters: dict = {}
    if ativo is not None:
        filters["ativo"] = ativo
    if tipo_contrato:
        filters["tipo_contrato"] = tipo_contrato
    return await svc.list_all(**filters)


@router.post("/colaboradores", response_model=ColaboradorResponse, status_code=status.HTTP_201_CREATED)
async def criar_colaborador(
    dados: ColaboradorCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = ColaboradorService(session, tenant_id)
    col = await svc.criar(dados)
    await session.commit()
    await session.refresh(col)
    return col


@router.delete("/colaboradores/{colaborador_id}", status_code=200)
async def desativar_colaborador(
    colaborador_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = ColaboradorService(session, tenant_id)
    await svc.desativar(colaborador_id)
    return {"message": "Colaborador desativado."}


# ── Diárias ───────────────────────────────────────────────────────────────────

@router.get("/diarias", response_model=List[DiariaResponse])
async def listar_diarias(
    colaborador_id: Optional[UUID] = None,
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    from sqlalchemy.future import select as sa_select
    stmt = sa_select(LancamentoDiaria).where(LancamentoDiaria.tenant_id == tenant_id)
    if colaborador_id:
        stmt = stmt.where(LancamentoDiaria.colaborador_id == colaborador_id)
    if status:
        stmt = stmt.where(LancamentoDiaria.status == status)
    if data_inicio:
        stmt = stmt.where(LancamentoDiaria.data >= data_inicio)
    if data_fim:
        stmt = stmt.where(LancamentoDiaria.data <= data_fim)
    stmt = stmt.order_by(LancamentoDiaria.data.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/diarias", response_model=DiariaResponse, status_code=status.HTTP_201_CREATED)
async def lancar_diaria(
    dados: DiarariaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = DiariaService(session, tenant_id)
    diaria = await svc.criar(dados)
    await session.commit()
    await session.refresh(diaria)
    return diaria


@router.post("/diarias/pagar-lote", status_code=200)
async def pagar_diarias(
    dados: PagarDiariasRequest,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = DiariaService(session, tenant_id)
    count = await svc.pagar_lote(dados.ids, dados.data_pagamento)
    return {"message": f"{count} diária(s) marcada(s) como pagas."}


# ── Empreitadas ───────────────────────────────────────────────────────────────

@router.get("/empreitadas", response_model=List[EmpreitadaResponse])
async def listar_empreitadas(
    colaborador_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    from sqlalchemy.future import select as sa_select
    stmt = sa_select(Empreitada).where(Empreitada.tenant_id == tenant_id)
    if colaborador_id:
        stmt = stmt.where(Empreitada.colaborador_id == colaborador_id)
    if status_filter:
        stmt = stmt.where(Empreitada.status == status_filter)
    stmt = stmt.order_by(Empreitada.data_inicio.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/empreitadas", response_model=EmpreitadaResponse, status_code=status.HTTP_201_CREATED)
async def criar_empreitada(
    dados: EmpreitadaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = EmpreitadaService(session, tenant_id)
    emp = await svc.criar(dados)
    await session.commit()
    await session.refresh(emp)
    return emp


@router.patch("/empreitadas/{empreitada_id}/concluir", response_model=EmpreitadaResponse)
async def concluir_empreitada(
    empreitada_id: UUID,
    dados: ConcluirEmpreitadaRequest,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = EmpreitadaService(session, tenant_id)
    return await svc.concluir(empreitada_id, dados.quantidade_final, dados.data_fim)


@router.patch("/empreitadas/{empreitada_id}/pagar", response_model=EmpreitadaResponse)
async def pagar_empreitada(
    empreitada_id: UUID,
    data_pagamento: Optional[date] = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = EmpreitadaService(session, tenant_id)
    return await svc.pagar(empreitada_id, data_pagamento)
