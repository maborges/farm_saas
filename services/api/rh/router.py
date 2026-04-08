from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, get_session_with_tenant, require_module
from rh.schemas import (
    EsocialEventoCreate, EsocialEventoUpdate, EsocialEventoResponse,
    DepartamentoCreate, DepartamentoUpdate, DepartamentoResponse,
    ColaboradorCreate, ColaboradorResponse,
    DiariaCreate, DiariaResponse, PagarDiariasRequest,
    EmpreitadaCreate, EmpreitadaResponse, ConcluirEmpreitadaRequest,
    DashboardRHResponse,
)
from rh.service import EsocialEventoService, DepartamentoService, ColaboradorService, DiariaService, EmpreitadaService, get_dashboard_rh

router = APIRouter(prefix="/rh", tags=["RH — Recursos Humanos"])

MODULE = "RH1_REMUNERACAO"


# ── eSocial ───────────────────────────────────────────────────────────────────

@router.get("/esocial/eventos", response_model=List[EsocialEventoResponse])
async def listar_eventos_esocial(
    tipo_evento: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    periodo: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = EsocialEventoService(session, tenant_id)
    return await svc.listar_filtrado(tipo_evento, status, periodo)


@router.post("/esocial/eventos", response_model=EsocialEventoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_evento_esocial(
    dados: EsocialEventoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = EsocialEventoService(session, tenant_id)
    ev = await svc.criar(dados)
    await session.commit()
    await session.refresh(ev)
    return ev


@router.patch("/esocial/eventos/{evento_id}", response_model=EsocialEventoResponse)
async def atualizar_evento_esocial(
    evento_id: UUID,
    dados: EsocialEventoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = EsocialEventoService(session, tenant_id)
    ev = await svc.atualizar(evento_id, dados)
    await session.commit()
    await session.refresh(ev)
    return ev


# ── Departamentos ─────────────────────────────────────────────────────────────

@router.get("/departamentos", response_model=List[DepartamentoResponse])
async def listar_departamentos(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = DepartamentoService(session, tenant_id)
    return await svc.listar_com_contagem()


@router.post("/departamentos", response_model=DepartamentoResponse, status_code=status.HTTP_201_CREATED)
async def criar_departamento(
    dados: DepartamentoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = DepartamentoService(session, tenant_id)
    dep = await svc.criar(dados)
    await session.commit()
    await session.refresh(dep)
    return {**dep.__dict__, "total_colaboradores": 0}


@router.patch("/departamentos/{departamento_id}", response_model=DepartamentoResponse)
async def atualizar_departamento(
    departamento_id: UUID,
    dados: DepartamentoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = DepartamentoService(session, tenant_id)
    dep = await svc.atualizar(departamento_id, dados)
    await session.commit()
    await session.refresh(dep)
    rows = await svc.listar_com_contagem()
    total = next((r["total_colaboradores"] for r in rows if str(r["id"]) == str(departamento_id)), 0)
    return {**dep.__dict__, "total_colaboradores": total}


@router.delete("/departamentos/{departamento_id}", status_code=200)
async def desativar_departamento(
    departamento_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = DepartamentoService(session, tenant_id)
    dep = await svc.get_or_fail(departamento_id)
    dep.ativo = False
    session.add(dep)
    await session.commit()
    return {"message": "Departamento desativado."}


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardRHResponse)
async def dashboard_rh(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    return await get_dashboard_rh(session, tenant_id)


# ── Colaboradores ─────────────────────────────────────────────────────────────

@router.get("/colaboradores", response_model=List[ColaboradorResponse])
async def listar_colaboradores(
    ativo: Optional[bool] = Query(True),
    tipo_contrato: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
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
    _: None = Depends(require_module(MODULE)),
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
    _: None = Depends(require_module(MODULE)),
):
    svc = ColaboradorService(session, tenant_id)
    await svc.desativar(colaborador_id)
    return {"message": "Colaborador desativado."}


# ── Diárias ───────────────────────────────────────────────────────────────────

@router.get("/diarias", response_model=List[DiariaResponse])
async def listar_diarias(
    colaborador_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = DiariaService(session, tenant_id)
    return await svc.listar_filtrado(colaborador_id, status, data_inicio, data_fim)


@router.post("/diarias", response_model=DiariaResponse, status_code=status.HTTP_201_CREATED)
async def lancar_diaria(
    dados: DiariaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
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
    _: None = Depends(require_module(MODULE)),
):
    svc = DiariaService(session, tenant_id)
    count = await svc.pagar_lote(dados.ids, dados.data_pagamento)
    return {"message": f"{count} diária(s) marcada(s) como pagas."}


# ── Empreitadas ───────────────────────────────────────────────────────────────

@router.get("/empreitadas", response_model=List[EmpreitadaResponse])
async def listar_empreitadas(
    colaborador_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = EmpreitadaService(session, tenant_id)
    return await svc.listar_filtrado(colaborador_id, status_filter)


@router.post("/empreitadas", response_model=EmpreitadaResponse, status_code=status.HTTP_201_CREATED)
async def criar_empreitada(
    dados: EmpreitadaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
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
    _: None = Depends(require_module(MODULE)),
):
    svc = EmpreitadaService(session, tenant_id)
    return await svc.concluir(empreitada_id, dados.quantidade_final, dados.data_fim)


@router.patch("/empreitadas/{empreitada_id}/pagar", response_model=EmpreitadaResponse)
async def pagar_empreitada(
    empreitada_id: UUID,
    data_pagamento: Optional[date] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = EmpreitadaService(session, tenant_id)
    return await svc.pagar(empreitada_id, data_pagamento)
