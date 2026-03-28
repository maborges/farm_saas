import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Text, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric
from core.database import Base


class MonitoramentoCatalogo(Base):
    """Catálogo de pragas, doenças e plantas daninhas. is_system=True = padrão AgroSaaS."""
    __tablename__ = "monitoramento_catalogo"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True, comment="NULL = registro global do sistema")

    tipo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # PRAGA | DOENCA | PLANTA_DANINHA
    nome_popular: Mapped[str] = mapped_column(String(100), nullable=False)
    nome_cientifico: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cultura: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)  # None = todas

    nde_padrao: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    unidade_medida: Mapped[str | None] = mapped_column(String(30), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)
