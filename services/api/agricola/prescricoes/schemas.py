from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime, date

class CamadaPrescricao(BaseModel):
    geometry: dict # GeoJSON
    rate: float
    unit: str = "KG/HA"

class PrescricaoVRABase(BaseModel):
    nome: str
    talhao_id: UUID
    safra_id: UUID
    tipo_operacao: str
    insumo: str
    camadas_json: List[dict] = []
    area_total_ha: Optional[float] = None
    quantidade_total_estimada: Optional[float] = None
    data_prescricao: Optional[date] = None
    arquivo_original_url: Optional[str] = None
    observacoes: Optional[str] = None

class PrescricaoVRACreate(PrescricaoVRABase):
    pass

class PrescricaoVRAResponse(PrescricaoVRABase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
