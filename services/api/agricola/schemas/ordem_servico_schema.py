from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
import uuid

class OrdemServicoCreate(BaseModel):
    fazenda_id: uuid.UUID = Field(..., description="ID da Fazenda onde ocorre a OS.")
    safra_id: uuid.UUID = Field(..., description="A qual Safra (orçamento) esse custo e esforço pertence.")
    tipo_atividade: str = Field(..., min_length=2, max_length=50, description="Ex: Plantio, Colheita, Pulverização")
    status: str = Field("PLANEJADA", description="Estado da OS (PLANEJADA, EM_ANDAMENTO, CONCLUIDA, CANCELADA)")
    data_prevista: Optional[date] = Field(None, description="Quando se espera iniciar o trato cultural")
    observacoes_campo: Optional[str] = Field(None, description="Relatos importantes ou receita do agrônomo")

class OrdemServicoUpdate(BaseModel):
    tipo_atividade: Optional[str] = Field(None, min_length=2, max_length=50)
    status: Optional[str] = None
    data_prevista: Optional[date] = None
    data_execucao: Optional[date] = Field(None, description="Data da real entrega do serviço pelo Tratorista")
    observacoes_campo: Optional[str] = None
    ativo: Optional[bool] = None

class OrdemServicoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    fazenda_id: uuid.UUID
    safra_id: uuid.UUID
    tipo_atividade: str
    status: str
    data_prevista: Optional[date]
    data_execucao: Optional[date]
    observacoes_campo: Optional[str]
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
