from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Literal, Optional, List
from datetime import date, datetime
import uuid

FormasPagamento = Literal["PIX", "BOLETO", "TRANSFERENCIA", "DINHEIRO", "CARTAO", "CHEQUE", "DEBITO_AUTOMATICO"]
StatusDespesa = Literal["A_PAGAR", "PAGO", "PAGO_PARCIAL", "ATRASADO", "CANCELADO"]


class RateioCreate(BaseModel):
    safra_id: Optional[uuid.UUID] = None
    talhao_id: Optional[uuid.UUID] = None
    valor_rateado: float = Field(..., gt=0)
    percentual: float = Field(..., gt=0, le=100)


class DespesaCreate(BaseModel):
    unidade_produtiva_id: uuid.UUID
    plano_conta_id: uuid.UUID
    descricao: str = Field(..., min_length=3, max_length=255)
    valor_total: float = Field(..., gt=0)

    data_emissao: date
    data_vencimento: date
    data_pagamento: Optional[date] = None
    competencia: Optional[date] = None

    status: StatusDespesa = "A_PAGAR"
    forma_pagamento: Optional[FormasPagamento] = None
    valor_pago: Optional[float] = Field(None, gt=0)

    # Vínculo com Pessoas — preferível ao campo texto livre
    pessoa_id: Optional[uuid.UUID] = None
    fornecedor: Optional[str] = Field(None, max_length=150, description="Texto livre (usar pessoa_id quando possível)")

    # Parcelamento: se total_parcelas > 1, cria N despesas automaticamente
    total_parcelas: int = Field(1, ge=1, le=360, description="1 = sem parcelamento")

    # Fiscal
    numero_nf: Optional[str] = Field(None, max_length=20)
    serie_nf: Optional[str] = Field(None, max_length=5)
    chave_nfe: Optional[str] = Field(None, max_length=44)
    nota_fiscal: Optional[str] = Field(None, max_length=100, description="Legado")

    observacoes: Optional[str] = None
    rateios: List[RateioCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_rateio(self) -> "DespesaCreate":
        if self.rateios:
            total_pct = sum(r.percentual for r in self.rateios)
            total_val = sum(r.valor_rateado for r in self.rateios)
            if abs(total_pct - 100.0) > 0.01:
                raise ValueError("A soma dos percentuais do rateio deve ser exatamente 100%.")
            if abs(total_val - self.valor_total) > 0.01:
                raise ValueError("A soma dos valores rateados deve ser igual ao valor total da despesa.")
        return self


class DespesaUpdate(BaseModel):
    descricao: Optional[str] = Field(None, min_length=3, max_length=255)
    plano_conta_id: Optional[uuid.UUID] = None
    valor_total: Optional[float] = Field(None, gt=0)
    valor_pago: Optional[float] = Field(None, ge=0)
    data_emissao: Optional[date] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    competencia: Optional[date] = None
    status: Optional[StatusDespesa] = None
    forma_pagamento: Optional[FormasPagamento] = None
    pessoa_id: Optional[uuid.UUID] = None
    fornecedor: Optional[str] = Field(None, max_length=150)
    numero_nf: Optional[str] = Field(None, max_length=20)
    serie_nf: Optional[str] = Field(None, max_length=5)
    chave_nfe: Optional[str] = Field(None, max_length=44)
    observacoes: Optional[str] = None


class DespesaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    unidade_produtiva_id: uuid.UUID
    plano_conta_id: uuid.UUID
    pessoa_id: Optional[uuid.UUID]
    descricao: str
    valor_total: float
    valor_pago: Optional[float]
    data_emissao: date
    data_vencimento: date
    data_pagamento: Optional[date]
    competencia: Optional[date]
    status: str
    forma_pagamento: Optional[str]
    grupo_parcela_id: Optional[uuid.UUID]
    numero_parcela: Optional[int]
    total_parcelas: Optional[int]
    numero_nf: Optional[str]
    serie_nf: Optional[str]
    chave_nfe: Optional[str]
    fornecedor: Optional[str]
    nota_fiscal: Optional[str]
    observacoes: Optional[str]
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DespesaListItem(BaseModel):
    """Versão resumida para listagens."""
    id: uuid.UUID
    unidade_produtiva_id: uuid.UUID
    pessoa_id: Optional[uuid.UUID]
    fornecedor: Optional[str]
    descricao: str
    valor_total: float
    valor_pago: Optional[float]
    data_vencimento: date
    data_pagamento: Optional[date]
    status: str
    numero_parcela: Optional[int]
    total_parcelas: Optional[int]

    model_config = ConfigDict(from_attributes=True)
