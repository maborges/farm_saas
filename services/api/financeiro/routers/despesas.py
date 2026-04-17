from datetime import date
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id, require_module
from financeiro.schemas.despesa_schema import (
    DespesaCreate,
    DespesaUpdate,
    DespesaResponse,
    DespesaListItem,
)
from financeiro.services.despesa_service import DespesaService

router = APIRouter(
    prefix="/despesas",
    tags=["Financeiro - Contas a Pagar (F1)"],
    dependencies=[Depends(require_module("F1_TESOURARIA"))],
)


@router.get("/", response_model=List[DespesaListItem])
async def listar_despesas(
    unidade_produtiva_id: Optional[uuid.UUID] = Query(None),
    status_filtro: Optional[str] = Query(None, alias="status"),
    vencimento_de: Optional[date] = Query(None, description="Filtrar vencimento a partir desta data"),
    vencimento_ate: Optional[date] = Query(None, description="Filtrar vencimento até esta data"),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Lista contas a pagar do tenant com filtros opcionais."""
    svc = DespesaService(db, tenant_id)
    return await svc.listar_com_filtros(
        unidade_produtiva_id=unidade_produtiva_id,
        status=status_filtro,
        vencimento_de=vencimento_de,
        vencimento_ate=vencimento_ate,
    )


@router.get("/vencendo", response_model=List[DespesaListItem])
async def despesas_vencendo(
    dias: int = Query(7, ge=0, le=90, description="Janela de dias a partir de hoje"),
    unidade_produtiva_id: Optional[uuid.UUID] = Query(None),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Retorna despesas a vencer nos próximos N dias (padrão: 7).
    Inclui as já vencidas (dias=0 retorna apenas hoje).
    Usado pelo dashboard de alertas financeiros.
    """
    svc = DespesaService(db, tenant_id)
    return await svc.listar_vencendo(dias=dias, unidade_produtiva_id=unidade_produtiva_id)


@router.post("/", response_model=List[DespesaResponse], status_code=status.HTTP_201_CREATED)
async def criar_despesa(
    payload: DespesaCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Cadastra uma nova despesa com suporte a parcelamento e rateio.
    Retorna lista de despesas criadas (N itens se parcelado).
    """
    svc = DespesaService(db, tenant_id)
    resultado = await svc.create_with_rateio(obj_in=payload)
    await db.commit()
    return resultado


@router.get("/{despesa_id}", response_model=DespesaResponse)
async def obter_despesa(
    despesa_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Retorna uma despesa pelo ID."""
    svc = DespesaService(db, tenant_id)
    return await svc.get_or_fail(despesa_id)


@router.patch("/{despesa_id}", response_model=DespesaResponse)
async def atualizar_despesa(
    despesa_id: uuid.UUID,
    payload: DespesaUpdate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Atualiza uma despesa. Se valor_pago >= valor_total, status muda para PAGO automaticamente.
    """
    svc = DespesaService(db, tenant_id)
    resultado = await svc.atualizar(despesa_id, payload)
    await db.commit()
    await db.refresh(resultado)
    return resultado


@router.delete("/{despesa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_despesa(
    despesa_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Soft delete: marca ativo=False."""
    svc = DespesaService(db, tenant_id)
    despesa = await svc.get_or_fail(despesa_id)
    despesa.ativo = False
    db.add(despesa)
    await db.commit()


class BaixaDespesaRequest(BaseModel):
    data_pagamento: date
    valor_pago: float
    forma_pagamento: str


@router.post("/{despesa_id}/baixar", response_model=DespesaResponse)
async def baixar_despesa(
    despesa_id: uuid.UUID,
    payload: BaixaDespesaRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Marca a despesa como PAGO."""
    svc = DespesaService(db, tenant_id)
    despesa = await svc.get_or_fail(despesa_id)
    despesa.data_pagamento = payload.data_pagamento
    despesa.valor_pago = payload.valor_pago
    despesa.forma_pagamento = payload.forma_pagamento
    despesa.status = "PAGO"
    db.add(despesa)
    await db.commit()
    await db.refresh(despesa)
    return despesa
