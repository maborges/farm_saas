import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUIDType

from core.database import Base


class SafraCenario(Base):
    __tablename__ = "safra_cenarios"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    safra_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="CUSTOM")
    eh_base: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ATIVO")
    unidade_medida_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("unidades_medida.id", ondelete="RESTRICT"), nullable=True
    )

    produtividade_default: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    preco_default: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    custo_ha_default: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    fator_custo_pct: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)

    area_total_ha: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    receita_bruta_total: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    custo_total: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    margem_contribuicao_total: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    depreciacao_total: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    ir_aliquota_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    ir_valor_total: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    resultado_liquido_total: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    ponto_equilibrio_sc_ha: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)

    calculado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    unidades: Mapped[list["SafraCenarioUnidade"]] = relationship(
        back_populates="cenario", cascade="all, delete-orphan", lazy="selectin"
    )


class SafraCenarioUnidade(Base):
    __tablename__ = "safra_cenarios_unidades"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cenario_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("safra_cenarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    production_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("production_units.id", ondelete="CASCADE"), nullable=False
    )
    unidade_medida_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("unidades_medida.id", ondelete="RESTRICT"), nullable=True
    )

    cultivo_nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area_nome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    area_ha: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    percentual_participacao: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    produtividade_simulada: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    preco_simulado: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    custo_total_simulado_ha: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    custo_base_fonte: Mapped[str | None] = mapped_column(String(20), nullable=True)

    produtividade_efetiva: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    preco_efetivo: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    custo_ha_efetivo: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    producao_total: Mapped[float | None] = mapped_column(Numeric(14, 3), nullable=True)
    receita_bruta: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    custo_total: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    margem_contribuicao: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    margem_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    depreciacao_ha: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    depreciacao_total: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    ir_valor: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    resultado_liquido: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    ponto_equilibrio: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    cenario: Mapped["SafraCenario"] = relationship(back_populates="unidades")
