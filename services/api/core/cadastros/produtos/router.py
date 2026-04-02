import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from core.dependencies import get_session, get_tenant_id
from core.exceptions import EntityNotFoundError
from .models import Marca, ModeloProduto, CategoriaProduto, Produto, ProdutoAgricola, ProdutoEstoque, ProdutoEPI
from .schemas import (
    MarcaCreate, MarcaUpdate, MarcaResponse,
    ModeloProdutoCreate, ModeloProdutoUpdate, ModeloProdutoResponse, ModeloProdutoComMarcaResponse,
    CategoriaProdutoCreate, CategoriaProdutoUpdate, CategoriaProdutoResponse,
    ProdutoCreate, ProdutoUpdate, ProdutoResponse,
)

router = APIRouter(tags=["Cadastros — Produtos"])


# ===========================================================================
# Marcas
# ===========================================================================

@router.get("/cadastros/marcas", response_model=list[MarcaResponse])
@router.get("/cadastros/marcas/", response_model=list[MarcaResponse])
async def listar_marcas(
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(Marca).where(
        or_(Marca.tenant_id.is_(None), Marca.tenant_id == tenant_id)
    ).order_by(Marca.nome)
    if ativo is not None:
        stmt = stmt.where(Marca.ativo == ativo)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/cadastros/marcas", response_model=MarcaResponse, status_code=201)
@router.post("/cadastros/marcas/", response_model=MarcaResponse, status_code=201)
async def criar_marca(
    data: MarcaCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    obj = Marca(tenant_id=tenant_id, sistema=False, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/cadastros/marcas/{marca_id}", response_model=MarcaResponse)
async def obter_marca(
    marca_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Marca).where(Marca.id == marca_id, Marca.tenant_id == tenant_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Marca não encontrada")
    return obj


@router.patch("/cadastros/marcas/{marca_id}", response_model=MarcaResponse)
async def atualizar_marca(
    marca_id: uuid.UUID,
    data: MarcaUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Marca).where(Marca.id == marca_id, Marca.tenant_id == tenant_id, Marca.sistema == False)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Marca não encontrada ou não editável")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/cadastros/marcas/{marca_id}", status_code=204)
async def remover_marca(
    marca_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    from core.exceptions import BusinessRuleError

    result = await session.execute(
        select(Marca).where(Marca.id == marca_id, Marca.tenant_id == tenant_id, Marca.sistema == False)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Marca não encontrada ou não editável")

    # Verifica se há modelos vinculados
    modelos_count = await session.execute(
        select(ModeloProduto).where(ModeloProduto.marca_id == marca_id)
    )
    if modelos_count.scalar_one_or_none():
        raise BusinessRuleError("Não é possível excluir marca com modelos vinculados. Desative os modelos primeiro.")

    obj.ativo = False
    await session.commit()


# ===========================================================================
# Modelos
# ===========================================================================

def _enrich_modelo(obj: ModeloProduto) -> dict:
    """Adiciona campos desnormalizados ao response de Modelo."""
    data = ModeloProdutoResponse.model_validate(obj).model_dump()
    if obj.marca:
        data["marca_nome"] = obj.marca.nome
    return data


@router.get("/cadastros/modelos-produto", response_model=list[ModeloProdutoComMarcaResponse])
@router.get("/cadastros/modelos-produto/", response_model=list[ModeloProdutoComMarcaResponse])
async def listar_modelos(
    marca_id: Optional[uuid.UUID] = Query(None),
    tipo_produto: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = (
        select(ModeloProduto)
        .where(or_(ModeloProduto.tenant_id.is_(None), ModeloProduto.tenant_id == tenant_id))
        .options(selectinload(ModeloProduto.marca))
        .order_by(ModeloProduto.nome)
    )
    if marca_id:
        stmt = stmt.where(ModeloProduto.marca_id == marca_id)
    if tipo_produto:
        stmt = stmt.where(
            (ModeloProduto.tipo_produto == tipo_produto) | (ModeloProduto.tipo_produto.is_(None))
        )
    if ativo is not None:
        stmt = stmt.where(ModeloProduto.ativo == ativo)
    result = await session.execute(stmt)
    return [_enrich_modelo(o) for o in result.scalars().all()]


@router.post("/cadastros/modelos-produto", response_model=ModeloProdutoComMarcaResponse, status_code=201)
@router.post("/cadastros/modelos-produto/", response_model=ModeloProdutoComMarcaResponse, status_code=201)
async def criar_modelo(
    data: ModeloProdutoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    # Valida que a marca pertence ao tenant ou é do sistema
    marca = await session.execute(
        select(Marca).where(
            Marca.id == data.marca_id,
            or_(Marca.tenant_id.is_(None), Marca.tenant_id == tenant_id),
        )
    )
    if not marca.scalar_one_or_none():
        raise EntityNotFoundError("Marca não encontrada")
    obj = ModeloProduto(tenant_id=tenant_id, sistema=False, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    
    # Reload com marca
    stmt = select(ModeloProduto).where(ModeloProduto.id == obj.id).options(selectinload(ModeloProduto.marca))
    res = await session.execute(stmt)
    return _enrich_modelo(res.scalar_one())


@router.get("/cadastros/modelos-produto/{modelo_id}", response_model=ModeloProdutoComMarcaResponse)
async def obter_modelo(
    modelo_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(ModeloProduto)
        .where(ModeloProduto.id == modelo_id, ModeloProduto.tenant_id == tenant_id)
        .options(selectinload(ModeloProduto.marca))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Modelo não encontrado")
    return _enrich_modelo(obj)


@router.patch("/cadastros/modelos-produto/{modelo_id}", response_model=ModeloProdutoComMarcaResponse)
async def atualizar_modelo(
    modelo_id: uuid.UUID,
    data: ModeloProdutoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(ModeloProduto)
        .where(ModeloProduto.id == modelo_id, ModeloProduto.tenant_id == tenant_id, ModeloProduto.sistema == False)
        .options(selectinload(ModeloProduto.marca))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Modelo não encontrado ou não editável")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return _enrich_modelo(obj)


@router.delete("/cadastros/modelos-produto/{modelo_id}", status_code=204)
async def remover_modelo(
    modelo_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(ModeloProduto).where(ModeloProduto.id == modelo_id, ModeloProduto.tenant_id == tenant_id, ModeloProduto.sistema == False)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Modelo não encontrado ou não editável")
    obj.ativo = False
    await session.commit()


# ===========================================================================
# Categorias de Produto
# ===========================================================================

@router.get("/cadastros/categorias-produto", response_model=list[CategoriaProdutoResponse])
@router.get("/cadastros/categorias-produto/", response_model=list[CategoriaProdutoResponse])
async def listar_categorias(
    parent_id: Optional[uuid.UUID] = Query(None, description="null = raízes"),
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = (
        select(CategoriaProduto)
        .where(or_(CategoriaProduto.tenant_id.is_(None), CategoriaProduto.tenant_id == tenant_id))
        .order_by(CategoriaProduto.ordem, CategoriaProduto.nome)
    )
    if parent_id is not None:
        stmt = stmt.where(CategoriaProduto.parent_id == parent_id)
    if ativo is not None:
        stmt = stmt.where(CategoriaProduto.ativo == ativo)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/cadastros/categorias-produto", response_model=CategoriaProdutoResponse, status_code=201)
@router.post("/cadastros/categorias-produto/", response_model=CategoriaProdutoResponse, status_code=201)
async def criar_categoria(
    data: CategoriaProdutoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    obj = CategoriaProduto(tenant_id=tenant_id, sistema=False, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/cadastros/categorias-produto/{cat_id}", response_model=CategoriaProdutoResponse)
async def obter_categoria(
    cat_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(CategoriaProduto).where(CategoriaProduto.id == cat_id, CategoriaProduto.tenant_id == tenant_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Categoria não encontrada")
    return obj


@router.patch("/cadastros/categorias-produto/{cat_id}", response_model=CategoriaProdutoResponse)
async def atualizar_categoria(
    cat_id: uuid.UUID,
    data: CategoriaProdutoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(CategoriaProduto).where(CategoriaProduto.id == cat_id, CategoriaProduto.tenant_id == tenant_id, CategoriaProduto.sistema == False)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Categoria não encontrada ou não editável")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/cadastros/categorias-produto/{cat_id}", status_code=204)
async def remover_categoria(
    cat_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(CategoriaProduto).where(CategoriaProduto.id == cat_id, CategoriaProduto.tenant_id == tenant_id, CategoriaProduto.sistema == False)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Categoria não encontrada ou não editável")
    obj.ativo = False
    await session.commit()


# ===========================================================================
# Produtos
# ===========================================================================

def _enrich_produto(obj: Produto) -> dict:
    """Adiciona campos desnormalizados ao response."""
    data = ProdutoResponse.model_validate(obj).model_dump()
    if obj.marca_rel:
        data["marca_nome"] = obj.marca_rel.nome
    if obj.modelo_rel:
        data["modelo_nome"] = obj.modelo_rel.nome
    if obj.categoria:
        data["categoria_nome"] = obj.categoria.nome
    return data


@router.get("/cadastros/produtos", response_model=list[ProdutoResponse])
@router.get("/cadastros/produtos/", response_model=list[ProdutoResponse])
async def listar_produtos(
    tipo: Optional[str] = Query(None),
    categoria_id: Optional[uuid.UUID] = Query(None),
    marca_id: Optional[uuid.UUID] = Query(None),
    ativo: Optional[bool] = Query(None),
    q: Optional[str] = Query(None, description="Busca por nome ou código"),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = (
        select(Produto)
        .where(Produto.tenant_id == tenant_id)
        .options(
            selectinload(Produto.marca_rel),
            selectinload(Produto.modelo_rel),
            selectinload(Produto.categoria),
            selectinload(Produto.detalhe_agricola),
            selectinload(Produto.detalhe_estoque),
            selectinload(Produto.detalhe_epi),
        )
        .order_by(Produto.nome)
    )
    if tipo:
        stmt = stmt.where(Produto.tipo == tipo)
    if categoria_id:
        stmt = stmt.where(Produto.categoria_id == categoria_id)
    if marca_id:
        stmt = stmt.where(Produto.marca_id == marca_id)
    if ativo is not None:
        stmt = stmt.where(Produto.ativo == ativo)
    if q:
        from sqlalchemy import or_
        stmt = stmt.where(
            or_(Produto.nome.ilike(f"%{q}%"), Produto.codigo_interno.ilike(f"%{q}%"))
        )
    result = await session.execute(stmt)
    objs = list(result.scalars().all())
    return [_enrich_produto(o) for o in objs]


@router.post("/cadastros/produtos", response_model=ProdutoResponse, status_code=201)
@router.post("/cadastros/produtos/", response_model=ProdutoResponse, status_code=201)
async def criar_produto(
    data: ProdutoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    payload = data.model_dump(exclude={"detalhe_agricola", "detalhe_estoque", "detalhe_epi"})
    produto = Produto(tenant_id=tenant_id, **payload)

    if data.detalhe_agricola:
        produto.detalhe_agricola = ProdutoAgricola(**data.detalhe_agricola.model_dump())
    if data.detalhe_estoque:
        produto.detalhe_estoque = ProdutoEstoque(**data.detalhe_estoque.model_dump())
    if data.detalhe_epi:
        produto.detalhe_epi = ProdutoEPI(**data.detalhe_epi.model_dump())

    session.add(produto)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Produto com este código interno já existe neste tenant.")

    # Reload com relacionamentos
    result = await session.execute(
        select(Produto)
        .where(Produto.id == produto.id)
        .options(
            selectinload(Produto.marca_rel),
            selectinload(Produto.modelo_rel),
            selectinload(Produto.categoria),
            selectinload(Produto.detalhe_agricola),
            selectinload(Produto.detalhe_estoque),
            selectinload(Produto.detalhe_epi),
        )
    )
    return _enrich_produto(result.scalar_one())


@router.get("/cadastros/produtos/{produto_id}", response_model=ProdutoResponse)
async def obter_produto(
    produto_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Produto)
        .where(Produto.id == produto_id, Produto.tenant_id == tenant_id)
        .options(
            selectinload(Produto.marca_rel),
            selectinload(Produto.modelo_rel),
            selectinload(Produto.categoria),
            selectinload(Produto.detalhe_agricola),
            selectinload(Produto.detalhe_estoque),
            selectinload(Produto.detalhe_epi),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Produto não encontrado")
    return _enrich_produto(obj)


@router.patch("/cadastros/produtos/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(
    produto_id: uuid.UUID,
    data: ProdutoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Produto)
        .where(Produto.id == produto_id, Produto.tenant_id == tenant_id)
        .options(
            selectinload(Produto.marca_rel),
            selectinload(Produto.modelo_rel),
            selectinload(Produto.categoria),
            selectinload(Produto.detalhe_agricola),
            selectinload(Produto.detalhe_estoque),
            selectinload(Produto.detalhe_epi),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Produto não encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    # Re-fetch para ter relacionamentos atualizados
    result2 = await session.execute(
        select(Produto)
        .where(Produto.id == produto_id)
        .options(
            selectinload(Produto.marca_rel),
            selectinload(Produto.modelo_rel),
            selectinload(Produto.categoria),
            selectinload(Produto.detalhe_agricola),
            selectinload(Produto.detalhe_estoque),
            selectinload(Produto.detalhe_epi),
        )
    )
    return _enrich_produto(result2.scalar_one())


@router.delete("/cadastros/produtos/{produto_id}", status_code=204)
async def remover_produto(
    produto_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(Produto).where(Produto.id == produto_id, Produto.tenant_id == tenant_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Produto não encontrado")
    obj.ativo = False
    await session.commit()
