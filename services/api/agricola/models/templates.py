import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, text, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class PhaseTemplate(Base):
    """
    Template de governança para uma fase da safra.
    Contém itens de checklist, tarefas padrão e regras de transição (gate).
    """
    __tablename__ = "phase_templates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True, comment="NULL = registro global do sistema")
    
    cultura: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    fase: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_system_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    # Relacionamentos
    checklist_items: Mapped[list["PhaseTemplateChecklistItem"]] = relationship("PhaseTemplateChecklistItem", back_populates="template", cascade="all, delete-orphan")
    tasks: Mapped[list["PhaseTemplateTask"]] = relationship("PhaseTemplateTask", back_populates="template", cascade="all, delete-orphan")
    gate_rules: Mapped[list["PhaseGateRule"]] = relationship("PhaseGateRule", back_populates="template", cascade="all, delete-orphan")


class PhaseTemplateChecklistItem(Base):
    """Itens de checklist vinculados a um template de fase."""
    __tablename__ = "phase_template_checklist_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phase_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("phase_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    obrigatorio: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    template: Mapped["PhaseTemplate"] = relationship("PhaseTemplate", back_populates="checklist_items")


class PhaseTemplateTask(Base):
    """Tarefas padrão geradas ao aplicar um template de fase."""
    __tablename__ = "phase_template_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phase_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("phase_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    
    tipo: Mapped[str] = mapped_column(String(30), nullable=False) # ex: PLANTIO, PULVERIZACAO
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criticidade: Mapped[str] = mapped_column(String(15), nullable=False, default="NORMAL") # CRITICA | NORMAL | OPCIONAL
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    template: Mapped["PhaseTemplate"] = relationship("PhaseTemplate", back_populates="tasks")


class PhaseGateRule(Base):
    """Regras extras de gate (passagem de fase) vinculadas ao template."""
    __tablename__ = "phase_gate_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phase_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("phase_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False) # ex: MANDATORY_CHECKLIST, MIN_SOIL_ANALYSIS
    config: Mapped[str | None] = mapped_column(Text, nullable=True) # JSON config
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    template: Mapped["PhaseTemplate"] = relationship("PhaseTemplate", back_populates="gate_rules")


class OperationTemplate(Base):
    """
    Template operacional (plano de ação) para uma fase ou tipo de operação.
    Contém a sequência de operações e insumos sugeridos.
    """
    __tablename__ = "operation_templates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    
    cultura: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    fase: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    is_system_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    items: Mapped[list["OperationTemplateItem"]] = relationship("OperationTemplateItem", back_populates="template", cascade="all, delete-orphan")


class OperationTemplateItem(Base):
    """Itens (operações individuais) dentro de um template operacional."""
    __tablename__ = "operation_template_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    operation_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operation_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    dose_sugerida: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    unidade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    can_generate_task: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    template: Mapped["OperationTemplate"] = relationship("OperationTemplate", back_populates="items")


class OperationDependency(Base):
    """Dependências entre itens de um template operacional (A deve ocorrer antes de B)."""
    __tablename__ = "operation_dependencies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operation_template_items.id", ondelete="CASCADE"), nullable=False, index=True)
    dependency_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operation_template_items.id", ondelete="CASCADE"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("item_id", "dependency_id", name="uq_operation_dependency"),
    )
