from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Integer, Date, Text, ForeignKey, text, Uuid, DateTime, JSON, Boolean
from uuid import UUID
import uuid
from datetime import datetime, date, timezone
from core.database import Base

class AnaliseSolo(Base):
    __tablename__ = "analises_solo"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    production_unit_id: Mapped[UUID | None] = mapped_column(ForeignKey("production_units.id", ondelete="SET NULL"), nullable=True)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)

    data_coleta: Mapped[date] = mapped_column(Date, nullable=False)
    laboratorio: Mapped[str | None] = mapped_column(String(150))
    codigo_amostra: Mapped[str | None] = mapped_column(String(50))
    profundidade_cm: Mapped[int | None] = mapped_column(Numeric(3, 0))

    # ── Físicos ────────────────────────────────────────────────────────────────
    argila_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    silte_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    areia_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))

    # ── Químicos ───────────────────────────────────────────────────────────────
    ph_agua: Mapped[float | None] = mapped_column(Numeric(4, 2))
    ph_cacl2: Mapped[float | None] = mapped_column(Numeric(4, 2))
    materia_organica_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    fosforo_p: Mapped[float | None] = mapped_column(Numeric(8, 2))       # mg/dm³
    potassio_k: Mapped[float | None] = mapped_column(Numeric(8, 2))      # mg/dm³
    calcio_ca: Mapped[float | None] = mapped_column(Numeric(8, 2))       # cmolc/dm³
    magnesio_mg: Mapped[float | None] = mapped_column(Numeric(8, 2))     # cmolc/dm³
    aluminio_al: Mapped[float | None] = mapped_column(Numeric(8, 2))     # cmolc/dm³
    hidrogenio_al_hal: Mapped[float | None] = mapped_column(Numeric(8, 2))  # cmolc/dm³

    # ── Calculados ─────────────────────────────────────────────────────────────
    ctc: Mapped[float | None] = mapped_column(Numeric(8, 2))             # Capacidade de Troca Catiônica
    v_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))           # Saturação por Bases (V%)
    saturacao_al_m_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))  # m% = Al / CTC × 100

    # ── Micronutrientes ────────────────────────────────────────────────────────
    zinco_zn: Mapped[float | None] = mapped_column(Numeric(8, 3))        # mg/dm³
    boro_b: Mapped[float | None] = mapped_column(Numeric(8, 3))          # mg/dm³
    ferro_fe: Mapped[float | None] = mapped_column(Numeric(8, 3))        # mg/dm³
    manganes_mn: Mapped[float | None] = mapped_column(Numeric(8, 3))     # mg/dm³

    # ── Contexto agronômico ────────────────────────────────────────────────────
    # SEQUEIRO | GOTEJAMENTO | PIVO_CENTRAL | ASPERSAO | SULCO
    tipo_irrigacao: Mapped[str | None] = mapped_column(String(20))
    # PLANTIO_DIRETO | CONVENCIONAL | MINIMO
    sistema_manejo: Mapped[str | None] = mapped_column(String(20))
    cultura_nome: Mapped[str | None] = mapped_column(String(100))        # Cultura vinculada
    cultura_anterior: Mapped[str | None] = mapped_column(String(100))    # Cultivo anterior (fertilidade residual)

    # ── Validade ───────────────────────────────────────────────────────────────
    validade_meses: Mapped[int | None] = mapped_column(Integer, default=12)

    # ── Extras ────────────────────────────────────────────────────────────────
    arquivo_laudo_url: Mapped[str | None] = mapped_column(String(500))
    observacoes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)


class RegraAgronomica(Base):
    __tablename__ = "agricola_regras_agronomicas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500))
    
    # Condição e Ação armazenadas como JSON para flexibilidade do motor de regras
    condicao_json: Mapped[dict] = mapped_column(JSON, nullable=False) 
    acao_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    prioridade: Mapped[int] = mapped_column(Integer, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
