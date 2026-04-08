from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime

class PlanoAssinaturaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    modulos_inclusos: List[str] = ["CORE"]
    limite_usuarios_minimo: int = 1
    limite_usuarios_maximo: Optional[int] = None
    limite_hectares: Optional[float] = None
    preco_mensal: float = 0.0
    preco_anual: float = 0.0
    ativo: bool = True
    is_default: bool = False
    disponivel_site: bool = False
    disponivel_crm: bool = True

class PlanoAssinaturaCreate(PlanoAssinaturaBase):
    pass

class PlanoAssinaturaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    modulos_inclusos: Optional[List[str]] = None
    limite_usuarios_minimo: Optional[int] = None
    limite_usuarios_maximo: Optional[int] = None
    limite_hectares: Optional[float] = None
    preco_mensal: Optional[float] = None
    preco_anual: Optional[float] = None
    ativo: Optional[bool] = None
    is_default: Optional[bool] = None
    disponivel_site: Optional[bool] = None
    disponivel_crm: Optional[bool] = None

class PlanoAssinaturaResponse(PlanoAssinaturaBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FaturaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    tenant_nome: Optional[str] = None
    plano_nome: Optional[str] = None
    valor: float
    data_vencimento: datetime
    status: str
    url_comprovante: Optional[str] = None
    data_envio_comprovante: Optional[datetime] = None
    justificativa_rejeicao: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReviewInvoiceRequest(BaseModel):
    aprovado: bool
    justificativa: Optional[str] = None
