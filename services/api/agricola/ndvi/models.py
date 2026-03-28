from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Date, ForeignKey, text, Uuid
from uuid import UUID
import uuid
from datetime import datetime, date
from core.database import Base

class ImagemNDVI(Base):
    __tablename__ = "imagens_ndvi"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)

    data_captura: Mapped[date] = mapped_column(Date, nullable=False)
    cobertura_nuvens_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    
    indice_medio: Mapped[float | None] = mapped_column(Numeric(4, 3))
    indice_minimo: Mapped[float | None] = mapped_column(Numeric(4, 3))
    indice_maximo: Mapped[float | None] = mapped_column(Numeric(4, 3))
    
    url_imagem_colorida: Mapped[str | None] = mapped_column(String(500))
    url_raw_data: Mapped[str | None] = mapped_column(String(500)) # GeoTIFF no S3/MinIO
    satelite: Mapped[str] = mapped_column(String(50), default='Sentinel-2')

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
