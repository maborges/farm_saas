from datetime import date
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id, require_module
from financeiro.schemas.receita_schema import (
    ReceitaCreate,
    ReceitaUpdate,
    ReceitaResponse,
    ReceitaListItem,
)
from financeiro.services.receita_service import ReceitaService

router = APIRouter(
    prefix="/receitas",
    tags=["Financeiro - Contas a Receber (F1)"],
    dependencies=[Depends(require_module("F1_TESOURARIA"))],
)


@router.get("/", response_model=List[ReceitaListItem])
async def listar_receitas(
    fazenda_id: Optional[uuid.UUID] = Query(None),
    status_filtro: Optional[str] = Query(None, alias="status"),
    vencimento_de: Optional[date] = Query(None, description="Filtrar vencimento a partir desta data"),
    vencimento_ate: Optional[date] = Query(None, description="Filtrar vencimento até esta data"),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Lista contas a receber do tenant com filtros opcionais."""
    svc = ReceitaService(db, tenant_id)
    return await svc.listar_com_filtros(
        fazenda_id=fazenda_id,
        status=status_filtro,
        vencimento_de=vencimento_de,
        vencimento_ate=vencimento_ate,
    )


@router.get("/vencendo", response_model=List[ReceitaListItem])
async def receitas_vencendo(
    dias: int = Query(7, ge=0, le=90, description="Janela de dias a partir de hoje"),
    fazenda_id: Optional[uuid.UUID] = Query(None),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Retorna receitas a vencer nos próximos N dias (padrão: 7).
    Usado pelo dashboard de alertas financeiros.
    """
    svc = ReceitaService(db, tenant_id)
    return await svc.listar_vencendo(dias=dias, fazenda_id=fazenda_id)


@router.post("/", response_model=List[ReceitaResponse], status_code=status.HTTP_201_CREATED)
async def criar_receita(
    payload: ReceitaCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Cadastra uma nova receita com suporte a parcelamento.
    Retorna lista de receitas criadas (N itens se parcelado).
    """
    svc = ReceitaService(db, tenant_id)
    resultado = await svc.create_parcelado(obj_in=payload)
    await db.commit()
    return resultado


@router.get("/{receita_id}", response_model=ReceitaResponse)
async def obter_receita(
    receita_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Retorna uma receita pelo ID."""
    svc = ReceitaService(db, tenant_id)
    return await svc.get_or_fail(receita_id)


@router.patch("/{receita_id}", response_model=ReceitaResponse)
async def atualizar_receita(
    receita_id: uuid.UUID,
    payload: ReceitaUpdate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Atualiza uma receita. Se valor_recebido >= valor_total, status muda para RECEBIDO automaticamente.
    """
    svc = ReceitaService(db, tenant_id)
    resultado = await svc.atualizar(receita_id, payload)
    await db.commit()
    await db.refresh(resultado)
    return resultado


@router.delete("/{receita_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_receita(
    receita_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Soft delete: marca ativo=False."""
    svc = ReceitaService(db, tenant_id)
    receita = await svc.get_or_fail(receita_id)
    receita.ativo = False
    db.add(receita)
    await db.commit()


class BaixaReceitaRequest(BaseModel):
    data_recebimento: date
    valor_recebido: float
    forma_recebimento: str


@router.post("/{receita_id}/baixar", response_model=ReceitaResponse)
async def baixar_receita(
    receita_id: uuid.UUID,
    payload: BaixaReceitaRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Marca a receita como RECEBIDO."""
    svc = ReceitaService(db, tenant_id)
    receita = await svc.get_or_fail(receita_id)
    receita.data_recebimento = payload.data_recebimento
    receita.valor_recebido = payload.valor_recebido
    receita.forma_recebimento = payload.forma_recebimento
    receita.status = "RECEBIDO"
    db.add(receita)
    await db.commit()
    await db.refresh(receita)
    return receita
