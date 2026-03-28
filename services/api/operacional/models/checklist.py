import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class StatusItemChecklist(str, enum.Enum):
    OK = "OK"
    NOK = "NOK"       # não conforme — bloqueia liberação
    NA = "NA"         # não aplicável


class ChecklistModelo(Base):
    """
    Template de checklist pré-operação por tipo de equipamento.

    Exemplo:
      tipo_equipamento = "TRATOR"
      itens = [
        {"ordem": 1, "descricao": "Nível óleo motor",  "obrigatorio": true},
        {"ordem": 2, "descricao": "Calibragem pneus",  "obrigatorio": true},
        {"ordem": 3, "descricao": "Nível água radiador","obrigatorio": false},
      ]
    """
    __tablename__ = "frota_checklist_modelos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo_equipamento: Mapped[str | None] = mapped_column(
        String(30), nullable=True, index=True,
        comment="Tipo de equipamento alvo (TRATOR, COLHEDORA…); NULL = genérico"
    )
    # Estrutura: [{"ordem": int, "descricao": str, "obrigatorio": bool}]
    itens: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    realizados: Mapped[list["ChecklistRealizado"]] = relationship(
        back_populates="modelo", lazy="noload"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ChecklistRealizado(Base):
    """
    Preenchimento de checklist por operador antes de usar o equipamento.

    - Se algum item obrigatório tiver status NOK → liberado_para_uso = False
    - O router pode bloquear ApontamentoUso se não houver checklist liberado no dia
    """
    __tablename__ = "frota_checklists_realizados"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_equipamentos.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    modelo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("frota_checklist_modelos.id", ondelete="RESTRICT"),
        nullable=False
    )
    operador_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"), nullable=True
    )

    data_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    # Respostas: [{"ordem": int, "descricao": str, "status": "OK"|"NOK"|"NA", "observacao": str|null}]
    respostas: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    liberado_para_uso: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observacoes_gerais: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Se NOK → pode gerar OS automaticamente
    os_gerada_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("frota_ordens_servico.id", ondelete="SET NULL"), nullable=True
    )

    modelo: Mapped["ChecklistModelo"] = relationship(back_populates="realizados", lazy="noload")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
