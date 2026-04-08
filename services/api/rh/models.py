import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, Date, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class Departamento(Base):
    __tablename__ = "rh_departamentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsavel_nome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ColaboradorRH(Base):
    """
    Especialização de Pessoa para o contexto de RH.

    pessoa_id é FK obrigatória para cadastros_pessoas.
    Dados de identificação (nome, CPF) ficam em cadastros_pessoas + cadastros_pessoas_documentos.
    Dados bancários (para pagamento de salário/diária) ficam em cadastros_pessoas_bancario.
    """
    __tablename__ = "rh_colaboradores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    pessoa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), nullable=True, index=True
    )

    departamento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rh_departamentos.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Dados de identificação (denormalizados para uso sem cadastros_pessoas)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True, index=True)

    # Dados exclusivos do contexto RH (não existem em Pessoa)
    cargo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tipo_contrato: Mapped[str] = mapped_column(
        String(20), default="DIARISTA", nullable=False,
        comment="CLT | DIARISTA | EMPREITEIRO | TERCEIRO | PJ"
    )
    valor_diaria: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_hora: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_admissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_demissao: Mapped[date | None] = mapped_column(Date, nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class EsocialEvento(Base):
    __tablename__ = "rh_esocial_eventos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    colaborador_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rh_colaboradores.id", ondelete="SET NULL"), nullable=True, index=True
    )
    tipo_evento: Mapped[str] = mapped_column(
        String(10), nullable=False,
        comment="S-2200 | S-2300 | S-2299 | S-1200 | S-2400"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="PENDENTE", nullable=False,
        comment="PENDENTE | ENVIADO | ERRO | PROCESSANDO"
    )
    numero_recibo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    codigo_erro: Mapped[str | None] = mapped_column(String(20), nullable=True)
    descricao_erro: Mapped[str | None] = mapped_column(Text, nullable=True)
    colaborador_nome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    periodo_apuracao: Mapped[str | None] = mapped_column(String(7), nullable=True, comment="YYYY-MM")
    xml_enviado: Mapped[str | None] = mapped_column(Text, nullable=True)
    enviado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class LancamentoDiaria(Base):
    __tablename__ = "rh_lancamentos_diarias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    colaborador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rh_colaboradores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True
    )
    safra_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("safras.id", ondelete="CASCADE"),
        nullable=True,
        comment="Safra à qual o lançamento está vinculado"
    )

    data: Mapped[date] = mapped_column(Date, nullable=False)
    horas_trabalhadas: Mapped[float] = mapped_column(Float, default=8.0, nullable=False)
    atividade: Mapped[str] = mapped_column(
        String(100), default="GERAL",
        comment="PLANTIO | COLHEITA | CAPINA | MANUTENCAO | IRRIGACAO | GERAL"
    )
    valor_diaria: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDENTE", comment="PENDENTE | PAGO")
    data_pagamento: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Empreitada(Base):
    __tablename__ = "rh_empreitadas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    colaborador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rh_colaboradores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True
    )
    safra_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("safras.id", ondelete="CASCADE"),
        nullable=True,
        comment="Safra à qual a empreitada está vinculada"
    )

    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    unidade: Mapped[str] = mapped_column(
        String(30), default="HECTARE",
        comment="HECTARE | SACA | HORA | UNIDADE | METRO"
    )
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    valor_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)

    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ABERTA", comment="ABERTA | CONCLUIDA | PAGA | CANCELADA")
    data_pagamento: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
