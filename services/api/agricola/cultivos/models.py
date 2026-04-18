import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Boolean, Integer, Date, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class Cultivo(Base):
    """Representa um cultivo específico dentro de uma safra.

    Um cultivo é a unidade de negócio — toda lógica de operação, custo,
    produção e resultado está centrada no cultivo, nunca no talhão ou safra.
    """
    __tablename__ = "cultivos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)

    # Identificação do cultivo
    cultura: Mapped[str] = mapped_column(String(50), nullable=False)
    cultivar_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("cadastros_culturas.id", ondelete="SET NULL"), nullable=True)
    cultivar_nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    commodity_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("cadastros_commodities.id", ondelete="SET NULL"), nullable=True)

    # Características técnicas
    sistema_plantio: Mapped[str | None] = mapped_column(String(30), nullable=True)
    populacao_prevista: Mapped[int | None] = mapped_column(Integer, nullable=True)
    populacao_real: Mapped[int | None] = mapped_column(Integer, nullable=True)
    espacamento_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Datas de plantio e colheita
    data_plantio_prevista: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_plantio_real: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_colheita_prevista: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_colheita_real: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Indicadores de desempenho
    produtividade_meta_sc_ha: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    produtividade_real_sc_ha: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    preco_venda_previsto: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    custo_previsto_ha: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    custo_realizado_ha: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Status e observações
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='PLANEJADO')
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    # Relacionamentos
    areas: Mapped[list["CultivoArea"]] = relationship(
        back_populates="cultivo", lazy="noload", cascade="all, delete-orphan"
    )


class CultivoArea(Base):
    """Subdivisão lógica de um cultivo vinculando-o a um talhão específico.

    Permite que um cultivo ocupe uma ou mais áreas (talhões) de forma aninhada,
    ou que um talhão tenha múltiplos cultivos simultâneos com áreas distintas.
    """
    __tablename__ = "cultivo_areas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    cultivo_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cultivos.id", ondelete="CASCADE"), nullable=False, index=True)
    area_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)

    # Área ocupada por este cultivo neste talhão (em hectares)
    area_ha: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))

    # Relacionamentos
    cultivo: Mapped["Cultivo"] = relationship(back_populates="areas", lazy="noload")
