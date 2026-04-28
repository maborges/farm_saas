from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
import uuid

TIPO_EVENTO_VALID = {
    "NASCIMENTO", "MORTE", "PESAGEM", "VACINACAO",
    "TRANSFERENCIA", "MEDICACAO", "VENDA", "ABATE",
}


class ManejoLoteCreate(BaseModel):
    lote_id: uuid.UUID
    tipo_evento: str = Field(
        ...,
        description="NASCIMENTO | MORTE | PESAGEM | VACINACAO | TRANSFERENCIA | MEDICACAO | VENDA | ABATE",
    )
    data_evento: Optional[date] = None
    quantidade_cabecas: Optional[int] = Field(None, ge=0)
    peso_total_kg: Optional[float] = Field(None, ge=0)
    produto_id: Optional[uuid.UUID] = Field(None, description="Produto/insumo utilizado (VACINACAO, MEDICACAO)")
    custo_total: Optional[float] = Field(None, ge=0, description="Custo do evento (VACINACAO/MEDICACAO)")
    valor_venda: Optional[float] = Field(None, ge=0, description="Receita do evento (VENDA/ABATE)")
    observacoes: Optional[str] = Field(None, max_length=1000)


class ManejoLoteResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    lote_id: uuid.UUID
    tipo_evento: str
    data_evento: date
    quantidade_cabecas: Optional[int]
    peso_total_kg: Optional[float]
    produto_id: Optional[uuid.UUID] = None
    custo_total: Optional[float]
    valor_venda: Optional[float]
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
