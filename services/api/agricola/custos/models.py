import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUIDType

from core.database import Base


class CostAllocation(Base):
    """Agricultural cost allocation by ProductionUnit."""

    __tablename__ = "cost_allocations"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    production_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("production_units.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    operation_execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("operacoes_execucoes.id", ondelete="SET NULL"), nullable=True
    )
    inventory_movement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("estoque_movimentos.id", ondelete="SET NULL"), nullable=True
    )
    fin_rateio_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("fin_rateios.id", ondelete="SET NULL"), nullable=True
    )
    cost_category: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")
    allocation_date: Mapped[date] = mapped_column(Date, nullable=False)
    allocation_method: Mapped[str] = mapped_column(String(24), nullable=False, default="DIRECT")
    allocation_basis: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
