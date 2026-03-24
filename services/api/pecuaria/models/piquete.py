import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class Piquete(Base):
    """
    Subdivisão da fazenda destinada ao pastejo (semelhante ao Talhão).
    """
    __tablename__ = "pec_piquetes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    fazenda_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    area_ha: Mapped[float] = mapped_column(Float, nullable=False)
    capacidade_suporte_ua: Mapped[float | None] = mapped_column(Float, nullable=True) # Unidades Animais suportadas
    
    poligono_geojson: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
