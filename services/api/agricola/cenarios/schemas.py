from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CenarioUnidadeInput(BaseModel):
    production_unit_id: UUID
    produtividade_simulada: float | None = Field(None, gt=0)
    preco_simulado: float | None = Field(None, gt=0)
    custo_total_simulado_ha: float | None = Field(None, ge=0)
    depreciacao_ha: float | None = Field(None, ge=0, description="Depreciação de ativos em R$/ha")
    unidade_medida_id: UUID | None = None


class CenarioCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: str | None = None
    tipo: str = Field("CUSTOM", pattern="^(OTIMISTA|PESSIMISTA|CUSTOM)$")
    unidade_medida_id: UUID | None = None
    produtividade_default: float | None = Field(None, gt=0)
    preco_default: float | None = Field(None, gt=0)
    custo_ha_default: float | None = Field(None, ge=0)
    fator_custo_pct: float | None = Field(None, gt=0, le=2.0)
    ir_aliquota_pct: float | None = Field(None, ge=0, le=100, description="Alíquota IR % (ex: 15.0 para Lucro Presumido)")
    unidades: list[CenarioUnidadeInput] = Field(default_factory=list)


class CenarioUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=100)
    descricao: str | None = None
    tipo: str | None = Field(None, pattern="^(OTIMISTA|PESSIMISTA|CUSTOM)$")
    status: str | None = Field(None, pattern="^(ATIVO|ARQUIVADO)$")
    unidade_medida_id: UUID | None = None
    produtividade_default: float | None = Field(None, gt=0)
    preco_default: float | None = Field(None, gt=0)
    custo_ha_default: float | None = Field(None, ge=0)
    fator_custo_pct: float | None = Field(None, gt=0, le=2.0)
    ir_aliquota_pct: float | None = Field(None, ge=0, le=100)
    unidades: list[CenarioUnidadeInput] | None = None


class DuplicarCenarioRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)


class CenarioUnidadeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    production_unit_id: UUID
    unidade_medida_id: UUID | None
    cultivo_nome: str | None
    area_nome: str | None
    area_ha: float
    percentual_participacao: float
    produtividade_simulada: float | None
    preco_simulado: float | None
    custo_total_simulado_ha: float | None
    custo_base_fonte: str | None
    produtividade_efetiva: float | None
    preco_efetivo: float | None
    custo_ha_efetivo: float | None
    producao_total: float | None
    receita_bruta: float | None
    custo_total: float | None
    margem_contribuicao: float | None
    margem_pct: float | None
    depreciacao_ha: float | None
    depreciacao_total: float | None
    ir_valor: float | None
    resultado_liquido: float | None
    ponto_equilibrio: float | None


class CenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    safra_id: UUID
    nome: str
    descricao: str | None
    tipo: str
    eh_base: bool
    status: str
    unidade_medida_id: UUID | None
    produtividade_default: float | None
    preco_default: float | None
    custo_ha_default: float | None
    fator_custo_pct: float | None
    area_total_ha: float | None
    receita_bruta_total: float | None
    custo_total: float | None
    margem_contribuicao_total: float | None
    depreciacao_total: float | None
    ir_aliquota_pct: float | None
    ir_valor_total: float | None
    resultado_liquido_total: float | None
    ponto_equilibrio_sc_ha: float | None
    calculado_em: datetime | None
    created_at: datetime
    updated_at: datetime
    unidades: list[CenarioUnidadeResponse] = []


class CenarioListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    safra_id: UUID
    nome: str
    tipo: str
    eh_base: bool
    status: str
    area_total_ha: float | None
    receita_bruta_total: float | None
    custo_total: float | None
    margem_contribuicao_total: float | None
    depreciacao_total: float | None
    ir_aliquota_pct: float | None
    ir_valor_total: float | None
    resultado_liquido_total: float | None
    ponto_equilibrio_sc_ha: float | None
    calculado_em: datetime | None


class ComparativoUnidadeItem(BaseModel):
    production_unit_id: UUID
    cultivo_nome: str | None
    area_nome: str | None
    area_ha: float


class ComparativoCenarioColuna(BaseModel):
    cenario_id: UUID
    nome: str
    tipo: str
    eh_base: bool
    area_total_ha: float | None
    receita_bruta_total: float | None
    custo_total: float | None
    margem_contribuicao_total: float | None
    depreciacao_total: float | None
    ir_aliquota_pct: float | None
    ir_valor_total: float | None
    resultado_liquido_total: float | None
    ponto_equilibrio_sc_ha: float | None
    unidades: list[CenarioUnidadeResponse]


class ComparativoResponse(BaseModel):
    cenarios: list[ComparativoCenarioColuna]
