import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
from core.cadastros.equipamentos.models import Equipamento as Maquinario  # backwards compat


class PlanoManutencao(Base):
    """Regras de periodicidade de manutenção (ex: a cada 250h ou 10.000km)."""
    __tablename__ = "frota_planos_manutencao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_equipamentos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    descricao: Mapped[str] = mapped_column(String(150), nullable=False)
    frequencia_horas: Mapped[float | None] = mapped_column(Float, nullable=True)
    frequencia_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    ultimo_registro_horas: Mapped[float | None] = mapped_column(Float, default=0.0)
    ultimo_registro_km: Mapped[float | None] = mapped_column(Float, default=0.0)


class OrdemServico(Base):
    """Workflow de manutenção de oficina."""
    __tablename__ = "frota_ordens_servico"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_equipamentos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    numero_os: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    tipo: Mapped[str] = mapped_column(String(30), comment="PREVENTIVA | CORRETIVA | REVISAO")
    status: Mapped[str] = mapped_column(String(20), default="ABERTA", comment="ABERTA | EM_EXECUCAO | CONCLUIDA | CANCELADA")

    descricao_problema: Mapped[str] = mapped_column(String(500))
    diagnostico_tecnico: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    data_abertura: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    data_conclusao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    horimetro_na_abertura: Mapped[float] = mapped_column(Float, default=0.0)
    km_na_abertura: Mapped[float | None] = mapped_column(Float, nullable=True)

    tecnico_responsavel: Mapped[str | None] = mapped_column(String(100), nullable=True)
    custo_total_pecas: Mapped[float] = mapped_column(Float, default=0.0)
    custo_mao_obra: Mapped[float] = mapped_column(Float, default=0.0)

    itens: Mapped[list["ItemOrdemServico"]] = relationship(back_populates="os", lazy="noload", cascade="all, delete-orphan")


class ItemOrdemServico(Base):
    """Peças e insumos consumidos na OS — baixa o estoque de almoxarifado."""
    __tablename__ = "frota_os_itens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    os_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("frota_ordens_servico.id", ondelete="CASCADE"), nullable=False
    )
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_produtos.id"), nullable=False
    )

    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    preco_unitario_na_data: Mapped[float] = mapped_column(Float, default=0.0)

    os: Mapped["OrdemServico"] = relationship(back_populates="itens", lazy="noload")


class RegistroManutencao(Base):
    """Histórico de manutenções realizadas num equipamento."""
    __tablename__ = "frota_registros_manutencao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_equipamentos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    os_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("frota_ordens_servico.id"), nullable=True
    )

    data_realizacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    tipo: Mapped[str] = mapped_column(String(30))
    descricao: Mapped[str] = mapped_column(String(500))
    custo_total: Mapped[float] = mapped_column(Float, default=0.0)

    horimetro_na_data: Mapped[float] = mapped_column(Float, default=0.0)
    km_na_data: Mapped[float | None] = mapped_column(Float, nullable=True)

    tecnico_responsavel: Mapped[str | None] = mapped_column(String(100), nullable=True)
