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


class RelatorioTecnico(Base):
    __tablename__ = "relatorios_tecnicos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id: Mapped[UUID] = mapped_column(Uuid, nullable=False) # Agrônomo responsável

    data_visita: Mapped[datetime] = mapped_column(nullable=False, server_default=text("(CURRENT_TIMESTAMP)"))
    estadio_fenologico: Mapped[str | None] = mapped_column(String(50))
    condicao_climatica: Mapped[dict | None] = mapped_column(JSON) # e.g. {"temp": 25, "umidade": 60, "ceu": "nublado"}
    
    observacoes_gerais: Mapped[str | None] = mapped_column(String(2000))
    recomendacoes: Mapped[str | None] = mapped_column(String(2000))
    
    # Presença de pragas/doenças (JSON para flexibilidade)
    # Ex: [{"nome": "Ferrugem", "nivel": "BAIXO", "tipo": "DOENCA"}]
    constatacoes: Mapped[list[dict]] = mapped_column(JSON, default=list)

    status: Mapped[str] = mapped_column(String(20), default="RASCUNHO") # RASCUNHO, FINALIZADO

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)
