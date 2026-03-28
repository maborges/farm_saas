from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Date, ForeignKey, text, Uuid
from uuid import UUID
import uuid
from datetime import datetime, date
from core.database import Base

class AnaliseSolo(Base):
    __tablename__ = "analises_solo"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)

    data_coleta: Mapped[date] = mapped_column(Date, nullable=False)
    laboratorio: Mapped[str | None] = mapped_column(String(150))
    codigo_amostra: Mapped[str | None] = mapped_column(String(50))
    profundidade_cm: Mapped[int | None] = mapped_column(Numeric(3, 0)) # Ex: 20 para 0-20cm

    # Fisicas
    argila_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    silte_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    areia_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))

    # Quimicas
    ph_agua: Mapped[float | None] = mapped_column(Numeric(4, 2))
    ph_cacl2: Mapped[float | None] = mapped_column(Numeric(4, 2))
    materia_organica_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    
    fosforo_p: Mapped[float | None] = mapped_column(Numeric(8, 2)) # mg/dm3
    potassio_k: Mapped[float | None] = mapped_column(Numeric(8, 2)) # mg/dm3
    calcio_ca: Mapped[float | None] = mapped_column(Numeric(8, 2)) # cmolc/dm3
    magnesio_mg: Mapped[float | None] = mapped_column(Numeric(8, 2)) # cmolc/dm3
    aluminio_al: Mapped[float | None] = mapped_column(Numeric(8, 2)) # cmolc/dm3
    hidrogenio_al_hal: Mapped[float | None] = mapped_column(Numeric(8, 2)) # cmolc/dm3
    
    # Calculados (Podem ser informados ou gerados pelo backend/banco)
    ctc: Mapped[float | None] = mapped_column(Numeric(8, 2)) # Capacidade de Troca Cationica
    v_pct: Mapped[float | None] = mapped_column(Numeric(5, 2)) # Saturacao por Bases

    arquivo_laudo_url: Mapped[str | None] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)
