import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class Rateio(Base):
    """
    Conecta uma conta a pagar/paga (R$) a um centro de custo ou talhão/safra (Hectares)
    """
    __tablename__ = "fin_rateios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    despesa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fin_despesas.id", ondelete="CASCADE"), nullable=False
    )

    # Entidades de Destino do Custo
    safra_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("safras.id", ondelete="SET NULL"), nullable=True
    )
    talhao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("talhoes.id", ondelete="SET NULL"), nullable=True
    )
    
    valor_rateado: Mapped[float] = mapped_column(Float, nullable=False)
    percentual: Mapped[float] = mapped_column(Float, nullable=False) # 1 a 100%

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
