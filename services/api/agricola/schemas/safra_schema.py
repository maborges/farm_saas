from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
import uuid

class SafraCreate(BaseModel):
    unidade_produtiva_id: uuid.UUID = Field(..., description="A qual fazenda esta safra pertence fisicamente.")
    nome: str = Field(..., min_length=3, max_length=150, description="Nome identificador. Ex: Soja 24/25")
    cultura: str = Field(..., min_length=2, max_length=100, description="Grão ou cultivar. Ex: Soja")
    data_inicio: date = Field(..., description="Data de planejamento do plantio (Kick-off).")
    data_fim: date = Field(..., description="Data limite para colheita.")
    produtividade_esperada_sc_ha: Optional[float] = Field(None, gt=0, description="Orçamento de expectativa de Sacas por Hectare.")
    ativa: bool = True

class SafraUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=150)
    cultura: Optional[str] = Field(None, min_length=2, max_length=100)
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    produtividade_esperada_sc_ha: Optional[float] = Field(None, gt=0)
    ativa: Optional[bool] = None

class SafraResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    unidade_produtiva_id: uuid.UUID
    nome: str
    cultura: str
    data_inicio: date
    data_fim: date
    produtividade_esperada_sc_ha: Optional[float]
    ativa: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
