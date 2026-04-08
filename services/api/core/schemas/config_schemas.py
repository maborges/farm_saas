from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Dict, List, Any, Literal
from uuid import UUID

class SMTPConfig(BaseModel):
    host: str = Field(..., example="smtp.mailtrap.io")
    port: int = Field(587, example=587)
    user: Optional[str] = None
    pwd: Optional[str] = Field(None, alias="pass")
    mail_from: str = Field(..., alias="from", example="noreply@agrosaas.com.br")

    class Config:
        populate_by_name = True

class SaaSConfigResponse(BaseModel):
    chave: str
    valor: Dict
    descricao: Optional[str]
    ativo: bool

class SaaSConfigUpdate(BaseModel):
    valor: Dict
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class TenantConfigResponse(BaseModel):
    categoria: str
    chave: str
    valor: Dict
    descricao: Optional[str]
    ativo: bool

    class Config:
        from_attributes = True

class TenantConfigUpdate(BaseModel):
    valor: Dict
    descricao: Optional[str] = None
    ativo: Optional[bool] = None


# =============================================================================
# SCHEMAS DE CONFIGURAÇÕES GLOBAIS
# =============================================================================

class ConfiguracoesGeraisResponse(BaseModel):
    """Resposta com todas as configurações gerais do tenant."""
    ano_agricola: Dict[str, int]
    unidade_area: str
    moeda: str
    fuso_horario: str
    idioma: str


class ConfiguracoesGeraisUpdate(BaseModel):
    """Payload para atualizar configurações gerais."""
    ano_agricola_inicio: Optional[int] = Field(None, ge=1, le=12, description="Mês de início (1-12)")
    ano_agricola_fim: Optional[int] = Field(None, ge=1, le=12, description="Mês de fim (1-12)")
    unidade_area: Optional[str] = None
    moeda: Optional[str] = None
    fuso_horario: Optional[str] = None
    idioma: Optional[str] = None


class ConversaoAreaRequest(BaseModel):
    """Payload para conversão de área."""
    valor: float = Field(..., gt=0, description="Valor a converter")
    unidade_origem: str = Field(..., description="Unidade de origem")
    unidade_destino: Optional[str] = Field(None, description="Unidade de destino (usa padrão do tenant se None)")


class ConversaoAreaResponse(BaseModel):
    """Resposta de conversão de área."""
    valor_original: float
    unidade_origem: str
    valor_convertido: float
    unidade_destino: str


class UnidadeAreaInfo(BaseModel):
    """Informações sobre uma unidade de área."""
    codigo: str
    nome: str


# =============================================================================
# SCHEMAS DE CATEGORIAS
# =============================================================================

class CategoriaItem(BaseModel):
    """Item de categoria."""
    id: str
    nome: str
    parent_id: Optional[str]
    ativa: bool
    metadata: Dict[str, Any]


class CategoriasResponse(BaseModel):
    """Resposta de lista de categorias."""
    tipo: str
    categorias: List[CategoriaItem]
    total: int


class CategoriaResponse(BaseModel):
    """Categoria da tabela CategoriaCustom."""
    id: UUID
    tipo: str
    nome: str
    slug: str
    parent_id: Optional[UUID]
    is_system: bool
    is_active: bool
    ordem: int
    cor_hex: Optional[str]
    icone: Optional[str]

    class Config:
        from_attributes = True


class CategoriaCreateRequest(BaseModel):
    """Payload para criar categoria."""
    tipo: Literal["despesa", "receita", "operacao", "produto", "insumo"]
    nome: str = Field(..., min_length=2, max_length=100)
    parent_id: Optional[UUID] = None
    cor_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icone: Optional[str] = Field(None, max_length=50)
    ordem: int = Field(0, ge=0)
    metadata: Optional[Dict[str, Any]] = None  # mantido para compatibilidade


class CategoriaUpdateRequest(BaseModel):
    """Payload para atualizar categoria."""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    cor_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icone: Optional[str] = Field(None, max_length=50)
    ordem: Optional[int] = Field(None, ge=0)
    metadata: Optional[Dict[str, Any]] = None  # mantido para compatibilidade


# =============================================================================
# SCHEMAS DE CONFIGURAÇÃO POR FAZENDA
# =============================================================================

class ConfiguracaoFazendaResponse(BaseModel):
    """Override de configurações por fazenda."""
    fazenda_id: UUID
    overrides: Dict[str, Any]

    class Config:
        from_attributes = True


class ConfiguracaoFazendaUpdate(BaseModel):
    """Payload para atualizar overrides de uma fazenda."""
    overrides: Dict[str, Any] = Field(..., description="Ex: {'fuso_horario': 'America/Cuiaba'}")


# =============================================================================
# SCHEMAS DE HISTÓRICO
# =============================================================================

class HistoricoConfiguracaoItem(BaseModel):
    id: UUID
    campo_alterado: str
    valor_anterior: Optional[Dict[str, Any]]
    valor_novo: Dict[str, Any]
    alterado_por: Optional[UUID]
    alterado_em: Any

    class Config:
        from_attributes = True


# =============================================================================
# SCHEMAS DE ONBOARDING
# =============================================================================

class OnboardingConfigRequest(BaseModel):
    """Payload de configuração inicial do onboarding."""
    ano_agricola_inicio: int = Field(7, ge=1, le=12, description="Mês de início (padrão: 7)")
    ano_agricola_fim: int = Field(6, ge=1, le=12, description="Mês de fim (padrão: 6)")
    unidade_area: str = Field("HA", description="Unidade de área padrão")
    moeda: str = Field("BRL", description="Moeda padrão")
    fuso_horario: str = Field("America/Sao_Paulo", description="Fuso horário")
    idioma: str = Field("pt-BR", description="Idioma da interface")
    aceitar_categorias_padrao: bool = Field(True, description="Aceitar categorias padrão do sistema")


# =============================================================================
# SCHEMAS DE SEGURANÇA (RATE LIMITING)
# =============================================================================

class SegurancaConfigResponse(BaseModel):
    """Resposta com configurações de segurança (rate limiting de login)."""
    rate_limiting_ativo: bool = Field(True, description="Se o bloqueio automático por tentativas está ativo")
    max_tentativas: int = Field(5, ge=1, le=20, description="Número máximo de tentativas antes do bloqueio")
    tempo_bloqueio_minutos: int = Field(15, ge=1, le=1440, description="Tempo de bloqueio em minutos")


class SegurancaConfigUpdate(BaseModel):
    """Payload para atualizar configurações de segurança."""
    rate_limiting_ativo: Optional[bool] = None
    max_tentativas: Optional[int] = Field(None, ge=1, le=20)
    tempo_bloqueio_minutos: Optional[int] = Field(None, ge=1, le=1440)
