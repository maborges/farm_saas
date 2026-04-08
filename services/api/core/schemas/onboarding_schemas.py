from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from core.utils.cpf_cnpj import validar_cpf_ou_cnpj, apenas_numeros

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
    cnpj_tenant: str
    # Grupo de fazendas — obrigatório: toda assinatura pertence a um grupo
    nome_grupo: str  # Ex: "Fazendas Região Sul", "Minha Propriedade"
    # Primeira fazenda — opcional: pode ser adicionada depois (status PENDENTE_FAZENDA)
    nome_fazenda: Optional[str] = None

    @field_validator("cnpj_tenant")
    @classmethod
    def validar_cnpj_tenant(cls, v: str) -> str:
        if not v:
            raise ValueError("CPF ou CNPJ é obrigatório.")
        
        if not validar_cpf_ou_cnpj(v):
            raise ValueError("CPF ou CNPJ inválido. Verifique os dados informados.")
        
        # Retorna apenas os números para armazenamento
        return apenas_numeros(v)
