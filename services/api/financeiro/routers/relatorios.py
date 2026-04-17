from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id, require_module
from financeiro.schemas.relatorio_schema import (
    FluxoCaixaResponse,
    LivroCaixaResponse,
    DREResponse,
    DashboardFinanceiroResponse,
    CentroCustoResponse,
)
from financeiro.services.relatorio_service import RelatorioService
from financeiro.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/relatorios",
    tags=["Financeiro — Relatórios (F1)"],
    dependencies=[Depends(require_module("F1_TESOURARIA"))],
)


@router.get("/dashboard", response_model=DashboardFinanceiroResponse)
async def dashboard_financeiro(
    unidade_produtiva_id: Optional[uuid.UUID] = Query(None),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Dashboard financeiro: posição atual, vencimentos próximos (7/15/30d),
    inadimplência, top categorias do mês e alertas priorizados.
    """
    svc = DashboardService(db, tenant_id)
    return await svc.resumo(unidade_produtiva_id)


@router.get("/fluxo-caixa", response_model=FluxoCaixaResponse)
async def fluxo_caixa(
    data_inicio: date = Query(..., description="Início do período (YYYY-MM-DD)"),
    data_fim: date = Query(..., description="Fim do período (YYYY-MM-DD)"),
    unidade_produtiva_id: Optional[uuid.UUID] = Query(None),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Fluxo de Caixa mensal: realizado (pagos/recebidos) + previsto (a vencer).
    Retorna um registro por mês dentro do período informado.
    """
    svc = RelatorioService(db, tenant_id)
    return await svc.fluxo_caixa(data_inicio, data_fim, unidade_produtiva_id)


@router.get("/livro-caixa", response_model=LivroCaixaResponse)
async def livro_caixa(
    competencia_inicio: date = Query(..., description="Início da competência fiscal (YYYY-MM-DD)"),
    competencia_fim: date = Query(..., description="Fim da competência fiscal (YYYY-MM-DD)"),
    unidade_produtiva_id: Optional[uuid.UUID] = Query(None),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Livro Caixa do Produtor Rural (RFB).
    Agrupa lançamentos realizados por categoria RFB do plano de contas.
    Usa o campo `competencia` do lançamento quando preenchido.
    """
    svc = RelatorioService(db, tenant_id)
    return await svc.livro_caixa(competencia_inicio, competencia_fim, unidade_produtiva_id)


@router.get("/centro-custos", response_model=CentroCustoResponse)
async def centro_custos(
    data_inicio: date = Query(..., description="Início do período (YYYY-MM-DD)"),
    data_fim: date = Query(..., description="Fim do período (YYYY-MM-DD)"),
    unidade_produtiva_id: Optional[uuid.UUID] = Query(None),
    safra_id: Optional[uuid.UUID] = Query(None, description="Filtrar por safra específica"),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Custo por centro de custo (safra/talhão).
    Considera despesas pagas com rateios registrados, agrupadas por categoria.
    """
    svc = RelatorioService(db, tenant_id)
    return await svc.centro_custos(data_inicio, data_fim, unidade_produtiva_id, safra_id)


@router.get("/dre", response_model=DREResponse)
async def dre(
    data_inicio: date = Query(..., description="Início do período (YYYY-MM-DD)"),
    data_fim: date = Query(..., description="Fim do período (YYYY-MM-DD)"),
    unidade_produtiva_id: Optional[uuid.UUID] = Query(None),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    DRE simplificado: Receita da Atividade Rural - Custeio = Resultado da Atividade.
    Agrupa por categoria RFB (custeio, investimento, não-dedutível).
    """
    svc = RelatorioService(db, tenant_id)
    return await svc.dre(data_inicio, data_fim, unidade_produtiva_id)
