from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime
import uuid


class FazendaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    grupo_id: uuid.UUID
    nome: str
    cpf_cnpj: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    codigo_car: Optional[str] = None
    nirf: Optional[str] = None
    uf: Optional[str] = None
    municipio: Optional[str] = None
    area_total_ha: Optional[Decimal] = None
    area_aproveitavel_ha: Optional[Decimal] = None
    area_app_ha: Optional[Decimal] = None
    area_rl_ha: Optional[Decimal] = None
    coordenadas_sede: Optional[str] = None
    geometria: Optional[dict] = None
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
