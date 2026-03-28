from pydantic import BaseModel, Field, model_validator, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional

class SafraCreate(BaseModel):
    talhao_id: UUID
    ano_safra: str = Field(..., pattern=r"^\d{4}(/\d{2,4})?$")
    cultura: str
    cultivar_id: UUID | None = None
    cultivar_nome: str | None = None
    commodity_id: UUID | None = None
    sistema_plantio: str | None = None
    data_plantio_prevista: date | None = None
    populacao_prevista: int | None = Field(None, gt=0, le=500000)
    espacamento_cm: int | None = Field(None, gt=0, le=200)
    area_plantada_ha: float | None = Field(None, gt=0)
    produtividade_meta_sc_ha: float | None = Field(None, gt=0)
    preco_venda_previsto: float | None = Field(None, gt=0)
    observacoes: str | None = None

    @model_validator(mode="after")
    def validar_cultivar(self):
        if not self.cultivar_id and not self.cultivar_nome:
            raise ValueError("Informe cultivar_id ou cultivar_nome")
        return self

class SafraUpdate(BaseModel):
    ano_safra: str | None = Field(None, pattern=r"^\d{4}(/\d{2,4})?$")
    cultura: str | None = None
    cultivar_id: UUID | None = None
    cultivar_nome: str | None = None
    commodity_id: UUID | None = None
    sistema_plantio: str | None = None
    data_plantio_prevista: date | None = None
    data_plantio_real: date | None = None
    data_colheita_prevista: date | None = None
    data_colheita_real: date | None = None
    populacao_prevista: int | None = Field(None, gt=0, le=500000)
    populacao_real: int | None = Field(None, gt=0, le=500000)
    espacamento_cm: int | None = Field(None, gt=0, le=200)
    area_plantada_ha: float | None = Field(None, gt=0)
    produtividade_meta_sc_ha: float | None = Field(None, gt=0)
    produtividade_real_sc_ha: float | None = Field(None, gt=0)
    preco_venda_previsto: float | None = Field(None, gt=0)
    custo_previsto_ha: float | None = Field(None, gt=0)
    custo_realizado_ha: float | None = Field(None, gt=0)
    status: str | None = None
    observacoes: str | None = None

class SafraAvancarFase(BaseModel):
    observacao: str | None = None
    dados_fase: dict | None = None


class SafraFaseHistoricoResponse(BaseModel):
    id: UUID
    safra_id: UUID
    fase_anterior: str | None
    fase_nova: str
    usuario_id: UUID | None
    observacao: str | None
    dados_fase: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SafraResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    talhao_id: UUID
    ano_safra: str
    cultura: str
    cultivar_id: UUID | None
    cultivar_nome: str | None
    commodity_id: UUID | None
    sistema_plantio: str | None
    data_plantio_prevista: date | None
    data_plantio_real: date | None
    data_colheita_prevista: date | None
    data_colheita_real: date | None
    populacao_prevista: int | None
    populacao_real: int | None
    espacamento_cm: int | None
    area_plantada_ha: float | None
    produtividade_meta_sc_ha: float | None
    produtividade_real_sc_ha: float | None
    preco_venda_previsto: float | None
    custo_previsto_ha: float | None
    custo_realizado_ha: float | None
    status: str
    observacoes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SafraTalhaoResponse(BaseModel):
    id: UUID
    safra_id: UUID
    area_id: UUID
    principal: bool
    area_ha: float | None

    model_config = ConfigDict(from_attributes=True)


class SafraTalhoesSincronizar(BaseModel):
    talhao_ids: list[UUID]
    areas_ha: dict[str, float] | None = None  # area_id (str) → ha
