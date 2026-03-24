from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List
from uuid import UUID
from datetime import datetime, date

from core.dependencies import get_session, get_current_admin, require_permission
from core.models.admin_audit_log import AdminAuditLog
from pydantic import BaseModel

router = APIRouter(
    prefix="/backoffice/audit",
    tags=["Backoffice - Auditoria"],
    dependencies=[Depends(require_permission("backoffice:audit:view"))],
)


# ==================== SCHEMAS ====================

class AuditLogResponse(BaseModel):
    id: UUID
    admin_user_id: UUID
    admin_email: str
    acao: str
    entidade: str
    entidade_id: UUID | None
    descricao: str | None
    dados_anteriores: dict | None
    dados_novos: dict | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditStatsResponse(BaseModel):
    total: int
    por_acao: dict[str, int]
    por_entidade: dict[str, int]
    por_admin: dict[str, int]


class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


# ==================== ENDPOINTS ====================

@router.get("/stats", response_model=AuditStatsResponse)
async def get_audit_stats(
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Estatísticas gerais de auditoria."""
    total = await session.scalar(select(func.count(AdminAuditLog.id)))

    # Por ação
    result = await session.execute(
        select(AdminAuditLog.acao, func.count(AdminAuditLog.id))
        .group_by(AdminAuditLog.acao)
        .order_by(desc(func.count(AdminAuditLog.id)))
        .limit(20)
    )
    por_acao = {row[0]: row[1] for row in result}

    # Por entidade
    result = await session.execute(
        select(AdminAuditLog.entidade, func.count(AdminAuditLog.id))
        .group_by(AdminAuditLog.entidade)
        .order_by(desc(func.count(AdminAuditLog.id)))
    )
    por_entidade = {row[0]: row[1] for row in result}

    # Por admin
    result = await session.execute(
        select(AdminAuditLog.admin_email, func.count(AdminAuditLog.id))
        .group_by(AdminAuditLog.admin_email)
        .order_by(desc(func.count(AdminAuditLog.id)))
        .limit(10)
    )
    por_admin = {row[0]: row[1] for row in result}

    return AuditStatsResponse(
        total=total or 0,
        por_acao=por_acao,
        por_entidade=por_entidade,
        por_admin=por_admin,
    )


@router.get("", response_model=AuditLogListResponse)
async def listar_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=200),
    acao: str | None = None,
    entidade: str | None = None,
    admin_email: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    busca: str | None = None,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Lista logs de auditoria com filtros e paginação."""
    stmt = select(AdminAuditLog)
    count_stmt = select(func.count(AdminAuditLog.id))

    # Filtros
    if acao:
        stmt = stmt.where(AdminAuditLog.acao == acao)
        count_stmt = count_stmt.where(AdminAuditLog.acao == acao)
    if entidade:
        stmt = stmt.where(AdminAuditLog.entidade == entidade)
        count_stmt = count_stmt.where(AdminAuditLog.entidade == entidade)
    if admin_email:
        stmt = stmt.where(AdminAuditLog.admin_email.ilike(f"%{admin_email}%"))
        count_stmt = count_stmt.where(AdminAuditLog.admin_email.ilike(f"%{admin_email}%"))
    if data_inicio:
        stmt = stmt.where(AdminAuditLog.created_at >= datetime.combine(data_inicio, datetime.min.time()))
        count_stmt = count_stmt.where(AdminAuditLog.created_at >= datetime.combine(data_inicio, datetime.min.time()))
    if data_fim:
        stmt = stmt.where(AdminAuditLog.created_at <= datetime.combine(data_fim, datetime.max.time()))
        count_stmt = count_stmt.where(AdminAuditLog.created_at <= datetime.combine(data_fim, datetime.max.time()))
    if busca:
        stmt = stmt.where(AdminAuditLog.descricao.ilike(f"%{busca}%"))
        count_stmt = count_stmt.where(AdminAuditLog.descricao.ilike(f"%{busca}%"))

    total = await session.scalar(count_stmt) or 0

    # Paginação e ordenação
    offset = (page - 1) * page_size
    stmt = stmt.order_by(desc(AdminAuditLog.created_at)).offset(offset).limit(page_size)

    result = await session.execute(stmt)
    logs = result.scalars().all()

    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Retorna detalhes de um log de auditoria."""
    log = await session.get(AdminAuditLog, log_id)
    if not log:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Log não encontrado")

    return AuditLogResponse.model_validate(log)
