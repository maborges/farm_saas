from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date, time, datetime
from typing import Optional, List

class InsumoOperacaoCreate(BaseModel):
    insumo_id: UUID
    lote_insumo: str | None = None
    dose_por_ha: float = Field(..., gt=0)
    unidade: str = Field(..., min_length=1, max_length=20)
    area_aplicada: float | None = None

class InsumoOperacaoResponse(BaseModel):
    id: UUID
    insumo_id: UUID
    lote_insumo: str | None
    dose_por_ha: float
    unidade: str
    area_aplicada: float | None
    quantidade_total: float | None
    custo_unitario: float | None
    custo_total: float | None
    carencia_dias: int | None
    data_reentrada: date | None
    epi_necessario: list[str] | None

    model_config = ConfigDict(from_attributes=True)

class OperacaoAgricolaCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID
    production_unit_id: UUID | None = None
    tarefa_id: UUID | None = None
    tipo: str
    subtipo: str | None = None
    descricao: str = Field(..., min_length=3, max_length=500)
    fase_safra: str | None = None  # None = auto-preenche com fase atual da safra
    data_prevista: date | None = None
    data_realizada: date
    hora_inicio: time | None = None
    hora_fim: time | None = None
    area_aplicada_ha: float | None = Field(None, gt=0)
    maquina_id: UUID | None = None
    implemento: str | None = None
    operador_id: UUID | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    observacoes: str | None = None
    insumos: list[InsumoOperacaoCreate] = []

class OperacaoAgricolaUpdate(BaseModel):
    tipo: str | None = None
    subtipo: str | None = None
    descricao: str | None = Field(None, min_length=3, max_length=500)
    fase_safra: str | None = None
    data_prevista: date | None = None
    data_realizada: date | None = None
    hora_inicio: time | None = None
    hora_fim: time | None = None
    area_aplicada_ha: float | None = Field(None, gt=0)
    maquina_id: UUID | None = None
    implemento: str | None = None
    operador_id: UUID | None = None
    production_unit_id: UUID | None = None
    status: str | None = None
    observacoes: str | None = None


class OperacaoPorFaseKPI(BaseModel):
    fase: str
    total_operacoes: int
    custo_total: float
    custo_por_ha: float
    area_total_ha: float


class SafraOperacoesPorFaseResponse(BaseModel):
    safra_id: UUID
    fases: list[OperacaoPorFaseKPI]
    custo_total_safra: float

class OperacaoAgricolaResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    safra_id: UUID
    talhao_id: UUID
    production_unit_id: UUID | None = None
    tarefa_id: UUID | None = None
    tipo: str
    subtipo: str | None
    descricao: str
    data_prevista: date | None
    data_realizada: date
    hora_inicio: time | None
    hora_fim: time | None
    area_aplicada_ha: float | None
    maquina_id: UUID | None
    implemento: str | None
    operador_id: UUID | None
    temperatura_c: float | None
    umidade_rel: float | None
    vento_kmh: float | None
    direcao_vento: str | None
    condicao_clima: str | None
    latitude: float | None
    longitude: float | None
    fase_safra: str | None
    custo_total: float
    custo_por_ha: float
    status: str
    observacoes: str | None
    fotos: list[str]
    created_at: datetime
    updated_at: datetime
    insumos: list[InsumoOperacaoResponse]

    model_config = ConfigDict(from_attributes=True)
