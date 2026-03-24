from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime, date
from typing import List, Optional

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class PerfilSimplesResponse(BaseModel):
    id: UUID
    nome: str
    permissoes: dict

class FazendaAcessoResponse(BaseModel):
    fazenda_id: UUID
    nome: str

class TenantAcessoResponse(BaseModel):
    tenant_id: UUID
    nome_tenant: str
    perfil: PerfilSimplesResponse
    fazendas: List[FazendaAcessoResponse]
    is_owner: bool
    plan_tier: str = "BASICO"
    max_fazendas: int = 1
    max_usuarios: int = 2
    modulos: List[str] = []

class UsuarioMeResponse(BaseModel):
    id: UUID
    email: str
    username: str
    nome_completo: Optional[str]
    foto_perfil_url: Optional[str]
    is_superuser: bool
    tenants: List[TenantAcessoResponse]
    
class UserCreateRequest(BaseModel):
    email: EmailStr
    username: str
    nome_completo: str
    senha: str
