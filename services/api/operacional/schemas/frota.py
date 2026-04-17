from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal

TipoOS = Literal["PREVENTIVA", "CORRETIVA", "REVISAO"]
StatusOS = Literal["ABERTA", "EM_EXECUCAO", "CONCLUIDA", "CANCELADA"]

TipoMaquinario = Literal[
    "TRATOR", "COLHEITADEIRA", "VEICULO_LEVE", "VEICULO_PESADO",
    "IMPLEMENTO", "PULVERIZADOR", "OUTROS"
]
TipoCombustivel = Literal["DIESEL", "GASOLINA", "ETANOL", "FLEX", "ELETRICO", "NAO_APLICAVEL"]
StatusMaquinario = Literal["ATIVO", "MANUTENCAO", "INATIVO"]

class MaquinarioBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    tipo: TipoMaquinario
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=50)
    ano: Optional[int] = Field(None, ge=1900, le=2100)
    placa_chassi: Optional[str] = Field(None, max_length=50)
    numero_serie: Optional[str] = Field(None, max_length=80)
    patrimonio: Optional[str] = Field(None, max_length=50)
    combustivel: TipoCombustivel = "DIESEL"
    potencia_cv: Optional[float] = Field(None, ge=0)
    capacidade_tanque_l: Optional[float] = Field(None, ge=0)
    horimetro_atual: float = 0.0
    km_atual: float = 0.0
    status: StatusMaquinario = "ATIVO"
    unidade_produtiva_id: UUID

class MaquinarioCreate(MaquinarioBase):
    pass

class MaquinarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    tipo: Optional[TipoMaquinario] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = None
    numero_serie: Optional[str] = None
    patrimonio: Optional[str] = None
    combustivel: Optional[TipoCombustivel] = None
    potencia_cv: Optional[float] = None
    capacidade_tanque_l: Optional[float] = None
    status: Optional[StatusMaquinario] = None
    horimetro_atual: Optional[float] = None
    km_atual: Optional[float] = None

class MaquinarioResponse(MaquinarioBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    planos: Optional[list["PlanoManutencaoResponse"]] = []

    model_config = ConfigDict(from_attributes=True)

class PlanoManutencaoBase(BaseModel):
    maquinario_id: UUID
    descricao: str
    frequencia_horas: Optional[float] = None
    frequencia_km: Optional[float] = None

class PlanoManutencaoCreate(PlanoManutencaoBase):
    pass

class PlanoManutencaoResponse(PlanoManutencaoBase):
    id: UUID
    ultimo_registro_horas: Optional[float] = None
    ultimo_registro_km: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class OrdemServicoBase(BaseModel):
    maquinario_id: UUID
    tipo: TipoOS
    descricao_problema: str
    horimetro_na_abertura: float
    km_na_abertura: Optional[float] = None
    tecnico_responsavel: Optional[str] = None

class OrdemServicoCreate(OrdemServicoBase):
    pass

class OrdemServicoUpdate(BaseModel):
    diagnostico_tecnico: Optional[str] = None
    custo_mao_obra: Optional[float] = Field(None, ge=0)

class OrdemServicoResponse(OrdemServicoBase):
    id: UUID
    tenant_id: UUID
    numero_os: str
    status: str
    data_abertura: datetime
    data_conclusao: Optional[datetime] = None
    custo_total_pecas: float

    model_config = ConfigDict(from_attributes=True)

class ItemOrdemServicoCreate(BaseModel):
    produto_id: UUID
    quantidade: float = Field(..., gt=0)


class ItemOrdemServicoResponse(BaseModel):
    id: UUID
    os_id: UUID
    produto_id: UUID
    quantidade: float
    preco_unitario_na_data: float

    model_config = ConfigDict(from_attributes=True)


class RegistroManutencaoResponse(BaseModel):
    id: UUID
    maquinario_id: UUID
    os_id: Optional[UUID]
    tipo: str
    descricao: str
    custo_total: float
    horimetro_na_data: float
    km_na_data: Optional[float]
    tecnico_responsavel: Optional[str]
    data_realizacao: datetime

    model_config = ConfigDict(from_attributes=True)
