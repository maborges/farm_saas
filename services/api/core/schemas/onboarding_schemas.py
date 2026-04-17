from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from core.utils.cpf_cnpj import validar_cpf_ou_cnpj, apenas_numeros

class ConviteCreateRequest(BaseModel):
    email_convidado: EmailStr
    perfil_id: UUID
    fazendas_ids: List[str] = []  # Lista de UUIDs de unidades produtivas em formato string (backward compat)
    data_validade_acesso: Optional[str] = None # YYYY-MM-DD
    
class ConviteResponse(BaseModel):
    id: UUID
    email_convidado: str
    perfil_id: UUID
    status: str
    token_convite: str
    created_at: datetime
    
class AssinanteRegisterRequest(BaseModel):
    """Payload de Onboarding Inicial — Usuário + Produtor (Tenant) + Plano"""
    # Dados do Usuário (Assinante Administrador)
    email: EmailStr
    username: str
    nome_completo: str
    senha: str
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    # Dados do Produtor (Tenant)
    nome_produtor: str  # Nome do produtor rural / empresa
    cnpj_tenant: Optional[str] = None  # CPF ou CNPJ — opcional no cadastro inicial
    # Plano escolhido
    plano_id: UUID
    ciclo: str = "MENSAL"  # MENSAL | ANUAL

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        from core.utils.cpf_cnpj import validar_cpf
        digits = "".join(c for c in v if c.isdigit()) if v else ""
        if len(digits) != 11:
            return v  # Skip validation if not 11 digits
        if not validar_cpf(digits):
            raise ValueError("CPF inválido. Verifique os dados informados.")
        return digits

    @field_validator("cnpj_tenant")
    @classmethod
    def validar_cnpj_tenant(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        if not validar_cpf_ou_cnpj(v):
            raise ValueError("CPF ou CNPJ inválido. Verifique os dados informados.")
        return apenas_numeros(v)
