import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class HistoricoConfiguracao(Base):
    """Audit log de alterações nas configurações do tenant."""
    __tablename__ = "historico_configuracao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    campo_alterado: Mapped[str] = mapped_column(String(100), nullable=False)
    valor_anterior: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    valor_novo: Mapped[dict] = mapped_column(JSON, nullable=False)
    alterado_por: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    alterado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
