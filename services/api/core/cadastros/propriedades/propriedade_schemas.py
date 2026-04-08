from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
import uuid

from .propriedade_models import NaturezaVinculo, TipoDocumentoExploracao


class PropriedadeCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    ie_isento: bool = False
    email: Optional[str] = Field(None, max_length=200)
    telefone: Optional[str] = Field(None, max_length=30)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    regime_tributario: Optional[str] = Field(None, max_length=30)
    cor: Optional[str] = Field(None, max_length=7)
    icone: Optional[str] = Field(None, max_length=50)
    ordem: int = 0
    observacoes: Optional[str] = None


class PropriedadeUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=200)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    ie_isento: Optional[bool] = None
    email: Optional[str] = Field(None, max_length=200)
    telefone: Optional[str] = Field(None, max_length=30)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    regime_tributario: Optional[str] = Field(None, max_length=30)
    cor: Optional[str] = Field(None, max_length=7)
    icone: Optional[str] = Field(None, max_length=50)
    ordem: Optional[int] = None
    ativo: Optional[bool] = None
    observacoes: Optional[str] = None


class PropriedadeResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    cpf_cnpj: Optional[str]
    inscricao_estadual: Optional[str]
    ie_isento: bool
    email: Optional[str]
    telefone: Optional[str]
    nome_fantasia: Optional[str]
    regime_tributario: Optional[str]
    cor: Optional[str]
    icone: Optional[str]
    ordem: int
    ativo: bool
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ExploracaoCreate(BaseModel):
    fazenda_id: uuid.UUID
    natureza: str
    data_inicio: date
    data_fim: Optional[date] = None
    numero_contrato: Optional[str] = Field(None, max_length=100)
    valor_anual: Optional[float] = Field(None, gt=0)
    percentual_producao: Optional[float] = Field(None, gt=0, le=100)
    area_explorada_ha: Optional[float] = Field(None, gt=0)
    observacoes: Optional[str] = None

    @field_validator("natureza")
    @classmethod
    def validar_natureza(cls, v: str) -> str:
        validos = {e.value for e in NaturezaVinculo}
        if v not in validos:
            raise ValueError(f"Natureza inválida. Valores aceitos: {sorted(validos)}")
        return v


class ExploracaoUpdate(BaseModel):
    natureza: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    numero_contrato: Optional[str] = Field(None, max_length=100)
    valor_anual: Optional[float] = None
    percentual_producao: Optional[float] = None
    area_explorada_ha: Optional[float] = None
    ativo: Optional[bool] = None
    observacoes: Optional[str] = None

    @field_validator("natureza")
    @classmethod
    def validar_natureza(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        validos = {e.value for e in NaturezaVinculo}
        if v not in validos:
            raise ValueError(f"Natureza inválida. Valores aceitos: {sorted(validos)}")
        return v


class ExploracaoResponse(BaseModel):
    id: uuid.UUID
    propriedade_id: uuid.UUID
    fazenda_id: uuid.UUID
    natureza: str
    data_inicio: date
    data_fim: Optional[date]
    numero_contrato: Optional[str]
    valor_anual: Optional[float]
    percentual_producao: Optional[float]
    area_explorada_ha: Optional[float]
    documento_s3_key: Optional[str]
    documento_tipo: Optional[str]
    ativo: bool
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class DocumentoExploracaoCreate(BaseModel):
    tipo: str
    nome_arquivo: str
    storage_path: str
    storage_backend: str = "local"
    tamanho_bytes: int
    mime_type: Optional[str] = None
    data_emissao: Optional[date] = None
    data_validade: Optional[date] = None
    numero_documento: Optional[str] = None
    orgao_expedidor: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        validos = {e.value for e in TipoDocumentoExploracao}
        if v not in validos:
            raise ValueError(f"Tipo inválido. Valores aceitos: {sorted(validos)}")
        return v


class DocumentoExploracaoResponse(BaseModel):
    id: uuid.UUID
    exploracao_id: uuid.UUID
    tipo: str
    nome_arquivo: str
    storage_path: str
    storage_backend: str
    tamanho_bytes: int
    mime_type: Optional[str]
    data_emissao: Optional[date]
    data_validade: Optional[date]
    numero_documento: Optional[str]
    orgao_expedidor: Optional[str]
    ativo: bool
    created_at: datetime
    model_config = {"from_attributes": True}
