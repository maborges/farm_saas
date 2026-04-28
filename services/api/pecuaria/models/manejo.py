import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, DateTime, Float, ForeignKey, Integer, Date, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class ManejoLote(Base):
    """
    Eventos de manejo coletivo por lote (ex: pesagem de grupo, vacinação em massa).

    Para eventos individuais por animal use pecuaria.animal.models.EventoAnimal.
    Para movimentação de animais entre lotes use EventoAnimal tipo TRANSFERENCIA_LOTE.
    """
    __tablename__ = "pec_manejos_lote"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_lotes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tipo_evento: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="NASCIMENTO | MORTE | PESAGEM | VACINACAO | TRANSFERENCIA | VENDA | ABATE"
    )
    data_evento: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    quantidade_cabecas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    peso_total_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    produto_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_produtos.id", ondelete="SET NULL"), nullable=True, index=True,
        comment="Produto/insumo utilizado no evento (VACINACAO, MEDICACAO)"
    )

    custo_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_venda: Mapped[float | None] = mapped_column(Float, nullable=True)

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
