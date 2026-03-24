from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date, datetime

class PrevisaoProdutividadeCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID
    data_previsao: date
    produtividade_estimada_sc_ha: float = Field(..., gt=0)
    margem_erro_pct: float | None = None
    fatores_peso: dict | None = None
    historico_clima: dict | None = None
    indice_ndvi_medio: float | None = None
    modelo_ia_versao: str | None = None
    run_id: str | None = None

class PrevisaoProdutividadeResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    safra_id: UUID
    talhao_id: UUID
    data_previsao: date
    produtividade_estimada_sc_ha: float
    margem_erro_pct: float | None
    fatores_peso: dict | None
    historico_clima: dict | None
    indice_ndvi_medio: float | None
    modelo_ia_versao: str | None
    run_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
