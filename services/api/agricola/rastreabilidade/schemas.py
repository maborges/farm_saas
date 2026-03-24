from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

class LoteRastreabilidadeBase(BaseModel):
    codigo_lote: str
    safra_id: UUID
    talhao_id: UUID
    produto: str
    variedade: Optional[str] = None
    quantidade_total: float
    unidade: str = "KG"
    certificacoes: List[str] = []
    observacoes: Optional[str] = None

class LoteRastreabilidadeCreate(LoteRastreabilidadeBase):
    pass

class LoteRastreabilidadeResponse(LoteRastreabilidadeBase):
    id: UUID
    data_geracao: datetime
    qr_code_url: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CertificacaoBase(BaseModel):
    fazenda_id: UUID
    nome: str
    extensao: Optional[str] = None
    data_emissao: date
    data_validade: date
    orgao_certificador: Optional[str] = None
    numero_registro: Optional[str] = None
    link_documento: Optional[str] = None

class CertificacaoCreate(CertificacaoBase):
    pass

class CertificacaoResponse(CertificacaoBase):
    id: UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
