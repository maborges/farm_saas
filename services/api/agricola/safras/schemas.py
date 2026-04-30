from pydantic import BaseModel, Field, model_validator, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class CultivoAreaCreate(BaseModel):
    """Definição de um cultivo dentro da safra."""
    area_id: UUID
    area_ha: float = Field(gt=0, description="Área em hectares")


class CultivoDefine(BaseModel):
    """Definição de um cultivo para ser criado com a safra."""
    cultura: str
    cultivar_id: UUID | None = None
    cultivar_nome: str | None = None
    commodity_id: UUID | None = None
    sistema_plantio: str | None = None
    populacao_prevista: int | None = Field(None, gt=0, le=500000)
    espacamento_cm: int | None = Field(None, gt=0, le=200)
    data_plantio_prevista: date | None = None
    produtividade_meta_sc_ha: float | None = Field(None, gt=0)
    preco_venda_previsto: float | None = Field(None, gt=0)
    observacoes: str | None = None
    consorciado: bool = False
    data_inicio: date | None = None
    data_fim: date | None = None
    areas: list[CultivoAreaCreate] = Field(default_factory=list, description="Talhões e áreas do cultivo")

    # Validação removida: cultivar_id e cultivar_nome são opcionais
    # A cultura já é obrigatória, cultivar é apenas complemento


class SafraCreate(BaseModel):
    """Cria uma safra com um ou mais cultivos atomicamente."""
    ano_safra: str = Field(..., pattern=r"^\d{4}(/\d{2,4})?$")
    talhao_ids: list[UUID] | None = None  # LEGADO: para compatibilidade
    cultivos: list[CultivoDefine] = Field(default_factory=list, description="Cultivos da safra")
    observacoes: str | None = None

    # Campos legados aceitos na raiz (compat. com clientes antigos e testes)
    cultura: str | None = None
    cultivar_id: UUID | None = None
    cultivar_nome: str | None = None
    commodity_id: UUID | None = None
    sistema_plantio: str | None = None
    area_plantada_ha: float | None = Field(None, gt=0)
    produtividade_meta_sc_ha: float | None = Field(None, gt=0)
    preco_venda_previsto: float | None = Field(None, gt=0)
    populacao_prevista: int | None = Field(None, gt=0, le=500000)
    espacamento_cm: int | None = Field(None, gt=0, le=200)
    data_plantio_prevista: date | None = None

    @model_validator(mode="after")
    def validar_campos(self):
        # Valida que ao menos uma forma de definir cultivos foi informada
        if not self.cultivos and not self.talhao_ids:
            raise ValueError("Informe cultivos ou talhao_ids")
        return self

class SafraUpdate(BaseModel):
    ano_safra: str | None = Field(None, pattern=r"^\d{4}(/\d{2,4})?$")
    cultura: str | None = None
    cultivar_id: UUID | None = None
    cultivar_nome: str | None = None
    commodity_id: UUID | None = None
    sistema_plantio: str | None = None
    data_plantio_prevista: date | None = None
    data_plantio_real: date | None = None
    data_colheita_prevista: date | None = None
    data_colheita_real: date | None = None
    populacao_prevista: int | None = Field(None, gt=0, le=500000)
    populacao_real: int | None = Field(None, gt=0, le=500000)
    espacamento_cm: int | None = Field(None, gt=0, le=200)
    area_plantada_ha: float | None = Field(None, gt=0)
    produtividade_meta_sc_ha: float | None = Field(None, gt=0)
    produtividade_real_sc_ha: float | None = Field(None, gt=0)
    preco_venda_previsto: float | None = Field(None, gt=0)
    custo_previsto_ha: float | None = Field(None, gt=0)
    custo_realizado_ha: float | None = Field(None, gt=0)
    status: str | None = None
    observacoes: str | None = None

class SafraAvancarFase(BaseModel):
    novo_status: str | None = None
    observacao: Optional[str] = None
    dados_fase: Optional[dict] = None
    forcar_avanco: bool = False
    justificativa_forcar_avanco: Optional[str] = None


class SafraFaseHistoricoResponse(BaseModel):
    id: UUID
    safra_id: UUID
    fase_anterior: str | None
    fase_nova: str
    usuario_id: UUID | None
    observacao: str | None
    dados_fase: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SafraResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    ano_safra: str
    cultura: str | None = None  # legado: cultura principal (detalhes em cultivos[])
    status: str
    observacoes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SafraTalhaoResponse(BaseModel):
    id: UUID
    safra_id: UUID
    area_id: UUID
    principal: bool
    area_ha: float | None

    model_config = ConfigDict(from_attributes=True)


class SafraTalhoesSincronizar(BaseModel):
    talhao_ids: list[UUID]
    areas_ha: dict[str, float] | None = None  # area_id (str) → ha


# ───── Estoque (Inventory) ─────────────────────────────────────────────────────

class SaldoDepositoItem(BaseModel):
    """Saldo atual de um produto em um depósito"""
    produto_id: UUID
    produto_nome: str
    deposito_id: UUID
    deposito_nome: str
    quantidade_atual: float
    unidade: str | None = None
    status_lotes: str | None = None  # "ATIVO", "COM_VENCIDOS", "COM_ESGOTADOS"
    preco_unitario_medio: float | None = None


class EstoqueResumoResponse(BaseModel):
    """Resumo de saldo de estoque para uma safra"""
    safra_id: UUID
    total_produtos_ativos: int
    total_depositos: int
    saldos: list[SaldoDepositoItem]

    model_config = ConfigDict(from_attributes=True)


class MovimentacaoSafraResponse(BaseModel):
    """Histórico de movimentação de estoque para uma safra"""
    id: UUID
    produto_id: UUID
    produto_nome: str
    lote_id: UUID | None
    numero_lote: str | None
    deposito_id: UUID
    deposito_nome: str
    tipo: str  # ENTRADA, SAIDA, AJUSTE, TRANSFERENCIA
    quantidade: float
    unidade: str | None
    custo_unitario: float | None
    custo_total: float | None
    motivo: str | None
    origem_id: UUID | None
    origem_tipo: str | None  # "OPERACAO_AGRICOLA", "PEDIDO_COMPRA", etc
    operacao_tipo: str | None  # Ex: "PLANTIO", "COLHEITA" (se origem_tipo == OPERACAO_AGRICOLA)
    data_movimentacao: datetime

    model_config = ConfigDict(from_attributes=True)


class LoteItemResponse(BaseModel):
    """Detalhe de um lote (batch) de estoque"""
    id: UUID
    numero_lote: str
    produto_id: UUID
    produto_nome: str
    deposito_id: UUID
    deposito_nome: str
    quantidade_inicial: float
    quantidade_atual: float
    custo_unitario: float
    status: str  # ATIVO, ESGOTADO
    data_fabricacao: date | None
    data_validade: date | None
    nota_fiscal_ref: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LotesResponse(BaseModel):
    """Resposta com lista de lotes consumidos em operações da safra"""
    safra_id: UUID
    total_lotes: int
    lotes: list[LoteItemResponse]
