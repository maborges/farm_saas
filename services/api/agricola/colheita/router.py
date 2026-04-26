import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session_with_tenant, get_tenant_id
from core.exceptions import EntityNotFoundError
from .service import ProdutoColhidoService
from .schemas import ProdutoColhidoCreate, ProdutoColhidoUpdate, ProdutoColhidoResponse, ResumoEstoqueResponse

router = APIRouter(prefix="/agricola/produtos-colhidos", tags=["Agrícola — Produtos Colhidos"])


@router.get("/resumo", response_model=ResumoEstoqueResponse)
async def resumo_estoque(
    status: Optional[str] = Query(None),
    commodity_id: Optional[uuid.UUID] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = ProdutoColhidoService(session, tenant_id)
    return await service.resumo_estoque(status=status, commodity_id=commodity_id)


@router.get("/", response_model=list[ProdutoColhidoResponse])
async def listar(
    safra_id: Optional[uuid.UUID] = Query(None),
    commodity_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = ProdutoColhidoService(session, tenant_id)
    return await service.listar(safra_id=safra_id, commodity_id=commodity_id, status=status)


@router.post("/", response_model=ProdutoColhidoResponse, status_code=201)
async def criar(
    data: ProdutoColhidoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = ProdutoColhidoService(session, tenant_id)
    obj = await service.criar(data)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/{produto_id}", response_model=ProdutoColhidoResponse)
async def obter(
    produto_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = ProdutoColhidoService(session, tenant_id)
    try:
        return await service.obter(produto_id)
    except EntityNotFoundError:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto colhido não encontrado")


@router.patch("/{produto_id}", response_model=ProdutoColhidoResponse)
async def atualizar(
    produto_id: uuid.UUID,
    data: ProdutoColhidoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = ProdutoColhidoService(session, tenant_id)
    try:
        obj = await service.atualizar(produto_id, data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto colhido não encontrado")


@router.delete("/{produto_id}", status_code=204)
async def remover(
    produto_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    service = ProdutoColhidoService(session, tenant_id)
    try:
        await service.remover(produto_id)
        await session.commit()
    except EntityNotFoundError:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto colhido não encontrado")
