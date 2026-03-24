from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Literal, Optional, List
from datetime import datetime
import uuid

NaturezaConta = Literal["SINTETICA", "ANALITICA"]
TipoConta = Literal["RECEITA", "DESPESA"]
CategoriaRFB = Literal[
    "RECEITA_ATIVIDADE",
    "RECEITA_FORA_ATIVIDADE",
    "CUSTEIO",
    "INVESTIMENTO",
    "NAO_DEDUTIVEL",
]


class PlanoContaCreate(BaseModel):
    parent_id: Optional[uuid.UUID] = None
    codigo: str = Field(..., min_length=1, max_length=20, description="Ex: 3.01")
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: Optional[str] = None
    tipo: TipoConta
    natureza: NaturezaConta = "ANALITICA"
    categoria_rfb: Optional[CategoriaRFB] = None
    ordem: int = Field(0, ge=0)


class PlanoContaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = None
    categoria_rfb: Optional[CategoriaRFB] = None
    ordem: Optional[int] = Field(None, ge=0)
    ativo: Optional[bool] = None


class PlanoContaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    codigo: str
    nome: str
    descricao: Optional[str]
    tipo: str
    natureza: str
    categoria_rfb: Optional[str]
    ordem: int
    is_sistema: bool
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanoContaNode(BaseModel):
    """Nó para exibição em árvore hierárquica."""
    id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    codigo: str
    nome: str
    tipo: str
    natureza: str
    categoria_rfb: Optional[str]
    ordem: int
    is_sistema: bool
    ativo: bool
    filhos: List["PlanoContaNode"] = []

    model_config = ConfigDict(from_attributes=True)


PlanoContaNode.model_rebuild()
