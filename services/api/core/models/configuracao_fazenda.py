import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
from core.database import Base


class ConfiguracaoFazenda(Base):
    """Override de configurações do tenant por fazenda específica.

    Ex: fuso horário diferente para fazenda em MT quando tenant é de SP.
    """
    __tablename__ = "configuracao_fazenda"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unidade_produtiva_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("unidades_produtivas.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    # JSONB no PostgreSQL, JSON no SQLite (fallback)
    overrides: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
