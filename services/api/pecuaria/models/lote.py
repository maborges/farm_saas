import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class LoteBovino(Base):
    """
    Agrupamento de Animais na Pecuária.
    """
    __tablename__ = "pec_lotes_bovinos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    fazenda_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    piquete_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_piquetes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    identificacao: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False) # Ex: Bezerros, Novilhas, Vacas, Touros
    raca: Mapped[str] = mapped_column(String(50), nullable=False)
    
    quantidade_cabecas: Mapped[int] = mapped_column(Integer, default=0)
    peso_medio_kg: Mapped[float] = mapped_column(Float, default=0.0)
    
    data_formacao: Mapped[date] = mapped_column(Date, default=date.today)
    
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
