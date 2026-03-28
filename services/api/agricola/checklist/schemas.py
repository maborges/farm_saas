from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


# --- Templates ---

class ChecklistTemplateCreate(BaseModel):
    cultura: str | None = None
    fase: str
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    obrigatorio: bool = False
    ordem: int = 0


class ChecklistTemplateUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    obrigatorio: bool | None = None
    ordem: int | None = None
    ativo: bool | None = None


class ChecklistTemplateResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    cultura: str | None
    fase: str
    titulo: str
    descricao: str | None
    obrigatorio: bool
    ordem: int
    ativo: bool
    is_system: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Itens por safra ---

class ChecklistItemConcluidoUpdate(BaseModel):
    concluido: bool


class ChecklistItemAdicionar(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    obrigatorio: bool = False
    ordem: int = 0


class SafraChecklistItemResponse(BaseModel):
    id: UUID
    safra_id: UUID
    template_id: UUID | None
    fase: str
    titulo: str
    descricao: str | None
    obrigatorio: bool
    ordem: int
    concluido: bool
    usuario_id: UUID | None
    concluido_em: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChecklistFaseStatus(BaseModel):
    fase: str
    total: int
    concluidos: int
    obrigatorios_pendentes: int
    pode_avancar: bool
    itens: list[SafraChecklistItemResponse]
