import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class TurnoEnum(str, enum.Enum):
    MANHA = "MANHA"
    TARDE = "TARDE"
    NOITE = "NOITE"
    INTEGRAL = "INTEGRAL"


class ApontamentoUso(Base):
    """
    Diário de bordo: registra uso de equipamento por operador/turno.

    - Atualiza automaticamente horimetro_atual e km_atual do Equipamento.
    - implementos: lista de UUIDs de equipamentos do tipo IMPLEMENTO acoplados
      no turno (armazenados em JSON para evitar tabela M2M desnecessária).
    """
    __tablename__ = "frota_apontamentos_uso"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_equipamentos.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Quem / quando
    operador_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"), nullable=True
    )
    data: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    turno: Mapped[str] = mapped_column(String(10), default="INTEGRAL", nullable=False)

    # Hodômetro / horímetro
    horimetro_inicio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    horimetro_fim: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    km_inicio: Mapped[float | None] = mapped_column(Float, nullable=True)
    km_fim: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Onde / o quê
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True
    )
    talhao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastros_areas_rurais.id", ondelete="SET NULL"),
        nullable=True,
        comment="Talhão onde a operação foi realizada"
    )
    operacao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operacoes_agricolas.id", ondelete="SET NULL"),
        nullable=True,
        comment="Tipo de operação realizada (plantio, pulverização, etc)"
    )

    # Implementos acoplados (lista de UUIDs de Equipamento tipo IMPLEMENTO)
    implementos_ids: Mapped[list | None] = mapped_column(
        JSON, nullable=True, comment="Lista de UUIDs de implementos acoplados no turno"
    )

    # Consumo declarado (opcional — pode ser lançado via Abastecimento)
    combustivel_consumido_l: Mapped[float | None] = mapped_column(Float, nullable=True)

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
