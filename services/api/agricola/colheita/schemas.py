from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
import uuid


class ProdutoColhidoCreate(BaseModel):
    safra_id: uuid.UUID
    talhao_id: uuid.UUID
    romaneio_id: Optional[uuid.UUID] = None
    commodity_id: uuid.UUID
    classificacao_id: Optional[uuid.UUID] = None
    quantidade: float = Field(gt=0)
    unidade: str
    peso_liquido_kg: float = Field(gt=0)
    umidade_pct: Optional[float] = None
    impureza_pct: Optional[float] = None
    avariados_pct: Optional[float] = None
    ardidos_pct: Optional[float] = None
    quebrados_pct: Optional[float] = None
    destino: Optional[str] = None
    armazem_id: Optional[uuid.UUID] = None
    data_entrada: date
    data_saida_prevista: Optional[date] = None
    nf_origem: Optional[str] = None
    observacoes: Optional[str] = None
    status: str = "ARMAZENADO"


class ProdutoColhidoUpdate(BaseModel):
    classificacao_id: Optional[uuid.UUID] = None
    destino: Optional[str] = None
    armazem_id: Optional[uuid.UUID] = None
    data_saida_prevista: Optional[date] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None


class ProdutoColhidoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    safra_id: uuid.UUID
    talhao_id: uuid.UUID
    romaneio_id: Optional[uuid.UUID]
    commodity_id: uuid.UUID
    classificacao_id: Optional[uuid.UUID]
    quantidade: float
    unidade: str
    peso_liquido_kg: float
    umidade_pct: Optional[float]
    impureza_pct: Optional[float]
    avariados_pct: Optional[float]
    ardidos_pct: Optional[float]
    quebrados_pct: Optional[float]
    destino: Optional[str]
    armazem_id: Optional[uuid.UUID]
    data_entrada: date
    data_saida_prevista: Optional[date]
    nf_origem: Optional[str]
    observacoes: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumoEstoqueItem(BaseModel):
    """Uma linha do resumo: commodity + armazém + status."""
    commodity_id: uuid.UUID
    commodity_nome: Optional[str] = None
    commodity_codigo: Optional[str] = None
    commodity_tipo: Optional[str] = None
    unidade: str
    armazem_id: Optional[uuid.UUID] = None
    status: str
    total_quantidade: float
    total_peso_kg: float
    num_lotes: int


class ResumoEstoqueResponse(BaseModel):
    itens: list[ResumoEstoqueItem]
    total_geral_kg: float
    total_lotes: int

    model_config = {"from_attributes": True}
