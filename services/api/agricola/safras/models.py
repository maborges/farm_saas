import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Boolean, Integer, Date, Text, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base

class Safra(Base):
    __tablename__ = "safras"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("talhoes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    ano_safra: Mapped[str] = mapped_column(String(10), nullable=False)
    cultura: Mapped[str] = mapped_column(String(50), nullable=False)
    cultivar_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("culturas.id", ondelete="SET NULL"), nullable=True)
    cultivar_nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sistema_plantio: Mapped[str | None] = mapped_column(String(30), nullable=True)
    
    data_plantio_prevista: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_plantio_real: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_colheita_prevista: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_colheita_real: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    populacao_prevista: Mapped[int | None] = mapped_column(Integer, nullable=True)
    populacao_real: Mapped[int | None] = mapped_column(Integer, nullable=True)
    espacamento_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area_plantada_ha: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    
    produtividade_meta_sc_ha: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    produtividade_real_sc_ha: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    preco_venda_previsto: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    custo_previsto_ha: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    custo_realizado_ha: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='PLANEJADA')
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    # Relacionamentos
    # talhao: Mapped["Talhao"] = relationship(back_populates="safras", lazy="noload")

