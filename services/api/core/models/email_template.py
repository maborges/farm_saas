import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class EmailTemplate(Base):
    """Templates de e-mail reutilizáveis."""
    __tablename__ = "email_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Conteúdo
    assunto: Mapped[str] = mapped_column(String(255), nullable=False)
    corpo_html: Mapped[str] = mapped_column(Text, nullable=False)
    corpo_texto: Mapped[str] = mapped_column(Text, nullable=False)

    # Variáveis disponíveis (JSON)
    variaveis: Mapped[dict] = mapped_column(JSON, default=list)
    # Ex: ["nome_usuario", "tenant_nome", "data_vencimento"]

    # Configuração
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    # transacional, marketing, sistema
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Auditoria
    editado_por_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class EmailLog(Base):
    """Log de e-mails enviados."""
    __tablename__ = "email_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Template (pode ser None se enviado manualmente)
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_templates.id"),
        nullable=True
    )
    template_codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Destinatário
    destinatario_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    destinatario_nome: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=True
    )

    # Conteúdo enviado
    assunto: Mapped[str] = mapped_column(String(255), nullable=False)
    corpo_html: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # enviado, falha, pendente
    erro_mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Provider
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Tracking
    aberto: Mapped[bool] = mapped_column(Boolean, default=False)
    data_abertura: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    clicado: Mapped[bool] = mapped_column(Boolean, default=False)
    data_clique: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auditoria
    enviado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
