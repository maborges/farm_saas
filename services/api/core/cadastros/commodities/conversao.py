"""
ConversaoUnidade — fatores de conversão entre unidades por commodity.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Float, ForeignKey, UniqueConstraint, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class ConversaoUnidade(Base):
    """
    Tabela de fatores de conversão para unidades secundárias por commodity.

    Exemplo:
        commodity_id = SOJA, origem = "SACA_60KG", destino = "TONELADA", fator = 0.06
        → 100 sacas soja × 0.06 = 6.0 toneladas

        commodity_id = ALGODAO, origem = "SACA_60KG", destino = "KG", fator = 15.0
        → 100 sacas algodão × 15.0 = 1500 kg (não 6000!)
    """
    __tablename__ = "cadastros_conversao_unidades"
    __table_args__ = (
        UniqueConstraint(
            "commodity_id", "unidade_origem", "unidade_destino",
            name="uq_conversao_commodity_origem_destino",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commodity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_commodities.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    unidade_origem: Mapped[str] = mapped_column(String(20), nullable=False)
    unidade_destino: Mapped[str] = mapped_column(String(20), nullable=False)
    fator: Mapped[float] = mapped_column(Float, nullable=False, comment="destino = origem × fator")
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    commodity: Mapped["Commodity"] = relationship(back_populates="conversoes", lazy="noload")

    def converter(self, quantidade_origem: float) -> float:
        """Aplica a conversão."""
        return quantidade_origem * self.fator
