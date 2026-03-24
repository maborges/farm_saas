from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Date, JSON, ForeignKey, text
from uuid import UUID
import uuid
from datetime import datetime, date
from core.database import Base

class PrevisaoProdutividade(Base):
    __tablename__ = "previsoes_produtividade"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("talhoes.id", ondelete="CASCADE"), nullable=False, index=True)

    data_previsao: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    
    # ML Estimates
    produtividade_estimada_sc_ha: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    margem_erro_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    
    # Factors considered in the model
    fatores_peso: Mapped[dict | None] = mapped_column(JSON)
    
    historico_clima: Mapped[dict | None] = mapped_column(JSON)
    indice_ndvi_medio: Mapped[float | None] = mapped_column(Numeric(4, 3))
    
    modelo_ia_versao: Mapped[str | None] = mapped_column(String(50))
    run_id: Mapped[str | None] = mapped_column(String(100)) # MLflow run_id

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
