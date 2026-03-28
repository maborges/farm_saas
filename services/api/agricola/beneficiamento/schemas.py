from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class LoteBeneficiamentoCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID | None = None
    numero_lote: str
    metodo: str = Field(..., pattern="^(NATURAL|LAVADO|HONEY|DESCASCADO)$")
    data_entrada: date
    peso_entrada_kg: float = Field(..., gt=0)
    umidade_entrada_pct: float | None = Field(None, ge=0, le=100)
    local_secagem: str | None = None
    observacoes: str | None = None


class LoteBeneficiamentoUpdate(BaseModel):
    status: str | None = None
    local_secagem: str | None = None
    data_inicio_secagem: date | None = None
    data_fim_secagem: date | None = None
    data_saida: date | None = None
    peso_saida_kg: float | None = Field(None, gt=0)
    umidade_saida_pct: float | None = Field(None, ge=0, le=100)
    peneira_principal: str | None = None
    bebida: str | None = None
    pontuacao_scaa: float | None = Field(None, ge=0, le=100)
    defeitos_intrinsecos: int | None = None
    defeitos_extrinsecos: int | None = None
    armazem_id: UUID | None = None
    saca_inicio: int | None = None
    saca_fim: int | None = None
    observacoes: str | None = None


class LoteBeneficiamentoResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    safra_id: UUID
    talhao_id: UUID | None
    numero_lote: str
    metodo: str
    status: str
    data_entrada: date
    peso_entrada_kg: float
    umidade_entrada_pct: float | None
    local_secagem: str | None
    data_inicio_secagem: date | None
    data_fim_secagem: date | None
    dias_secagem: int | None
    data_saida: date | None
    peso_saida_kg: float | None
    umidade_saida_pct: float | None
    fator_reducao: float | None
    sacas_beneficiadas: float | None
    perda_pct: float | None
    peneira_principal: str | None
    bebida: str | None
    pontuacao_scaa: float | None
    defeitos_intrinsecos: int | None
    defeitos_extrinsecos: int | None
    armazem_id: UUID | None
    saca_inicio: int | None
    saca_fim: int | None
    observacoes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BeneficiamentoKPIs(BaseModel):
    total_lotes: int
    peso_entrada_total_kg: float
    peso_saida_total_kg: float
    sacas_beneficiadas_total: float
    fator_reducao_medio: float | None
    lotes_em_processo: int
    lotes_concluidos: int
    pontuacao_media_scaa: float | None
