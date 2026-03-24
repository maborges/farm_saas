from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class NotificacaoCreate(BaseModel):
    tipo: str
    titulo: str
    mensagem: str
    meta: dict = {}


class NotificacaoResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    tipo: str
    titulo: str
    mensagem: str
    lida: bool
    meta: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MarcarLidasRequest(BaseModel):
    ids: Optional[list[UUID]] = None  # None = mark all
