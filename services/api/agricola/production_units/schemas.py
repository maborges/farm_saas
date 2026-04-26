from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductionUnitCreate(BaseModel):
    cultivo_id: uuid.UUID
    area_id: uuid.UUID
    cultivo_area_id: uuid.UUID | None = None
    percentual_participacao: Decimal = Field(default=Decimal("100"), ge=0, le=100)
    area_ha: Decimal = Field(..., gt=0)
    data_inicio: date | None = None
    data_fim: date | None = None


class ProductionUnitUpdate(BaseModel):
    percentual_participacao: Decimal | None = Field(default=None, ge=0, le=100)
    area_ha: Decimal | None = Field(default=None, gt=0)
    data_inicio: date | None = None
    data_fim: date | None = None
    status: str | None = None


class ProductionUnitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    safra_id: uuid.UUID
    cultivo_id: uuid.UUID
    area_id: uuid.UUID
    cultivo_area_id: uuid.UUID | None
    percentual_participacao: Decimal
    area_ha: Decimal
    status: str
    data_inicio: date | None
    data_fim: date | None
    created_at: datetime
    updated_at: datetime

    # Enriquecidos pelo service
    cultivo_nome: str | None = None
    area_nome: str | None = None


class StatusConsorcioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    area_id: uuid.UUID
    area_nome: str | None = None
    soma_participacao: Decimal
    qtd_unidades: int
    status: str
    calculado_em: datetime
