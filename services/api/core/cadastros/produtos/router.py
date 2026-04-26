import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from core.dependencies import get_session_with_tenant, get_tenant_id
from core.exceptions import EntityNotFoundError, BusinessRuleError
from .schemas import (
    MarcaCreate, MarcaUpdate, MarcaResponse,
    ModeloProdutoCreate, ModeloProdutoUpdate, ModeloProdutoResponse, ModeloProdutoComMarcaResponse,
    CategoriaProdutoCreate, CategoriaProdutoUpdate, CategoriaProdutoResponse,
    ProdutoCreate, ProdutoUpdate, ProdutoResponse,
    ProdutoCulturaCreate, ProdutoCulturaUpdate, ProdutoCulturaResponse,
    SoloParametroCulturaCreate, SoloParametroCulturaUpdate, SoloParametroCulturaResponse,
)
from .service import ProdutoService

router = APIRouter(tags=["Cadastros — Produtos"])


def _enrich_modelo(obj) -> dict:
    data = ModeloProdutoResponse.model_validate(obj).model_dump()
    if obj.marca:
        data["marca_nome"] = obj.marca.nome
    return data


def _enrich_produto(obj) -> dict:
    from .schemas import ProdutoResponse
    data = ProdutoResponse.model_validate(obj).model_dump()
    if obj.marca_rel:
        data["marca_nome"] = obj.marca_rel.nome
    if obj.modelo_rel:
        data["modelo_nome"] = obj.modelo_rel.nome
    if obj.categoria:
        data["categoria_nome"] = obj.categoria.nome
    return data


# ===========================================================================
# Marcas
# ===========================================================================

