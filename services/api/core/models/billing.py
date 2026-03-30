import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, JSON, Text, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class PlanoAssinatura(Base):
    """Pacotes de produtos (módulos) comercializáveis."""
    __tablename__ = "planos_assinatura"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    
    # Ex: ["CORE", "A1", "F1", "P1"]
    modulos_inclusos: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Limites de usuários (para pricing dinâmico)
    limite_usuarios_minimo: Mapped[int] = mapped_column(default=1, comment="Quantidade mínima de usuários para este plano")
    limite_usuarios_maximo: Mapped[int | None] = mapped_column(default=None, comment="Quantidade máxima de usuários. NULL = ilimitado")

    # DEPRECATED: mantido por compatibilidade, use plano_pricing para cálculo real
    limite_usuarios: Mapped[int] = mapped_column(default=5, comment="DEPRECATED: valor de referência apenas")
    limite_hectares: Mapped[float | None] = mapped_column(Numeric(10,2))
    
    preco_mensal: Mapped[float] = mapped_column(Numeric(10,2), default=0.0)
    preco_anual: Mapped[float] = mapped_column(Numeric(10,2), default=0.0)
    
    # Tier do plano — governa profundidade de funcionalidades em todos os módulos
    # BASICO: funcionalidades simples | PROFISSIONAL: rateio/cenários | PREMIUM: IA/benchmarking
    plan_tier: Mapped[str] = mapped_column(
        String(20),
        default="BASICO",
        comment="BASICO, PROFISSIONAL ou PREMIUM — define profundidade financeira"
    )

    # Limites quantitativos (-1 = ilimitado)
    max_fazendas: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment="Máximo de fazendas. -1 = ilimitado"
    )
    max_categorias_plano: Mapped[int] = mapped_column(
        Integer,
        default=10,
        comment="Máximo de categorias personalizáveis no plano de contas. -1 = ilimitado"
    )

    # Trial
    tem_trial: Mapped[bool] = mapped_column(Boolean, default=True)
    dias_trial: Mapped[int] = mapped_column(default=15)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)

    # Melhorar descrição
    descricao_marketing: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Destacar plano
    destaque: Mapped[bool] = mapped_column(Boolean, default=False)
    ordem: Mapped[int] = mapped_column(default=0)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Controle de canal de comercialização (independentes entre si)
    disponivel_site: Mapped[bool] = mapped_column(Boolean, default=False, comment="Visível no checkout/landing público")
    disponivel_crm: Mapped[bool] = mapped_column(Boolean, default=True, comment="Visível no CRM para conversão de leads e ofertas personalizadas")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AssinaturaTenant(Base):
    """
    Assinatura de um tenant ou grupo de fazendas.

    Um tenant pode ter múltiplas assinaturas:
    - 1 assinatura PRINCIPAL (todas as fazendas)
    - N assinaturas GRUPO (por grupo de fazendas)
    - N assinaturas ADICIONAL (add-ons)
    """
    __tablename__ = "assinaturas_tenant"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant proprietário (removido unique=True para permitir múltiplas assinaturas)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # Mudado de unique=True para index=True
    )

    plano_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planos_assinatura.id"),
        nullable=False
    )

    # Grupo de fazendas (se NULL, assinatura vale para todas as fazendas)
    grupo_fazendas_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grupos_fazendas.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Se NULL, assinatura principal do tenant. Se preenchido, assinatura específica do grupo."
    )

    # Tipo de assinatura
    tipo_assinatura: Mapped[str] = mapped_column(
        String(20),
        default="PRINCIPAL",
        comment="PRINCIPAL (tenant inteiro), GRUPO (grupo específico), ADICIONAL (add-on de módulos)"
    )

    ciclo_pagamento: Mapped[str] = mapped_column(String(20), default="MENSAL") # MENSAL, ANUAL

    # Quantidade de usuários contratados (para pricing dinâmico)
    usuarios_contratados: Mapped[int] = mapped_column(Integer, default=5, comment="Quantidade de usuários simultâneos contratados")

    status: Mapped[str] = mapped_column(String(30), default="PENDENTE") # PENDENTE, PENDENTE_PAGAMENTO, ATIVA, SUSPENSA, CANCELADA, BLOQUEADA

    # Stripe
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    data_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    data_proxima_renovacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    data_bloqueio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Data do último bloqueio")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Fatura(Base):
    """Faturas e Comprovantes de Pagamento (Revisados pelo Financeiro Interno)."""
    __tablename__ = "faturas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assinatura_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assinaturas_tenant.id", ondelete="CASCADE"), nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    valor: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    data_vencimento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    status: Mapped[str] = mapped_column(String(30), default="ABERTA") # ABERTA, EM_ANALISE, PAGA, REJEITADA, VENCIDA
    
    # Comprovante (Envio manual pelo Produtor)
    url_comprovante: Mapped[str | None] = mapped_column(String(500))
    data_envio_comprovante: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Revisão pelo Operador Financeiro AgroSaaS (is_superuser do modulo de usuarios)
    justificativa_rejeicao: Mapped[str | None] = mapped_column(Text)
    operador_revisao_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    data_aprovacao_rejeicao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
