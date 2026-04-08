"""Serviço de telemetria — incrementa contador diário de uso de módulos."""
import uuid
from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy import select, func, desc, text

from core.models.module_usage import ModuleUsageStat


async def increment_module_usage(
    session: AsyncSession,
    tenant_id: UUID,
    module_id: str,
    dia: date | None = None,
) -> None:
    """Upsert atômico: incrementa o contador do dia ou cria nova linha."""
    today = dia or date.today()

    # Detectar dialeto para usar upsert nativo
    dialect = session.bind.dialect.name if session.bind else "postgresql"  # type: ignore[union-attr]

    if dialect == "postgresql":
        stmt = (
            pg_insert(ModuleUsageStat)
            .values(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                module_id=module_id,
                dia=today,
                total_requests=1,
            )
            .on_conflict_do_update(
                constraint="uq_module_usage_per_day",
                set_={"total_requests": ModuleUsageStat.total_requests + 1},
            )
        )
        await session.execute(stmt)
    else:
        # SQLite fallback — sem upsert nativo em SQLAlchemy <2.0, usar get+update
        existing = await session.scalar(
            select(ModuleUsageStat).where(
                ModuleUsageStat.tenant_id == tenant_id,
                ModuleUsageStat.module_id == module_id,
                ModuleUsageStat.dia == today,
            )
        )
        if existing:
            existing.total_requests += 1
            session.add(existing)
        else:
            session.add(ModuleUsageStat(
                tenant_id=tenant_id,
                module_id=module_id,
                dia=today,
                total_requests=1,
            ))


async def get_usage_by_module(
    session: AsyncSession,
    tenant_id: UUID,
    days: int = 30,
) -> list[dict]:
    """Retorna total de requests por módulo nos últimos N dias."""
    from datetime import timedelta
    since = date.today() - timedelta(days=days)
    stmt = (
        select(
            ModuleUsageStat.module_id,
            func.sum(ModuleUsageStat.total_requests).label("total"),
            func.max(ModuleUsageStat.dia).label("ultimo_acesso"),
        )
        .where(
            ModuleUsageStat.tenant_id == tenant_id,
            ModuleUsageStat.dia >= since,
        )
        .group_by(ModuleUsageStat.module_id)
        .order_by(desc("total"))
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "module_id": r.module_id,
            "total_requests": int(r.total),
            "ultimo_acesso": r.ultimo_acesso.isoformat(),
        }
        for r in rows
    ]


async def get_daily_usage(
    session: AsyncSession,
    tenant_id: UUID,
    module_id: str,
    days: int = 30,
) -> list[dict]:
    """Série temporal diária para um módulo específico."""
    from datetime import timedelta
    since = date.today() - timedelta(days=days)
    stmt = (
        select(ModuleUsageStat.dia, ModuleUsageStat.total_requests)
        .where(
            ModuleUsageStat.tenant_id == tenant_id,
            ModuleUsageStat.module_id == module_id,
            ModuleUsageStat.dia >= since,
        )
        .order_by(ModuleUsageStat.dia)
    )
    rows = (await session.execute(stmt)).all()
    return [{"dia": r.dia.isoformat(), "total_requests": r.total_requests} for r in rows]
