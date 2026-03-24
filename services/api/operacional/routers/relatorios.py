from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date, timedelta
import uuid

from core.dependencies import get_session, get_current_tenant
from core.models.tenant import Tenant
from operacional.services.relatorio_service import OperacionalRelatorioService

router = APIRouter(prefix="/operacional/relatorios", tags=["Operacional — Relatórios"])


def _svc(session: AsyncSession, tenant: Tenant) -> OperacionalRelatorioService:
    return OperacionalRelatorioService(session, tenant.id)


@router.get("/custo-maquinario")
async def custo_por_maquinario(
    fazenda_id: Optional[uuid.UUID] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Custo total de manutenção (peças + mão de obra) por maquinário."""
    return await _svc(session, tenant).custo_por_maquinario(fazenda_id, data_inicio, data_fim)


@router.get("/consumo-insumos")
async def consumo_insumos_por_safra(
    safra_id: Optional[uuid.UUID] = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Consumo de insumos (quantidade e custo) por safra e por produto."""
    return await _svc(session, tenant).consumo_insumos_por_safra(safra_id)


@router.get("/movimentacoes")
async def movimentacoes_por_periodo(
    data_inicio: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    data_fim: date = Query(default_factory=date.today),
    fazenda_id: Optional[uuid.UUID] = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Movimentações de estoque agrupadas por produto e tipo no período."""
    return await _svc(session, tenant).movimentacoes_por_periodo(data_inicio, data_fim, fazenda_id)
