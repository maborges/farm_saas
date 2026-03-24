import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Numeric, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class ContaBancaria(Base):
    """Conta bancária do produtor, usada para importar extratos OFX."""
    __tablename__ = "fin_contas_bancarias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL"), nullable=True)

    nome: Mapped[str] = mapped_column(String(100), nullable=False)          # "Bradesco Conta Corrente"
    banco: Mapped[str | None] = mapped_column(String(50))                   # "237"
    agencia: Mapped[str | None] = mapped_column(String(20))
    conta: Mapped[str | None] = mapped_column(String(30))
    tipo: Mapped[str] = mapped_column(String(20), default="CORRENTE")       # CORRENTE | POUPANCA | INVESTIMENTO
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class LancamentoBancario(Base):
    """Lançamento importado de extrato OFX."""
    __tablename__ = "fin_lancamentos_bancarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    conta_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fin_contas_bancarias.id", ondelete="CASCADE"), nullable=False, index=True)

    data: Mapped[date] = mapped_column(Date, nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)    # positivo=crédito, negativo=débito
    descricao: Mapped[str | None] = mapped_column(String(500))
    id_ofx: Mapped[str | None] = mapped_column(String(100), index=True)     # FITID do OFX para deduplicação
    tipo: Mapped[str] = mapped_column(String(10))                           # CREDIT | DEBIT

    # Conciliação
    status_conciliacao: Mapped[str] = mapped_column(String(20), default="NAO_CONCILIADO")  # NAO_CONCILIADO | CONCILIADO | IGNORADO
    despesa_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fin_despesas.id", ondelete="SET NULL"), nullable=True)
    receita_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fin_receitas.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
