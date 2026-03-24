from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class CulturaCreate(BaseModel):
    nome: str
    nome_cientifico: str | None = None
    variedade: str | None = None
    ciclo_dias: int | None = None
    ativa: bool = True

class CulturaUpdate(BaseModel):
    nome: str | None = None
    nome_cientifico: str | None = None
    variedade: str | None = None
    ciclo_dias: int | None = None
    ativa: bool | None = None

class CulturaResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    nome: str
    nome_cientifico: str | None
    variedade: str | None
    ciclo_dias: int | None
    ativa: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
