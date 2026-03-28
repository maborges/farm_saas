"""
Módulo CRM - Gestão Flexível de Ofertas Comerciais.

Este módulo permite ao backoffice gerenciar ofertas de forma flexível:
- Planos tradicionais (Básico, Profissional, Enterprise)
- Módulos adicionais (add-ons)
- Ofertas personalizadas por lead

Models:
- ModuloOferta: Módulos/serviços que podem ser oferecidos (CRM, Email, Analytics, etc)
- PrecificacaoModulo: Preço de cada módulo
- PlanoComercial: Agregação de módulos em planos
- OfertaPersonalizada: Ofertas customizadas por lead
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    String, Boolean, DateTime, Text, ForeignKey, JSON, Numeric,
    Index, UniqueConstraint, ARRAY,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class ModuloOferta(Base):
    """Módulos/serviços que podem ser oferecidos aos assinantes."""
    __tablename__ = "crm_produtos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificação
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Categorização
    categoria: Mapped[str] = mapped_column(
        String(50), nullable=False, default="core",
        comment="core (CRM, Email, Analytics) | addon (Integrações, API, SLA Premium)"
    )

    # Controle
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    posicao: Mapped[int] = mapped_column(default=0)  # Para ordenação

    # Metadata
    icone: Mapped[str | None] = mapped_column(String(50), nullable=True)  # emoji ou classe icon
    features: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # lista de features do módulo

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PrecificacaoModulo(Base):
    """Preço de um módulo (pode variar por período, tier, etc)."""
    __tablename__ = "crm_precificacao_modulo"
    __table_args__ = (
        UniqueConstraint('modulo_oferta_id', 'vigencia_inicio', name='uq_modulo_vigencia'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    modulo_oferta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_produtos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Preços
    preco_mensal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    preco_anual: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Vigência
    vigencia_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    vigencia_fim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Conditions
    condicoes: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment="Ex: {minimo_usuarios: 5, desconto_volume: 0.1}"
    )

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PlanoComercial(Base):
    """Plano = agregação de módulos (estratégia de bundling)."""
    __tablename__ = "crm_planos_comerciais"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificação
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Estratégia de oferta
    tipo_oferta: Mapped[str] = mapped_column(
        String(50), nullable=False, default="bundle",
        comment="bundle (fixo) | modular (customizável) | misto (base + add-ons)"
    )

    # Módulos inclusos (JSON array de UUIDs)
    modulos_inclusos: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # Preço agregado (se for bundle fixo)
    preco_mensal_padrao: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    preco_anual_padrao: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Metadata comercial
    público_alvo: Mapped[str | None] = mapped_column(String(100), nullable=True)  # "startup", "pme", "enterprise"
    tier: Mapped[int] = mapped_column(default=1)  # 1=básico, 2=pro, 3=enterprise

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    posicao: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class OfertaPersonalizada(Base):
    """Oferta comercial customizada por lead (venda consultiva)."""
    __tablename__ = "crm_ofertas_personalizadas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Vinculação ao lead
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Estratégia de oferta para este lead
    tipo_oferta: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="plano_padrao (um dos planos) | custom_modular (módulos à la carte) | enterprise (totalmente customizado)"
    )

    # Opções oferecidas
    plano_base_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_planos_comerciais.id"),
        nullable=True,
    )

    # Se modular: módulos selecionados (JSON array de UUIDs)
    modulos_selecionados: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=list)

    # Preço final (pode ter desconto)
    preco_total_mensal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    preco_total_anual: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Justificativa comercial
    desconto_percentual: Mapped[float | None] = mapped_column(default=0)
    justificativa: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Vigência
    vigencia_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    vigencia_fim: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="proposta",
        comment="proposta | aceita | rejeitada | expirada"
    )

    observacoes: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # observações, condições especiais

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships (será definido no modelo LeadCRM se necessário)


# Relacionamento será definido na classe LeadCRM
# (adicionar campo ofertas lá se necessário)
