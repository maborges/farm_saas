import uuid
import enum
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, Date, DateTime, Float, ForeignKey, Text, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as SQLUUID
from core.database import Base


class StatusCAR(str, enum.Enum):
    ATIVO = "ATIVO"
    PENDENTE = "PENDENTE"
    CANCELADO = "CANCELADO"
    SUSPENSO = "SUSPENSO"
    EM_ANALISE = "EM_ANALISE"


class TipoAlerta(str, enum.Enum):
    DESMATAMENTO = "DESMATAMENTO"
    QUEIMADA = "QUEIMADA"
    INUNDACAO = "INUNDACAO"
    EROSAO = "EROSAO"
    OUTRO = "OUTRO"


class SeveridadeAlerta(str, enum.Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class StatusAlerta(str, enum.Enum):
    NOVO = "NOVO"
    EM_ANALISE = "EM_ANALISE"
    RESOLVIDO = "RESOLVIDO"
    IGNORADO = "IGNORADO"


class StatusOutorga(str, enum.Enum):
    ATIVA = "ATIVA"
    VENCIDA = "VENCIDA"
    SUSPENSA = "SUSPENSA"
    CANCELADA = "CANCELADA"
    EM_RENOVACAO = "EM_RENOVACAO"


class TipoUsoOutorga(str, enum.Enum):
    IRRIGACAO = "IRRIGACAO"
    DESSEDENTACAO = "DESSEDENTACAO"
    USO_INDUSTRIAL = "USO_INDUSTRIAL"
    AQUICULTURA = "AQUICULTURA"
    OUTRO = "OUTRO"


class RegistroCAR(Base):
    __tablename__ = "amb_registros_car"

    id: Mapped[uuid.UUID] = mapped_column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        SQLUUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    fazenda_nome: Mapped[str] = mapped_column(String(200), nullable=False)
    codigo_car: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    municipio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(SQLEnum(StatusCAR), nullable=False, default=StatusCAR.PENDENTE)
    area_total_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_app_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_rl_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_vegetacao_nativa_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_uso_consolidado_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_inscricao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_atualizacao: Mapped[date | None] = mapped_column(Date, nullable=True)
    pendencias: Mapped[str | None] = mapped_column(Text, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AlertaAmbiental(Base):
    __tablename__ = "amb_alertas"

    id: Mapped[uuid.UUID] = mapped_column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        SQLUUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    fazenda_nome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tipo: Mapped[str] = mapped_column(SQLEnum(TipoAlerta), nullable=False, default=TipoAlerta.DESMATAMENTO)
    severidade: Mapped[str] = mapped_column(SQLEnum(SeveridadeAlerta), nullable=False, default=SeveridadeAlerta.MEDIA)
    status: Mapped[str] = mapped_column(SQLEnum(StatusAlerta), nullable=False, default=StatusAlerta.NOVO)
    area_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    fonte: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="PRODES | DETER | SICAR | MANUAL")
    talhao_nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_deteccao: Mapped[date] = mapped_column(Date, nullable=False, default=lambda: date.today())
    data_resolucao: Mapped[date | None] = mapped_column(Date, nullable=True)
    resolucao_descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OutorgaHidrica(Base):
    __tablename__ = "amb_outorgas_hidricas"

    id: Mapped[uuid.UUID] = mapped_column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        SQLUUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    fazenda_nome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    numero_outorga: Mapped[str] = mapped_column(String(100), nullable=False)
    orgao_emissor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tipo_uso: Mapped[str] = mapped_column(SQLEnum(TipoUsoOutorga), nullable=False, default=TipoUsoOutorga.IRRIGACAO)
    corpo_hidrico: Mapped[str | None] = mapped_column(String(200), nullable=True)
    vazao_outorgada_ls: Mapped[float | None] = mapped_column(Float, nullable=True)
    vazao_outorgada_m3h: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(SQLEnum(StatusOutorga), nullable=False, default=StatusOutorga.ATIVA)
    data_emissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_vencimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
