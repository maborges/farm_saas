import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Boolean, Integer, Date, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


# Fases válidas do ciclo de vida da safra (em ordem)
SAFRA_FASES_ORDEM = [
    "PLANEJADA",
    "PREPARO_SOLO",
    "PLANTIO",
    "DESENVOLVIMENTO",
    "COLHEITA",
    "POS_COLHEITA",
    "ENCERRADA",
]

# Mapa de transições permitidas
SAFRA_TRANSICOES = {
    "PLANEJADA":     ["PREPARO_SOLO", "CANCELADA"],
    "PREPARO_SOLO":  ["PLANTIO", "CANCELADA"],
    "PLANTIO":       ["DESENVOLVIMENTO", "CANCELADA"],
    "DESENVOLVIMENTO": ["COLHEITA", "CANCELADA"],
    "COLHEITA":      ["POS_COLHEITA", "CANCELADA"],
    "POS_COLHEITA":  ["ENCERRADA"],
    "ENCERRADA":     [],
    "CANCELADA":     [],
}


class Safra(Base):
    __tablename__ = "safras"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)
    
    ano_safra: Mapped[str] = mapped_column(String(10), nullable=False)
    cultura: Mapped[str] = mapped_column(String(50), nullable=False)
    cultivar_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("cadastros_culturas.id", ondelete="SET NULL"), nullable=True)
    cultivar_nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    commodity_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("cadastros_commodities.id", ondelete="SET NULL"), nullable=True)
    sistema_plantio: Mapped[str | None] = mapped_column(String(30), nullable=True)
    
    data_plantio_prevista: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_plantio_real: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_colheita_prevista: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_colheita_real: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    populacao_prevista: Mapped[int | None] = mapped_column(Integer, nullable=True)
    populacao_real: Mapped[int | None] = mapped_column(Integer, nullable=True)
    espacamento_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area_plantada_ha: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    
    produtividade_meta_sc_ha: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    produtividade_real_sc_ha: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    preco_venda_previsto: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    custo_previsto_ha: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    custo_realizado_ha: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='PLANEJADA')
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    # Relacionamentos
    # talhao: Mapped["Talhao"] = relationship(back_populates="safras", lazy="noload")
    fase_historico: Mapped[list["SafraFaseHistorico"]] = relationship(
        back_populates="safra", lazy="noload", cascade="all, delete-orphan"
    )


class SafraTalhao(Base):
    """Associação N:N entre Safra e talhões (AreaRural).
    O campo talhao_id em Safra permanece como talhão primário (compat. legado).
    """
    __tablename__ = "safra_talhoes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    area_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)
    area_ha: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))


class SafraFaseHistorico(Base):
    __tablename__ = "safra_fase_historico"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    safra_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    fase_anterior: Mapped[str | None] = mapped_column(String(30), nullable=True)
    fase_nova: Mapped[str] = mapped_column(String(30), nullable=False)
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(UUID, nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_fase: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))

    safra: Mapped["Safra"] = relationship(back_populates="fase_historico", lazy="noload")
