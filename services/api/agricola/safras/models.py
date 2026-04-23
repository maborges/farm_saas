import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, Boolean, Integer, Date, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base

if TYPE_CHECKING:
    from agricola.cultivos.models import Cultivo


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
    """Representa o período agrícola (safra) — contexto de negócio superior.

    Os cultivos (unidades de negócio) estão aninhados dentro de uma safra.
    Campos específicos de cultura (cultura, cultivar, datas, produtividade, preço)
    foram movidos para a entidade Cultivo.
    """
    __tablename__ = "safras"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    ano_safra: Mapped[str] = mapped_column(String(10), nullable=False)
    cultura: Mapped[str | None] = mapped_column(String(100), nullable=True)  # legado: cultura principal
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='PLANEJADA')
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    # Relacionamentos
    cultivos: Mapped[list["Cultivo"]] = relationship(
        foreign_keys="[Cultivo.safra_id]",
        back_populates="safra",
        lazy="noload",
        cascade="all, delete-orphan"
    )
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
    
    # Bypass mechanism
    forcou_avanco: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    justificativa_avanco: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))

    safra: Mapped["Safra"] = relationship(back_populates="fase_historico", lazy="noload")
