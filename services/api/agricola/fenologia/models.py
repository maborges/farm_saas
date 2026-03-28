import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, text, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class FenologiaEscala(Base):
    """Catálogo de estágios fenológicos por cultura. is_system=True = padrão do AgroSaaS."""
    __tablename__ = "fenologia_escalas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    cultura: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))


class SafraTalhaoGrupo(Base):
    """Agrupamento de talhões dentro de uma safra para manejo coletivo."""
    __tablename__ = "safra_talhao_grupos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    safra_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    cor: Mapped[str | None] = mapped_column(String(7), nullable=True)   # hex: #3B82F6
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    itens: Mapped[list["SafraTalhaoGrupoItem"]] = relationship(
        back_populates="grupo", lazy="noload", cascade="all, delete-orphan"
    )


class SafraTalhaoGrupoItem(Base):
    """Talhão dentro de um grupo da safra."""
    __tablename__ = "safra_talhao_grupo_itens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    grupo_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("safra_talhao_grupos.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    grupo: Mapped["SafraTalhaoGrupo"] = relationship(back_populates="itens", lazy="noload")


class SafraFenologiaRegistro(Base):
    """Registro de observação fenológica — série temporal por talhão (ou grupo de talhões)."""
    __tablename__ = "safra_fenologia_registros"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    safra_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    escala_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("fenologia_escalas.id", ondelete="RESTRICT"), nullable=False)
    grupo_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safra_talhao_grupos.id", ondelete="SET NULL"), nullable=True, index=True)

    data_observacao: Mapped[date] = mapped_column(Date, nullable=False)
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(UUID, nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))

    escala: Mapped["FenologiaEscala"] = relationship(lazy="joined")
