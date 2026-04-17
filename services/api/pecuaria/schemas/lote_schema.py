from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
import uuid

class LoteBovinoCreate(BaseModel):
    unidade_produtiva_id: uuid.UUID
    piquete_id: Optional[uuid.UUID] = None
    identificacao: str = Field(..., min_length=2, max_length=100, description="Nome ou Número do Lote")
    categoria: str = Field(..., max_length=50, description="Ex: Bezerros, Vacas Paridas")
    raca: str = Field(..., max_length=50)
    quantidade_cabecas: int = Field(..., ge=1, description="O lote precisa ter pelo menos um animal na fundação")
    peso_medio_kg: float = Field(0.0, ge=0)
    data_formacao: Optional[date] = None

class LoteBovinoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    unidade_produtiva_id: uuid.UUID
    piquete_id: Optional[uuid.UUID] = Field(None, validation_alias="area_id")
    identificacao: str
    categoria: str
    raca: str
    quantidade_cabecas: int
    peso_medio_kg: float
    data_formacao: date
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
