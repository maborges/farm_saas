from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Any
import json
from uuid import UUID
from datetime import datetime

class TalhaoCreate(BaseModel):
    fazenda_id: UUID
    nome: str = Field(..., min_length=1, max_length=100)
    codigo: str | None = Field(None, max_length=20)
    geometria_geojson: dict | None = None             # GeoJSON Polygon do frontend (MapLibre)
    area_ha_manual: float | None = Field(None, gt=0, le=100000)
    tipo_solo: str | None = None
    classe_solo: str | None = None
    textura_solo: str | None = None
    relevo: str | None = None
    irrigado: bool = False
    sistema_irrigacao: str | None = None

    @model_validator(mode="after")
    def validar_area(self):
        if not self.geometria_geojson and not self.area_ha_manual:
            raise ValueError("É necessário informar geometria ou área manual do talhão")
        return self

class TalhaoUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=100)
    codigo: str | None = Field(None, max_length=20)
    geometria_geojson: dict | None = None
    area_ha_manual: float | None = Field(None, gt=0, le=100000)
    tipo_solo: str | None = None
    classe_solo: str | None = None
    textura_solo: str | None = None
    relevo: str | None = None
    irrigado: bool | None = None
    sistema_irrigacao: str | None = None

class TalhaoResponse(BaseModel):
    id: UUID
    fazenda_id: UUID
    nome: str
    codigo: str | None
    area_ha: float | None
    area_ha_manual: float | None
    area_efetiva_ha: float | None                     # computed property do model
    tipo_solo: str | None
    classe_solo: str | None
    textura_solo: str | None
    relevo: str | None
    irrigado: bool
    sistema_irrigacao: str | None
    ativo: bool
    geometria_geojson: dict | None = None             # serializado pelo service
    centroide_lat: float | None = None
    centroide_lng: float | None = None
    historico_culturas: list[dict]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
