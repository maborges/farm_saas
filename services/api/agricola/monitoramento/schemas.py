from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List, Dict, Any

class MonitoramentoPragasCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID
    data_avaliacao: date
    tipo: str | None = None
    nome_cientifico: str | None = None
    nome_popular: str | None = None
    nivel_infestacao: float | None = None
    unidade_medida: str | None = None
    nde_cultura: float | None = None
    atingiu_nde: bool = False
    fotos: list[str] = []
    pontos_coleta: list[dict] = []
    diagnostico_ia: dict | None = None
    tecnico_id: UUID | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    observacoes: str | None = None

class MonitoramentoPragasUpdate(BaseModel):
    data_avaliacao: date | None = None
    tipo: str | None = None
    nome_cientifico: str | None = None
    nome_popular: str | None = None
    nivel_infestacao: float | None = None
    unidade_medida: str | None = None
    nde_cultura: float | None = None
    atingiu_nde: bool | None = None
    fotos: list[str] | None = None
    pontos_coleta: list[dict] | None = None
    diagnostico_ia: dict | None = None
    tecnico_id: UUID | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    observacoes: str | None = None

class MonitoramentoPragasResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    safra_id: UUID
    talhao_id: UUID
    data_avaliacao: date
    tipo: str | None
    nome_cientifico: str | None
    nome_popular: str | None
    nivel_infestacao: float | None
    unidade_medida: str | None
    nde_cultura: float | None
    atingiu_nde: bool
    fotos: list[str]
    pontos_coleta: list[dict] | None
    diagnostico_ia: dict | None
    tecnico_id: UUID | None
    latitude: float | None
    longitude: float | None
    observacoes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
