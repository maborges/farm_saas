import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_current_tenant
from core.models.tenant import Tenant
from core.cadastros.service import CatalogoProdutoService
from core.cadastros.schemas import ProdutoCatalogoCreate, ProdutoCatalogoUpdate, ProdutoCatalogoResponse

router = APIRouter(prefix="/cadastros", tags=["Cadastros — Catálogo"])


def _svc(session: AsyncSession, tenant: Tenant) -> CatalogoProdutoService:
    return CatalogoProdutoService(session, tenant.id)


@router.get("/produtos", response_model=List[ProdutoCatalogoResponse])
async def listar_produtos(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de produto"),
    apenas_ativos: bool = Query(True),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    produtos = await svc.listar(tipo=tipo, apenas_ativos=apenas_ativos)
    return [await svc.build_response(p) for p in produtos]


@router.post("/produtos", response_model=ProdutoCatalogoResponse, status_code=201)
async def criar_produto(
    data: ProdutoCatalogoCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    produto = await svc.criar(data)
    await session.commit()
    await session.refresh(produto)
    return await svc.build_response(produto)


@router.get("/produtos/{produto_id}", response_model=ProdutoCatalogoResponse)
async def obter_produto(
    produto_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    produto = await svc.obter(produto_id)
    return await svc.build_response(produto)


@router.patch("/produtos/{produto_id}", response_model=ProdutoCatalogoResponse)
async def atualizar_produto(
    produto_id: uuid.UUID,
    data: ProdutoCatalogoUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    svc = _svc(session, tenant)
    produto = await svc.atualizar(produto_id, data)
    await session.commit()
    await session.refresh(produto)
    return await svc.build_response(produto)


@router.delete("/produtos/{produto_id}", status_code=204)
async def desativar_produto(
    produto_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Soft-delete: marca produto como inativo."""
    svc = _svc(session, tenant)
    produto = await svc.obter(produto_id)
    produto.ativo = False
    await session.commit()
