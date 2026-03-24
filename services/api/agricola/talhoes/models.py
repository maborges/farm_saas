from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Boolean, JSON, ForeignKey, text
from uuid import UUID
import uuid
from datetime import datetime
from core.database import Base

class Talhao(Base):
    __tablename__ = "talhoes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    fazenda_id: Mapped[UUID] = mapped_column(ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str | None] = mapped_column(String(20))
    area_ha: Mapped[float | None] = mapped_column(Numeric(12, 4))
    area_ha_manual: Mapped[float | None] = mapped_column(Numeric(12, 4))
    
    # Temporário para SQLite (no PostGIS usar Geometry("POLYGON", srid=4326))
    geometria: Mapped[dict | None] = mapped_column(JSON, nullable=True) 
    # Temporário para SQLite (no PostGIS usar Geometry("POINT", srid=4326))
    centroide: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    tipo_solo: Mapped[str | None] = mapped_column(String(50))
    classe_solo: Mapped[str | None] = mapped_column(String(10))
    textura_solo: Mapped[str | None] = mapped_column(String(20))
    relevo: Mapped[str | None] = mapped_column(String(20))
    irrigado: Mapped[bool] = mapped_column(Boolean, default=False)
    sistema_irrigacao: Mapped[str | None] = mapped_column(String(50))
    historico_culturas: Mapped[list] = mapped_column(JSON, default=list)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    # Relacionamentos
    # safras: Mapped[list["Safra"]] = relationship(back_populates="talhao", lazy="noload")
    # analises_solo: Mapped[list["AnaliseSolo"]] = relationship(back_populates="talhao", lazy="noload")

    @property
    def area_efetiva_ha(self) -> float | None:
        """Retorna area_ha (PostGIS) ou area_ha_manual como fallback."""
        return self.area_ha or self.area_ha_manual
