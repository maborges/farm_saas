from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime
import uuid


class AbastecimentoCreate(BaseModel):
    equipamento_id: uuid.UUID
    data: datetime
    operador_id: Optional[uuid.UUID] = None

    horimetro_na_data: float
    km_na_data: Optional[float] = None

    tipo_combustivel: str = "DIESEL"
    litros: float
    preco_litro: float = 0.0
    tanque_cheio: bool = True

    local: str = "INTERNO"
    fornecedor_id: Optional[uuid.UUID] = None
    nota_fiscal: Optional[str] = None
    observacoes: Optional[str] = None

    @model_validator(mode="after")
    def calc_custo(self):
        # custo_total calculado automaticamente se não enviado
        return self


class AbastecimentoUpdate(BaseModel):
    data: Optional[datetime] = None
    horimetro_na_data: Optional[float] = None
    km_na_data: Optional[float] = None
    tipo_combustivel: Optional[str] = None
    litros: Optional[float] = None
    preco_litro: Optional[float] = None
    tanque_cheio: Optional[bool] = None
    local: Optional[str] = None
    fornecedor_id: Optional[uuid.UUID] = None
    nota_fiscal: Optional[str] = None
    observacoes: Optional[str] = None


class AbastecimentoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    equipamento_id: uuid.UUID
    operador_id: Optional[uuid.UUID]
    data: datetime
    horimetro_na_data: float
    km_na_data: Optional[float]
    tipo_combustivel: str
    litros: float
    preco_litro: float
    custo_total: float
    tanque_cheio: bool
    local: str
    fornecedor_id: Optional[uuid.UUID]
    nota_fiscal: Optional[str]
    observacoes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
