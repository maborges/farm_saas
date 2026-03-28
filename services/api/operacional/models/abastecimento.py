import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class LocalAbastecimento(str, enum.Enum):
    INTERNO = "INTERNO"   # tanque/posto da fazenda
    EXTERNO = "EXTERNO"   # posto de combustível externo


class Abastecimento(Base):
    """
    Registro de abastecimento por equipamento.

    Alimenta custo operacional de combustível e índices de consumo (l/h, km/l).
    Atualiza horimetro_atual / km_atual do Equipamento via trigger no service.
    """
    __tablename__ = "frota_abastecimentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_equipamentos.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    data: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    operador_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"), nullable=True
    )

    # Leitura no momento do abastecimento
    horimetro_na_data: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    km_na_data: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Combustível
    tipo_combustivel: Mapped[str] = mapped_column(String(20), nullable=False, default="DIESEL")
    litros: Mapped[float] = mapped_column(Float, nullable=False)
    preco_litro: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    custo_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Tanque cheio? (útil para calcular consumo real entre abastecimentos)
    tanque_cheio: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Origem
    local: Mapped[str] = mapped_column(String(20), default="INTERNO", nullable=False)
    fornecedor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"),
        nullable=True,
        comment="Fornecedor do combustível (quando abastecimento externo)"
    )
    nota_fiscal: Mapped[str | None] = mapped_column(String(50), nullable=True)

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
