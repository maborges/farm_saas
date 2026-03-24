import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum

class TicketStatus(str, enum.Enum):
    ABERTO = "ABERTO"
    EM_ATENDIMENTO = "EM_ATENDIMENTO"
    AGUARDANDO_CLIENTE = "AGUARDANDO_CLIENTE"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"

class TicketPriority(str, enum.Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"

class ChamadoSuporte(Base):
    """Representa um ticket de suporte aberto por um usuário."""
    __tablename__ = "chamados_suporte"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    usuario_abertura_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    
    assunto: Mapped[str] = mapped_column(String(200), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), default="TECNICO") # TECNICO, FINANCEIRO, DÚVIDA
    
    status: Mapped[TicketStatus] = mapped_column(SQLEnum(TicketStatus), default=TicketStatus.ABERTO)
    prioridade: Mapped[TicketPriority] = mapped_column(SQLEnum(TicketPriority), default=TicketPriority.MEDIA)
    
    # Atendimento
    atendente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=True
    )
    data_primeira_resposta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    data_resolucao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    sla_vencimento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Avaliação
    avaliacao_nota: Mapped[int | None] = mapped_column(nullable=True)  # 1-5
    avaliacao_comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    avaliacao_data: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    mensagens: Mapped[list["MensagemChamado"]] = relationship("MensagemChamado", back_populates="chamado", cascade="all, delete-orphan", order_by="MensagemChamado.created_at")
    atendente: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[atendente_id])

class MensagemChamado(Base):
    """Mensagens trocadas dentro de um chamado."""
    __tablename__ = "mensagens_chamado"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chamado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chamados_suporte.id", ondelete="CASCADE"), index=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    is_admin_reply: Mapped[bool] = mapped_column(default=False)
    
    anexo_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    chamado: Mapped["ChamadoSuporte"] = relationship("ChamadoSuporte", back_populates="mensagens")
