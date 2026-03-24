from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime

class NDVICreate(BaseModel):
    talhao_id: UUID
    data_captura: date
    cobertura_nuvens_pct: float | None = None
    indice_medio: float | None = None
    indice_minimo: float | None = None
    indice_maximo: float | None = None
    url_imagem_colorida: str | None = None
    url_raw_data: str | None = None
    satelite: str = 'Sentinel-2'

class NDVIResponse(BaseModel):
    id: UUID
    talhao_id: UUID
    data_captura: date
    cobertura_nuvens_pct: float | None
    indice_medio: float | None
    indice_minimo: float | None
    indice_maximo: float | None
    url_imagem_colorida: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
