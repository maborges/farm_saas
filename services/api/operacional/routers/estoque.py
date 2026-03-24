from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from core.dependencies import get_session, get_current_tenant
from core.models.tenant import Tenant
from operacional.services.estoque_service import EstoqueService
from core.dependencies import get_current_user
from core.models.auth import Usuario
from operacional.schemas.estoque import (
    DepositoCreate, DepositoUpdate, DepositoResponse,
    SaldoResponse,
    EntradaEstoqueRequest, SaidaEstoqueRequest,
    AjusteEstoqueRequest, TransferenciaEstoqueRequest,
    MovimentacaoResponse, AlertaEstoqueItem,
    LoteCreate, LoteUpdate, LoteResponse,
    RequisicaoCreate, RequisicaoAprovarRequest, RequisicaoEntregarRequest, RequisicaoResponse,
    ReservaCreate, ReservaCancelarRequest, ReservaConsumirRequest, ReservaResponse,
)

router = APIRouter(prefix="/estoque", tags=["Operacional — Estoque"])


def _svc(session: AsyncSession, tenant: Tenant) -> EstoqueService:
    return EstoqueService(session, tenant.id)


# ── Lotes ─────────────────────────────────────────────────────────────────────

@router.get("/lotes", response_model=List[LoteResponse])
async def listar_lotes(
    produto_id: Optional[uuid.UUID] = Query(None),
    deposito_id: Optional[uuid.UUID] = Query(None),
    vencendo_em_dias: Optional[int] = Query(None, description="Lotes vencendo nos próximos N dias"),
    apenas_ativos: bool = Query(True),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    return await _svc(session, tenant).listar_lotes(produto_id, deposito_id, vencendo_em_dias, apenas_ativos)


@router.post("/lotes", response_model=LoteResponse, status_code=201)
async def criar_lote(
    data: LoteCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.criar_lote(data)
    await session.commit()
    return result


@router.patch("/lotes/{lote_id}", response_model=LoteResponse)
async def atualizar_lote(
    lote_id: uuid.UUID,
    data: LoteUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.atualizar_lote(lote_id, data)
    await session.commit()
    return result


@router.get("/lotes/alertas-validade", response_model=List[LoteResponse])
async def alertas_validade(
    dias: int = Query(30, description="Alertar lotes vencendo em X dias"),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    return await _svc(session, tenant).listar_lotes(vencendo_em_dias=dias)


# ── Depósitos ─────────────────────────────────────────────────────────────────

@router.get("/depositos", response_model=List[DepositoResponse])
async def listar_depositos(
    fazenda_id: Optional[uuid.UUID] = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    return await _svc(session, tenant).listar_depositos(fazenda_id)


@router.post("/depositos", response_model=DepositoResponse, status_code=201)
async def criar_deposito(
    data: DepositoCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.criar_deposito(data)
    await session.commit()
    return result


@router.patch("/depositos/{deposito_id}", response_model=DepositoResponse)
async def atualizar_deposito(
    deposito_id: uuid.UUID,
    data: DepositoUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.atualizar_deposito(deposito_id, data)
    await session.commit()
    return result


# ── Saldos ────────────────────────────────────────────────────────────────────

@router.get("/saldos", response_model=List[SaldoResponse])
async def listar_saldos(
    fazenda_id: Optional[uuid.UUID] = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    return await _svc(session, tenant).listar_saldos(fazenda_id)


@router.get("/alertas", response_model=List[AlertaEstoqueItem])
async def alertas_estoque_minimo(
    fazenda_id: Optional[uuid.UUID] = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    return await _svc(session, tenant).alertas_estoque_minimo(fazenda_id)


# ── Movimentações ─────────────────────────────────────────────────────────────

@router.get("/movimentacoes", response_model=List[MovimentacaoResponse])
async def listar_movimentacoes(
    produto_id: Optional[uuid.UUID] = Query(None),
    deposito_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    return await _svc(session, tenant).listar_movimentacoes(produto_id, deposito_id, limit)


@router.post("/movimentacoes/entrada", response_model=MovimentacaoResponse, status_code=201)
async def registrar_entrada(
    data: EntradaEstoqueRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.registrar_entrada(data)
    await session.commit()
    return result


@router.post("/movimentacoes/saida", response_model=MovimentacaoResponse, status_code=201)
async def registrar_saida(
    data: SaidaEstoqueRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.registrar_saida(data)
    await session.commit()
    return result


@router.post("/movimentacoes/ajuste", response_model=MovimentacaoResponse, status_code=201)
async def registrar_ajuste(
    data: AjusteEstoqueRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.registrar_ajuste(data)
    await session.commit()
    return result


@router.post("/movimentacoes/transferencia", response_model=List[MovimentacaoResponse], status_code=201)
async def registrar_transferencia(
    data: TransferenciaEstoqueRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.registrar_transferencia(data)
    await session.commit()
    return result


# ── Requisições de Material ────────────────────────────────────────────────────

@router.post("/requisicoes", response_model=RequisicaoResponse, status_code=201)
async def criar_requisicao(
    data: RequisicaoCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),
):
    svc = _svc(session, tenant)
    result = await svc.criar_requisicao(data, usuario.id)
    await session.commit()
    return result


@router.get("/requisicoes", response_model=List[RequisicaoResponse])
async def listar_requisicoes(
    fazenda_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    return await _svc(session, tenant).listar_requisicoes(fazenda_id, status)


@router.patch("/requisicoes/{req_id}/aprovar", response_model=RequisicaoResponse)
async def aprovar_requisicao(
    req_id: uuid.UUID,
    data: RequisicaoAprovarRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),
):
    svc = _svc(session, tenant)
    result = await svc.aprovar_requisicao(req_id, data, usuario.id)
    await session.commit()
    return result


@router.patch("/requisicoes/{req_id}/separar", response_model=RequisicaoResponse)
async def separar_requisicao(
    req_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.atualizar_status_requisicao(req_id, "SEPARANDO")
    await session.commit()
    return result


@router.patch("/requisicoes/{req_id}/entregar", response_model=RequisicaoResponse)
async def entregar_requisicao(
    req_id: uuid.UUID,
    data: RequisicaoEntregarRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.entregar_requisicao(req_id, data)
    await session.commit()
    return result


@router.patch("/requisicoes/{req_id}/recusar", response_model=RequisicaoResponse)
async def recusar_requisicao(
    req_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.atualizar_status_requisicao(req_id, "RECUSADA")
    await session.commit()
    return result


# ── Reservas de Estoque ────────────────────────────────────────────────────────

@router.get("/reservas", response_model=List[ReservaResponse])
async def listar_reservas(
    produto_id: Optional[uuid.UUID] = Query(None),
    deposito_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query("ATIVA", description="ATIVA | CONSUMIDA | CANCELADA | (vazio=todos)"),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    return await _svc(session, tenant).listar_reservas(produto_id, deposito_id, status or None)


@router.post("/reservas", response_model=ReservaResponse, status_code=201)
async def criar_reserva(
    data: ReservaCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),
):
    svc = _svc(session, tenant)
    result = await svc.criar_reserva(data, usuario.id)
    await session.commit()
    return result


@router.patch("/reservas/{reserva_id}/cancelar", response_model=ReservaResponse)
async def cancelar_reserva(
    reserva_id: uuid.UUID,
    data: ReservaCancelarRequest = ReservaCancelarRequest(),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.cancelar_reserva(reserva_id)
    await session.commit()
    return result


@router.patch("/reservas/{reserva_id}/consumir", response_model=ReservaResponse)
async def consumir_reserva(
    reserva_id: uuid.UUID,
    data: ReservaConsumirRequest = ReservaConsumirRequest(),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    result = await svc.consumir_reserva(reserva_id, data)
    await session.commit()
    return result
