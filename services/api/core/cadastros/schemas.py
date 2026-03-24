from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime


# ── Extensões ─────────────────────────────────────────────────────────────────

class ProdutoAgricolaDetalheSchema(BaseModel):
    registro_mapa: Optional[str] = None
    classe_agronomica: Optional[str] = None
    principio_ativo: Optional[str] = None
    formulacao: Optional[str] = None
    periodo_carencia_dias: Optional[int] = None
    cultivar: Optional[str] = None
    cultura: Optional[str] = None


class ProdutoEstoqueDetalheSchema(BaseModel):
    localizacao_default: Optional[str] = None
    peso_unitario_kg: Optional[float] = None
    volume_unitario_l: Optional[float] = None
    perecivel: bool = False
    prazo_validade_dias: Optional[int] = None
    ncm: Optional[str] = None


# ── Produto Catálogo ───────────────────────────────────────────────────────────

class ProdutoCatalogoCreate(BaseModel):
    nome: str
    tipo: str = "OUTROS"
    unidade_medida: str = "UN"
    codigo_interno: Optional[str] = None
    sku: Optional[str] = None
    descricao: Optional[str] = None
    estoque_minimo: float = 0.0
    preco_medio: float = 0.0
    ativo: bool = True
    detalhe_agricola: Optional[ProdutoAgricolaDetalheSchema] = None
    detalhe_estoque: Optional[ProdutoEstoqueDetalheSchema] = None


class ProdutoCatalogoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    unidade_medida: Optional[str] = None
    codigo_interno: Optional[str] = None
    sku: Optional[str] = None
    descricao: Optional[str] = None
    estoque_minimo: Optional[float] = None
    preco_medio: Optional[float] = None
    ativo: Optional[bool] = None
    detalhe_agricola: Optional[ProdutoAgricolaDetalheSchema] = None
    detalhe_estoque: Optional[ProdutoEstoqueDetalheSchema] = None


class ProdutoCatalogoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    tipo: str
    unidade_medida: str
    codigo_interno: Optional[str]
    sku: Optional[str]
    descricao: Optional[str]
    estoque_minimo: float
    preco_medio: float
    ativo: bool
    created_at: datetime
    updated_at: datetime
    detalhe_agricola: Optional[ProdutoAgricolaDetalheSchema] = None
    detalhe_estoque: Optional[ProdutoEstoqueDetalheSchema] = None

    model_config = {"from_attributes": True}
