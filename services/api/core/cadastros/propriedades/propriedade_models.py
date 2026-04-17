import uuid
import enum
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, Text, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class NaturezaVinculo(str, enum.Enum):
    PROPRIA = "propria"
    ARRENDAMENTO = "arrendamento"
    PARCERIA = "parceria"
    COMODATO = "comodato"
    POSSE = "posse"


class TipoDocumentoExploracao(str, enum.Enum):
    CONTRATO_ARRENDAMENTO = "contrato_arrendamento"
    CONTRATO_PARCERIA = "contrato_parceria"
    CONTRATO_COMODATO = "contrato_comodato"
    ESCRITURA = "escritura"
    MATRICULA = "matricula"
    CCIR = "ccir"
    ITR = "itr"
    CAR = "car"
    OUTRO = "outro"


class Propriedade(Base):
    __tablename__ = "cadastros_propriedades"
    __table_args__ = (Index("ix_propriedades_tenant", "tenant_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf_cnpj: Mapped[str | None] = mapped_column(String(18), nullable=True)
    inscricao_estadual: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ie_isento: Mapped[bool] = mapped_column(Boolean, default=False)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200), nullable=True)
    regime_tributario: Mapped[str | None] = mapped_column(String(30), nullable=True)
    cor: Mapped[str | None] = mapped_column(String(7), nullable=True)
    icone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    exploracoes: Mapped[list["ExploracaoRural"]] = relationship(back_populates="propriedade", lazy="noload", cascade="all, delete-orphan")


class ExploracaoRural(Base):
    __tablename__ = "cadastros_exploracoes_rurais"
    __table_args__ = (
        Index("ix_exploracoes_tenant", "tenant_id"),
        Index("ix_exploracoes_vigencia", "data_inicio", "data_fim"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    propriedade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_propriedades.id", ondelete="CASCADE"), nullable=False, index=True)
    unidade_produtiva_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("unidades_produtivas.id", ondelete="CASCADE"), nullable=False, index=True)
    natureza: Mapped[str] = mapped_column(String(30), nullable=False, default=NaturezaVinculo.PROPRIA)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date | None] = mapped_column(Date, nullable=True)
    numero_contrato: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valor_anual: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentual_producao: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_explorada_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    documento_s3_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    documento_tipo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    propriedade: Mapped["Propriedade"] = relationship(back_populates="exploracoes", lazy="noload")


class DocumentoExploracao(Base):
    __tablename__ = "cadastros_documentos_exploracao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    exploracao_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_exploracoes_rurais.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_backend: Mapped[str] = mapped_column(String(10), nullable=False, default="local")
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data_emissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_validade: Mapped[date | None] = mapped_column(Date, nullable=True)
    numero_documento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    orgao_expedidor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
