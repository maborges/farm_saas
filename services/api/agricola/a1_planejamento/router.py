"""
Router do módulo A1 - Planejamento de Safra.
"""
from fastapi import APIRouter, Depends, status, Query
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from core.dependencies import get_session, get_tenant_id, require_module
from core.constants import Modulos
from agricola.a1_planejamento.schemas import (
    ItemOrcamentoCreate,
    ItemOrcamentoUpdate,
    ItemOrcamentoResponse,
    OrcamentoSafraResponse,
    CampanhasResponse,
)
from agricola.a1_planejamento.service import PlanejamentoService

router = APIRouter(
    prefix="/agricola/planejamento",
    tags=["Agrícola - Planejamento de Safra (A1)"],
    dependencies=[Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO))],
)


@router.get("/campanhas", response_model=CampanhasResponse)
async def listar_campanhas(
    ano_safra: Optional[str] = Query(None, description="Ex: 2024/2025"),
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """KPIs de todas as safras: área, custo previsto vs. realizado, produtividade e receita esperada."""
    svc = PlanejamentoService(db, tenant_id)
    return await svc.listar_campanhas(ano_safra)


@router.get("/safras/{safra_id}/orcamento", response_model=OrcamentoSafraResponse)
async def get_orcamento(
    safra_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Orçamento completo da safra: previsto (itens) × realizado (operações + rateios financeiros).
    Inclui desvio %, ponto de equilíbrio em sc/ha e breakdown por categoria.
    """
    svc = PlanejamentoService(db, tenant_id)
    return await svc.get_orcamento(safra_id)


@router.get("/safras/{safra_id}/itens", response_model=List[ItemOrcamentoResponse])
async def listar_itens(
    safra_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Lista todos os itens do orçamento previsto da safra."""
    svc = PlanejamentoService(db, tenant_id)
    return await svc.listar_itens(safra_id)


@router.post(
    "/safras/{safra_id}/itens",
    response_model=ItemOrcamentoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_item(
    safra_id: UUID,
    payload: ItemOrcamentoCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Adiciona um item ao orçamento previsto. custo_total = quantidade × custo_unitario."""
    svc = PlanejamentoService(db, tenant_id)
    return await svc.criar_item(safra_id, payload)


@router.patch("/safras/{safra_id}/itens/{item_id}", response_model=ItemOrcamentoResponse)
async def atualizar_item(
    safra_id: UUID,
    item_id: UUID,
    payload: ItemOrcamentoUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Atualiza um item do orçamento. Recalcula custo_total automaticamente."""
    svc = PlanejamentoService(db, tenant_id)
    return await svc.atualizar_item(item_id, payload)


@router.delete("/safras/{safra_id}/itens/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_item(
    safra_id: UUID,
    item_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Remove um item do orçamento."""
    svc = PlanejamentoService(db, tenant_id)
    await svc.deletar_item(item_id)
