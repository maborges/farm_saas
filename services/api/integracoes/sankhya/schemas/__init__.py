"""Schemas para integração Sankhya."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class SankhyaConfigCreate(BaseModel):
    ws_url: str = Field(..., description="URL do WS Sankhya")
    username: str
    password: str
    sync_interval: int = 900  # 15 minutos


class SankhyaConfigResponse(BaseModel):
    id: int
    tenant_id: str
    ws_url: str
    username: str
    ativo: bool
    ultimo_teste: Optional[datetime]
    teste_status: Optional[str]
    ultimo_sync: Optional[datetime]
    sync_interval: int
    created_at: datetime

    class Config:
        from_attributes = True


class SankhyaSyncLogResponse(BaseModel):
    id: int
    tenant_id: str
    tipo: str
    operacao: str
    status: str
    registros_processados: int
    registros_sucesso: int
    registros_erro: int
    tempo_execucao_ms: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class SankhyaPessoaResponse(BaseModel):
    id: int
    sankhya_id: str
    tipo: str
    nome: str
    nome_fantasia: Optional[str]
    cpf: Optional[str]
    cnpj: Optional[str]
    email: Optional[str]
    telefone: Optional[str]
    cidade: Optional[str]
    uf: Optional[str]
    ativo: bool
    sincronizado_em: Optional[datetime]

    class Config:
        from_attributes = True


class SankhyaProdutoResponse(BaseModel):
    id: int
    sankhya_id: str
    codigo: str
    nome: str
    ncm: Optional[str]
    unidade: str
    preco_custo: Optional[float]
    preco_venda: Optional[float]
    ativo: bool
    sincronizado_em: Optional[datetime]

    class Config:
        from_attributes = True


class SankhyaNFEResponse(BaseModel):
    id: int
    sankhya_id: Optional[str]
    tipo_operacao: str
    numero: str
    serie: Optional[str]
    chave_acesso: Optional[str]
    valor_total: float
    data_emissao: Optional[date]
    status_sankhya: Optional[str]
    exportado_sankhya: bool
    sincronizado_em: Optional[datetime]

    class Config:
        from_attributes = True


class SankhyaLancamentoFinanceiroResponse(BaseModel):
    id: int
    sankhya_id: Optional[str]
    tipo: str
    numero_documento: Optional[str]
    valor: float
    valor_saldo: Optional[float]
    data_vencimento: Optional[date]
    status: Optional[str]
    exportado_sankhya: bool
    sincronizado_em: Optional[datetime]

    class Config:
        from_attributes = True


class SankhyaTestConnectionResponse(BaseModel):
    sucesso: bool
    mensagem: str


class SankhyaSyncStatusResponse(BaseModel):
    configurado: bool
    ativo: bool
    ultimo_sync: Optional[datetime]
    proximo_sync: Optional[datetime]
    status_conexao: str
