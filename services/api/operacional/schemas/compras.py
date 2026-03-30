from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid


# ── Recebimento Parcial ────────────────────────────────────────────────────────

class ItemRecebimentoCreate(BaseModel):
    item_pedido_id: uuid.UUID
    quantidade_recebida: float = Field(..., gt=0)
    preco_real_unitario: float = Field(0.0, ge=0)
    numero_lote_fornecedor: Optional[str] = Field(None, max_length=100, description="Supplier batch number")
    lote_id: Optional[uuid.UUID] = None


class RecebimentoCreate(BaseModel):
    numero_nf: Optional[str] = Field(None, max_length=50)
    chave_nfe: Optional[str] = Field(None, max_length=60)
    observacoes: Optional[str] = Field(None, max_length=500)
    itens: List[ItemRecebimentoCreate] = Field(..., min_length=1)


class ItemRecebimentoResponse(BaseModel):
    id: uuid.UUID
    item_pedido_id: uuid.UUID
    quantidade_recebida: float
    preco_real_unitario: float
    numero_lote_fornecedor: Optional[str]
    lote_id: Optional[uuid.UUID]
    model_config = ConfigDict(from_attributes=True)


class RecebimentoResponse(BaseModel):
    id: uuid.UUID
    pedido_id: uuid.UUID
    data_recebimento: datetime
    numero_nf: Optional[str]
    chave_nfe: Optional[str]
    observacoes: Optional[str]
    itens: List[ItemRecebimentoResponse] = []
    model_config = ConfigDict(from_attributes=True)


# ── Devolução ao Fornecedor ────────────────────────────────────────────────────

class ItemDevolucaoCreate(BaseModel):
    produto_id: uuid.UUID
    deposito_origem_id: uuid.UUID
    quantidade: float = Field(..., gt=0)
    custo_unitario: float = Field(0.0, ge=0)
    lote_id: Optional[uuid.UUID] = None


class DevolucaoCreate(BaseModel):
    fornecedor_id: uuid.UUID
    pedido_id: Optional[uuid.UUID] = None
    motivo: str = Field(..., description="DEFEITO | QUANTIDADE_ERRADA | FORA_SPEC | VENCIDO | OUTRO")
    observacoes: Optional[str] = Field(None, max_length=500)
    itens: List[ItemDevolucaoCreate] = Field(..., min_length=1)


class DevolucaoStatusUpdate(BaseModel):
    status: str = Field(..., description="ENVIADA | CONCLUIDA | RECUSADA")
    numero_nf_devolucao: Optional[str] = Field(None, max_length=50)


class ItemDevolucaoResponse(BaseModel):
    id: uuid.UUID
    produto_id: uuid.UUID
    deposito_origem_id: uuid.UUID
    quantidade: float
    custo_unitario: float
    lote_id: Optional[uuid.UUID]
    model_config = ConfigDict(from_attributes=True)


class DevolucaoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    fornecedor_id: uuid.UUID
    pedido_id: Optional[uuid.UUID]
    data_devolucao: datetime
    motivo: str
    status: str
    numero_nf_devolucao: Optional[str]
    observacoes: Optional[str]
    itens: List[ItemDevolucaoResponse] = []
    model_config = ConfigDict(from_attributes=True)
