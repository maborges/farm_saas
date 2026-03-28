from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional

class RomaneioColheitaCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID
    numero_romaneio: str | None = None
    data_colheita: date
    turno: str | None = None
    maquina_colhedora_id: UUID | None = None
    operador_id: UUID | None = None
    
    peso_bruto_kg: float = Field(..., gt=0)
    tara_kg: float | None = Field(0, ge=0)
    
    umidade_pct: float | None = Field(None, ge=0, le=100)
    impureza_pct: float | None = Field(None, ge=0, le=100)
    avariados_pct: float | None = Field(None, ge=0, le=100)
    
    destino: str | None = None
    armazem_id: UUID | None = None
    preco_saca: float | None = None
    observacoes: str | None = None

class RomaneioColheitaUpdate(BaseModel):
    data_colheita: date | None = None
    turno: str | None = None
    maquina_colhedora_id: UUID | None = None
    operador_id: UUID | None = None
    peso_bruto_kg: float | None = Field(None, gt=0)
    tara_kg: float | None = Field(None, ge=0)
    umidade_pct: float | None = Field(None, ge=0, le=100)
    impureza_pct: float | None = Field(None, ge=0, le=100)
    avariados_pct: float | None = Field(None, ge=0, le=100)
    destino: str | None = None
    preco_saca: float | None = None
    observacoes: str | None = None


class RomaneioKPIs(BaseModel):
    total_romaneios: int
    total_sacas: float
    receita_total: float
    produtividade_sc_ha: float | None


class RomaneioColheitaResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    safra_id: UUID
    talhao_id: UUID
    numero_romaneio: str | None
    data_colheita: date
    turno: str | None
    peso_bruto_kg: float
    tara_kg: float | None
    peso_liquido_kg: float | None
    umidade_pct: float | None
    impureza_pct: float | None
    avariados_pct: float | None
    desconto_umidade_kg: float | None
    desconto_impureza_kg: float | None
    peso_liquido_padrao_kg: float | None
    sacas_60kg: float | None
    produtividade_sc_ha: float | None = None
    destino: str | None
    preco_saca: float | None
    receita_total: float | None
    observacoes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
