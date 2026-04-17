from pydantic import BaseModel, EmailStr, Field, field_validator
from core.utils.cpf_cnpj import validar_cpf
from uuid import UUID
from datetime import datetime, date
from typing import List, Optional

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ==================== SCHEMAS PARA DESBLOQUEIO ====================

class LoginDesbloqueioRequest(BaseModel):
    """Request para desbloqueio de usuário por email."""
    email: EmailStr

class LoginDesbloqueioResponse(BaseModel):
    """Resposta do desbloqueio."""
    sucesso: bool
    mensagem: str
    email: str

class LoginTentativasInfoResponse(BaseModel):
    """Informações sobre tentativas de login de um usuário."""
    email: str
    tentativas_count: int
    bloqueado: bool
    data_bloqueio: Optional[str] = None
    data_desbloqueio: Optional[str] = None
    ultima_tentativa: Optional[str] = None
    motivo_falha: Optional[str] = None

class LoginBloqueadoItem(BaseModel):
    """Item da lista de bloqueados recentes."""
    email: str
    tentativas_count: int
    data_bloqueio: Optional[str] = None
    data_desbloqueio: Optional[str] = None
    motivo_falha: Optional[str] = None

class LoginBloqueadosListaResponse(BaseModel):
    """Lista de usuários bloqueados recentes."""
    total: int
    bloqueados: List[LoginBloqueadoItem]
    
class PerfilSimplesResponse(BaseModel):
    id: UUID
    nome: str
    permissoes: dict

class UnidadeProdutivaAcessoResponse(BaseModel):
    unidade_produtiva_id: UUID
    nome: str

# Backward compatibility alias
FazendaAcessoResponse = UnidadeProdutivaAcessoResponse

class TenantAcessoResponse(BaseModel):
    tenant_id: UUID
    nome_tenant: str
    perfil: Optional[PerfilSimplesResponse]
    fazendas: List[UnidadeProdutivaAcessoResponse]
    is_owner: bool
    plan_tier: str = "BASICO"
    max_fazendas: int = 1
    max_usuarios: int = 2
    modulos: List[str] = []

class UsuarioMeResponse(BaseModel):
    id: UUID
    email: str
    username: str
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    nome_completo: Optional[str]
    foto_perfil_url: Optional[str]
    is_superuser: bool
    tenants: List[TenantAcessoResponse]

class UserCreateRequest(BaseModel):
    email: EmailStr
    username: str
    nome_completo: str
    senha: str
    cpf: Optional[str] = Field(None, min_length=11, max_length=11, description="CPF sem formatação, 11 dígitos")
    telefone: Optional[str] = None

    @field_validator("cpf")
    @classmethod
    def cpf_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = "".join(c for c in v if c.isdigit())
        if not validar_cpf(digits):
            raise ValueError("CPF inválido — verifique os dígitos verificadores")
        return digits

class UserUpdateRequest(BaseModel):
    nome_completo: Optional[str] = None
    telefone: Optional[str] = None
    foto_perfil_url: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    """Alteração de senha pelo próprio usuário (requer senha atual)."""
    senha_atual: str = Field(..., min_length=6, description="Senha atual do usuário")
    nova_senha: str = Field(..., min_length=8, description="Nova senha (mínimo 8 caracteres)")
    confirmar_senha: str = Field(..., min_length=8, description="Confirmação da nova senha")

class ChangePasswordResponse(BaseModel):
    success: bool
    message: str

class CreateSubscriptionRequest(BaseModel):
    """Criação de nova assinatura (tenant) por um usuário já logado."""
    nome: str = Field(..., min_length=2, max_length=200, description="Nome do produtor ou empresa")
    cpf_cnpj: Optional[str] = Field(None, description="CPF ou CNPJ — opcional no cadastro inicial")
    plano_id: UUID
    ciclo: str = Field("MENSAL", pattern="^(MENSAL|ANUAL)$")

class CreateSubscriptionResponse(BaseModel):
    access_token: str
    tenant_id: UUID
    nome_tenant: str
    is_trial: bool
    trial_expira_em: Optional[datetime] = None
    data_primeiro_vencimento: Optional[date] = None

# ==================== SCHEMAS PARA RECUPERAÇÃO DE SENHA ====================

class ForgotPasswordRequest(BaseModel):
    """Request para solicitar recuperação de senha."""
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    """Resposta do forgot password."""
    sucesso: bool
    mensagem: str
    email: Optional[str] = None

class VerifyResetTokenRequest(BaseModel):
    """Request para verificar um token de recuperação."""
    token: str

class VerifyResetTokenResponse(BaseModel):
    """Resposta da verificação do token."""
    valido: bool
    mensagem: str
    email: Optional[str] = None
    expira_em: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    """Request para redefinir a senha com token."""
    token: str
    nova_senha: str = Field(..., min_length=6, description="Nova senha com no mínimo 6 caracteres")
    confirmar_senha: str

    @property
    def senhas_coincidem(self) -> bool:
        return self.nova_senha == self.confirmar_senha

class ResetPasswordResponse(BaseModel):
    """Resposta do reset de senha."""
    sucesso: bool
    mensagem: str
