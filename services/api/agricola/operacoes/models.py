from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Boolean, Date, Time, Text, ForeignKey, text, JSON, Uuid
from uuid import UUID
import uuid
from datetime import datetime, date, time
from core.database import Base

class OperacaoAgricola(Base):
    __tablename__ = "operacoes_agricolas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    cultivo_id: Mapped[UUID | None] = mapped_column(ForeignKey("cultivos.id", ondelete="CASCADE"), nullable=True, index=True)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)
    tarefa_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("safra_tarefas.id", ondelete="SET NULL"), nullable=True, index=True)

    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    subtipo: Mapped[str | None] = mapped_column(String(50))
    descricao: Mapped[str] = mapped_column(Text, nullable=False)

    data_prevista: Mapped[date | None] = mapped_column(Date)
    data_realizada: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time | None] = mapped_column(Time)
    hora_fim: Mapped[time | None] = mapped_column(Time)

    area_aplicada_ha: Mapped[float | None] = mapped_column(Numeric(12, 4))
    maquina_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True) # References maquinas(id) if exists
    implemento: Mapped[str | None] = mapped_column(String(100))
    operador_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"),
        nullable=True,
        comment="Operador que realizou a operação agrícola"
    )

    temperatura_c: Mapped[float | None] = mapped_column(Numeric(5, 2))
    umidade_rel: Mapped[float | None] = mapped_column(Numeric(5, 2))
    vento_kmh: Mapped[float | None] = mapped_column(Numeric(5, 2))
    direcao_vento: Mapped[str | None] = mapped_column(String(10))
    condicao_clima: Mapped[str | None] = mapped_column(String(30))

    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))

    custo_total: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    custo_por_ha: Mapped[float] = mapped_column(Numeric(12, 4), default=0)

    fase_safra: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default='REALIZADA')
    observacoes: Mapped[str | None] = mapped_column(Text)
    fotos: Mapped[list[str]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    # Relacionamentos
    insumos: Mapped[list["InsumoOperacao"]] = relationship(back_populates="operacao", cascade="all, delete-orphan", lazy="selectin")

class InsumoOperacao(Base):
    __tablename__ = "insumos_operacao"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    operacao_id: Mapped[UUID] = mapped_column(ForeignKey("operacoes_agricolas.id", ondelete="CASCADE"), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    insumo_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("cadastros_produtos.id"), nullable=False, index=True)
    
    lote_insumo: Mapped[str | None] = mapped_column(String(50))
    dose_por_ha: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    
    area_aplicada: Mapped[float | None] = mapped_column(Numeric(12, 4))
    quantidade_total: Mapped[float | None] = mapped_column(Numeric(12, 4))
    custo_unitario: Mapped[float | None] = mapped_column(Numeric(12, 4))
    custo_total: Mapped[float | None] = mapped_column(Numeric(15, 2))
    
    carencia_dias: Mapped[int | None] = mapped_column(Numeric(4, 0)) # Using INT/Numeric(4,0)
    data_reentrada: Mapped[date | None] = mapped_column(Date)
    epi_necessario: Mapped[list[str] | None] = mapped_column(JSON)

    operacao: Mapped["OperacaoAgricola"] = relationship(back_populates="insumos")
