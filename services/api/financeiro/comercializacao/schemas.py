from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
import uuid


STATUS_VALIDOS = {"RASCUNHO", "CONFIRMADO", "EM_TRANSITO", "ENTREGUE", "FINALIZADO", "CANCELADO"}


class ComercializacaoCreate(BaseModel):
    commodity_id: uuid.UUID
    comprador_id: uuid.UUID
    numero_contrato: Optional[str] = None
    quantidade: float = Field(gt=0)
    unidade: str
    preco_unitario: float = Field(gt=0)
    moeda: str = "BRL"
    forma_pagamento: Optional[str] = None
    data_entrega_prevista: Optional[date] = None
    local_entrega: Optional[str] = None
    frete_por_conta: Optional[str] = None
    produto_colhido_id: Optional[uuid.UUID] = None
    observacoes: Optional[str] = None

    @field_validator("moeda")
    @classmethod
    def moeda_valida(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError("Moeda deve ter 3 caracteres (ex: BRL, USD)")
        return v.upper()


class ComercializacaoUpdate(BaseModel):
    numero_contrato: Optional[str] = None
    preco_unitario: Optional[float] = None
    forma_pagamento: Optional[str] = None
    data_entrega_prevista: Optional[date] = None
    data_entrega_real: Optional[date] = None
    local_entrega: Optional[str] = None
    frete_por_conta: Optional[str] = None
    nf_numero: Optional[str] = None
    nf_serie: Optional[str] = None
    nf_chave: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_valido(cls, v: str | None) -> str | None:
        if v is not None and v not in STATUS_VALIDOS:
            raise ValueError(f"Status deve ser um de: {', '.join(sorted(STATUS_VALIDOS))}")
        return v


class ComercializacaoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    numero_contrato: Optional[str]
    commodity_id: uuid.UUID
    comprador_id: uuid.UUID
    quantidade: float
    unidade: str
    preco_unitario: float
    moeda: str
    valor_total: float
    forma_pagamento: Optional[str]
    data_pagamento: Optional[date]
    data_entrega_prevista: Optional[date]
    data_entrega_real: Optional[date]
    local_entrega: Optional[str]
    frete_por_conta: Optional[str]
    produto_colhido_id: Optional[uuid.UUID]
    nf_numero: Optional[str]
    nf_serie: Optional[str]
    nf_chave: Optional[str]
    status: str
    observacoes: Optional[str]
    receita_id: Optional[uuid.UUID]
    criado_por: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
