import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Integer, Date, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class ManejoLote(Base):
    """
    Eventos de vida na pecuária: Nascimento, Morte, Pesagem, Vacinação.
    """
    __tablename__ = "pec_manejos_lote"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    lote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_lotes_bovinos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tipo_evento: Mapped[str] = mapped_column(String(50), nullable=False) # NASCIMENTO, MORTE, PESAGEM, VACINACAO, TRANSFERENCIA
    data_evento: Mapped[date] = mapped_column(Date, default=date.today)
    
    quantidade_cabecas: Mapped[int | None] = mapped_column(Integer, nullable=True) # Quantos nasceram / morreram
    peso_total_kg: Mapped[float | None] = mapped_column(Float, nullable=True) # Caso seja evento de pesagem

    # Campos financeiros
    custo_total: Mapped[float | None] = mapped_column(Float, nullable=True)   # VACINACAO / MEDICACAO
    valor_venda: Mapped[float | None] = mapped_column(Float, nullable=True)   # VENDA / ABATE

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
