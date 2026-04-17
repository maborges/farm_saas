from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, date
import uuid


class EquipamentoCreate(BaseModel):
    nome: str
    tipo: str = "OUTRO"
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano_fabricacao: Optional[int] = None
    ano_modelo: Optional[int] = None
    placa: Optional[str] = None
    chassi: Optional[str] = None
    numero_serie: Optional[str] = None
    patrimonio: Optional[str] = None
    combustivel: str = "DIESEL"
    potencia_cv: Optional[float] = None
    capacidade_tanque_l: Optional[float] = None
    status: str = "ATIVO"
    horimetro_atual: float = 0.0
    km_atual: float = 0.0
    unidade_produtiva_id: Optional[uuid.UUID] = None
    valor_aquisicao: Optional[float] = None
    data_aquisicao: Optional[date] = None
    observacoes: Optional[str] = None
    dados_extras: Optional[dict[str, Any]] = None


class EquipamentoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano_fabricacao: Optional[int] = None
    ano_modelo: Optional[int] = None
    placa: Optional[str] = None
    chassi: Optional[str] = None
    numero_serie: Optional[str] = None
    patrimonio: Optional[str] = None
    combustivel: Optional[str] = None
    potencia_cv: Optional[float] = None
    capacidade_tanque_l: Optional[float] = None
    status: Optional[str] = None
    horimetro_atual: Optional[float] = None
    km_atual: Optional[float] = None
    unidade_produtiva_id: Optional[uuid.UUID] = None
    valor_aquisicao: Optional[float] = None
    data_aquisicao: Optional[date] = None
    observacoes: Optional[str] = None
    dados_extras: Optional[dict[str, Any]] = None


class EquipamentoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    unidade_produtiva_id: Optional[uuid.UUID]
    nome: str
    tipo: str
    marca: Optional[str]
    modelo: Optional[str]
    ano_fabricacao: Optional[int]
    ano_modelo: Optional[int]
    placa: Optional[str]
    chassi: Optional[str]
    numero_serie: Optional[str]
    patrimonio: Optional[str]
    combustivel: str
    potencia_cv: Optional[float]
    capacidade_tanque_l: Optional[float]
    status: str
    horimetro_atual: float
    km_atual: float
    valor_aquisicao: Optional[float]
    data_aquisicao: Optional[date]
    observacoes: Optional[str]
    dados_extras: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
