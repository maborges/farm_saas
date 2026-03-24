from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Boolean, Date, JSON, Text, ForeignKey, text, ARRAY, Uuid
from uuid import UUID
import uuid
from datetime import datetime, date
from core.database import Base

class MonitoramentoPragas(Base):
    __tablename__ = "monitoramento_pragas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("talhoes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    data_avaliacao: Mapped[date] = mapped_column(Date, nullable=False)

    tipo: Mapped[str | None] = mapped_column(String(20)) # PRAGA, DOENCA, PLANTA_DANINHA
    nome_cientifico: Mapped[str | None] = mapped_column(String(100))
    nome_popular: Mapped[str | None] = mapped_column(String(100))

    nivel_infestacao: Mapped[float | None] = mapped_column(Numeric(8, 4))
    unidade_medida: Mapped[str | None] = mapped_column(String(30))
    nde_cultura: Mapped[float | None] = mapped_column(Numeric(8, 4))
    atingiu_nde: Mapped[bool] = mapped_column(Boolean, default=False)

    fotos: Mapped[list[str]] = mapped_column(JSON, default=list)
    pontos_coleta: Mapped[list[dict] | None] = mapped_column(JSON, default=list)
    diagnostico_ia: Mapped[dict | None] = mapped_column(JSON)
    
    tecnico_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True) # ForeignKey to usuarios
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    observacoes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
