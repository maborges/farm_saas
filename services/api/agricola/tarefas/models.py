import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Text, ForeignKey, Date, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUIDType
from core.database import Base


class SafraTarefa(Base):
    """
    Tarefa planejada dentro de uma safra.
    Representa uma intenção de ação — o planejamento do que deve ser feito.
    A execução real é registrada como OperacaoAgricola (com tarefa_id vinculado).

    Origens:
      SOLO     — gerada automaticamente pela análise de solo (nasce PENDENTE_APROVACAO)
      TEMPLATE — gerada automaticamente ao entrar em uma fase (nasce PENDENTE_APROVACAO)
      MANUAL   — criada pelo agrônomo/gestor (nasce APROVADA)
    """
    __tablename__ = "safra_tarefas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    safra_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    talhao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("cadastros_areas_rurais.id", ondelete="SET NULL"), nullable=True, index=True
    )
    cultivo_area_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("cultivo_areas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    analise_solo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("analises_solo.id", ondelete="SET NULL"), nullable=True
    )

    # Origem e tipo
    origem: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # CALAGEM | ADUBACAO_FOSFORO | ADUBACAO_POTASSIO | ADUBACAO_NITROGENIO
    # GRADAGEM | PLANTIO | PULVERIZACAO | IRRIGACAO | COLHEITA | OUTRO
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    # Fase da safra na qual a tarefa será executada (ex: PREPARO_SOLO, PLANTIO)
    fase: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)

    # Criticidade: CRITICA | NORMAL | OPCIONAL
    # CRITICA bloqueia o avanço de fase caso não esteja concluída/cancelada
    criticidade: Mapped[str] = mapped_column(String(15), nullable=False, default="NORMAL")

    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    obs: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Prioridade: BAIXA | MEDIA | ALTA | URGENTE
    prioridade: Mapped[str] = mapped_column(String(10), nullable=False, default="MEDIA")

    # Status: PENDENTE_APROVACAO | APROVADA | EM_EXECUCAO | CONCLUIDA | CANCELADA
    status: Mapped[str] = mapped_column(String(25), nullable=False, default="PENDENTE_APROVACAO", index=True)

    # Dados estimados (sugestão para pré-preencher a Operação)
    dose_estimada_kg_ha: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    quantidade_total_estimada_kg: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    area_ha: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    custo_estimado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    data_prevista: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Aprovação
    aprovado_por: Mapped[uuid.UUID | None] = mapped_column(UUIDType, nullable=True)
    aprovado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Conclusão via operação
    operacao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("operacoes_agricolas.id", ondelete="SET NULL"), nullable=True
    )
    concluida_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Cancelamento
    cancelado_por: Mapped[uuid.UUID | None] = mapped_column(UUIDType, nullable=True)
    cancelado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    motivo_cancelamento: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[uuid.UUID | None] = mapped_column(UUIDType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_safra_tarefas_tenant_safra_status", "tenant_id", "safra_id", "status"),
        Index("ix_safra_tarefas_talhao", "talhao_id"),
    )
