import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


class TurnoOrdenha(str, enum.Enum):
    MANHA   = "MANHA"
    TARDE   = "TARDE"
    NOITE   = "NOITE"
    UNICA   = "UNICA"


class ProducaoLeite(Base):
    """
    Registro de produção leiteira — produto do ativo biológico (IAS 41).

    Pode ser registrado por animal individual (alta precisão) ou por lote
    (controle coletivo). Em ambos os casos gera receita ao ser vendido/entregue.

    O leite coletado entra no estoque de commodities (BOVINO_LEITE).
    """
    __tablename__ = "pec_producao_leite"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unidade_produtiva_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("unidades_produtivas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Pode registrar por animal ou por lote (um dos dois obrigatório)
    animal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_animais.id", ondelete="SET NULL"), nullable=True, index=True,
        comment="Registro individual por animal (alta precisão)"
    )
    lote_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_lotes.id", ondelete="SET NULL"), nullable=True, index=True,
        comment="Registro coletivo por lote"
    )

    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    turno: Mapped[str] = mapped_column(String(10), nullable=False, default="MANHA")

    # Produção
    volume_litros: Mapped[float] = mapped_column(Float, nullable=False)
    temperatura_c: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Qualidade (análise laboratorial)
    gordura_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    proteina_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    ccs: Mapped[int | None] = mapped_column(nullable=True, comment="Contagem de Células Somáticas (x1000/ml)")
    cbt: Mapped[int | None] = mapped_column(nullable=True, comment="Contagem Bacteriana Total (x1000/ml)")
    lactose_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    esd_pct: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Extrato Seco Desengordurado")

    # Destino
    destino: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="LATICINIO | QUEIJARIA | CONSUMO_PROPRIO | DESCARTE")
    pessoa_destino_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"), nullable=True,
        comment="Laticínio ou comprador"
    )
    preco_litro: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_total: Mapped[float | None] = mapped_column(Float, nullable=True)

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
