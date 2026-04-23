from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any


# --- Phase Templates ---

class PhaseTemplateChecklistItemBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    obrigatorio: bool = False
    ordem: int = 0
    ativo: bool = True

class PhaseTemplateChecklistItemCreate(PhaseTemplateChecklistItemBase):
    pass

class PhaseTemplateChecklistItemRead(PhaseTemplateChecklistItemBase):
    id: UUID
    phase_template_id: UUID
    model_config = ConfigDict(from_attributes=True)


class PhaseTemplateTaskBase(BaseModel):
    tipo: str
    titulo: str
    descricao: Optional[str] = None
    criticidade: str = "NORMAL"
    ordem: int = 0

class PhaseTemplateTaskCreate(PhaseTemplateTaskBase):
    pass

class PhaseTemplateTaskRead(PhaseTemplateTaskBase):
    id: UUID
    phase_template_id: UUID
    model_config = ConfigDict(from_attributes=True)


class PhaseGateRuleBase(BaseModel):
    rule_type: str
    config: Optional[str] = None # JSON string
    ativo: bool = True

class PhaseGateRuleCreate(PhaseGateRuleBase):
    pass

class PhaseGateRuleRead(PhaseGateRuleBase):
    id: UUID
    phase_template_id: UUID
    model_config = ConfigDict(from_attributes=True)


class PhaseTemplateBase(BaseModel):
    cultura: Optional[str] = None
    fase: str
    titulo: str
    descricao: Optional[str] = None
    ativo: bool = True
    is_system_default: bool = False

class PhaseTemplateCreate(PhaseTemplateBase):
    pass

class PhaseTemplateUpdate(BaseModel):
    cultura: Optional[str] = None
    fase: Optional[str] = None
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class PhaseTemplateRead(PhaseTemplateBase):
    id: UUID
    tenant_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PhaseTemplateDetail(PhaseTemplateRead):
    checklist_items: List[PhaseTemplateChecklistItemRead] = []
    tasks: List[PhaseTemplateTaskRead] = []
    gate_rules: List[PhaseGateRuleRead] = []


# --- Operation Templates ---

class OperationTemplateItemBase(BaseModel):
    tipo: str
    titulo: str
    descricao: Optional[str] = None
    dose_sugerida: Optional[float] = None
    unidade: Optional[str] = None
    can_generate_task: bool = True
    ordem: int = 0

class OperationTemplateItemCreate(OperationTemplateItemBase):
    dependency_ids: List[UUID] = []

class OperationTemplateItemRead(OperationTemplateItemBase):
    id: UUID
    operation_template_id: UUID
    model_config = ConfigDict(from_attributes=True)


class OperationTemplateBase(BaseModel):
    cultura: Optional[str] = None
    fase: Optional[str] = None
    titulo: str
    descricao: Optional[str] = None
    ativo: bool = True
    is_system_default: bool = False

class OperationTemplateCreate(OperationTemplateBase):
    pass

class OperationTemplateUpdate(BaseModel):
    cultura: Optional[str] = None
    fase: Optional[str] = None
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class OperationTemplateRead(OperationTemplateBase):
    id: UUID
    tenant_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class OperationTemplateDetail(OperationTemplateRead):
    items: List[OperationTemplateItemRead] = []


# --- Ações de Aplicação ---

class ApplyPhaseTemplateRequest(BaseModel):
    safra_id: UUID
    phase_template_id: UUID

class ApplyOperationTemplateRequest(BaseModel):
    safra_id: UUID
    operation_template_id: UUID
    talhao_ids: List[UUID] = []
