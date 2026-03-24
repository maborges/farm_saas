import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base

class Fazenda(Base):
    __tablename__ = "fazendas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # Campo essencial para a barreira RLS
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Grupo de fazendas (permite agrupar fazendas com assinatura compartilhada)
    grupo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grupos_fazendas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Grupo ao qual esta fazenda pertence (NULL = sem grupo)"
    )

    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True)
    inscricao_estadual: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Medidas
    area_total_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    coordenadas_sede: Mapped[str | None] = mapped_column(String(100), nullable=True) # Ex: lat,long
    
    # Suporte a polígono (GeoJSON) - Limite da propriedade
    geometria: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="fazendas")
