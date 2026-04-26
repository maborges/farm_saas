"""
Router — ComercializacaoCommodity
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session_with_tenant, get_tenant_id
from core.exceptions import EntityNotFoundError, BusinessRuleError
from .schemas import ComercializacaoCreate, ComercializacaoUpdate, ComercializacaoResponse
from .service import ComercializacaoService

router = APIRouter(prefix="/comercializacoes", tags=["Financeiro — Comercializações"])


@router.get("/", response_model=list[ComercializacaoResponse])
async def listar(
    status: Optional[str] = Query(None),
    commodity_id: Optional[uuid.UUID] = Query(None),
    comprador_id: Optional[uuid.UUID] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ComercializacaoService(session, tenant_id)
    return await svc.listar(status=status, commodity_id=commodity_id, comprador_id=comprador_id)


@router.post("/", response_model=ComercializacaoResponse, status_code=201)
async def criar(
    data: ComercializacaoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ComercializacaoService(session, tenant_id)
    try:
        obj = await svc.criar(data)
        await session.commit()
        await session.refresh(obj)
        return obj
    except EntityNotFoundError as e:
        raise HTTPException(http_status.HTTP_404_NOT_FOUND, str(e))


@router.get("/{comercializacao_id}", response_model=ComercializacaoResponse)
async def obter(
    comercializacao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ComercializacaoService(session, tenant_id)
    try:
        return await svc.obter(comercializacao_id)
    except EntityNotFoundError:
        raise HTTPException(http_status.HTTP_404_NOT_FOUND, "Comercialização não encontrada")


@router.patch("/{comercializacao_id}", response_model=ComercializacaoResponse)
async def atualizar(
    comercializacao_id: uuid.UUID,
    data: ComercializacaoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ComercializacaoService(session, tenant_id)
    try:
        obj = await svc.obter(comercializacao_id)
    except EntityNotFoundError:
        raise HTTPException(http_status.HTTP_404_NOT_FOUND, "Comercialização não encontrada")

    if data.status and data.status != obj.status:
        try:
            await svc.transicionar_status(obj, data.status, data.data_entrega_real)
        except BusinessRuleError as e:
            raise HTTPException(http_status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
        await session.refresh(obj)
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
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ComercializacaoService(session, tenant_id)
    try:
        await svc.remover(comercializacao_id)
        await session.commit()
    except EntityNotFoundError:
        raise HTTPException(http_status.HTTP_404_NOT_FOUND, "Comercialização não encontrada")
    except BusinessRuleError as e:
        raise HTTPException(http_status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
