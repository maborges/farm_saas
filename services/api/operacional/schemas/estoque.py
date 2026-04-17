from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, List
from datetime import datetime, date
import uuid

TipoDeposito = Literal["GERAL", "COMBUSTIVEL", "DEFENSIVOS", "PECAS", "GRAOS", "OUTROS"]
StatusLote = Literal["ATIVO", "VENCIDO", "ESGOTADO", "BLOQUEADO"]


# ── Lote ──────────────────────────────────────────────────────────────────────

class LoteCreate(BaseModel):
    produto_id: uuid.UUID
    deposito_id: uuid.UUID
    numero_lote: str = Field(..., min_length=1, max_length=100)
    data_fabricacao: Optional[date] = None
    data_validade: Optional[date] = None
    quantidade_inicial: float = Field(..., gt=0)
    custo_unitario: float = Field(0.0, ge=0)
    nota_fiscal_ref: Optional[str] = Field(None, max_length=100)


class LoteUpdate(BaseModel):
    data_validade: Optional[date] = None
    nota_fiscal_ref: Optional[str] = Field(None, max_length=100)
    status: Optional[StatusLote] = None


class LoteResponse(BaseModel):
    id: uuid.UUID
    produto_id: uuid.UUID
    deposito_id: uuid.UUID
    numero_lote: str
    data_fabricacao: Optional[date]
    data_validade: Optional[date]
    quantidade_inicial: float
    quantidade_atual: float
    custo_unitario: float
    nota_fiscal_ref: Optional[str]
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
TipoMovimentacao = Literal["ENTRADA", "SAIDA", "TRANSFERENCIA", "AJUSTE"]


# ── Depósito ──────────────────────────────────────────────────────────────────

class DepositoCreate(BaseModel):
    unidade_produtiva_id: uuid.UUID
    nome: str = Field(..., min_length=2, max_length=100)
    tipo: TipoDeposito = "GERAL"
    localizacao_desc: Optional[str] = Field(None, max_length=200)


class DepositoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    tipo: Optional[TipoDeposito] = None
    localizacao_desc: Optional[str] = None
    ativo: Optional[bool] = None


class DepositoResponse(BaseModel):
    id: uuid.UUID
    unidade_produtiva_id: uuid.UUID
    nome: str
    tipo: str
    localizacao_desc: Optional[str]
    ativo: bool
    model_config = ConfigDict(from_attributes=True)


# ── Saldo ─────────────────────────────────────────────────────────────────────

class SaldoResponse(BaseModel):
    id: uuid.UUID
    deposito_id: uuid.UUID
    produto_id: uuid.UUID
    produto_nome: str
    deposito_nome: str
    quantidade_atual: float
    quantidade_reservada: float = 0.0
    quantidade_disponivel: float = 0.0
    unidade_medida: str
    preco_medio: float = 0.0
    abaixo_minimo: bool
    ultima_atualizacao: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Movimentações ─────────────────────────────────────────────────────────────

class EntradaEstoqueRequest(BaseModel):
    deposito_id: uuid.UUID
    produto_id: uuid.UUID
    quantidade: float = Field(..., gt=0)
    custo_unitario: float = Field(0.0, ge=0)
    motivo: Optional[str] = Field(None, max_length=255)
    origem_id: Optional[uuid.UUID] = None
    origem_tipo: Optional[str] = Field(None, max_length=50, description="PEDIDO_COMPRA | AJUSTE | INICIAL")
    lote_id: Optional[uuid.UUID] = None


class SaidaEstoqueRequest(BaseModel):
    deposito_id: Optional[uuid.UUID] = None  # None = busca automática por fazenda
    unidade_produtiva_id: Optional[uuid.UUID] = None
    produto_id: uuid.UUID
    quantidade: float = Field(..., gt=0)
    motivo: Optional[str] = Field(None, max_length=255)
    origem_id: Optional[uuid.UUID] = None
    origem_tipo: Optional[str] = Field(None, max_length=50)
    lote_id: Optional[uuid.UUID] = None  # Se informado, desconta do lote específico (PEPS por padrão)


class AjusteEstoqueRequest(BaseModel):
    deposito_id: uuid.UUID
    produto_id: uuid.UUID
    quantidade_nova: float = Field(..., ge=0, description="Quantidade correta após inventário")
    motivo: str = Field(..., min_length=3, max_length=255)


