import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


CategoriaOrcamento = (
    "SEMENTE",
    "FERTILIZANTE",
    "DEFENSIVO",
    "COMBUSTIVEL",
    "MAO_DE_OBRA",
    "SERVICO",
    "SEGURO",
    "OUTROS",
)


class ItemOrcamentoSafra(Base):
    """
    Item do orçamento previsto de uma safra (linha a linha).
    Alimenta o comparativo previsto × realizado do módulo A1.
    """
    __tablename__ = "agricola_orcamento_itens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    safra_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cultivo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cultivos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    production_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production_units.id", ondelete="SET NULL"), nullable=True
    )

    # SEMENTE, FERTILIZANTE, DEFENSIVO, COMBUSTIVEL, MAO_DE_OBRA, SERVICO, SEGURO, OUTROS
    categoria: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)

    quantidade: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False, comment="kg, L, sc, d/H, ha, etc.")
    custo_unitario: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    custo_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    # Ordem de exibição dentro da categoria
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
