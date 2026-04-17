from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import uuid


# ---------------------------------------------------------------------------
# Marca
# ---------------------------------------------------------------------------

class MarcaCreate(BaseModel):
    nome: str
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    pais_origem: Optional[str] = "Brasil"
    website: Optional[str] = None
    observacoes: Optional[str] = None


class MarcaUpdate(BaseModel):
    nome: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    pais_origem: Optional[str] = None
    website: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class MarcaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID]  # Nullable for system marcas
    nome: str
    nome_fantasia: Optional[str]
    cnpj: Optional[str]
    pais_origem: Optional[str]
    website: Optional[str]
    observacoes: Optional[str]
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ModeloProduto
# ---------------------------------------------------------------------------

class ModeloProdutoCreate(BaseModel):
    marca_id: uuid.UUID
    nome: str
    referencia: Optional[str] = None
    descricao: Optional[str] = None
    tipo_produto: Optional[str] = None


class ModeloProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    referencia: Optional[str] = None
    descricao: Optional[str] = None
    tipo_produto: Optional[str] = None
    ativo: Optional[bool] = None


class ModeloProdutoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID]  # Nullable for system models
    marca_id: uuid.UUID
    nome: str
    referencia: Optional[str]
    descricao: Optional[str]
    tipo_produto: Optional[str]
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ModeloProdutoComMarcaResponse(ModeloProdutoResponse):
    marca_nome: Optional[str] = None

    @classmethod
    def from_orm_with_marca(cls, obj: Any) -> "ModeloProdutoComMarcaResponse":
        data = cls.model_validate(obj)
        if obj.marca:
            data.marca_nome = obj.marca.nome
        return data


# ---------------------------------------------------------------------------
# CategoriaProduto
# ---------------------------------------------------------------------------

class CategoriaProdutoCreate(BaseModel):
    parent_id: Optional[uuid.UUID] = None
    nome: str
    descricao: Optional[str] = None
    cor: Optional[str] = None
    icone: Optional[str] = None
    ordem: int = 0


class CategoriaProdutoUpdate(BaseModel):
    parent_id: Optional[uuid.UUID] = None
    nome: Optional[str] = None
    descricao: Optional[str] = None
    cor: Optional[str] = None
    icone: Optional[str] = None
    ordem: Optional[int] = None
    ativo: Optional[bool] = None


class CategoriaProdutoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID]  # Nullable for system categories
    parent_id: Optional[uuid.UUID]
    nome: str
    descricao: Optional[str]
    cor: Optional[str]
    icone: Optional[str]
    ordem: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Produto
# ---------------------------------------------------------------------------

class ProdutoAgricolaCreate(BaseModel):
    registro_mapa: Optional[str] = None
    classe_agronomica: Optional[str] = None
    classe_toxicologica: Optional[str] = None
    principio_ativo: Optional[str] = None
    formulacao: Optional[str] = None
    periodo_carencia_dias: Optional[int] = None
    intervalo_reentrada_horas: Optional[int] = None
    epi_obrigatorio: Optional[list] = None
    cultivar: Optional[str] = None
    cultura_alvo: Optional[str] = None
    tsi: bool = False
    pureza_pct: Optional[float] = None
    germinacao_pct: Optional[float] = None
    composicao_npk: Optional[str] = None
    densidade_g_ml: Optional[float] = None


class ProdutoAgricolaResponse(ProdutoAgricolaCreate):
    id: uuid.UUID
    produto_id: uuid.UUID
    model_config = {"from_attributes": True}


class ProdutoEstoqueCreate(BaseModel):
    localizacao_default: Optional[str] = None
    peso_unitario_kg: Optional[float] = None
    volume_unitario_l: Optional[float] = None
    perecivel: bool = False
    prazo_validade_dias: Optional[int] = None
    ncm: Optional[str] = None
    requer_receituario: bool = False
    lote_controlado: bool = False


class ProdutoEstoqueResponse(ProdutoEstoqueCreate):
    id: uuid.UUID
    produto_id: uuid.UUID
    model_config = {"from_attributes": True}


class ProdutoEPICreate(BaseModel):
    ca_numero: Optional[str] = None
    ca_validade: Optional[datetime] = None
    tipo_protecao: Optional[str] = None
    vida_util_meses: Optional[int] = None
    tamanho: Optional[str] = None


class ProdutoEPIResponse(ProdutoEPICreate):
    id: uuid.UUID
    produto_id: uuid.UUID
    model_config = {"from_attributes": True}


