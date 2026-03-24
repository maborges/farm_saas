from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class FazendaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    cnpj: Optional[str]
    inscricao_estadual: Optional[str]
    area_total_ha: Optional[float]
    coordenadas_sede: Optional[str]
    geometria: Optional[dict] = None
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
