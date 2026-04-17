from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete
from typing import List
from uuid import UUID
from datetime import datetime

from core.dependencies import get_session, get_current_admin, require_permission
from core.models.sessao import SessaoAtiva
from pydantic import BaseModel

router = APIRouter(
    prefix="/backoffice/sessions",
    tags=["Backoffice - Sessões"],
    dependencies=[Depends(require_permission("backoffice:sessions:view"))],
)


# ==================== SCHEMAS ====================

class SessionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    usuario_id: UUID
    unidade_produtiva_id: UUID | None
    ip_address: str | None
    user_agent: str | None
    inicio: datetime
    ultimo_heartbeat: datetime
    expira_em: datetime
    status: str

    class Config:
        from_attributes = True


class SessionStatsResponse(BaseModel):
    total_ativas: int
    total_expiradas: int
    por_status: dict[str, int]
    por_tenant: dict[str, int]


# ==================== ENDPOINTS ====================

@router.get("/stats", response_model=SessionStatsResponse)
async def get_session_stats(
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Estatísticas de sessões."""
    # Por status
    result = await session.execute(
        select(SessaoAtiva.status, func.count(SessaoAtiva.id))
        .group_by(SessaoAtiva.status)
    )
    por_status = {row[0]: row[1] for row in result}

    ativas = por_status.get("ATIVA", 0)
    expiradas = por_status.get("EXPIRADA", 0)

    # Por tenant (top 10)
    result = await session.execute(
        select(SessaoAtiva.tenant_id.cast(str), func.count(SessaoAtiva.id))
        .where(SessaoAtiva.status == "ATIVA")
        .group_by(SessaoAtiva.tenant_id)
        .order_by(desc(func.count(SessaoAtiva.id)))
        .limit(10)
    )
    por_tenant = {row[0]: row[1] for row in result}

    return SessionStatsResponse(
        total_ativas=ativas,
        total_expiradas=expiradas,
        por_status=por_status,
        por_tenant=por_tenant,
    )


@router.get("", response_model=List[SessionResponse])
async def listar_sessions(
    status_filtro: str | None = None,
    tenant_id: UUID | None = None,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Lista sessões com filtros opcionais."""
    stmt = select(SessaoAtiva).order_by(desc(SessaoAtiva.ultimo_heartbeat)).limit(200)

    if status_filtro:
        stmt = stmt.where(SessaoAtiva.status == status_filtro)
    if tenant_id:
        stmt = stmt.where(SessaoAtiva.tenant_id == tenant_id)

    result = await session.execute(stmt)
    return result.scalars().all()


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("backoffice:sessions:delete"))],
)
async def encerrar_session(
    session_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Encerra (kill) uma sessão ativa."""
    sessao = await session.get(SessaoAtiva, session_id)
    if not sessao:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    sessao.status = "ENCERRADA"
    await session.commit()


@router.delete(
    "/tenant/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("backoffice:sessions:delete"))],
)
async def encerrar_sessions_tenant(
    tenant_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Encerra todas as sessões ativas de um tenant."""
    stmt = (
        select(SessaoAtiva)
        .where(SessaoAtiva.tenant_id == tenant_id)
        .where(SessaoAtiva.status == "ATIVA")
    )
    result = await session.execute(stmt)
    sessoes = result.scalars().all()

    for s in sessoes:
        s.status = "ENCERRADA"

    await session.commit()
