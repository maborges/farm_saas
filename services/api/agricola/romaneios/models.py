from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Boolean, Date, Text, ForeignKey, text, Uuid
from uuid import UUID
import uuid
from datetime import datetime, date
from core.database import Base

class RomaneioColheita(Base):
    __tablename__ = "romaneios_colheita"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("talhoes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    numero_romaneio: Mapped[str | None] = mapped_column(String(30))
    data_colheita: Mapped[date] = mapped_column(Date, nullable=False)
    turno: Mapped[str | None] = mapped_column(String(10))
    maquina_colhedora_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    operador_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    
    peso_bruto_kg: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    tara_kg: Mapped[float | None] = mapped_column(Numeric(12, 3), default=0)
    peso_liquido_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    
    umidade_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    impureza_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    avariados_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    desconto_umidade_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    desconto_impureza_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    peso_liquido_padrao_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    
    sacas_60kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    
    destino: Mapped[str | None] = mapped_column(String(30)) # ARMAZEM, TERCESIRO...
    armazem_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    nf_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    preco_saca: Mapped[float | None] = mapped_column(Numeric(12, 2))
    receita_total: Mapped[float | None] = mapped_column(Numeric(15, 2))
    
    observacoes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)
