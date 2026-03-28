from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date, datetime


# ─── Escalas ─────────────────────────────────────────────────────────────────

class FenologiaEscalaCreate(BaseModel):
    cultura: str
    codigo: str = Field(..., min_length=1, max_length=20)
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: str | None = None
    ordem: int = 0


class FenologiaEscalaUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    ordem: int | None = None
    ativo: bool | None = None


class FenologiaEscalaResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    cultura: str
    codigo: str
    nome: str
    descricao: str | None
    ordem: int
    is_system: bool
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


# ─── Grupos de talhões ────────────────────────────────────────────────────────

class GrupoTalhaoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    cor: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    ordem: int = 0


class GrupoTalhaoUpdate(BaseModel):
    nome: str | None = None
    cor: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    ordem: int | None = None


class GrupoSincronizarTalhoes(BaseModel):
    talhao_ids: list[UUID]


class GrupoItemResponse(BaseModel):
    id: UUID
    talhao_id: UUID

    model_config = ConfigDict(from_attributes=True)


class GrupoTalhaoResponse(BaseModel):
    id: UUID
    safra_id: UUID
    nome: str
    cor: str | None
    ordem: int
    itens: list[GrupoItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class CopiarGruposDeSafra(BaseModel):
    safra_origem_id: UUID


# ─── Registros de fenologia ───────────────────────────────────────────────────

class FenologiaRegistroCreate(BaseModel):
    escala_id: UUID
    data_observacao: date
    observacao: str | None = None
    dados_extras: dict | None = None


class FenologiaRegistroGrupoCreate(FenologiaRegistroCreate):
    grupo_id: UUID


class FenologiaRegistroResponse(BaseModel):
    id: UUID
    safra_id: UUID
    talhao_id: UUID
    grupo_id: UUID | None
    escala_id: UUID
    data_observacao: date
    usuario_id: UUID | None
    observacao: str | None
    dados_extras: dict | None
    created_at: datetime
    escala_codigo: str | None = None
    escala_nome: str | None = None
    escala_ordem: int | None = None

    model_config = ConfigDict(from_attributes=True)
