import uuid
from datetime import datetime, date
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, field_validator
import re


# ── Endereço ─────────────────────────────────────────────────────────────────

class EnderecoBase(BaseModel):
    tipo: str = "PRINCIPAL"
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    pais: str = "BRA"
    lat: Optional[float] = None
    lng: Optional[float] = None


class EnderecoCreate(EnderecoBase):
    pass


class EnderecoResponse(EnderecoBase):
    id: uuid.UUID
    ativo: bool

    model_config = {"from_attributes": True}


# ── Tipo de Relacionamento ────────────────────────────────────────────────────

class TipoRelacionamentoBase(BaseModel):
    codigo: str
    nome: str
    descricao: Optional[str] = None
    cor: str = "#6B7280"
    icone: str = "user"


class TipoRelacionamentoCreate(TipoRelacionamentoBase):
    pass


class TipoRelacionamentoResponse(TipoRelacionamentoBase):
    id: uuid.UUID
    sistema: bool
    ativo: bool
    tenant_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}


# ── Relacionamento Pessoa ─────────────────────────────────────────────────────

class RelacionamentoCreate(BaseModel):
    tipo_id: uuid.UUID
    fazenda_id: Optional[uuid.UUID] = None
    observacoes: Optional[str] = None
    ativo_desde: Optional[date] = None
    ativo_ate: Optional[date] = None
    dados_extras: Optional[dict[str, Any]] = None


class RelacionamentoResponse(RelacionamentoCreate):
    id: uuid.UUID
    tipo: TipoRelacionamentoResponse

    model_config = {"from_attributes": True}


# ── PII ───────────────────────────────────────────────────────────────────────

class PessoaPIIUpdate(BaseModel):
    # PF
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    data_nascimento: Optional[date] = None
    # PJ
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    ie: Optional[str] = None
    data_fundacao: Optional[date] = None
    # Contato
    email: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None


class PessoaPIIResponse(PessoaPIIUpdate):
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Pessoa ────────────────────────────────────────────────────────────────────

class PessoaCreate(BaseModel):
    tipo: str  # PF | PJ
    nome_exibicao: str
    base_legal: str = "CONTRATO"
    reter_dados_ate: Optional[date] = None
    # PII embutida no create para conveniência
    pii: Optional[PessoaPIIUpdate] = None
    # Endereços iniciais
    enderecos: list[EnderecoCreate] = []
    # Relacionamentos iniciais
    relacionamentos: list[RelacionamentoCreate] = []

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        if v not in ("PF", "PJ"):
            raise ValueError("tipo deve ser PF ou PJ")
        return v


class PessoaUpdate(BaseModel):
    nome_exibicao: Optional[str] = None
    base_legal: Optional[str] = None
    reter_dados_ate: Optional[date] = None
    ativo: Optional[bool] = None


class PessoaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    tipo: str
    nome_exibicao: str
    base_legal: str
    reter_dados_ate: Optional[date]
    anonimizado_em: Optional[datetime]
    ativo: bool
    created_at: datetime
    updated_at: datetime
    # Relacionamentos resumidos (sem PII) — sempre retornados
    relacionamentos: list[RelacionamentoResponse] = []

    model_config = {"from_attributes": True}


class PessoaComPIIResponse(PessoaResponse):
    """Retornado apenas quando o chamador tem permissão para ver dados PII."""
    pii: Optional[PessoaPIIResponse] = None
    enderecos: list[EnderecoResponse] = []


# ── Consentimento ─────────────────────────────────────────────────────────────

class ConsentimentoCreate(BaseModel):
    finalidade: str
    concedido: bool
    canal: str = "WEB"
    ip_origem: Optional[str] = None
    versao_politica: Optional[str] = None


class ConsentimentoResponse(ConsentimentoCreate):
    id: uuid.UUID
    criado_em: datetime

    model_config = {"from_attributes": True}
