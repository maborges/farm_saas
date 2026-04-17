from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import datetime
import uuid

from .models import UNIDADES_PESO_FIXO, UNIDADES_SEM_PESO_FIXO


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_codigo_format(value: str) -> str:
    """Valida e normaliza o código da commodity."""
    if not value or not value.strip():
        raise ValueError("Código é obrigatório")
    if " " in value:
        raise ValueError("Código não pode conter espaços")
    return value.upper().strip()


# ---------------------------------------------------------------------------
# Commodity
# ---------------------------------------------------------------------------

class CommodityCreate(BaseModel):
    nome: str
    codigo: str
    descricao: Optional[str] = None
    tipo: str
    unidade_padrao: str
    peso_unidade: Optional[float] = None
    umidade_padrao_pct: Optional[float] = None
    impureza_padrao_pct: Optional[float] = None
    possui_cotacao: bool = False
    bolsa_referencia: Optional[str] = None
    codigo_bolsa: Optional[str] = None
    ativo: bool = True

    @field_validator("codigo")
    @classmethod
    def codigo_upper(cls, v: str) -> str:
        return _validate_codigo_format(v)

    @model_validator(mode="after")
    def validate_peso_unidade(self):
        if self.unidade_padrao in UNIDADES_PESO_FIXO:
            if self.peso_unidade is None:
                raise ValueError(
                    f"peso_unidade é obrigatório para unidade {self.unidade_padrao}"
                )
        elif self.unidade_padrao in UNIDADES_SEM_PESO_FIXO:
            if self.peso_unidade is not None:
                raise ValueError(
                    f"peso_unidade não deve ser usado com unidade {self.unidade_padrao}"
                )
        return self


class CommodityUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    unidade_padrao: Optional[str] = None
    peso_unidade: Optional[float] = None
    umidade_padrao_pct: Optional[float] = None
    impureza_padrao_pct: Optional[float] = None
    possui_cotacao: Optional[bool] = None
    bolsa_referencia: Optional[str] = None
    codigo_bolsa: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("codigo")
    @classmethod
    def codigo_upper(cls, v: str | None) -> str | None:
        if v is not None:
            return _validate_codigo_format(v)
        return v

    @model_validator(mode="after")
    def validate_peso_unidade(self):
        unidade = self.unidade_padrao
        peso = self.peso_unidade
        # Só valida se ambos foram informados
        if unidade is not None and peso is not None:
            if unidade in UNIDADES_SEM_PESO_FIXO:
                raise ValueError(
                    f"peso_unidade não deve ser usado com unidade {unidade}"
                )
        return self


class CommodityResponse(BaseModel):
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID]
    nome: str
    codigo: str
    descricao: Optional[str]
    tipo: str
    unidade_padrao: str
    peso_unidade: Optional[float]
    umidade_padrao_pct: Optional[float]
    impureza_padrao_pct: Optional[float]
    possui_cotacao: bool
    bolsa_referencia: Optional[str]
    codigo_bolsa: Optional[str]
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# CommodityClassificacao
# ---------------------------------------------------------------------------

class CommodityClassificacaoCreate(BaseModel):
    classe: str
    descricao: Optional[str] = None
    umidade_max_pct: Optional[float] = None
    impureza_max_pct: Optional[float] = None
    avariados_max_pct: Optional[float] = None
    ardidos_max_pct: Optional[float] = None
    esverdeados_max_pct: Optional[float] = None
    quebrados_max_pct: Optional[float] = None
    desconto_umidade_por_ponto: Optional[float] = None
    desconto_impureza_por_ponto: Optional[float] = None
    parametros_extras: Optional[dict] = None
    ativo: bool = True


class CommodityClassificacaoUpdate(BaseModel):
    classe: Optional[str] = None
    descricao: Optional[str] = None
    umidade_max_pct: Optional[float] = None
    impureza_max_pct: Optional[float] = None
    avariados_max_pct: Optional[float] = None
    ardidos_max_pct: Optional[float] = None
    esverdeados_max_pct: Optional[float] = None
    quebrados_max_pct: Optional[float] = None
    desconto_umidade_por_ponto: Optional[float] = None
    desconto_impureza_por_ponto: Optional[float] = None
    parametros_extras: Optional[dict] = None
    ativo: Optional[bool] = None


class CommodityClassificacaoResponse(BaseModel):
    id: uuid.UUID
    commodity_id: uuid.UUID
    classe: str
    descricao: Optional[str]
    umidade_max_pct: Optional[float]
    impureza_max_pct: Optional[float]
    avariados_max_pct: Optional[float]
    ardidos_max_pct: Optional[float]
    esverdeados_max_pct: Optional[float]
    quebrados_max_pct: Optional[float]
    desconto_umidade_por_ponto: Optional[float]
    desconto_impureza_por_ponto: Optional[float]
    parametros_extras: Optional[dict]
    ativo: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# CotacaoCommodity
# ---------------------------------------------------------------------------

class CotacaoCommodityCreate(BaseModel):
    data: datetime
    preco: float
    moeda: str = "BRL"
    fonte: Optional[str] = None


class CotacaoCommodityUpdate(BaseModel):
    data: Optional[datetime] = None
    preco: Optional[float] = None
    moeda: Optional[str] = None
    fonte: Optional[str] = None


class CotacaoCommodityResponse(BaseModel):
    id: uuid.UUID
    commodity_id: uuid.UUID
    data: datetime
    preco: float
    moeda: str
    fonte: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Commodity com detalhes (classificacoes + ultima cotacao)
# ---------------------------------------------------------------------------

class CommodityDetalhadaResponse(CommodityResponse):
    classificacoes: list[CommodityClassificacaoResponse] = []
    ultima_cotacao: Optional[CotacaoCommodityResponse] = None
