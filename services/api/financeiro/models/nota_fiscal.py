import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as SQLUUID
from core.database import Base


class TipoNF(str, enum.Enum):
    NFP_E = "NFP-e"
    NF_E = "NF-e"
    NFC_E = "NFC-e"


class StatusSEFAZ(str, enum.Enum):
    EM_DIGITACAO = "em_digitacao"
    ASSINADA = "assinada"
    TRANSMITIDA = "transmitida"
    AUTORIZADA = "autorizada"
    CANCELADA = "cancelada"
    DENEGADA = "denegada"
    INUTILIZADA = "inutilizada"


class NotaFiscal(Base):
    __tablename__ = "fin_notas_fiscais"

    id: Mapped[uuid.UUID] = mapped_column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unidade_produtiva_id: Mapped[uuid.UUID | None] = mapped_column(
        SQLUUID(as_uuid=True), ForeignKey("unidades_produtivas.id", ondelete="SET NULL"), nullable=True
    )

    tipo: Mapped[str] = mapped_column(SQLEnum(TipoNF), nullable=False, default=TipoNF.NFP_E)
    numero: Mapped[int | None] = mapped_column(Integer, nullable=True)
    serie: Mapped[str] = mapped_column(String(10), nullable=False, default="1")

    # Emitente
    emitente_nome: Mapped[str] = mapped_column(String(200), nullable=False)
    emitente_cpf_cnpj: Mapped[str | None] = mapped_column(String(18), nullable=True)

    # Destinatário
    destinatario_nome: Mapped[str] = mapped_column(String(200), nullable=False)
    destinatario_documento: Mapped[str | None] = mapped_column(String(18), nullable=True)
    destinatario_uf: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # Valores
    valor_produtos: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    valor_frete: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    valor_icms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # SEFAZ
    status_sefaz: Mapped[str] = mapped_column(
        SQLEnum(StatusSEFAZ), nullable=False, default=StatusSEFAZ.EM_DIGITACAO
    )
    chave_acesso: Mapped[str | None] = mapped_column(String(44), nullable=True, index=True)
    numero_protocolo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    numero_recibo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    motivo_cancelamento: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Produto principal (simplificado)
    descricao_produto: Mapped[str | None] = mapped_column(String(300), nullable=True)
    ncm: Mapped[str | None] = mapped_column(String(8), nullable=True)
    quantidade: Mapped[float | None] = mapped_column(Float, nullable=True)
    unidade: Mapped[str | None] = mapped_column(String(6), nullable=True)

    data_emissao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    data_autorizacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    data_cancelamento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
