from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
import uuid


class DocumentoEquipamentoCreate(BaseModel):
    equipamento_id: uuid.UUID
    tipo: str
    descricao: Optional[str] = None
    numero: Optional[str] = None
    orgao_emissor: Optional[str] = None
    data_emissao: Optional[date] = None
    data_vencimento: Optional[date] = None
    arquivo_url: Optional[str] = None
    observacoes: Optional[str] = None


class DocumentoEquipamentoUpdate(BaseModel):
    tipo: Optional[str] = None
    descricao: Optional[str] = None
    numero: Optional[str] = None
    orgao_emissor: Optional[str] = None
    data_emissao: Optional[date] = None
    data_vencimento: Optional[date] = None
    arquivo_url: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class DocumentoEquipamentoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    equipamento_id: uuid.UUID
    tipo: str
    descricao: Optional[str]
    numero: Optional[str]
    orgao_emissor: Optional[str]
    data_emissao: Optional[date]
    data_vencimento: Optional[date]
    arquivo_url: Optional[str]
    observacoes: Optional[str]
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
