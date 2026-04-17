from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime

class ClimaResponse(BaseModel):
    id: UUID
    unidade_produtiva_id: UUID
    data_registro: date
    precipitacao_mm: float | None
    temp_max_c: float | None
    temp_min_c: float | None
    temp_media_c: float | None
    umidade_rel_pct: float | None
    evapotranspiracao_mm: float | None
    gdu_calculado: float | None
    fonte: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
