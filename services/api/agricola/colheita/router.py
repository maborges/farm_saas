import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id
from core.exceptions import EntityNotFoundError
from .models import ProdutoColhido
from .schemas import ProdutoColhidoCreate, ProdutoColhidoUpdate, ProdutoColhidoResponse, ResumoEstoqueResponse

router = APIRouter(prefix="/agricola/produtos-colhidos", tags=["Agrícola — Produtos Colhidos"])


@router.get("/", response_model=list[ProdutoColhidoResponse])
async def listar(
    safra_id: Optional[uuid.UUID] = Query(None),
    commodity_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ProdutoColhido).where(ProdutoColhido.tenant_id == tenant_id)
    if safra_id:
        stmt = stmt.where(ProdutoColhido.safra_id == safra_id)
    if commodity_id:
        stmt = stmt.where(ProdutoColhido.commodity_id == commodity_id)
    if status:
        stmt = stmt.where(ProdutoColhido.status == status)
    result = await session.execute(stmt.order_by(ProdutoColhido.data_entrada.desc()))
    return list(result.scalars().all())


@router.post("/", response_model=ProdutoColhidoResponse, status_code=201)
async def criar(
    data: ProdutoColhidoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    obj = ProdutoColhido(tenant_id=tenant_id, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/{produto_id}", response_model=ProdutoColhidoResponse)
async def obter(
    produto_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ProdutoColhido).where(
        ProdutoColhido.id == produto_id,
        ProdutoColhido.tenant_id == tenant_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Produto colhido não encontrado")
    return obj


@router.patch("/{produto_id}", response_model=ProdutoColhidoResponse)
async def atualizar(
    produto_id: uuid.UUID,
    data: ProdutoColhidoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ProdutoColhido).where(
        ProdutoColhido.id == produto_id,
        ProdutoColhido.tenant_id == tenant_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Produto colhido não encontrado")

    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)

    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/{produto_id}", status_code=204)
async def remover(
    produto_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ProdutoColhido).where(
        ProdutoColhido.id == produto_id,
        ProdutoColhido.tenant_id == tenant_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Produto colhido não encontrado")
    await session.delete(obj)
    await session.commit()


# ===========================================================================
# Resumo de estoque
# ===========================================================================

@router.get("/resumo", response_model=ResumoEstoqueResponse)
async def resumo_estoque(
    status: Optional[str] = Query(None, description="Filtrar por status (ARMAZENADO, RESERVADO, VENDIDO, etc.)"),
    commodity_id: Optional[uuid.UUID] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """
    Agrega ProdutoColhido por commodity + armazém + status.
    Retorna resumo do estoque disponível.
    """
    # Query agregada
    stmt = select(
        ProdutoColhido.commodity_id,
        ProdutoColhido.unidade,
        ProdutoColhido.armazem_id,
        ProdutoColhido.status,
        func.sum(ProdutoColhido.quantidade).label("total_quantidade"),
        func.sum(ProdutoColhido.peso_liquido_kg).label("total_peso_kg"),
        func.count(ProdutoColhido.id).label("num_lotes"),
    ).where(
        ProdutoColhido.tenant_id == tenant_id,
    )

    if status:
        stmt = stmt.where(ProdutoColhido.status == status)
    if commodity_id:
        stmt = stmt.where(ProdutoColhido.commodity_id == commodity_id)

    stmt = stmt.group_by(
        ProdutoColhido.commodity_id,
        ProdutoColhido.unidade,
        ProdutoColhido.armazem_id,
        ProdutoColhido.status,
    )

    rows = (await session.execute(stmt)).all()

    # Buscar nomes das commodities
    commodity_ids = list({r.commodity_id for r in rows}) if rows else []
    commodity_map = {}
    if commodity_ids:
        from core.cadastros.commodities.models import Commodity
        c_stmt = select(Commodity).where(Commodity.id.in_(commodity_ids))
        commodities = (await session.execute(c_stmt)).scalars().all()
        commodity_map = {c.id: c for c in commodities}

    itens = []
    total_geral_kg = 0.0
    total_lotes = 0

    for r in rows:
        qty = float(r.total_quantidade)
        peso = float(r.total_peso_kg)
        total_geral_kg += peso
        total_lotes += int(r.num_lotes)

        c = commodity_map.get(r.commodity_id)
        itens.append({
            "commodity_id": r.commodity_id,
            "commodity_nome": c.nome if c else None,
            "commodity_codigo": c.codigo if c else None,
            "commodity_tipo": c.tipo if c else None,
            "unidade": r.unidade,
            "armazem_id": r.armazem_id,
            "status": r.status,
            "total_quantidade": round(qty, 3),
            "total_peso_kg": round(peso, 3),
            "num_lotes": int(r.num_lotes),
        })

    return ResumoEstoqueResponse(
        itens=itens,
        total_geral_kg=round(total_geral_kg, 3),
        total_lotes=total_lotes,
    )
