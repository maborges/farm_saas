"""Helper para serializar modelos SQLAlchemy e gravar TenantAuditLog."""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect as sa_inspect


def _serialize(obj: Any) -> dict | None:
    """Converte instância SQLAlchemy em dict serializável (sem relações lazy)."""
    if obj is None:
        return None
    try:
        mapper = sa_inspect(type(obj))
        result = {}
        for col in mapper.columns:
            val = getattr(obj, col.key)
            if isinstance(val, uuid.UUID):
                val = str(val)
            elif hasattr(val, "isoformat"):  # datetime / date
                val = val.isoformat()
            elif isinstance(val, Decimal):
                val = float(val)
            result[col.key] = val
        return result
    except Exception:
        return None


async def write_audit_log(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID | None,
    action: str,
    resource: str,
    resource_id: uuid.UUID | None,
    payload_before: dict | None,
    payload_after: dict | None,
    ip_address: str | None = None,
) -> None:
    """Grava um TenantAuditLog na mesma sessão/transação da operação original."""
    # Import local para evitar circular import
    from core.models.tenant_audit_log import TenantAuditLog

    log = TenantAuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        payload_before=payload_before,
        payload_after=payload_after,
        ip_address=ip_address,
    )
    session.add(log)
