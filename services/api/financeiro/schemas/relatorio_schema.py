from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import uuid


# ── Dashboard ─────────────────────────────────────────────────────────────────

class VencimentoProximo(BaseModel):
    id: uuid.UUID
    tipo: str  # RECEITA | DESPESA
    descricao: str
    valor: float
    data_vencimento: date
    dias_restantes: int
    pessoa_nome: Optional[str]  # fornecedor ou cliente (texto livre)


class TopCategoria(BaseModel):
    plano_conta_nome: str
    categoria_rfb: Optional[str]
    total: float
    quantidade: int


class AlertaFinanceiro(BaseModel):
    tipo: str   # VENCIMENTO_PROXIMO | ATRASADO | SALDO_NEGATIVO
    nivel: str  # INFO | ALERTA | CRITICO
    mensagem: str
    valor: float
    data_referencia: Optional[date] = None


class DashboardFinanceiroResponse(BaseModel):
    data_referencia: date
    unidade_produtiva_id: Optional[uuid.UUID]

    # Resumo do mês corrente
    total_recebido_mes: float
    total_pago_mes: float
    saldo_mes: float

    # Posição geral (todos os status abertos)
    total_a_receber: float
    total_a_pagar: float
    total_atrasado_receitas: float   # A_RECEBER vencido (< hoje)
    total_atrasado_despesas: float   # A_PAGAR vencido (< hoje)

    # Próximos vencimentos agrupados por janela
    vencendo_7d: List[VencimentoProximo]
    vencendo_8_15d: List[VencimentoProximo]
    vencendo_16_30d: List[VencimentoProximo]

    # Top 5 categorias (mês corrente)
    top_despesas: List[TopCategoria]
    top_receitas: List[TopCategoria]

    # Alertas priorizados
    alertas: List[AlertaFinanceiro]


class FluxoCaixaPeriodo(BaseModel):
    """Dados de um mês dentro do fluxo de caixa."""
    periodo: date  # Primeiro dia do mês

    # Realizado: valores já recebidos/pagos
    receitas_realizadas: float = 0.0
    despesas_realizadas: float = 0.0
    saldo_realizado: float = 0.0

    # Previsto: valores a vencer no período (status A_RECEBER / A_PAGAR / ATRASADO)
    receitas_previstas: float = 0.0
    despesas_previstas: float = 0.0
    saldo_previsto: float = 0.0

    # Saldo acumulado (running total do realizado)
    saldo_acumulado: float = 0.0


class FluxoCaixaTotais(BaseModel):
    total_receitas_realizadas: float
    total_despesas_realizadas: float
    total_saldo_realizado: float
    total_receitas_previstas: float
    total_despesas_previstas: float
    total_saldo_previsto: float


class FluxoCaixaResponse(BaseModel):
    data_inicio: date
    data_fim: date
    unidade_produtiva_id: Optional[uuid.UUID]
    periodos: List[FluxoCaixaPeriodo]
    totais: FluxoCaixaTotais


# ── Livro Caixa ───────────────────────────────────────────────────────────────

class LivroCaixaLancamento(BaseModel):
    data: date
    descricao: str
    tipo: str  # RECEITA | DESPESA
    categoria_rfb: Optional[str]
    plano_conta_nome: str
    valor: float
    forma: Optional[str]
    documento: Optional[str]  # numero_nf


class LivroCaixaGrupo(BaseModel):
    """Agrupamento por categoria RFB dentro do Livro Caixa."""
    categoria_rfb: str
    tipo: str
    total: float
    lancamentos: List[LivroCaixaLancamento]


class LivroCaixaResponse(BaseModel):
    competencia_inicio: date
    competencia_fim: date
    unidade_produtiva_id: Optional[uuid.UUID]
    total_receitas: float
    total_despesas: float
    resultado: float
    grupos: List[LivroCaixaGrupo]


# ── DRE ───────────────────────────────────────────────────────────────────────

class DREResponse(BaseModel):
    data_inicio: date
    data_fim: date
    unidade_produtiva_id: Optional[uuid.UUID]
    receita_bruta: float
    total_custeio: float
    total_investimento: float
    total_nao_dedutivel: float
    resultado_atividade_rural: float
    outras_receitas: float
    resultado_liquido: float


# ── Centro de Custos ──────────────────────────────────────────────────────────

class CentroCustoCategoria(BaseModel):
    plano_conta_nome: str
    categoria_rfb: Optional[str]
    total_rateado: float
    quantidade: int


class CentroCusto(BaseModel):
    """Custo agrupado por safra + talhão."""
    safra_id: Optional[uuid.UUID]
    safra_nome: Optional[str]       # "{cultura} {ano_safra}"
    talhao_id: Optional[uuid.UUID]
    talhao_nome: Optional[str]
    total_rateado: float
    por_categoria: List[CentroCustoCategoria]


class CentroCustoResponse(BaseModel):
    data_inicio: date
    data_fim: date
    unidade_produtiva_id: Optional[uuid.UUID]
    total_geral: float
    centros: List[CentroCusto]
