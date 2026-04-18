from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from uuid import UUID


class CultivoAreaCreate(BaseModel):
    area_id: UUID
    area_ha: float = Field(gt=0, description="Área em hectares")


class CultivoAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cultivo_id: UUID
    area_id: UUID
    area_ha: float


class CultivoCreate(BaseModel):
    cultura: str
    cultivar_id: UUID | None = None
    cultivar_nome: str | None = None
    commodity_id: UUID | None = None
    sistema_plantio: str | None = None
    populacao_prevista: int | None = None
    espacamento_cm: int | None = None
    data_plantio_prevista: date | None = None
    produtividade_meta_sc_ha: float | None = None
    preco_venda_previsto: float | None = None
    consorciado: bool = False
    observacoes: str | None = None
    areas: list[CultivoAreaCreate] = Field(default_factory=list, description="Talhões e áreas associadas")


class CultivoUpdate(BaseModel):
    cultura: str | None = None
    cultivar_id: UUID | None = None
    cultivar_nome: str | None = None
    commodity_id: UUID | None = None
    sistema_plantio: str | None = None
    populacao_prevista: int | None = None
    populacao_real: int | None = None
    espacamento_cm: int | None = None
    data_plantio_prevista: date | None = None
    data_plantio_real: date | None = None
    data_colheita_prevista: date | None = None
    data_colheita_real: date | None = None
    produtividade_meta_sc_ha: float | None = None
    produtividade_real_sc_ha: float | None = None
    preco_venda_previsto: float | None = None
    custo_previsto_ha: float | None = None
    custo_realizado_ha: float | None = None
    consorciado: bool | None = None
    status: str | None = None
    observacoes: str | None = None


class CultivoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    safra_id: UUID
    cultura: str
    cultivar_id: UUID | None
    cultivar_nome: str | None
    commodity_id: UUID | None
    sistema_plantio: str | None
    populacao_prevista: int | None
    populacao_real: int | None
    espacamento_cm: int | None
    data_plantio_prevista: date | None
    data_plantio_real: date | None
    data_colheita_prevista: date | None
    data_colheita_real: date | None
    produtividade_meta_sc_ha: float | None
    produtividade_real_sc_ha: float | None
    preco_venda_previsto: float | None
    custo_previsto_ha: float | None
    custo_realizado_ha: float | None
    consorciado: bool
    status: str
    observacoes: str | None
    areas: list[CultivoAreaResponse] = Field(default_factory=list)
    created_at: str
    updated_at: str
