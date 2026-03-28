import uuid
import enum
from datetime import datetime, date, timezone
from sqlalchemy import String, DateTime, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class TipoDocumentoEquipamento(str, enum.Enum):
    CRLV = "CRLV"
    SEGURO = "SEGURO"
    LAUDO_VISTORIA = "LAUDO_VISTORIA"
    ART = "ART"             # Anotação de Responsabilidade Técnica
    MANUAL = "MANUAL"
    CONTRATO_LEASING = "CONTRATO_LEASING"
    OUTRO = "OUTRO"


class DocumentoEquipamento(Base):
    """
    Documentos com prazo de validade vinculados a um equipamento.

    Alertas de vencimento devem ser gerados via job/query:
      SELECT * FROM frota_documentos_equipamentos
      WHERE data_vencimento <= NOW() + INTERVAL '30 days'
        AND tenant_id = :tid AND ativo = true
    """
    __tablename__ = "frota_documentos_equipamentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_equipamentos.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    descricao: Mapped[str | None] = mapped_column(String(200), nullable=True)

    numero: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Número do documento")
    orgao_emissor: Mapped[str | None] = mapped_column(String(100), nullable=True)

    data_emissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_vencimento: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    arquivo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
