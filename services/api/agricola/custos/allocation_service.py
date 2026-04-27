from datetime import date
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from agricola.custos.models import CostAllocation
from agricola.operacoes.models import OperacaoExecucao  # noqa: F401 - registers FK target in metadata
from agricola.production_units.models import ProductionUnit  # noqa: F401 - registers FK target in metadata
from core.models.tenant import Tenant  # noqa: F401 - registers FK target in metadata
from financeiro.models.rateio import Rateio
from operacional.models.estoque import EstoqueMovimento  # noqa: F401 - registers FK target in metadata


async def registrar_cost_allocation(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    production_unit_id: UUID,
    source: str,
    amount: float,
    allocation_date: date,
    cost_category: str = "OUTROS",
    source_id: UUID | None = None,
    operation_execution_id: UUID | None = None,
    inventory_movement_id: UUID | None = None,
    fin_rateio_id: UUID | None = None,
    allocation_method: str = "DIRECT",
    allocation_basis: float | None = None,
) -> CostAllocation:
    allocation = CostAllocation(
        tenant_id=tenant_id,
        production_unit_id=production_unit_id,
        source=source,
        source_id=source_id,
        operation_execution_id=operation_execution_id,
        inventory_movement_id=inventory_movement_id,
        fin_rateio_id=fin_rateio_id,
        cost_category=cost_category,
        amount=amount,
        allocation_date=allocation_date,
        allocation_method=allocation_method,
        allocation_basis=allocation_basis,
    )
    session.add(allocation)
    return allocation


async def registrar_allocations_fin_rateio(session: AsyncSession, rateio: Rateio) -> int:
    """Project a financial rateio into agricultural cost allocations when PU can be resolved."""
    result = await session.execute(
        text(
            """
            WITH r AS (
              SELECT
                fr.id AS rateio_id,
                fr.tenant_id,
                fr.valor_rateado::numeric AS valor_rateado,
                fr.safra_id,
                fr.talhao_id,
                d.cultivo_id,
                COALESCE(d.competencia, d.data_pagamento, d.data_emissao) AS allocation_date
              FROM fin_rateios fr
              JOIN fin_despesas d
                ON d.id = fr.despesa_id
               AND d.tenant_id = fr.tenant_id
              WHERE fr.id = :rateio_id
                AND fr.safra_id IS NOT NULL
                AND fr.valor_rateado <> 0
            ),
            candidatos AS (
              SELECT
                r.*,
                pu.id AS production_unit_id,
                pu.area_ha::numeric AS area_ha
              FROM r
              JOIN production_units pu
                ON pu.tenant_id = r.tenant_id
               AND pu.safra_id = r.safra_id
               AND pu.status <> 'CANCELADA'
               AND (r.talhao_id IS NULL OR pu.area_id = r.talhao_id)
               AND (r.cultivo_id IS NULL OR pu.cultivo_id = r.cultivo_id)
            ),
            ponderado AS (
              SELECT
                c.*,
                SUM(c.area_ha) OVER (PARTITION BY c.rateio_id) AS total_area,
                COUNT(*) OVER (PARTITION BY c.rateio_id) AS qtd_pus
              FROM candidatos c
            ),
            inserted AS (
              INSERT INTO cost_allocations (
                id, tenant_id, production_unit_id,
                source, source_id, fin_rateio_id,
                cost_category, amount, allocation_date,
                allocation_method, allocation_basis
              )
              SELECT
                gen_random_uuid(),
                p.tenant_id,
                p.production_unit_id,
                'FIN_RATEIO',
                p.rateio_id,
                p.rateio_id,
                'DESPESA_FINANCEIRA',
                CASE
                  WHEN p.qtd_pus = 1 THEN round(p.valor_rateado, 2)
                  ELSE round((p.valor_rateado * p.area_ha / NULLIF(p.total_area, 0))::numeric, 2)
                END,
                p.allocation_date,
                CASE WHEN p.qtd_pus = 1 THEN 'DIRECT' ELSE 'AREA_HA' END,
                CASE WHEN p.qtd_pus = 1 THEN p.area_ha ELSE p.total_area END
              FROM ponderado p
              WHERE p.total_area > 0
                AND NOT EXISTS (
                  SELECT 1
                    FROM cost_allocations ca
                   WHERE ca.source = 'FIN_RATEIO'
                     AND ca.source_id = p.rateio_id
                     AND ca.production_unit_id = p.production_unit_id
                )
              RETURNING id
            )
            SELECT COUNT(*) FROM inserted
            """
        ),
        {"rateio_id": rateio.id},
    )
    return int(result.scalar_one() or 0)
