import uuid
from datetime import date
from sqlalchemy import String, Date, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class ModuleUsageStat(Base):
    """Contador diário de acessos por tenant+módulo. Incrementado via require_module()."""
    __tablename__ = "module_usage_stats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    dia: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint("tenant_id", "module_id", "dia", name="uq_module_usage_per_day"),
        Index("ix_module_usage_tenant_dia", "tenant_id", "dia"),
    )
