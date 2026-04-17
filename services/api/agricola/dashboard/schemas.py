"""Schemas para dashboard agrícola com dados financeiros."""
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class FinanceiroResumo(BaseModel):
    """Resumo financeiro de uma safra."""

    # Operações
    total_operacoes: int
    custo_operacoes_total: float
    custo_por_ha: float

    # Romaneios
    total_romaneios: int
    total_sacas: float
    produtividade_sc_ha: float | None

    # Comercializações (vendas reais)
    total_comercializacoes: int = 0
    receita_comercializacoes: float = 0.0
    valor_total_vendido: float = 0.0  # só as FINALIZADO

    # Financeiro Integrado
    despesa_total: float  # De fin_despesas WHERE origem_tipo = OPERACAO_AGRICOLA
    receita_total: float  # De fin_receitas + comercializacoes
    lucro_bruto: float
    roi_pct: float | None

    # Margens
    margem_bruta: float = 0.0
    margem_por_ha: float = 0.0
    margem_pct: float | None = None  # (margem / receita) * 100


class SafraResumoFinanceiro(BaseModel):
    """Resumo financeiro completo de uma safra."""

    id: UUID
    cultura: str
    ano_safra: str
    status: str
    area_plantada_ha: float

    financeiro: FinanceiroResumo

    class Config:
        from_attributes = True


class TalhaoMargemItem(BaseModel):
    """Margem por talhão dentro de uma safra."""
    talhao_id: UUID
    talhao_nome: str
    area_ha: float
    custo_operacoes: float
    custo_por_ha: float
    receita_romaneios: float
    receita_comercializacoes: float
    receita_total: float
    margem_bruta: float
    margem_pct: float | None
    produtividade_sc_ha: float | None
    sacas_colhidas: float


class SafraMargemCompleta(BaseModel):
    """Dashboard de margem por safra com breakdown por talhão."""
    safra_id: UUID
    cultura: str
    ano_safra: str
    status: str
    area_total_ha: float

    custo_total: float
    custo_por_ha: float
    receita_total: float
    receita_por_ha: float
    margem_bruta: float
    margem_por_ha: float
    margem_pct: float | None
    roi_pct: float | None

    por_talhao: list[TalhaoMargemItem]

    breakdown_operacoes: list[dict] = Field(
        default_factory=list,
        description="Custo por tipo de operação: [{tipo, valor, percentual}]"
    )

