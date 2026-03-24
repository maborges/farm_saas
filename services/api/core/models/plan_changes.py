"""
Modelos para gerenciamento de mudanças de plano (upgrade/downgrade) e pricing dinâmico.

Implementa:
- Matriz de preços por plano e faixa de usuários
- Histórico de solicitações de mudança de plano
- Integração com gateway Asaas
- Bloqueios por inadimplência
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Text, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class PlanoPricing(Base):
    """
    Matriz de preços por plano e faixa de usuários.

    Exemplo:
    - Plano Básico: 1-5 users = R$30/user, 6-10 users = R$25/user
    - Plano Pro: 1-10 users = R$40/user, 11-30 = R$35/user
    """
    __tablename__ = "plano_pricing"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    plano_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planos_assinatura.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Faixa de usuários (ex: 1-10, 11-50, 51-100)
    faixa_inicio: Mapped[int] = mapped_column(Integer, nullable=False, comment="Início da faixa (inclusivo)")
    faixa_fim: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Fim da faixa (inclusivo). NULL = ilimitado")

    # Preço por usuário nesta faixa
    preco_por_usuario_mensal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    preco_por_usuario_anual: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    # Controle
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index('idx_plano_faixa', 'plano_id', 'faixa_inicio', 'faixa_fim'),
    )


class MudancaPlano(Base):
    """
    Registro de solicitações de mudança de plano (upgrade/downgrade).

    Estados possíveis:
    - pendente_pagamento: Aguardando pagamento do cliente
    - liberado_manualmente: Admin liberou sem pagamento (com prazo para regularizar)
    - pago: Pagamento confirmado via webhook
    - aplicado: Mudança efetivada no tenant
    - bloqueado: Tenant bloqueado por inadimplência (liberação manual não paga)
    - cancelado: Solicitação cancelada antes de aplicar
    """
    __tablename__ = "mudancas_plano"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relacionamentos
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    assinatura_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assinaturas_tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Estado anterior
    plano_origem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planos_assinatura.id"),
        nullable=False
    )
    usuarios_origem: Mapped[int] = mapped_column(Integer, nullable=False)

    # Estado desejado
    plano_destino_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planos_assinatura.id"),
        nullable=False
    )
    usuarios_destino: Mapped[int] = mapped_column(Integer, nullable=False)

    # Tipo de mudança
    tipo_mudanca: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="UPGRADE_PLANO, DOWNGRADE_PLANO, UPGRADE_USUARIOS, DOWNGRADE_USUARIOS, UPGRADE_COMPLETO, DOWNGRADE_COMPLETO"
    )

    # Financeiro
    valor_calculado: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Valor a ser cobrado (upgrade) ou creditado (downgrade futuro)"
    )
    valor_proporcional: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Valor proporcional aos dias restantes do ciclo"
    )
    dias_restantes_ciclo: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Gateway de pagamento
    cobranca_asaas_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    url_pagamento: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Status e controle
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pendente_pagamento",
        index=True,
        comment="pendente_pagamento, liberado_manualmente, pago, aplicado, bloqueado, cancelado"
    )

    # Liberação manual (backoffice)
    liberado_manualmente: Mapped[bool] = mapped_column(Boolean, default=False)
    aprovado_por_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_users.id"),
        nullable=True
    )
    motivo_liberacao_manual: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_limite_pagamento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Prazo para regularizar pagamento em caso de liberação manual"
    )

    # Solicitação
    solicitado_por_usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False
    )

    # Aplicação da mudança
    aplicado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    aplicado_por_job: Mapped[bool] = mapped_column(Boolean, default=False)

    # Agendamento (para downgrade)
    agendado_para: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data de aplicação agendada (usado em downgrades)"
    )

    # Auditoria
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index('idx_mudanca_status_tenant', 'status', 'tenant_id'),
        Index('idx_mudanca_agendado', 'agendado_para'),
    )


class CobrancaAsaas(Base):
    """
    Registro de cobranças criadas no gateway Asaas.

    Mantém histórico de todas as interações com o gateway de pagamento.
    """
    __tablename__ = "cobrancas_asaas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relacionamentos
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    mudanca_plano_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mudancas_plano.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    assinatura_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assinaturas_tenant.id", ondelete="SET NULL"),
        nullable=True
    )

    # Dados do Asaas
    asaas_charge_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    asaas_customer_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Financeiro
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)

    # Status da cobrança
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True,
        comment="PENDING, RECEIVED, CONFIRMED, OVERDUE, REFUNDED, RECEIVED_IN_CASH, REFUND_REQUESTED, CHARGEBACK_REQUESTED, CHARGEBACK_DISPUTE, AWAITING_CHARGEBACK_REVERSAL, DUNNING_REQUESTED, DUNNING_RECEIVED, AWAITING_RISK_ANALYSIS"
    )

    # URLs e dados de pagamento
    url_pagamento: Mapped[str | None] = mapped_column(String(500), nullable=True)
    codigo_barras: Mapped[str | None] = mapped_column(String(100), nullable=True)
    qrcode_pix: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Datas
    data_vencimento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_pagamento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Webhook
    ultimo_webhook_recebido: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class HistoricoBloqueio(Base):
    """
    Histórico de bloqueios de tenants por inadimplência.

    Registra quando um tenant foi bloqueado e desbloqueado,
    mantendo auditoria completa.
    """
    __tablename__ = "historico_bloqueios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    mudanca_plano_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mudancas_plano.id", ondelete="SET NULL"),
        nullable=True
    )

    assinatura_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assinaturas_tenant.id", ondelete="SET NULL"),
        nullable=True
    )

    # Tipo de bloqueio
    motivo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="INADIMPLENCIA_MUDANCA_PLANO, INADIMPLENCIA_MENSALIDADE, VIOLACAO_TERMOS, MANUAL"
    )

    # Descrição detalhada
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Datas
    data_bloqueio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_desbloqueio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Responsáveis
    bloqueado_por_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_users.id"),
        nullable=True
    )
    desbloqueado_por_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_users.id"),
        nullable=True
    )

    bloqueado_automaticamente: Mapped[bool] = mapped_column(Boolean, default=False)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index('idx_bloqueio_tenant_data', 'tenant_id', 'data_bloqueio'),
    )
