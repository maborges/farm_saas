from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, JSON, ForeignKey, text
from uuid import UUID
import uuid
from datetime import datetime

from core.database import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo: Mapped[str] = mapped_column(String(60), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensagem: Mapped[str] = mapped_column(String(1000), nullable=False)
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("(CURRENT_TIMESTAMP)"), nullable=False
    )
