"""Router para CRUD de Propriedades e Explorações Rurais."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id
from core.base_service import BaseService
from .propriedade_models import Propriedade, ExploracaoRural, DocumentoExploracao
from .propriedade_schemas import (
    PropriedadeCreate,
    PropriedadeUpdate,
    PropriedadeResponse,
    ExploracaoCreate,
    ExploracaoUpdate,
    ExploracaoResponse,
    DocumentoExploracaoCreate,
    DocumentoExploracaoResponse,
)
from .propriedade_service import (
    PropriedadeService,
    ExploracaoRuralService,
    DocumentoExploracaoService,
)

router = APIRouter(prefix="/cadastros", tags=["Cadastros — Produtores"])


# ===========================================================================
# Propriedades - CRUD
# ===========================================================================

@router.post("/propriedades", response_model=PropriedadeResponse, status_code=201)
async def criar_propriedade(
    data: PropriedadeCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Cria uma nova propriedade."""
    service = PropriedadeService(Propriedade, session, tenant_id)
    result = await service.create(data)
    await session.commit()
    await session.refresh(result)
    return result


@router.get("/propriedades", response_model=list[PropriedadeResponse])
async def listar_propriedades(
    ativo: Optional[bool] = Query(True, description="Filtrar por status ativo"),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Lista todas as propriedades do tenant."""
    service = PropriedadeService(Propriedade, session, tenant_id)
    return await service.list_all(ativo=ativo)


@router.get("/propriedades/{propriedade_id}", response_model=PropriedadeResponse)
async def obter_propriedade(
    propriedade_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Obtém uma propriedade por ID."""
    service = PropriedadeService(Propriedade, session, tenant_id)
    return await service.get_or_fail(propriedade_id)


@router.patch("/propriedades/{propriedade_id}", response_model=PropriedadeResponse)
async def atualizar_propriedade(
    propriedade_id: uuid.UUID,
    data: PropriedadeUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Atualiza uma propriedade."""
    service = PropriedadeService(Propriedade, session, tenant_id)
    result = await service.update(propriedade_id, data)
    await session.commit()
    await session.refresh(result)
    return result


@router.delete("/propriedades/{propriedade_id}", status_code=204)
async def remover_propriedade(
    propriedade_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Remove uma propriedade."""
    service = PropriedadeService(Propriedade, session, tenant_id)
    await service.hard_delete(propriedade_id)


# ===========================================================================
# Explorações - Sub-recursos de Propriedade
# ===========================================================================

@router.get(
    "/propriedades/{propriedade_id}/exploracoes",
    response_model=list[ExploracaoResponse],
)
async def listar_exploracoes_por_propriedade(
    propriedade_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Lista todas as explorações de uma propriedade."""
    # Verificar se propriedade existe e pertence ao tenant
    prop_service = PropriedadeService(Propriedade, session, tenant_id)
    await prop_service.get_or_fail(propriedade_id)
    
    expl_service = ExploracaoRuralService(session, tenant_id)
    return await expl_service.listar_por_propriedade(propriedade_id)


@router.post(
    "/propriedades/{propriedade_id}/exploracoes",
    response_model=ExploracaoResponse,
    status_code=201,
)
async def criar_exploracao(
    propriedade_id: uuid.UUID,
    data: ExploracaoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Cria uma nova exploração para uma propriedade."""
    # Verificar se propriedade existe e pertence ao tenant
    prop_service = PropriedadeService(Propriedade, session, tenant_id)
    await prop_service.get_or_fail(propriedade_id)

    expl_service = ExploracaoRuralService(session, tenant_id)
    result = await expl_service.criar(propriedade_id, data)
    await session.commit()
    await session.refresh(result)
    return result


@router.patch(
    "/exploracoes/{exploracao_id}",
    response_model=ExploracaoResponse,
)
async def atualizar_exploracao(
    exploracao_id: uuid.UUID,
    data: ExploracaoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Atualiza uma exploração."""
    expl_service = ExploracaoRuralService(session, tenant_id)
    result = await expl_service.atualizar(exploracao_id, data)
    await session.commit()
    await session.refresh(result)
    return result


@router.delete("/exploracoes/{exploracao_id}", status_code=204)
async def remover_exploracao(
    exploracao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Remove uma exploração (soft delete)."""
    expl_service = ExploracaoRuralService(session, tenant_id)
    await expl_service.remover(exploracao_id)


# ===========================================================================
# Explorações - Recursos de Fazenda
# ===========================================================================

@router.get(
    "/fazendas/{unidade_produtiva_id}/exploracoes",
    response_model=list[ExploracaoResponse],
)
async def listar_exploracoes_por_fazenda(
    unidade_produtiva_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Lista todas as explorações de uma fazenda."""
    expl_service = ExploracaoRuralService(session, tenant_id)
    # Filtrar manualmente por unidade_produtiva_id
    from sqlalchemy import select, and_
    
    stmt = select(ExploracaoRural).where(
        and_(
            ExploracaoRural.unidade_produtiva_id == unidade_produtiva_id,
            ExploracaoRural.tenant_id == tenant_id,
        )
    ).order_by(ExploracaoRural.data_inicio.desc())
    
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get(
    "/fazendas/{unidade_produtiva_id}/exploracoes/vigentes",
    response_model=list[ExploracaoResponse],
)
async def listar_exploracoes_vigentes_por_fazenda(
    unidade_produtiva_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Lista explorações vigentes (ativas) de uma fazenda."""
    expl_service = ExploracaoRuralService(session, tenant_id)
    return await expl_service.listar_vigentes_por_fazenda(unidade_produtiva_id)
