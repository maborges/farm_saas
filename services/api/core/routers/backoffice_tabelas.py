"""
Backoffice — Tabelas Padrão do Sistema

Gerencia registros com tenant_id=NULL e sistema=True que são disponibilizados
para todos os tenants como valores padrão (Marcas, Modelos, Categorias de Produto).
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.dependencies import get_session, get_current_admin
from core.exceptions import EntityNotFoundError
from core.cadastros.produtos.models import Marca, ModeloProduto, CategoriaProduto, ProdutoCultura
from core.cadastros.commodities.models import Commodity
from agricola.checklist.models import ChecklistTemplate
from agricola.monitoramento.catalogo_model import MonitoramentoCatalogo

router = APIRouter(
    prefix="/backoffice/tabelas",
    tags=["Backoffice — Tabelas Padrão"],
    dependencies=[Depends(get_current_admin)],
)


# ---------------------------------------------------------------------------
# Schemas inline (simples, sem camada extra de schemas)
# ---------------------------------------------------------------------------

class MarcaSistemaCreate(BaseModel):
    nome: str
    nome_fantasia: Optional[str] = None
    pais_origem: Optional[str] = "Brasil"
    website: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: bool = True

class MarcaSistemaUpdate(BaseModel):
    nome: Optional[str] = None
    nome_fantasia: Optional[str] = None
    pais_origem: Optional[str] = None
    website: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None

class ModeloSistemaCreate(BaseModel):
    marca_id: uuid.UUID
    nome: str
    referencia: Optional[str] = None
    descricao: Optional[str] = None
    tipo_produto: Optional[str] = None
    ativo: bool = True

class ModeloSistemaUpdate(BaseModel):
    nome: Optional[str] = None
    referencia: Optional[str] = None
    descricao: Optional[str] = None
    tipo_produto: Optional[str] = None
    ativo: Optional[bool] = None

class CategoriaSistemaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    cor: Optional[str] = None
    icone: Optional[str] = None
    ordem: int = 0
    ativo: bool = True

class CategoriaSistemaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    cor: Optional[str] = None
    icone: Optional[str] = None
    ordem: Optional[int] = None
    ativo: Optional[bool] = None


# ===========================================================================
# Marcas do Sistema
# ===========================================================================

@router.get("/marcas")
async def listar_marcas_sistema(
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Marca).where(Marca.tenant_id.is_(None)).order_by(Marca.nome)
    if ativo is not None:
        stmt = stmt.where(Marca.ativo == ativo)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/marcas", status_code=201)
async def criar_marca_sistema(
    data: MarcaSistemaCreate,
    session: AsyncSession = Depends(get_session),
):
    obj = Marca(tenant_id=None, sistema=True, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.patch("/marcas/{marca_id}")
async def atualizar_marca_sistema(
    marca_id: uuid.UUID,
    data: MarcaSistemaUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Marca).where(Marca.id == marca_id, Marca.tenant_id.is_(None))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Marca não encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/marcas/{marca_id}", status_code=204)
async def remover_marca_sistema(
    marca_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    from core.exceptions import BusinessRuleError

    result = await session.execute(
        select(Marca).where(Marca.id == marca_id, Marca.tenant_id.is_(None))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Marca não encontrada")

    # Verifica se há modelos vinculados
    modelos_count = await session.execute(
        select(ModeloProduto).where(ModeloProduto.marca_id == marca_id)
    )
    if modelos_count.scalar_one_or_none():
        raise BusinessRuleError("Não é possível excluir marca com modelos vinculados. Exclua os modelos primeiro.")

    await session.delete(obj)
    await session.commit()


# ===========================================================================
# Modelos do Sistema
# ===========================================================================

def _enrich_modelo_sistema(obj: ModeloProduto) -> dict:
    """Adiciona marca_nome ao response."""
    # Como não tem schema ModeloResponse aqui, usamos dict
    return {
        "id": str(obj.id),
        "marca_id": str(obj.marca_id),
        "marca_nome": obj.marca.nome if obj.marca else None,
        "nome": obj.nome,
        "referencia": obj.referencia,
        "descricao": obj.descricao,
        "tipo_produto": obj.tipo_produto,
        "ativo": obj.ativo,
        "created_at": obj.created_at,
        "updated_at": obj.updated_at,
    }


@router.get("/modelos")
async def listar_modelos_sistema(
    marca_id: Optional[uuid.UUID] = Query(None),
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(ModeloProduto)
        .where(ModeloProduto.tenant_id.is_(None))
        .options(selectinload(ModeloProduto.marca))
        .order_by(ModeloProduto.nome)
    )
    if marca_id:
        stmt = stmt.where(ModeloProduto.marca_id == marca_id)
    if ativo is not None:
        stmt = stmt.where(ModeloProduto.ativo == ativo)
    result = await session.execute(stmt)
    return [_enrich_modelo_sistema(o) for o in result.scalars().all()]


@router.post("/modelos", status_code=201)
async def criar_modelo_sistema(
    data: ModeloSistemaCreate,
    session: AsyncSession = Depends(get_session),
):
    # Valida que a marca é do sistema
    marca = (await session.execute(
        select(Marca).where(Marca.id == data.marca_id, Marca.tenant_id.is_(None))
    )).scalar_one_or_none()
    if not marca:
        raise EntityNotFoundError("Marca do sistema não encontrada")
    obj = ModeloProduto(tenant_id=None, sistema=True, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.patch("/modelos/{modelo_id}")
async def atualizar_modelo_sistema(
    modelo_id: uuid.UUID,
    data: ModeloSistemaUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ModeloProduto).where(ModeloProduto.id == modelo_id, ModeloProduto.tenant_id.is_(None))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Modelo não encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/modelos/{modelo_id}", status_code=204)
async def remover_modelo_sistema(
    modelo_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ModeloProduto).where(ModeloProduto.id == modelo_id, ModeloProduto.tenant_id.is_(None))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Modelo não encontrado")
    await session.delete(obj)
    await session.commit()


# ===========================================================================
# Categorias do Sistema
# ===========================================================================

@router.get("/categorias-produto")
async def listar_categorias_sistema(
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(CategoriaProduto)
        .where(CategoriaProduto.tenant_id.is_(None))
        .order_by(CategoriaProduto.ordem, CategoriaProduto.nome)
    )
    if ativo is not None:
        stmt = stmt.where(CategoriaProduto.ativo == ativo)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/categorias-produto", status_code=201)
async def criar_categoria_sistema(
    data: CategoriaSistemaCreate,
    session: AsyncSession = Depends(get_session),
):
    obj = CategoriaProduto(tenant_id=None, sistema=True, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.patch("/categorias-produto/{cat_id}")
async def atualizar_categoria_sistema(
    cat_id: uuid.UUID,
    data: CategoriaSistemaUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(CategoriaProduto).where(CategoriaProduto.id == cat_id, CategoriaProduto.tenant_id.is_(None))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Categoria não encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/categorias-produto/{cat_id}", status_code=204)
async def remover_categoria_sistema(
    cat_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(CategoriaProduto).where(CategoriaProduto.id == cat_id, CategoriaProduto.tenant_id.is_(None))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Categoria não encontrada")
    await session.delete(obj)
    await session.commit()


# ===========================================================================
# Culturas do Sistema (tenant_id=NULL, sistema=True)
# ===========================================================================

class CulturaSistemaCreate(BaseModel):
    nome: str
    nome_cientifico: Optional[str] = None
    grupo: Optional[str] = None
    ciclo_dias_min: Optional[int] = None
    ciclo_dias_max: Optional[int] = None
    espacamento_cm: Optional[float] = None
    produtividade_media_sc_ha: Optional[float] = None
    ativa: bool = True

class CulturaSistemaUpdate(BaseModel):
    nome: Optional[str] = None
    nome_cientifico: Optional[str] = None
    grupo: Optional[str] = None
    ciclo_dias_min: Optional[int] = None
    ciclo_dias_max: Optional[int] = None
    espacamento_cm: Optional[float] = None
    produtividade_media_sc_ha: Optional[float] = None
    ativa: Optional[bool] = None


@router.get("/culturas")
async def listar_culturas_sistema(
    ativa: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ProdutoCultura).where(ProdutoCultura.tenant_id.is_(None)).order_by(ProdutoCultura.nome)
    if ativa is not None:
        stmt = stmt.where(ProdutoCultura.ativa == ativa)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/culturas", status_code=201)
async def criar_cultura_sistema(data: CulturaSistemaCreate, session: AsyncSession = Depends(get_session)):
    obj = ProdutoCultura(tenant_id=None, sistema=True, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.patch("/culturas/{cultura_id}")
async def atualizar_cultura_sistema(
    cultura_id: uuid.UUID, data: CulturaSistemaUpdate, session: AsyncSession = Depends(get_session),
):
    obj = (await session.execute(select(ProdutoCultura).where(ProdutoCultura.id == cultura_id, ProdutoCultura.tenant_id.is_(None)))).scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Cultura não encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit(); await session.refresh(obj)
    return obj


@router.delete("/culturas/{cultura_id}", status_code=204)
async def remover_cultura_sistema(cultura_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    obj = (await session.execute(select(ProdutoCultura).where(ProdutoCultura.id == cultura_id, ProdutoCultura.tenant_id.is_(None)))).scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Cultura não encontrada")
    await session.delete(obj); await session.commit()


# ===========================================================================
# Commodities do Sistema (tenant_id=NULL, sistema=True)
# ===========================================================================

class CommoditySistemaCreate(BaseModel):
    nome: str
    codigo: str
    tipo: str
    unidade_padrao: str = "SACA_60KG"
    peso_unidade: Optional[float] = None
    possui_cotacao: bool = False
    bolsa_referencia: Optional[str] = None
    codigo_bolsa: Optional[str] = None
    descricao: Optional[str] = None
    ativo: bool = True

class CommoditySistemaUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    tipo: Optional[str] = None
    unidade_padrao: Optional[str] = None
    peso_unidade: Optional[float] = None
    possui_cotacao: Optional[bool] = None
    bolsa_referencia: Optional[str] = None
    codigo_bolsa: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None


@router.get("/commodities")
async def listar_commodities_sistema(
    ativo: Optional[bool] = Query(None),
    tipo: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Commodity).where(Commodity.tenant_id.is_(None)).order_by(Commodity.nome)
    if ativo is not None:
        stmt = stmt.where(Commodity.ativo == ativo)
    if tipo:
        stmt = stmt.where(Commodity.tipo == tipo)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/commodities", status_code=201)
async def criar_commodity_sistema(data: CommoditySistemaCreate, session: AsyncSession = Depends(get_session)):
    obj = Commodity(tenant_id=None, sistema=True, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.patch("/commodities/{commodity_id}")
async def atualizar_commodity_sistema(
    commodity_id: uuid.UUID, data: CommoditySistemaUpdate, session: AsyncSession = Depends(get_session),
):
    obj = (await session.execute(select(Commodity).where(Commodity.id == commodity_id, Commodity.tenant_id.is_(None)))).scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Commodity não encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit(); await session.refresh(obj)
    return obj


@router.delete("/commodities/{commodity_id}", status_code=204)
async def remover_commodity_sistema(commodity_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    obj = (await session.execute(select(Commodity).where(Commodity.id == commodity_id, Commodity.tenant_id.is_(None)))).scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Commodity não encontrada")
    await session.delete(obj); await session.commit()


# ===========================================================================
# Checklist Templates do Sistema (tenant_id=NULL, is_system=True)
# ===========================================================================

class ChecklistTemplateSistemaCreate(BaseModel):
    cultura: Optional[str] = None
    fase: str
    titulo: str
    descricao: Optional[str] = None
    obrigatorio: bool = False
    ordem: int = 0

class ChecklistTemplateSistemaUpdate(BaseModel):
    cultura: Optional[str] = None
    fase: Optional[str] = None
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    obrigatorio: Optional[bool] = None
    ordem: Optional[int] = None
    ativo: Optional[bool] = None


@router.get("/checklist-templates")
async def listar_checklist_templates_sistema(
    cultura: Optional[str] = Query(None),
    fase: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ChecklistTemplate).where(ChecklistTemplate.tenant_id.is_(None)).order_by(ChecklistTemplate.fase, ChecklistTemplate.ordem)
    if cultura:
        stmt = stmt.where(ChecklistTemplate.cultura == cultura)
    if fase:
        stmt = stmt.where(ChecklistTemplate.fase == fase)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/checklist-templates", status_code=201)
async def criar_checklist_template_sistema(data: ChecklistTemplateSistemaCreate, session: AsyncSession = Depends(get_session)):
    obj = ChecklistTemplate(tenant_id=None, is_system=True, ativo=True, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.patch("/checklist-templates/{template_id}")
async def atualizar_checklist_template_sistema(
    template_id: uuid.UUID, data: ChecklistTemplateSistemaUpdate, session: AsyncSession = Depends(get_session),
):
    obj = (await session.execute(select(ChecklistTemplate).where(ChecklistTemplate.id == template_id, ChecklistTemplate.tenant_id.is_(None)))).scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Template não encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit(); await session.refresh(obj)
    return obj


@router.delete("/checklist-templates/{template_id}", status_code=204)
async def remover_checklist_template_sistema(template_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    obj = (await session.execute(select(ChecklistTemplate).where(ChecklistTemplate.id == template_id, ChecklistTemplate.tenant_id.is_(None)))).scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Template não encontrado")
    await session.delete(obj); await session.commit()


# ===========================================================================
# Catálogo de Monitoramento do Sistema (tenant_id=NULL, is_system=True)
# ===========================================================================

class MonitoramentoCatalogoSistemaCreate(BaseModel):
    tipo: str
    nome_popular: str
    nome_cientifico: Optional[str] = None
    cultura: Optional[str] = None
    nde_padrao: Optional[float] = None
    unidade_medida: Optional[str] = None
    descricao: Optional[str] = None
    ativo: bool = True

class MonitoramentoCatalogoSistemaUpdate(BaseModel):
    tipo: Optional[str] = None
    nome_popular: Optional[str] = None
    nome_cientifico: Optional[str] = None
    cultura: Optional[str] = None
    nde_padrao: Optional[float] = None
    unidade_medida: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None


@router.get("/monitoramento-catalogo")
async def listar_monitoramento_catalogo_sistema(
    tipo: Optional[str] = Query(None),
    cultura: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(MonitoramentoCatalogo).where(MonitoramentoCatalogo.tenant_id.is_(None)).order_by(MonitoramentoCatalogo.tipo, MonitoramentoCatalogo.nome_popular)
    if tipo:
        stmt = stmt.where(MonitoramentoCatalogo.tipo == tipo)
    if cultura:
        stmt = stmt.where(or_(MonitoramentoCatalogo.cultura == cultura, MonitoramentoCatalogo.cultura.is_(None)))
    if ativo is not None:
        stmt = stmt.where(MonitoramentoCatalogo.ativo == ativo)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/monitoramento-catalogo", status_code=201)
async def criar_monitoramento_catalogo_sistema(data: MonitoramentoCatalogoSistemaCreate, session: AsyncSession = Depends(get_session)):
    obj = MonitoramentoCatalogo(tenant_id=None, is_system=True, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.patch("/monitoramento-catalogo/{catalogo_id}")
async def atualizar_monitoramento_catalogo_sistema(
    catalogo_id: uuid.UUID, data: MonitoramentoCatalogoSistemaUpdate, session: AsyncSession = Depends(get_session),
):
    obj = (await session.execute(select(MonitoramentoCatalogo).where(MonitoramentoCatalogo.id == catalogo_id, MonitoramentoCatalogo.tenant_id.is_(None)))).scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Entrada do catálogo não encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit(); await session.refresh(obj)
    return obj


@router.delete("/monitoramento-catalogo/{catalogo_id}", status_code=204)
async def remover_monitoramento_catalogo_sistema(catalogo_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    obj = (await session.execute(select(MonitoramentoCatalogo).where(MonitoramentoCatalogo.id == catalogo_id, MonitoramentoCatalogo.tenant_id.is_(None)))).scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Entrada do catálogo não encontrada")
    await session.delete(obj); await session.commit()
