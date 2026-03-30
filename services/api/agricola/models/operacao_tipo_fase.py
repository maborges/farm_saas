"""Model para lookup de tipos de operação e fases permitidas."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class OperacaoTipoFase(Base):
    """
    Lookup table que define quais fases da safra cada tipo de operação é permitido.

    Exemplo:
    - PLANTIO → [PLANTIO, DESENVOLVIMENTO]
    - COLHEITA → [COLHEITA]
    - PULVERIZAÇÃO → [DESENVOLVIMENTO, COLHEITA]

    Usado para validação em criar_operacao() — operação só pode ser registrada
    em fases permitidas para seu tipo.
    """
    __tablename__ = "agricola_operacao_tipo_fase"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tipo_operacao: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
        comment="Tipo de operação: PLANTIO, COLHEITA, PULVERIZAÇÃO, etc."
    )

    fases_permitidas: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        comment='Lista de fases da safra permitidas: ["PLANTIO", "DESENVOLVIMENTO"]'
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descrição do tipo de operação"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="CURRENT_TIMESTAMP",
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<OperacaoTipoFase tipo={self.tipo_operacao} fases={self.fases_permitidas}>"
