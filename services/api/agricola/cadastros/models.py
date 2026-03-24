from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, ForeignKey, text
from uuid import UUID
import uuid
from datetime import datetime
from core.database import Base

class Cultura(Base):
    __tablename__ = "culturas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    nome_cientifico: Mapped[str | None] = mapped_column(String(150))
    variedade: Mapped[str | None] = mapped_column(String(100))
    ciclo_dias: Mapped[int | None] = mapped_column()
    
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)
