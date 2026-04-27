import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, Numeric, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUIDType

from core.database import Base


class UnidadeMedida(Base):
    __tablename__ = "unidades_medida"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    codigo: Mapped[str] = mapped_column(String(16), nullable=False)
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    dimensao: Mapped[str] = mapped_column(String(24), nullable=False)
    codigo_canonico: Mapped[str] = mapped_column(String(16), nullable=False)
    fator_canonico: Mapped[float] = mapped_column(Numeric(18, 9), nullable=False)
    sistema: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    casas_decimais: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)
    eh_canonica: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))


class UnidadeMedidaConversao(Base):
    __tablename__ = "unidades_medida_conversoes"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )
    unidade_origem_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("unidades_medida.id", ondelete="RESTRICT"), nullable=False
    )
    unidade_destino_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("unidades_medida.id", ondelete="RESTRICT"), nullable=False
    )
    fator: Mapped[float] = mapped_column(Numeric(18, 9), nullable=False)
    cultura: Mapped[str | None] = mapped_column(String(100), nullable=True)
    commodity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("cadastros_commodities.id", ondelete="SET NULL"), nullable=True
    )
    contexto: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
