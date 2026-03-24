from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class ConviteCreateRequest(BaseModel):
    email_convidado: EmailStr
    perfil_id: UUID
    fazendas_ids: List[str] # Lista de UUIDs de fazendas em formato string
    data_validade_acesso: Optional[str] = None # YYYY-MM-DD
    
class ConviteResponse(BaseModel):
    id: UUID
    email_convidado: str
    perfil_id: UUID
    status: str
    token_convite: str
    created_at: datetime
    
class AssinanteRegisterRequest(BaseModel):
    """Payload de Onboarding Inicial (Produtor criando conta nova no site)"""
    email: EmailStr
    username: str
    nome_completo: str
    senha: str
    nome_fazenda: str # Nome da primeira propriedade
    cnpj_tenant: str
