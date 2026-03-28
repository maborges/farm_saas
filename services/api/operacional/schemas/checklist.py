from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import uuid


# ---------- Modelo / Template ----------

class ChecklistItemModelo(BaseModel):
    ordem: int
    descricao: str
    obrigatorio: bool = True


class ChecklistModeloCreate(BaseModel):
    nome: str
    tipo_equipamento: Optional[str] = None
    itens: list[ChecklistItemModelo]
    ativo: bool = True


class ChecklistModeloUpdate(BaseModel):
    nome: Optional[str] = None
    tipo_equipamento: Optional[str] = None
    itens: Optional[list[ChecklistItemModelo]] = None
    ativo: Optional[bool] = None


class ChecklistModeloResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    tipo_equipamento: Optional[str]
    itens: list[Any]
    ativo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Realizado / Preenchido ----------

class ChecklistRespostaItem(BaseModel):
    ordem: int
    descricao: str
    status: str  # OK | NOK | NA
    observacao: Optional[str] = None


class ChecklistRealizadoCreate(BaseModel):
    equipamento_id: uuid.UUID
    modelo_id: uuid.UUID
    operador_id: Optional[uuid.UUID] = None
    respostas: list[ChecklistRespostaItem]
    observacoes_gerais: Optional[str] = None


class ChecklistRealizadoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    equipamento_id: uuid.UUID
    modelo_id: uuid.UUID
    operador_id: Optional[uuid.UUID]
    data_hora: datetime
    respostas: list[Any]
    liberado_para_uso: bool
    observacoes_gerais: Optional[str]
    os_gerada_id: Optional[uuid.UUID]
    created_at: datetime

    model_config = {"from_attributes": True}
