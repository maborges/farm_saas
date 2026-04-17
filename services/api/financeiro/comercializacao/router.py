"""
Router — ComercializacaoCommodity
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id
from core.exceptions import EntityNotFoundError, BusinessRuleError
from .models import ComercializacaoCommodity
from .schemas import ComercializacaoCreate, ComercializacaoUpdate, ComercializacaoResponse
from .service import ComercializacaoService

router = APIRouter(prefix="/comercializacoes", tags=["Financeiro — Comercializações"])


# Transições permitidas de status
TRANSICOES = {
    "RASCUNHO":     ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO":   ["EM_TRANSITO", "CANCELADO"],
    "EM_TRANSITO":  ["ENTREGUE", "CANCELADO"],
    "ENTREGUE":     ["FINALIZADO"],
    "FINALIZADO":   [],
    "CANCELADO":    [],
}


@router.get("/", response_model=list[ComercializacaoResponse])
async def listar(
    status: Optional[str] = Query(None),
    commodity_id: Optional[uuid.UUID] = Query(None),
    comprador_id: Optional[uuid.UUID] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ComercializacaoCommodity).where(
        ComercializacaoCommodity.tenant_id == tenant_id,
    )
    if status:
        stmt = stmt.where(ComercializacaoCommodity.status == status)
    if commodity_id:
        stmt = stmt.where(ComercializacaoCommodity.commodity_id == commodity_id)
    if comprador_id:
        stmt = stmt.where(ComercializacaoCommodity.comprador_id == comprador_id)
    result = await session.execute(stmt.order_by(ComercializacaoCommodity.created_at.desc()))
    return list(result.scalars().all())


@router.post("/", response_model=ComercializacaoResponse, status_code=201)
async def criar(
    data: ComercializacaoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    # Validar que a commodity existe e é acessível
    from core.cadastros.commodities.models import Commodity
    stmt_c = select(Commodity).where(
        Commodity.id == data.commodity_id,
        or_(Commodity.tenant_id == tenant_id, Commodity.sistema == True),
    )
    commodity = (await session.execute(stmt_c)).scalar_one_or_none()
    if not commodity:
        raise EntityNotFoundError("Commodity não encontrada")

    # Validar comprador
    from core.cadastros.pessoas.models import Pessoa
    stmt_p = select(Pessoa).where(
        Pessoa.id == data.comprador_id,
        Pessoa.tenant_id == tenant_id,
    )
    comprador = (await session.execute(stmt_p)).scalar_one_or_none()
    if not comprador:
        raise EntityNotFoundError("Comprador não encontrado")

    # Calcular valor total
    valor_total = round(data.quantidade * data.preco_unitario, 2)

    obj = ComercializacaoCommodity(
        tenant_id=tenant_id,
        valor_total=valor_total,
        **data.model_dump(),
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/{comercializacao_id}", response_model=ComercializacaoResponse)
async def obter(
    comercializacao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ComercializacaoCommodity).where(
        ComercializacaoCommodity.id == comercializacao_id,
        ComercializacaoCommodity.tenant_id == tenant_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Comercialização não encontrada")
    return obj


@router.patch("/{comercializacao_id}", response_model=ComercializacaoResponse)
async def atualizar(
    comercializacao_id: uuid.UUID,
    data: ComercializacaoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ComercializacaoService(session, tenant_id)

    stmt = select(ComercializacaoCommodity).where(
        ComercializacaoCommodity.id == comercializacao_id,
        ComercializacaoCommodity.tenant_id == tenant_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Comercialização não encontrada")

    # Se está alterando status, usar service (com efeitos colaterais)
    if data.status and data.status != obj.status:
        await svc.transicionar_status(obj, data.status, data.data_entrega_real)
        # Recarregar após efeitos colaterais do service
        await session.refresh(obj)
        # Remover status do patch para não sobrescrever
        patch = data.model_dump(exclude_none=True, exclude={"status", "data_entrega_real"})
    else:
        patch = data.model_dump(exclude_none=True)

    for k, v in patch.items():
        setattr(obj, k, v)

    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/{comercializacao_id}", status_code=204)
async def remover(
    comercializacao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(ComercializacaoCommodity).where(
        ComercializacaoCommodity.id == comercializacao_id,
        ComercializacaoCommodity.tenant_id == tenant_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Comercialização não encontrada")
    if obj.status not in ("RASCUNHO", "CANCELADO"):
        raise BusinessRuleError("Só é possível excluir comercializações em RASCUNHO ou CANCELADO")
    await session.delete(obj)
    await session.commit()
