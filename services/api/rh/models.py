import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, Date, DateTime, Float, ForeignKey, text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class ColaboradorRH(Base):
    __tablename__ = "rh_colaboradores"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True)
    pessoa_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)  # link opcional a Pessoa

    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True)
    cargo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tipo_contrato: Mapped[str] = mapped_column(String(20), default="DIARISTA")  # CLT | DIARISTA | EMPREITEIRO | TERCEIRO
    valor_diaria: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_hora: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_admissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_demissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    observacoes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))


class LancamentoDiaria(Base):
    __tablename__ = "rh_lancamentos_diarias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    colaborador_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("rh_colaboradores.id", ondelete="CASCADE"), nullable=False, index=True)
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True)
    safra_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)

    data: Mapped[date] = mapped_column(Date, nullable=False)
    horas_trabalhadas: Mapped[float] = mapped_column(Float, default=8.0)
    atividade: Mapped[str] = mapped_column(String(100), default="GERAL")  # PLANTIO, COLHEITA, CAPINA, MANUTENCAO, GERAL
    valor_diaria: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDENTE")  # PENDENTE | PAGO
    data_pagamento: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))


class Empreitada(Base):
    __tablename__ = "rh_empreitadas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    colaborador_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("rh_colaboradores.id", ondelete="CASCADE"), nullable=False, index=True)
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True)
    safra_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)

    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    unidade: Mapped[str] = mapped_column(String(30), default="HECTARE")  # HECTARE | SACA | HORA | UNIDADE | METRO
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    valor_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)

    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ABERTA")  # ABERTA | CONCLUIDA | PAGA | CANCELADA
    data_pagamento: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
