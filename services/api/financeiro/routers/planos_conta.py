from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id, require_module
from financeiro.schemas.plano_conta_schema import (
    PlanoContaCreate,
    PlanoContaUpdate,
    PlanoContaResponse,
    PlanoContaNode,
)
from financeiro.services.plano_conta_service import PlanoContaService

router = APIRouter(
    prefix="/planos-conta",
    tags=["Financeiro - Plano de Contas (F1)"],
    dependencies=[Depends(require_module("F1"))],
)


@router.get("/", response_model=List[PlanoContaResponse])
async def listar_planos(
    tipo: Optional[str] = Query(None, description="RECEITA | DESPESA"),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Lista plano de contas (flat). Filtrar por tipo quando necessário."""
    svc = PlanoContaService(db, tenant_id)
    filters = {}
    if tipo:
        filters["tipo"] = tipo
    return await svc.list_all(**filters)


@router.get("/arvore", response_model=List[PlanoContaNode])
async def listar_arvore(
    tipo: Optional[str] = Query(None, description="RECEITA | DESPESA"),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Retorna plano de contas em estrutura hierárquica (grupos + analíticas)."""
    svc = PlanoContaService(db, tenant_id)
    return await svc.listar_arvore(tipo=tipo)


@router.post("/seed", status_code=status.HTTP_200_OK)
async def seed_categorias_padrao(
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Popula o plano de contas com as categorias padrão RFB para Produtor Rural.
    Operação idempotente — ignora categorias já existentes.
    """
    svc = PlanoContaService(db, tenant_id)
    criados = await svc.seed_padrao()
    await db.commit()
    return {"criados": criados, "mensagem": f"{criados} categorias adicionadas ao plano de contas."}


@router.post("/", response_model=PlanoContaResponse, status_code=status.HTTP_201_CREATED)
async def criar_plano(
    payload: PlanoContaCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Cadastra uma nova categoria no plano de contas."""
    svc = PlanoContaService(db, tenant_id)
    resultado = await svc.criar(payload)
    await db.commit()
    await db.refresh(resultado)
    return resultado


@router.get("/{plano_id}", response_model=PlanoContaResponse)
async def obter_plano(
    plano_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Retorna uma categoria pelo ID."""
    svc = PlanoContaService(db, tenant_id)
    return await svc.get_or_fail(plano_id)


@router.patch("/{plano_id}", response_model=PlanoContaResponse)
async def atualizar_plano(
    plano_id: uuid.UUID,
    payload: PlanoContaUpdate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Atualiza nome, descrição, categoria_rfb ou ordem."""
    svc = PlanoContaService(db, tenant_id)
    resultado = await svc.atualizar(plano_id, payload)
    await db.commit()
    await db.refresh(resultado)
    return resultado


@router.delete("/{plano_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_plano(
    plano_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """
    Remove uma categoria. Bloqueia se:
    - for categoria de sistema (is_sistema=True)
    - tiver subcategorias filhas
    """
    svc = PlanoContaService(db, tenant_id)
    await svc.deletar(plano_id)
    await db.commit()
