from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class PiqueteCreate(BaseModel):
    fazenda_id: uuid.UUID
    nome: str = Field(..., min_length=2, max_length=100)
    area_ha: float = Field(..., gt=0, description="Área do piquete em hectares")
    capacidade_suporte_ua: Optional[float] = Field(None, ge=0, description="Unidades Animais suportadas")


class PiqueteResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    fazenda_id: uuid.UUID
    nome: str
    area_ha: float
    capacidade_suporte_ua: Optional[float]
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
