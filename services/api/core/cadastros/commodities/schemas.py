from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import uuid


class CommodityCreate(BaseModel):
    nome: str
    tipo: str
    unidade: str = "SACA_60KG"
    fator_conversao_tonelada: float = 1.0
    umidade_padrao: Optional[float] = None
    impureza_padrao: Optional[float] = None
    preco_referencia: Optional[float] = None
    ativo: bool = True
    dados_extras: Optional[dict[str, Any]] = None


class CommodityUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    unidade: Optional[str] = None
    fator_conversao_tonelada: Optional[float] = None
    umidade_padrao: Optional[float] = None
    impureza_padrao: Optional[float] = None
    preco_referencia: Optional[float] = None
    ativo: Optional[bool] = None
    dados_extras: Optional[dict[str, Any]] = None


class CommodityResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    tipo: str
    unidade: str
    fator_conversao_tonelada: float
    umidade_padrao: Optional[float]
    impureza_padrao: Optional[float]
    preco_referencia: Optional[float]
    ativo: bool
    dados_extras: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