class TransferenciaEstoqueRequest(BaseModel):
    deposito_origem_id: uuid.UUID
    deposito_destino_id: uuid.UUID
    produto_id: uuid.UUID
    quantidade: float = Field(..., gt=0)
    motivo: Optional[str] = None


class MovimentacaoResponse(BaseModel):
    id: uuid.UUID
    deposito_id: uuid.UUID
    produto_id: uuid.UUID
    lote_id: Optional[uuid.UUID]
    tipo: str
    quantidade: float
    custo_unitario: Optional[float]
    custo_total: Optional[float]
    motivo: Optional[str]
    origem_id: Optional[uuid.UUID]
    origem_tipo: Optional[str]
    data_movimentacao: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Requisição Interna ────────────────────────────────────────────────────────

class ItemRequisicaoCreate(BaseModel):
    produto_id: uuid.UUID
    quantidade_solicitada: float = Field(..., gt=0)
    deposito_id: Optional[uuid.UUID] = None
    observacoes: Optional[str] = Field(None, max_length=255)


class RequisicaoCreate(BaseModel):
    unidade_produtiva_id: uuid.UUID
    data_necessidade: Optional[date] = None
    origem_tipo: str = Field("OUTRO", description="ORDEM_SERVICO | MANUTENCAO | PRODUCAO | OUTRO")
    origem_id: Optional[uuid.UUID] = None
    observacoes: Optional[str] = Field(None, max_length=500)
    itens: List[ItemRequisicaoCreate] = Field(..., min_length=1)


class ItemAprovacaoUpdate(BaseModel):
    item_id: uuid.UUID
    quantidade_aprovada: float = Field(..., ge=0)
    deposito_id: Optional[uuid.UUID] = None


class RequisicaoAprovarRequest(BaseModel):
    itens: List[ItemAprovacaoUpdate]


class ItemEntregaUpdate(BaseModel):
    item_id: uuid.UUID
    quantidade_entregue: float = Field(..., ge=0)
    lote_id: Optional[uuid.UUID] = None


class RequisicaoEntregarRequest(BaseModel):
    itens: List[ItemEntregaUpdate]


class ItemRequisicaoResponse(BaseModel):
    id: uuid.UUID
    produto_id: uuid.UUID
    deposito_id: Optional[uuid.UUID]
    lote_id: Optional[uuid.UUID]
    quantidade_solicitada: float
    quantidade_aprovada: Optional[float]
    quantidade_entregue: Optional[float]
    observacoes: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class RequisicaoResponse(BaseModel):
    id: uuid.UUID
    unidade_produtiva_id: uuid.UUID
    solicitante_id: uuid.UUID
    aprovador_id: Optional[uuid.UUID]
    data_solicitacao: datetime
    data_necessidade: Optional[date]
    status: str
    origem_tipo: str
    origem_id: Optional[uuid.UUID]
    observacoes: Optional[str]
    itens: List[ItemRequisicaoResponse] = []
    model_config = ConfigDict(from_attributes=True)


# ── Reservas de Estoque ────────────────────────────────────────────────────────

class ReservaCreate(BaseModel):
    produto_id: uuid.UUID
    deposito_id: uuid.UUID
    quantidade: float = Field(..., gt=0)
    motivo: str = Field(..., min_length=3, max_length=255)
    referencia_tipo: Optional[str] = Field(None, max_length=50, description="ORDEM_SERVICO | PEDIDO_COMPRA | SAFRA | REQUISICAO | MANUAL")
    referencia_id: Optional[uuid.UUID] = None


class ReservaCancelarRequest(BaseModel):
    motivo: Optional[str] = Field(None, max_length=255)


class ReservaConsumirRequest(BaseModel):
    quantidade: Optional[float] = Field(None, gt=0, description="Se omitido, consome a quantidade total reservada")
    motivo: Optional[str] = Field(None, max_length=255)


class ReservaResponse(BaseModel):
    id: uuid.UUID
    produto_id: uuid.UUID
    deposito_id: uuid.UUID
    criado_por_id: Optional[uuid.UUID]
    quantidade: float
    motivo: str
    referencia_tipo: Optional[str]
    referencia_id: Optional[uuid.UUID]
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Alertas ───────────────────────────────────────────────────────────────────

class AlertaEstoqueItem(BaseModel):
    produto_id: uuid.UUID
    produto_nome: str
    deposito_nome: str
    quantidade_atual: float
    estoque_minimo: float
    unidade_medida: str
    deficit: float
