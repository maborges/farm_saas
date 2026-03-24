import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Boolean, DateTime, Numeric, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class Cupom(Base):
    """Cupons de desconto para assinaturas."""
    __tablename__ = "cupons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Tipo de Desconto
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # percentual, valor_fixo
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Aplicação
    aplicavel_em: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default='primeira_mensalidade'
    )  # primeira_mensalidade, todos_meses, plano_anual
    duracao_meses: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Limites de uso
    uso_maximo: Mapped[int] = mapped_column(Integer, default=1)
    uso_atual: Mapped[int] = mapped_column(Integer, default=0)
    uso_por_cliente: Mapped[int] = mapped_column(Integer, default=1)

    # Validade
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Auditoria
    criado_por_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def pode_ser_usado(self) -> bool:
        """Verifica se cupom ainda pode ser usado."""
        hoje = date.today()
        return (
            self.ativo and
            self.data_inicio <= hoje <= self.data_fim and
            self.uso_atual < self.uso_maximo
        )
