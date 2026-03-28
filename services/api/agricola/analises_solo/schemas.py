from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime

class AnaliseSoloCreate(BaseModel):
    talhao_id: UUID
    data_coleta: date
    laboratorio: str | None = None
    codigo_amostra: str | None = None
    profundidade_cm: int | None = None
    argila_pct: float | None = None
    silte_pct: float | None = None
    areia_pct: float | None = None
    ph_agua: float | None = None
    ph_cacl2: float | None = None
    materia_organica_pct: float | None = None
    fosforo_p: float | None = None
    potassio_k: float | None = None
    calcio_ca: float | None = None
    magnesio_mg: float | None = None
    aluminio_al: float | None = None
    hidrogenio_al_hal: float | None = None
    ctc: float | None = None
    v_pct: float | None = None
    arquivo_laudo_url: str | None = None

class AnaliseSoloUpdate(BaseModel):
    laboratorio: str | None = None
    codigo_amostra: str | None = None
    profundidade_cm: int | None = None
    argila_pct: float | None = None
    silte_pct: float | None = None
    areia_pct: float | None = None
    ph_agua: float | None = None
    ph_cacl2: float | None = None
    materia_organica_pct: float | None = None
    fosforo_p: float | None = None
    potassio_k: float | None = None
    calcio_ca: float | None = None
    magnesio_mg: float | None = None
    aluminio_al: float | None = None
    hidrogenio_al_hal: float | None = None
    ctc: float | None = None
    v_pct: float | None = None
    arquivo_laudo_url: str | None = None


class AnaliseSoloResponse(AnaliseSoloCreate):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
