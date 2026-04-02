"""Schemas para Contabilidade."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date


class IntegracaoContabilCreate(BaseModel):
    sistema: str  # dominio, fortes, contmatic
    nome: str = Field(..., max_length=100)
    configuracoes: Optional[Dict] = {}


class IntegracaoContabilResponse(BaseModel):
    id: int
    tenant_id: str
    sistema: str
    nome: str
    ativo: bool
    ultima_exportacao: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ExportacaoContabilCreate(BaseModel):
    integracao_id: int
    tipo: str = 'lancamentos'
    periodo_inicio: date
    periodo_fim: date


class ExportacaoContabilResponse(BaseModel):
    id: int
    tenant_id: str
    integracao_id: int
    tipo: str
    periodo_inicio: date
    periodo_fim: date
    arquivo_nome: Optional[str]
    arquivo_formato: Optional[str]
    status: str
    registros_exportados: int
    agendada: bool
    created_at: datetime
    processada_em: Optional[datetime]

    class Config:
        from_attributes = True


class LancamentoContabilCreate(BaseModel):
    data_lancamento: date
    documento: Optional[str] = None
    historico: str
    valor_debito: float = 0
    valor_credito: float = 0
    conta_debito: Optional[str] = None
    conta_credito: Optional[str] = None
    centro_custo: Optional[str] = None
    origem: Optional[str] = None
    origem_id: Optional[int] = None


class LancamentoContabilResponse(BaseModel):
    id: int
    data_lancamento: date
    documento: Optional[str]
    historico: str
    valor_debito: float
    valor_credito: float
    conta_debito: Optional[str]
    conta_credito: Optional[str]
    exportado: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PlanoContasResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    tipo: Optional[str]
    natureza: Optional[str]
    nivel: int
    sistema_origem: Optional[str]
    ativo: bool

    class Config:
        from_attributes = True


class MapeamentoContabilCreate(BaseModel):
    integracao_id: int
    entidade_agrosaas: str
    campo_agrosaas: str
    valor_agrosaas: Optional[str] = None
    conta_contabil: Optional[str] = None
    centro_custo: Optional[str] = None
    tipo_operacao: Optional[str] = None


class MapeamentoContabilResponse(BaseModel):
    id: int
    entidade_agrosaas: str
    campo_agrosaas: str
    conta_contabil: Optional[str]
    centro_custo: Optional[str]
    tipo_operacao: Optional[str]
    ativo: bool

    class Config:
        from_attributes = True
