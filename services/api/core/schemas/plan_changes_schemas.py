"""
Pydantic schemas para mudanças de plano e pricing dinâmico.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# PLANO PRICING (Matriz de preços)
# ============================================================================

class PlanoPricingBase(BaseModel):
    """Base schema para pricing de planos."""
    plano_id: UUID
    faixa_inicio: int = Field(..., ge=1, description="Início da faixa de usuários (inclusivo)")
    faixa_fim: Optional[int] = Field(None, ge=1, description="Fim da faixa (inclusivo). NULL = ilimitado")
    preco_por_usuario_mensal: Decimal = Field(..., ge=0, decimal_places=2)
    preco_por_usuario_anual: Decimal = Field(..., ge=0, decimal_places=2)
    ativo: bool = True

    @field_validator('faixa_fim')
    @classmethod
    def validar_faixa(cls, v: Optional[int], info) -> Optional[int]:
        """Valida que faixa_fim >= faixa_inicio."""
        if v is not None and 'faixa_inicio' in info.data:
            if v < info.data['faixa_inicio']:
                raise ValueError('faixa_fim deve ser maior ou igual a faixa_inicio')
        return v


class PlanoPricingCreate(PlanoPricingBase):
    """Schema para criar pricing de plano."""
    pass


class PlanoPricingUpdate(BaseModel):
    """Schema para atualizar pricing de plano."""
    faixa_inicio: Optional[int] = Field(None, ge=1)
    faixa_fim: Optional[int] = None
    preco_por_usuario_mensal: Optional[Decimal] = Field(None, ge=0)
    preco_por_usuario_anual: Optional[Decimal] = Field(None, ge=0)
    ativo: Optional[bool] = None


class PlanoPricingResponse(PlanoPricingBase):
    """Schema de resposta para pricing de plano."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CalculoPrecoPorUsuarioResponse(BaseModel):
    """Resposta do cálculo de preço por quantidade de usuários."""
    plano_id: UUID
    plano_nome: str
    quantidade_usuarios: int
    ciclo: str  # MENSAL ou ANUAL
    detalhamento_faixas: list[dict]  # Lista de faixas aplicadas com preços
    valor_total: Decimal
    valor_por_usuario_medio: Decimal


# ============================================================================
# MUDANÇAS DE PLANO
# ============================================================================

class SolicitarMudancaPlanoRequest(BaseModel):
    """Request para solicitar mudança de plano."""
    plano_destino_id: UUID
    usuarios_destino: int = Field(..., ge=1, description="Quantidade de usuários desejada")
    assinatura_id: Optional[UUID] = Field(None, description="ID da assinatura (se tenant tem múltiplas)")


class SimularMudancaPlanoRequest(BaseModel):
    """Request para simular mudança de plano sem criar solicitação."""
    plano_destino_id: UUID
    usuarios_destino: int = Field(..., ge=1)
    assinatura_id: Optional[UUID] = None


class SimularMudancaPlanoResponse(BaseModel):
    """Resposta da simulação de mudança de plano."""
    tipo_mudanca: str  # UPGRADE_PLANO, DOWNGRADE_PLANO, etc
    plano_atual: dict
    plano_novo: dict
    usuarios_atual: int
    usuarios_novo: int
    valor_atual_mensal: Decimal
    valor_novo_mensal: Decimal
    diferenca_mensal: Decimal
    dias_restantes_ciclo: int
    valor_proporcional: Decimal
    data_proxima_cobranca: datetime
    mensagem: str


class MudancaPlanoResponse(BaseModel):
    """Resposta de mudança de plano solicitada."""
    id: UUID
    tenant_id: UUID
    assinatura_id: UUID
    tipo_mudanca: str
    plano_origem_id: UUID
    plano_destino_id: UUID
    usuarios_origem: int
    usuarios_destino: int
    valor_calculado: Decimal
    valor_proporcional: Decimal
    dias_restantes_ciclo: Optional[int]
    status: str
    cobranca_asaas_id: Optional[str]
    url_pagamento: Optional[str]
    liberado_manualmente: bool
    data_limite_pagamento: Optional[datetime]
    agendado_para: Optional[datetime]
    solicitado_por_usuario_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AprovarMudancaManualmenteRequest(BaseModel):
    """Request para admin aprovar mudança manualmente (sem pagamento imediato)."""
    motivo_liberacao: str = Field(..., min_length=10, description="Justificativa da liberação manual")
    dias_tolerancia_pagamento: int = Field(5, ge=1, le=30, description="Dias para regularizar pagamento")


class AprovarMudancaManualmenteResponse(BaseModel):
    """Resposta da aprovação manual."""
    mudanca_id: UUID
    status: str
    data_limite_pagamento: datetime
    mensagem: str


class CancelarMudancaPlanoRequest(BaseModel):
    """Request para cancelar mudança de plano pendente."""
    motivo: Optional[str] = None


class ListarMudancasPlanoResponse(BaseModel):
    """Lista de mudanças de plano."""
    mudancas: list[MudancaPlanoResponse]
    total: int
    pagina: int
    por_pagina: int


# ============================================================================
# COBRANÇAS ASAAS
# ============================================================================

class CobrancaAsaasResponse(BaseModel):
    """Resposta de cobrança do Asaas."""
    id: UUID
    tenant_id: UUID
    mudanca_plano_id: Optional[UUID]
    assinatura_id: Optional[UUID]
    asaas_charge_id: str
    valor: Decimal
    descricao: str
    status: str
    url_pagamento: Optional[str]
    codigo_barras: Optional[str]
    qrcode_pix: Optional[str]
    data_vencimento: datetime
    data_pagamento: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookAsaasPayload(BaseModel):
    """Payload recebido do webhook do Asaas."""
    event: str  # PAYMENT_RECEIVED, PAYMENT_CONFIRMED, etc
    payment: dict  # Dados do pagamento


# ============================================================================
# HISTÓRICO DE BLOQUEIOS
# ============================================================================

class HistoricoBloqueioResponse(BaseModel):
    """Resposta de histórico de bloqueio."""
    id: UUID
    tenant_id: UUID
    motivo: str
    descricao: Optional[str]
    data_bloqueio: datetime
    data_desbloqueio: Optional[datetime]
    bloqueado_automaticamente: bool
    bloqueado_por_admin_id: Optional[UUID]
    desbloqueado_por_admin_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class DesbloquearTenantRequest(BaseModel):
    """Request para desbloquear tenant."""
    motivo_desbloqueio: str = Field(..., min_length=10)


# ============================================================================
# DASHBOARDS E RELATÓRIOS
# ============================================================================

class ResumoMudancasPlanoResponse(BaseModel):
    """Resumo de mudanças de plano para dashboard."""
    total_upgrades_mes: int
    total_downgrades_mes: int
    total_pendentes: int
    total_bloqueados: int
    receita_upgrades_mes: Decimal
    taxa_conversao_upgrades: float


class PlanoComPricingResponse(BaseModel):
    """Plano completo com matriz de pricing."""
    id: UUID
    nome: str
    descricao: Optional[str]
    modulos_inclusos: list[str]
    limite_usuarios_minimo: int
    limite_usuarios_maximo: Optional[int]
    tem_trial: bool
    dias_trial: int
    is_free: bool
    ativo: bool
    pricing: list[PlanoPricingResponse]
    created_at: datetime

    model_config = {"from_attributes": True}
