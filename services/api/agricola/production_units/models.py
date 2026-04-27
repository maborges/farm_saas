import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUIDType

from core.database import Base


class ProductionUnit(Base):
    """Unidade econômica/operacional da safra: safra + cultivo + área."""

    __tablename__ = "production_units"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    safra_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cultivo_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("cultivos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    area_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cultivo_area_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("cultivo_areas.id", ondelete="SET NULL"), nullable=True
    )

    percentual_participacao: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=100)
    area_ha: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ATIVA")
    data_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_fim: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))


class StatusConsorcioArea(Base):
    """Read model agregado de participação por tenant/safra/área."""

    __tablename__ = "status_consorcio_area"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    safra_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("safras.id", ondelete="CASCADE"), nullable=False
    )
    area_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False
    )
    soma_participacao: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    qtd_unidades: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    calculado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
