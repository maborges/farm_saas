from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, ForeignKey, text, Uuid
from uuid import UUID
import uuid
from datetime import datetime
from core.database import Base

class ConversaAgronomo(Base):
    __tablename__ = "conversas_agronomo"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True) # References usuarios(id)
    
    titulo: Mapped[str | None] = mapped_column(String(200))
    contexto_atual: Mapped[dict | None] = mapped_column(JSON) # e.g., {"talhao_id": "...", "safra_id": "..."}
    
    historico_mensagens: Mapped[list[dict]] = mapped_column(JSON, default=list)
    # Ex: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)