class ProdutoCreate(BaseModel):
    nome: str
    tipo: str
    unidade_medida: str = "UN"
    codigo_interno: Optional[str] = None
    sku: Optional[str] = None
    codigo_barras: Optional[str] = None
    descricao: Optional[str] = None
    marca_id: Optional[uuid.UUID] = None
    modelo_id: Optional[uuid.UUID] = None
    marca: Optional[str] = None
    fabricante: Optional[str] = None
    referencia_fabricante: Optional[str] = None
    categoria_id: Optional[uuid.UUID] = None
    imagem_url: Optional[str] = None
    qtd_conteudo: Optional[float] = None
    unidade_conteudo: Optional[str] = None
    estoque_minimo: float = 0.0
    preco_medio: float = 0.0
    preco_ultima_compra: Optional[float] = None
    dados_extras: Optional[dict[str, Any]] = None
    # Extensões opcionais inline
    detalhe_agricola: Optional[ProdutoAgricolaCreate] = None
    detalhe_estoque: Optional[ProdutoEstoqueCreate] = None
    detalhe_epi: Optional[ProdutoEPICreate] = None


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    unidade_medida: Optional[str] = None
    codigo_interno: Optional[str] = None
    sku: Optional[str] = None
    codigo_barras: Optional[str] = None
    descricao: Optional[str] = None
    marca_id: Optional[uuid.UUID] = None
    modelo_id: Optional[uuid.UUID] = None
    marca: Optional[str] = None
    fabricante: Optional[str] = None
    referencia_fabricante: Optional[str] = None
    categoria_id: Optional[uuid.UUID] = None
    imagem_url: Optional[str] = None
    qtd_conteudo: Optional[float] = None
    unidade_conteudo: Optional[str] = None
    estoque_minimo: Optional[float] = None
    preco_medio: Optional[float] = None
    preco_ultima_compra: Optional[float] = None
    dados_extras: Optional[dict[str, Any]] = None
    ativo: Optional[bool] = None


class ProdutoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    tipo: str
    unidade_medida: str
    codigo_interno: Optional[str]
    sku: Optional[str]
    codigo_barras: Optional[str]
    descricao: Optional[str]
    marca_id: Optional[uuid.UUID]
    modelo_id: Optional[uuid.UUID]
    marca: Optional[str]
    fabricante: Optional[str]
    referencia_fabricante: Optional[str]
    categoria_id: Optional[uuid.UUID]
    imagem_url: Optional[str]
    qtd_conteudo: Optional[float]
    unidade_conteudo: Optional[str]
    estoque_minimo: float
    preco_medio: float
    preco_ultima_compra: Optional[float]
    dados_extras: Optional[dict[str, Any]]
    ativo: bool
    created_at: datetime
    updated_at: datetime
    # Dados desnormalizados para leitura
    marca_nome: Optional[str] = None
    modelo_nome: Optional[str] = None
    categoria_nome: Optional[str] = None
    detalhe_agricola: Optional[ProdutoAgricolaResponse] = None
    detalhe_estoque: Optional[ProdutoEstoqueResponse] = None
    detalhe_epi: Optional[ProdutoEPIResponse] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ProdutoCultura — catálogo de culturas agrícolas
# ---------------------------------------------------------------------------

class ProdutoCulturaCreate(BaseModel):
    nome: str
    nome_cientifico: Optional[str] = None
    grupo: Optional[str] = None  # GRAOS | FIBRAS | FRUTAS | HORTALICAS | PASTAGEM | OUTRO
    ciclo_dias_min: Optional[int] = None
    ciclo_dias_max: Optional[int] = None
    espacamento_cm: Optional[float] = None
    populacao_plantas_ha: Optional[int] = None
    produtividade_media_sc_ha: Optional[float] = None
    dados_extras: Optional[dict] = None


class ProdutoCulturaUpdate(BaseModel):
    nome: Optional[str] = None
    nome_cientifico: Optional[str] = None
    grupo: Optional[str] = None
    ciclo_dias_min: Optional[int] = None
    ciclo_dias_max: Optional[int] = None
    espacamento_cm: Optional[float] = None
    populacao_plantas_ha: Optional[int] = None
    produtividade_media_sc_ha: Optional[float] = None
    dados_extras: Optional[dict] = None
    ativa: Optional[bool] = None


class ProdutoCulturaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID]
    sistema: bool
    nome: str
    nome_cientifico: Optional[str]
    grupo: Optional[str]
    ciclo_dias_min: Optional[int]
    ciclo_dias_max: Optional[int]
    espacamento_cm: Optional[float]
    populacao_plantas_ha: Optional[int]
    produtividade_media_sc_ha: Optional[float]
    dados_extras: Optional[dict]
    ativa: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
