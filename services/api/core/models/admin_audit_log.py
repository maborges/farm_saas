import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class AdminAuditLog(Base):
    """Log de auditoria de ações administrativas."""
    __tablename__ = "admin_audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Quem fez a ação
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_users.id"),
        nullable=False,
        index=True
    )
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # O que foi feito
    acao: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Ex: tenant.impersonate, subscription.suspend, ticket.assign

    entidade: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # tenant, subscription, ticket, etc

    entidade_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Detalhes
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_anteriores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dados_novos: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Contexto
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
