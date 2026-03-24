from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
import uuid
from datetime import datetime
import re

TipoPrincipal = Literal["FORNECEDOR", "CLIENTE", "FUNCIONARIO", "PARCEIRO", "PRESTADOR", "OUTRO"]
TipoPessoa = Literal["PF", "PJ"]
TipoConta = Literal["CORRENTE", "POUPANCA", "PIX"]


class PessoaBase(BaseModel):
    tipo_principal: TipoPrincipal
    tipos: list[TipoPrincipal] = []
    tipo_pessoa: TipoPessoa = "PJ"
    nome: str = Field(..., min_length=2, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    rg_ie: Optional[str] = Field(None, max_length=30)

    # Contato
    email: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)

    # Endereço
    cep: Optional[str] = Field(None, max_length=9)
    logradouro: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, max_length=2)

    # Dados bancários
    banco_codigo: Optional[str] = Field(None, max_length=10)
    banco_agencia: Optional[str] = Field(None, max_length=10)
    banco_conta: Optional[str] = Field(None, max_length=20)
    banco_tipo_conta: Optional[TipoConta] = None
    banco_chave_pix: Optional[str] = Field(None, max_length=100)

    observacoes: Optional[str] = None
    tags: list[str] = []

    @field_validator("tipos")
    @classmethod
    def garantir_tipo_principal_na_lista(cls, v, info):
        tipo_principal = info.data.get("tipo_principal")
        if tipo_principal and tipo_principal not in v:
            v = [tipo_principal] + v
        return v

    @field_validator("uf")
    @classmethod
    def uf_uppercase(cls, v):
        return v.upper() if v else v

    @field_validator("cpf_cnpj")
    @classmethod
    def limpar_cpf_cnpj(cls, v):
        if v:
            return re.sub(r"[^\d]", "", v)
        return v


class PessoaCreate(PessoaBase):
    pass


class PessoaUpdate(BaseModel):
    tipo_principal: Optional[TipoPrincipal] = None
    tipos: Optional[list[TipoPrincipal]] = None
    nome: Optional[str] = Field(None, min_length=2, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    rg_ie: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    cep: Optional[str] = Field(None, max_length=9)
    logradouro: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, max_length=2)
    banco_codigo: Optional[str] = Field(None, max_length=10)
    banco_agencia: Optional[str] = Field(None, max_length=10)
    banco_conta: Optional[str] = Field(None, max_length=20)
    banco_tipo_conta: Optional[TipoConta] = None
    banco_chave_pix: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None
    tags: Optional[list[str]] = None
    ativo: Optional[bool] = None


class PessoaResponse(PessoaBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PessoaListItem(BaseModel):
    """Versão resumida para listagens — sem dados bancários."""
    id: uuid.UUID
    tipo_principal: TipoPrincipal
    tipos: list[TipoPrincipal]
    tipo_pessoa: TipoPessoa
    nome: str
    nome_fantasia: Optional[str]
    cpf_cnpj: Optional[str]
    email: Optional[str]
    celular: Optional[str]
    cidade: Optional[str]
    uf: Optional[str]
    ativo: bool
    tags: list[str]

    model_config = {"from_attributes": True}
