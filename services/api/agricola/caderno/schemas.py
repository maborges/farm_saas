from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional, Literal


# ─── Fotos ────────────────────────────────────────────────────────────────────

class FotoResponse(BaseModel):
    id: UUID
    url: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_captura: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Entradas ─────────────────────────────────────────────────────────────────

class EntradaCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID
    tipo: str  # MONITORAMENTO | VISITA_TECNICA | EPI_ENTREGA | OBSERVACAO | CLIMA | SOLO
    descricao: str
    data_registro: date
    nivel_severidade: Optional[str] = None
    recomendacao: Optional[str] = None
    numero_receituario: Optional[str] = None
    digitalizacao_retroativa: bool = False
    justificativa_retroativa: Optional[str] = None


class EntradaUpdate(BaseModel):
    descricao: Optional[str] = None
    nivel_severidade: Optional[str] = None
    recomendacao: Optional[str] = None
    numero_receituario: Optional[str] = None


class EntradaDeleteRequest(BaseModel):
    motivo_exclusao: str = Field(..., min_length=10)


class EntradaResponse(BaseModel):
    id: UUID
    safra_id: UUID
    talhao_id: UUID
    tipo: str
    descricao: str
    data_registro: date
    usuario_id: UUID
    operacao_id: Optional[UUID] = None
    nivel_severidade: Optional[str] = None
    recomendacao: Optional[str] = None
    numero_receituario: Optional[str] = None
    excluida: bool
    motivo_exclusao: Optional[str] = None
    digitalizacao_retroativa: bool
    fotos: list[FotoResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Visita Técnica ───────────────────────────────────────────────────────────

class VisitaTecnicaCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID
    nome_rt: str
    crea: str
    data_visita: date
    observacoes: Optional[str] = None
    recomendacoes: Optional[str] = None
    constatacoes: list[dict] = []


class VisitaTecnicaResponse(BaseModel):
    id: UUID
    safra_id: UUID
    talhao_id: UUID
    nome_rt: str
    crea: str
    data_visita: date
    observacoes: Optional[str] = None
    recomendacoes: Optional[str] = None
    constatacoes: list[dict] = []
    assinado: bool
    data_assinatura: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssinarVisitaRequest(BaseModel):
    nome_rt: str
    crea: str


# ─── EPI Entrega ──────────────────────────────────────────────────────────────

class EPIEntregaCreate(BaseModel):
    nome_trabalhador: str
    trabalhador_id: Optional[UUID] = None
    epi_tipo: str
    quantidade: int = 1
    data_entrega: date
    validade: Optional[date] = None
    operacao_id: Optional[UUID] = None


class EPIEntregaResponse(BaseModel):
    id: UUID
    nome_trabalhador: str
    epi_tipo: str
    quantidade: int
    data_entrega: date
    validade: Optional[date] = None
    assinatura_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Exportação ───────────────────────────────────────────────────────────────

ModeloCertificacao = Literal["padrao", "globalgap", "organico", "mapa"]


class ExportacaoCreate(BaseModel):
    safra_id: UUID
    talhao_id: Optional[UUID] = None
    modelo: ModeloCertificacao = "padrao"  # padrao | globalgap | organico | mapa
    modelo_certificacao: Optional[str] = None  # legado — mapeado internamente
    assinado_por: Optional[str] = None
    crea_rt: Optional[str] = None


class ExportacaoResponse(BaseModel):
    id: UUID
    safra_id: UUID
    url_pdf: str
    data_geracao: datetime
    assinado_por: Optional[str] = None
    crea_rt: Optional[str] = None
    crea_validade: Optional[date] = None
    modelo_certificacao: str

    model_config = {"from_attributes": True}


class AssinarExportacaoRequest(BaseModel):
    assinado_por: str = Field(..., min_length=3, max_length=200)
    crea_rt: str = Field(..., min_length=4, max_length=30)
    crea_validade: Optional[date] = None  # Data de validade do CREA


# ─── Timeline (agregada) ──────────────────────────────────────────────────────

class TimelineItem(BaseModel):
    id: UUID
    tipo: str
    subtipo: Optional[str] = None  # para diferenciar entrada manual de operação auto
    descricao: str
    data_registro: date
    talhao_id: UUID
    nivel_severidade: Optional[str] = None
    fotos_count: int = 0
    excluida: bool = False
    origem: str  # "caderno" | "operacao" | "visita"
