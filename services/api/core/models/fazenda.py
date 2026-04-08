import uuid
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class Fazenda(Base):
    __tablename__ = "fazendas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Campo essencial para a barreira RLS
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Grupo de fazendas — obrigatório (Model B: acesso via grupo)
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grupos_fazendas.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Grupo ao qual esta fazenda pertence (obrigatório)"
    )

    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cpf_cnpj: Mapped[str | None] = mapped_column(String(18), nullable=True, comment="CPF (11 dígitos) ou CNPJ (14 dígitos) do proprietário")
    inscricao_estadual: Mapped[str | None] = mapped_column(String(50), nullable=True)
    codigo_car: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Código CAR no formato SICAR: UF-XXXXXXXXXXXXXXX")
    nirf: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="Número do Imóvel na Receita Federal")
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True, comment="UF (estado) da propriedade")
    municipio: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Áreas (Numeric para precisão fiscal — ITR, CAR)
    area_total_ha: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    area_aproveitavel_ha: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    area_app_ha: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True, comment="Área de Preservação Permanente")
    area_rl_ha: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True, comment="Área de Reserva Legal")

    coordenadas_sede: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Polígono GeoJSON da propriedade
    geometria: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

