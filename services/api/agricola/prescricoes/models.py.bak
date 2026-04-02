from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Date, Text, ForeignKey, text, JSON, Numeric
from uuid import UUID
import uuid
from datetime import datetime, date
from core.database import Base

class PrescricaoVRA(Base):
    __tablename__ = "prescricoes_vra"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False)
    
    tipo_operacao: Mapped[str] = mapped_column(String(50)) # ADUBAÇÃO, SEMEADURA, DEFENSIVO
    insumo: Mapped[str] = mapped_column(String(100))
    
    # Dados da grade de prescrição (Variable Rate Application)
    # No SQLite/JSON guardamos os polígonos de taxa
    # Ex: [{"polygon": ..., "rate": 150.0, "unit": "KG/HA"}]
    camadas_json: Mapped[list[dict]] = mapped_column(JSON, default=list)
    
    area_total_ha: Mapped[float | None] = mapped_column(Numeric(12, 2))
    quantidade_total_estimada: Mapped[float | None] = mapped_column(Numeric(12, 2))
    
    data_prescricao: Mapped[date] = mapped_column(Date, default=date.today)
    
    arquivo_original_url: Mapped[str | None] = mapped_column(String(255)) # Link para shapefile/kml
    
    status: Mapped[str] = mapped_column(String(20), default="PENDENTE") # PENDENTE, EXECUTADA, CANCELADA
    
    observacoes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)
