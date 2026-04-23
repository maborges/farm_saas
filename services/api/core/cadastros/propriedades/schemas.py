from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Any, List
from datetime import datetime, date
import uuid

from .models import TipoArea, TipoInfraestrutura, FormatoArquivoGeo, StatusProcessamentoGeo


# ---------------------------------------------------------------------------
# AreaRural
# ---------------------------------------------------------------------------

class SumarioAreasResponse(BaseModel):
    area_total_ha: float
    area_produtiva_ha: float
    area_ambiental_ha: float
    area_infraestrutura_ha: float


class AreaRuralCreate(BaseModel):
    nome: str
    tipo: str = TipoArea.GLEBA
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    unidade_produtiva_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    area_hectares: Optional[float] = None
    area_hectares_manual: Optional[float] = None
    geometria: Optional[dict[str, Any]] = None
    centroide_lat: Optional[float] = None
    centroide_lng: Optional[float] = None
    tipo_solo_id: Optional[uuid.UUID] = None
    irrigado: bool = False
    tipo_irrigacao_id: Optional[uuid.UUID] = None
    dados_extras: Optional[dict[str, Any]] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        tipos_validos = {e.value for e in TipoArea}
        if v not in tipos_validos:
            raise ValueError(f"Tipo inválido. Valores aceitos: {sorted(tipos_validos)}")
        return v

    @field_validator("area_hectares", "area_hectares_manual")
    @classmethod
    def area_positiva(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Área deve ser maior que zero")
        return v


class AreaRuralUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    area_hectares: Optional[float] = None
    area_hectares_manual: Optional[float] = None
    geometria: Optional[dict[str, Any]] = None
    centroide_lat: Optional[float] = None
    centroide_lng: Optional[float] = None
    tipo_solo_id: Optional[uuid.UUID] = None
    irrigado: Optional[bool] = None
    tipo_irrigacao_id: Optional[uuid.UUID] = None
    dados_extras: Optional[dict[str, Any]] = None
    ativo: Optional[bool] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        tipos_validos = {e.value for e in TipoArea}
        if v not in tipos_validos:
            raise ValueError(f"Tipo inválido. Valores aceitos: {sorted(tipos_validos)}")
        return v


class AreaRuralResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    unidade_produtiva_id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    tipo: str
    nome: str
    codigo: Optional[str]
    descricao: Optional[str]
    area_hectares: Optional[float]
    area_hectares_manual: Optional[float]
    geometria: Optional[dict[str, Any]]
    centroide_lat: Optional[float]
    centroide_lng: Optional[float]
    tipo_solo_id: Optional[uuid.UUID]
    tipo_solo_nome: Optional[str] = None
    irrigado: bool
    tipo_irrigacao_id: Optional[uuid.UUID]
    tipo_irrigacao_nome: Optional[str] = None
    dados_extras: Optional[dict[str, Any]]
    ativo: bool
    created_at: datetime
    updated_at: datetime
    cultivo_atual: Optional["CultivoResumo"] = None

    model_config = {"from_attributes": True}


class CultivoResumo(BaseModel):
    id: uuid.UUID
    cultura: str
    safra_nome: str
    data_plantio_real: Optional[date]
    status: str
    
    model_config = {"from_attributes": True}


class AreaRuralTree(AreaRuralResponse):
    """Response com filhos aninhados (para endpoint /tree)."""
    filhos: list["AreaRuralTree"] = []


# ---------------------------------------------------------------------------
# MatriculaImovel
# ---------------------------------------------------------------------------

class MatriculaCreate(BaseModel):
    area_id: uuid.UUID
    numero_matricula: str
    cartorio: Optional[str] = None
    comarca: Optional[str] = None
    livro: Optional[str] = None
    folha: Optional[str] = None
    data_registro: Optional[datetime] = None
    area_matricula_ha: Optional[float] = None
    car_numero: Optional[str] = None
    nirf: Optional[str] = None
    incra: Optional[str] = None
    ccir: Optional[str] = None
    sncr: Optional[str] = None
    itr_numero: Optional[str] = None


class MatriculaUpdate(BaseModel):
    numero_matricula: Optional[str] = None
    cartorio: Optional[str] = None
    comarca: Optional[str] = None
    livro: Optional[str] = None
    folha: Optional[str] = None
    data_registro: Optional[datetime] = None
    area_matricula_ha: Optional[float] = None
    car_numero: Optional[str] = None
    nirf: Optional[str] = None
    incra: Optional[str] = None
    ccir: Optional[str] = None
    sncr: Optional[str] = None
    itr_numero: Optional[str] = None
    ativo: Optional[bool] = None


class MatriculaResponse(BaseModel):
    id: uuid.UUID
    area_id: uuid.UUID
    numero_matricula: str
    cartorio: Optional[str]
    comarca: Optional[str]
    livro: Optional[str]
    folha: Optional[str]
    data_registro: Optional[datetime]
    area_matricula_ha: Optional[float]
    car_numero: Optional[str]
    nirf: Optional[str]
    incra: Optional[str]
    ccir: Optional[str]
    sncr: Optional[str]
    itr_numero: Optional[str]
    ativo: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# RegistroAmbiental
# ---------------------------------------------------------------------------

TIPOS_REGISTRO_AMBIENTAL = {
    "CAR_APP", "CAR_RL", "LICENCA_IBAMA", "AIA", "OUTORGA_AGUA", "OUTRO"
}


class RegistroAmbientalCreate(BaseModel):
    area_id: uuid.UUID
    tipo_registro: str
    numero: Optional[str] = None
    orgao: Optional[str] = None
    data_emissao: Optional[datetime] = None
    data_validade: Optional[datetime] = None
    link_documento: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("tipo_registro")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        if v not in TIPOS_REGISTRO_AMBIENTAL:
            raise ValueError(f"Tipo inválido. Valores aceitos: {sorted(TIPOS_REGISTRO_AMBIENTAL)}")
        return v


class RegistroAmbientalUpdate(BaseModel):
    tipo_registro: Optional[str] = None
    numero: Optional[str] = None
    orgao: Optional[str] = None
    data_emissao: Optional[datetime] = None
    data_validade: Optional[datetime] = None
    link_documento: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class RegistroAmbientalResponse(BaseModel):
    id: uuid.UUID
    area_id: uuid.UUID
    tipo_registro: str
    numero: Optional[str]
    orgao: Optional[str]
    data_emissao: Optional[datetime]
    data_validade: Optional[datetime]
    link_documento: Optional[str]
    observacoes: Optional[str]
    ativo: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ValorPatrimonial
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Infraestrutura
# ---------------------------------------------------------------------------

class InfraestruturaCreate(BaseModel):
    area_rural_id: Optional[uuid.UUID] = None  # injetado via path param pelo router
    nome: str
    tipo: str
    capacidade: Optional[float] = None
    unidade_capacidade: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    observacoes: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        tipos_validos = {e.value for e in TipoInfraestrutura}
        if v not in tipos_validos:
            raise ValueError(f"Tipo inválido. Valores aceitos: {sorted(tipos_validos)}")
        return v


class InfraestruturaUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    capacidade: Optional[float] = None
    unidade_capacidade: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    observacoes: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        tipos_validos = {e.value for e in TipoInfraestrutura}
        if v not in tipos_validos:
            raise ValueError(f"Tipo inválido. Valores aceitos: {sorted(tipos_validos)}")
        return v


class InfraestruturaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    area_rural_id: uuid.UUID
    nome: str
    tipo: str
    capacidade: Optional[float]
    unidade_capacidade: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    observacoes: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ArquivoGeo
# ---------------------------------------------------------------------------

class ArquivoGeoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    area_rural_id: uuid.UUID
    uploaded_by: Optional[uuid.UUID]
    nome_arquivo: str
    formato: str
    tamanho_bytes: int
    storage_backend: str
    storage_path: str
    status: str
    poligonos_extraidos: Optional[int]
    area_ha_extraida: Optional[float]
    erro_msg: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ArquivoGeoProcessadoResponse(BaseModel):
    """Retorno do endpoint de upload incluindo polígonos extraídos."""
    arquivo: ArquivoGeoResponse
    poligonos: Optional[Any] = None  # GeoJSON extraído para preview


METODOS_AVALIACAO = {"MERCADO", "CUSTO", "RENDA", "DECLARADO", "LAUDO"}


class ValorPatrimonialCreate(BaseModel):
    area_id: uuid.UUID
    data_avaliacao: datetime
    metodo: str = "DECLARADO"
    valor_terra_nua: Optional[float] = None
    valor_benfeitorias: Optional[float] = None
    valor_lavoura_perene: Optional[float] = None
    valor_total: Optional[float] = None
    moeda: str = "BRL"
    responsavel: Optional[str] = None
    numero_laudo: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("metodo")
    @classmethod
    def validar_metodo(cls, v: str) -> str:
        if v not in METODOS_AVALIACAO:
            raise ValueError(f"Método inválido. Valores aceitos: {sorted(METODOS_AVALIACAO)}")
        return v

    @field_validator("valor_terra_nua", "valor_benfeitorias", "valor_lavoura_perene", "valor_total")
    @classmethod
    def valor_positivo(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Valor não pode ser negativo")
        return v


class ValorPatrimonialUpdate(BaseModel):
    data_avaliacao: Optional[datetime] = None
    metodo: Optional[str] = None
    valor_terra_nua: Optional[float] = None
    valor_benfeitorias: Optional[float] = None
    valor_lavoura_perene: Optional[float] = None
    valor_total: Optional[float] = None
    moeda: Optional[str] = None
    responsavel: Optional[str] = None
    numero_laudo: Optional[str] = None
    observacoes: Optional[str] = None


class ValorPatrimonialResponse(BaseModel):
    id: uuid.UUID
    area_id: uuid.UUID
    data_avaliacao: datetime
    metodo: str
    valor_terra_nua: Optional[float]
    valor_benfeitorias: Optional[float]
    valor_lavoura_perene: Optional[float]
    valor_total: Optional[float]
    moeda: str
    responsavel: Optional[str]
    numero_laudo: Optional[str]
    observacoes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Schemas de Hierarquia Completa (Propriedade → Fazenda → Áreas)
# ---------------------------------------------------------------------------

class FazendaHierarquiaResponse(BaseModel):
    """Resposta de uma fazenda com sua hierarquia de áreas rurais."""
    unidade_produtiva_id: uuid.UUID
    exploracao_id: uuid.UUID
    natureza: str
    data_inicio: datetime
    data_fim: Optional[datetime]
    areas: list["AreaRuralTreeResponse"] = []


class PropriedadeComHierarquiaResponse(BaseModel):
    """
    Resposta completa da propriedade com toda hierarquia.
    
    Inclui:
    - Dados da propriedade econômica
    - Lista de fazendas vinculadas (via ExploracaoRural)
    - Para cada fazenda: árvore de áreas rurais (Glebas → Talhões → Piquetes)
    """
    propriedade: "PropriedadeResponse"
    fazendas: list[FazendaHierarquiaResponse] = []


# ---------------------------------------------------------------------------
# Seletores / Lookup
# ---------------------------------------------------------------------------

class TipoSoloResponse(BaseModel):
    id: uuid.UUID
    nome: str
    descricao: Optional[str] = None
    retencao_agua: str
    lixiviacao: str
    ctc_resumo: str
    ativo: bool

    model_config = {"from_attributes": True}


class TipoIrrigacaoResponse(BaseModel):
    id: uuid.UUID
    nome: str
    metodo: Optional[str] = None
    descricao: Optional[str] = None
    ativo: bool

    model_config = {"from_attributes": True}


# Forward references
AreaRuralTreeResponse = AreaRuralTree
