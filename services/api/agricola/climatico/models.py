from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Date, ForeignKey, text
from uuid import UUID
import uuid
from datetime import datetime, date
from core.database import Base

class RegistroClima(Base):
    __tablename__ = "registros_clima"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    fazenda_id: Mapped[UUID] = mapped_column(ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)

    data_registro: Mapped[date] = mapped_column(Date, nullable=False)
    
    precipitacao_mm: Mapped[float | None] = mapped_column(Numeric(6, 2))
    temp_max_c: Mapped[float | None] = mapped_column(Numeric(5, 2))
    temp_min_c: Mapped[float | None] = mapped_column(Numeric(5, 2))
    temp_media_c: Mapped[float | None] = mapped_column(Numeric(5, 2))
    umidade_rel_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    evapotranspiracao_mm: Mapped[float | None] = mapped_column(Numeric(6, 2))
    
    gdu_calculado: Mapped[float | None] = mapped_column(Numeric(5, 2)) # Graus-Dia Acumulados diário (Base 10 graus ex)
    
    fonte: Mapped[str] = mapped_column(String(50), default="ESTACAO_LOCAL") # ou OPEN_METEO

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
