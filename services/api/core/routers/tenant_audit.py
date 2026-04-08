from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel

from core.dependencies import get_session, get_tenant_id, require_permission
from core.models.tenant_audit_log import TenantAuditLog

router = APIRouter(
    prefix="/audit-log",
    tags=["Auditoria"],
    dependencies=[Depends(require_permission("tenant:audit:view"))],
)


# ==================== SCHEMAS ====================

class TenantAuditLogResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID | None
    action: str
    resource: str
    resource_id: UUID | None
    payload_before: dict | None
    payload_after: dict | None
    ip_address: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class TenantAuditLogListResponse(BaseModel):
    items: List[TenantAuditLogResponse]
    total: int
    page: int
    page_size: int


# ==================== ENDPOINTS ====================

@router.get("", response_model=TenantAuditLogListResponse)
async def listar_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=200),
    action: str | None = None,
    resource: str | None = None,
    resource_id: UUID | None = None,
    user_id: UUID | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Lista logs de auditoria do tenant com filtros e paginação."""
    stmt = select(TenantAuditLog).where(TenantAuditLog.tenant_id == tenant_id)
    count_stmt = select(func.count(TenantAuditLog.id)).where(TenantAuditLog.tenant_id == tenant_id)

    if action:
        stmt = stmt.where(TenantAuditLog.action == action)
        count_stmt = count_stmt.where(TenantAuditLog.action == action)
    if resource:
        stmt = stmt.where(TenantAuditLog.resource == resource)
        count_stmt = count_stmt.where(TenantAuditLog.resource == resource)
    if resource_id:
        stmt = stmt.where(TenantAuditLog.resource_id == resource_id)
        count_stmt = count_stmt.where(TenantAuditLog.resource_id == resource_id)
    if user_id:
        stmt = stmt.where(TenantAuditLog.user_id == user_id)
        count_stmt = count_stmt.where(TenantAuditLog.user_id == user_id)
    if data_inicio:
        stmt = stmt.where(TenantAuditLog.created_at >= datetime.combine(data_inicio, datetime.min.time()))
        count_stmt = count_stmt.where(TenantAuditLog.created_at >= datetime.combine(data_inicio, datetime.min.time()))
    if data_fim:
        stmt = stmt.where(TenantAuditLog.created_at <= datetime.combine(data_fim, datetime.max.time()))
        count_stmt = count_stmt.where(TenantAuditLog.created_at <= datetime.combine(data_fim, datetime.max.time()))

    total = await session.scalar(count_stmt) or 0
    offset = (page - 1) * page_size
    stmt = stmt.order_by(desc(TenantAuditLog.created_at)).offset(offset).limit(page_size)

    result = await session.execute(stmt)
    logs = result.scalars().all()

    return TenantAuditLogListResponse(
        items=[TenantAuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{log_id}", response_model=TenantAuditLogResponse)
async def get_audit_log(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Retorna detalhes de um log de auditoria."""
    log = await session.get(TenantAuditLog, log_id)
    if not log or log.tenant_id != tenant_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Log não encontrado")
    return TenantAuditLogResponse.model_validate(log)
