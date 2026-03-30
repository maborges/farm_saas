"""
Módulo CRM — Gestão de leads e pipeline comercial.

Models:
- PipelineEstagio: Estágios do funil (colunas do Kanban)
- LeadCRM: Prospects e oportunidades comerciais
- AtividadeCRM: Follow-ups, notas e tarefas vinculadas a um lead
"""
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import (
    String, Boolean, DateTime, Text, ForeignKey, JSON,
    Integer, Numeric, Date,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class PipelineEstagio(Base):
    """Estágios do pipeline comercial (colunas do Kanban)."""
    __tablename__ = "crm_pipeline_estagios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    cor: Mapped[str] = mapped_column(String(20), nullable=False, default="#3b82f6")
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class LeadCRM(Base):
    """Lead/prospect comercial."""
    __tablename__ = "crm_leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Dados do lead
    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    empresa: Mapped[str | None] = mapped_column(String(200), nullable=True)
    documento: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Pipeline
    estagio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_pipeline_estagios.id"),
        nullable=False,
        index=True,
    )

    # Comercial
    origem: Mapped[str] = mapped_column(
        String(50), nullable=False, default="manual",
        comment="manual, site, indicacao, evento, social, parceiro"
    )
    valor_estimado: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    plano_interesse: Mapped[str | None] = mapped_column(String(100), nullable=True)
    qtd_fazendas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    qtd_usuarios: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Responsável (admin do backoffice)
    responsavel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_users.id"),
        nullable=True,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="ativo",
        comment="ativo, aprovado, convertido, perdido"
    )
    motivo_perda: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_conversao: Mapped[date | None] = mapped_column(Date, nullable=True)
    tenant_convertido_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True,
        comment="ID do tenant criado após conversão"
    )

    # Notas gerais
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadados
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    estagio: Mapped["PipelineEstagio"] = relationship("PipelineEstagio", lazy="joined")
    atividades: Mapped[list["AtividadeCRM"]] = relationship(
        "AtividadeCRM", back_populates="lead", order_by="desc(AtividadeCRM.created_at)", lazy="selectin"
    )


class AtividadeCRM(Base):
    """Atividades/follow-ups de um lead."""
    __tablename__ = "crm_atividades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tipo: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="ligacao, email, reuniao, nota, tarefa, whatsapp"
    )
    descricao: Mapped[str] = mapped_column(Text, nullable=False)

    # Agendamento
    data_agendada: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    concluida: Mapped[bool] = mapped_column(Boolean, default=False)

    # Quem criou
    admin_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_users.id"),
        nullable=True,
    )
    admin_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    lead: Mapped["LeadCRM"] = relationship("LeadCRM", back_populates="atividades")
