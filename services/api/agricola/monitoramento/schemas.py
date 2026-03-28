from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date, datetime


# ─── Catálogo ────────────────────────────────────────────────────────────────

class MonitoramentoCatalogoCreate(BaseModel):
    tipo: str  # PRAGA | DOENCA | PLANTA_DANINHA
    nome_popular: str
    nome_cientifico: str | None = None
    cultura: str | None = None
    nde_padrao: float | None = None
    unidade_medida: str | None = None
    descricao: str | None = None

class MonitoramentoCatalogoResponse(BaseModel):
    id: UUID
    tipo: str
    nome_popular: str
    nome_cientifico: str | None
    cultura: str | None
    nde_padrao: float | None
    unidade_medida: str | None
    descricao: str | None
    is_system: bool
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


# ─── Monitoramento ────────────────────────────────────────────────────────────

class MonitoramentoPragasCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID
    data_avaliacao: date
    catalogo_id: UUID | None = None
    tipo: str | None = None
    nome_cientifico: str | None = None
    nome_popular: str | None = None
    nivel_infestacao: float | None = None
    unidade_medida: str | None = None
    nde_cultura: float | None = None
    acao_tomada: str | None = None  # CONTROLE | MONITORAR | NENHUMA
    estagio_fenologico_id: UUID | None = None
    estagio_fenologico_codigo: str | None = None
    fotos: list[str] = []
    pontos_coleta: list[dict] = []
    diagnostico_ia: dict | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    observacoes: str | None = None

class MonitoramentoPragasUpdate(BaseModel):
    data_avaliacao: date | None = None
    tipo: str | None = None
    nome_cientifico: str | None = None
    nome_popular: str | None = None
    nivel_infestacao: float | None = None
    unidade_medida: str | None = None
    nde_cultura: float | None = None
    acao_tomada: str | None = None
    fotos: list[str] | None = None
    pontos_coleta: list[dict] | None = None
    diagnostico_ia: dict | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    observacoes: str | None = None

class MonitoramentoPragasResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    safra_id: UUID
    talhao_id: UUID
    data_avaliacao: date
    catalogo_id: UUID | None
    tipo: str | None
    nome_cientifico: str | None
    nome_popular: str | None
    nivel_infestacao: float | None
    unidade_medida: str | None
    nde_cultura: float | None
    atingiu_nde: bool
    acao_tomada: str | None
    estagio_fenologico_codigo: str | None
    estagio_fenologico_id: UUID | None
    fotos: list[str]
    pontos_coleta: list[dict] | None
    diagnostico_ia: dict | None
    tecnico_id: UUID | None
    latitude: float | None
    longitude: float | None
    observacoes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