@router.get("/cadastros/marcas", response_model=list[MarcaResponse])
@router.get("/cadastros/marcas/", response_model=list[MarcaResponse])
async def listar_marcas(
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await ProdutoService(session, tenant_id).listar_marcas(ativo=ativo)


@router.post("/cadastros/marcas", response_model=MarcaResponse, status_code=201)
@router.post("/cadastros/marcas/", response_model=MarcaResponse, status_code=201)
async def criar_marca(
    data: MarcaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    obj = await ProdutoService(session, tenant_id).criar_marca(data)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/cadastros/marcas/{marca_id}", response_model=MarcaResponse)
async def obter_marca(
    marca_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await ProdutoService(session, tenant_id)._get_marca(marca_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Marca não encontrada")


@router.patch("/cadastros/marcas/{marca_id}", response_model=MarcaResponse)
async def atualizar_marca(
    marca_id: uuid.UUID,
    data: MarcaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await ProdutoService(session, tenant_id).atualizar_marca(marca_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@router.delete("/cadastros/marcas/{marca_id}", status_code=204)
async def remover_marca(
    marca_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        await ProdutoService(session, tenant_id).remover_marca(marca_id)
        await session.commit()
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))
    except BusinessRuleError as e:
        raise HTTPException(422, str(e))


# ===========================================================================
# Modelos
# ===========================================================================

@router.get("/cadastros/modelos-produto", response_model=list[ModeloProdutoComMarcaResponse])
@router.get("/cadastros/modelos-produto/", response_model=list[ModeloProdutoComMarcaResponse])
async def listar_modelos(
    marca_id: Optional[uuid.UUID] = Query(None),
    tipo_produto: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    objs = await ProdutoService(session, tenant_id).listar_modelos(marca_id=marca_id, tipo_produto=tipo_produto, ativo=ativo)
    return [_enrich_modelo(o) for o in objs]


@router.post("/cadastros/modelos-produto", response_model=ModeloProdutoComMarcaResponse, status_code=201)
@router.post("/cadastros/modelos-produto/", response_model=ModeloProdutoComMarcaResponse, status_code=201)
async def criar_modelo(
    data: ModeloProdutoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await ProdutoService(session, tenant_id).criar_modelo(data)
        await session.commit()
        await session.refresh(obj)
        return _enrich_modelo(obj)
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/cadastros/modelos-produto/{modelo_id}", response_model=ModeloProdutoComMarcaResponse)
async def obter_modelo(
    modelo_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return _enrich_modelo(await ProdutoService(session, tenant_id)._get_modelo(modelo_id))
    except EntityNotFoundError:
        raise HTTPException(404, "Modelo não encontrado")


@router.patch("/cadastros/modelos-produto/{modelo_id}", response_model=ModeloProdutoComMarcaResponse)
async def atualizar_modelo(
    modelo_id: uuid.UUID,
    data: ModeloProdutoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await ProdutoService(session, tenant_id).atualizar_modelo(modelo_id, data)
        await session.commit()
        await session.refresh(obj)
        return _enrich_modelo(obj)
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@router.delete("/cadastros/modelos-produto/{modelo_id}", status_code=204)
async def remover_modelo(
    modelo_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        await ProdutoService(session, tenant_id).remover_modelo(modelo_id)
        await session.commit()
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


# ===========================================================================
# Categorias de Produto
# ===========================================================================

@router.get("/cadastros/categorias-produto", response_model=list[CategoriaProdutoResponse])
@router.get("/cadastros/categorias-produto/", response_model=list[CategoriaProdutoResponse])
async def listar_categorias(
    parent_id: Optional[uuid.UUID] = Query(None),
    ativo: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await ProdutoService(session, tenant_id).listar_categorias(parent_id=parent_id, ativo=ativo)


@router.post("/cadastros/categorias-produto", response_model=CategoriaProdutoResponse, status_code=201)
@router.post("/cadastros/categorias-produto/", response_model=CategoriaProdutoResponse, status_code=201)
async def criar_categoria(
    data: CategoriaProdutoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    obj = await ProdutoService(session, tenant_id).criar_categoria(data)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/cadastros/categorias-produto/{cat_id}", response_model=CategoriaProdutoResponse)
async def obter_categoria(
    cat_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await ProdutoService(session, tenant_id)._get_categoria(cat_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Categoria não encontrada")


@router.patch("/cadastros/categorias-produto/{cat_id}", response_model=CategoriaProdutoResponse)
async def atualizar_categoria(
    cat_id: uuid.UUID,
    data: CategoriaProdutoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await ProdutoService(session, tenant_id).atualizar_categoria(cat_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@router.delete("/cadastros/categorias-produto/{cat_id}", status_code=204)
async def remover_categoria(
    cat_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        await ProdutoService(session, tenant_id).remover_categoria(cat_id)
        await session.commit()
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


# ===========================================================================
# Produtos
# ===========================================================================

@router.get("/cadastros/produtos", response_model=list[ProdutoResponse])
@router.get("/cadastros/produtos/", response_model=list[ProdutoResponse])
async def listar_produtos(
    tipo: Optional[str] = Query(None),
    categoria_id: Optional[uuid.UUID] = Query(None),
    marca_id: Optional[uuid.UUID] = Query(None),
    ativo: Optional[bool] = Query(None),
    q: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    objs = await ProdutoService(session, tenant_id).listar_produtos(tipo=tipo, categoria_id=categoria_id, marca_id=marca_id, ativo=ativo, q=q)
    return [_enrich_produto(o) for o in objs]


@router.post("/cadastros/produtos", response_model=ProdutoResponse, status_code=201)
@router.post("/cadastros/produtos/", response_model=ProdutoResponse, status_code=201)
async def criar_produto(
    data: ProdutoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await ProdutoService(session, tenant_id).criar_produto(data)
        await session.commit()
        await session.refresh(obj)
        return _enrich_produto(obj)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Produto com este código interno já existe neste tenant.")


@router.get("/cadastros/produtos/{produto_id}", response_model=ProdutoResponse)
async def obter_produto(
    produto_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return _enrich_produto(await ProdutoService(session, tenant_id)._get_produto(produto_id))
    except EntityNotFoundError:
        raise HTTPException(404, "Produto não encontrado")


@router.patch("/cadastros/produtos/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(
    produto_id: uuid.UUID,
    data: ProdutoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await ProdutoService(session, tenant_id).atualizar_produto(produto_id, data)
        await session.commit()
        await session.refresh(obj)
        return _enrich_produto(obj)
    except EntityNotFoundError:
        raise HTTPException(404, "Produto não encontrado")


@router.delete("/cadastros/produtos/{produto_id}", status_code=204)
async def remover_produto(
    produto_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        await ProdutoService(session, tenant_id).remover_produto(produto_id)
        await session.commit()
    except EntityNotFoundError:
        raise HTTPException(404, "Produto não encontrado")


# ===========================================================================
# Culturas Agrícolas (ProdutoCultura)
# ===========================================================================

@router.get("/cadastros/culturas", response_model=list[ProdutoCulturaResponse])
@router.get("/cadastros/culturas/", response_model=list[ProdutoCulturaResponse])
async def listar_culturas(
    grupo: Optional[str] = Query(None),
    ativa: Optional[bool] = Query(None),
    q: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await ProdutoService(session, tenant_id).listar_culturas(grupo=grupo, ativa=ativa, q=q)


@router.post("/cadastros/culturas", response_model=ProdutoCulturaResponse, status_code=201)
@router.post("/cadastros/culturas/", response_model=ProdutoCulturaResponse, status_code=201)
async def criar_cultura(
    data: ProdutoCulturaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    obj = await ProdutoService(session, tenant_id).criar_cultura(data)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.patch("/cadastros/culturas/{cultura_id}", response_model=ProdutoCulturaResponse)
async def atualizar_cultura(
    cultura_id: uuid.UUID,
    data: ProdutoCulturaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await ProdutoService(session, tenant_id).atualizar_cultura(cultura_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@router.delete("/cadastros/culturas/{cultura_id}", status_code=204)
async def remover_cultura(
    cultura_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        await ProdutoService(session, tenant_id).remover_cultura(cultura_id)
        await session.commit()
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


# ---------------------------------------------------------------------------
# Solo — Parâmetros de interpretação por cultura
# ---------------------------------------------------------------------------

@router.get("/cadastros/culturas/{cultura_id}/parametros-solo", response_model=list[SoloParametroCulturaResponse])
async def listar_parametros_solo(
    cultura_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await ProdutoService(session, tenant_id).listar_parametros_solo(cultura_id)


@router.post("/cadastros/culturas/{cultura_id}/parametros-solo", response_model=SoloParametroCulturaResponse, status_code=201)
async def criar_parametro_solo(
    cultura_id: uuid.UUID,
    data: SoloParametroCulturaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await ProdutoService(session, tenant_id).criar_parametro_solo(cultura_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@router.patch("/cadastros/culturas/{cultura_id}/parametros-solo/{param_id}", response_model=SoloParametroCulturaResponse)
async def atualizar_parametro_solo(
    cultura_id: uuid.UUID,
    param_id: uuid.UUID,
    data: SoloParametroCulturaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        obj = await ProdutoService(session, tenant_id).atualizar_parametro_solo(param_id, cultura_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))


@router.delete("/cadastros/culturas/{cultura_id}/parametros-solo/{param_id}", status_code=204)
async def deletar_parametro_solo(
    cultura_id: uuid.UUID,
    param_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        await ProdutoService(session, tenant_id).remover_parametro_solo(param_id, cultura_id)
        await session.commit()
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e))
