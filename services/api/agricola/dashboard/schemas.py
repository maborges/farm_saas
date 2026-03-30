"""Schemas para dashboard agrícola com dados financeiros."""
from pydantic import BaseModel
from uuid import UUID


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

    # Financeiro Integrado
    despesa_total: float  # De fin_despesas WHERE origem_tipo = OPERACAO_AGRICOLA
    receita_total: float  # De fin_receitas WHERE origem_tipo = ROMANEIO_COLHEITA
    lucro_bruto: float
    roi_pct: float | None


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
