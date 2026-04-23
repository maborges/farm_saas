from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date
from typing import Optional


class TarefaCreate(BaseModel):
    talhao_id: Optional[UUID] = None
    cultivo_area_id: Optional[UUID] = None
    analise_solo_id: Optional[UUID] = None
    origem: str = "MANUAL"
    tipo: str = Field(..., description="CALAGEM|ADUBACAO_FOSFORO|ADUBACAO_POTASSIO|ADUBACAO_NITROGENIO|GRADAGEM|PLANTIO|PULVERIZACAO|IRRIGACAO|COLHEITA|OUTRO")
    fase: Optional[str] = Field(None, description="Fase da safra")
    criticidade: str = Field("NORMAL", description="CRITICA|NORMAL|OPCIONAL")
    descricao: str = Field(..., min_length=3, max_length=300)
    obs: Optional[str] = None
    prioridade: str = "MEDIA"
    dose_estimada_kg_ha: Optional[float] = None
    quantidade_total_estimada_kg: Optional[float] = None
    area_ha: Optional[float] = None
    custo_estimado: Optional[float] = None
    data_prevista: Optional[date] = None


class TarefaUpdate(BaseModel):
    fase: Optional[str] = None
    criticidade: Optional[str] = None
    descricao: Optional[str] = Field(None, min_length=3, max_length=300)
    obs: Optional[str] = None
    prioridade: Optional[str] = None
    talhao_id: Optional[UUID] = None
    tipo: Optional[str] = None
    custo_estimado: Optional[float] = None
    data_prevista: Optional[date] = None


class TarefaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    safra_id: UUID
    talhao_id: Optional[UUID]
    cultivo_area_id: Optional[UUID]
    analise_solo_id: Optional[UUID]
    origem: str
    tipo: str
    fase: Optional[str]
    criticidade: str
    descricao: str
    obs: Optional[str]
    prioridade: str
    status: str
    dose_estimada_kg_ha: Optional[float]
    quantidade_total_estimada_kg: Optional[float]
    area_ha: Optional[float]
    custo_estimado: Optional[float]
    data_prevista: Optional[date]
    aprovado_por: Optional[UUID]
    aprovado_em: Optional[datetime]
    operacao_id: Optional[UUID]
    concluida_em: Optional[datetime]
    cancelado_por: Optional[UUID]
    cancelado_em: Optional[datetime]
    motivo_cancelamento: Optional[str]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
