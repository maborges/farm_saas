"""step19: cost_allocations by production unit

Revision ID: step19_cost_allocations
Revises: step18_estoque_movimentos
Create Date: 2026-04-24

Creates the agricultural cost allocation view by ProductionUnit. Financial
rateios remain the accounting source of truth; this table is the agricultural
analysis layer.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "step19_cost_allocations"
down_revision: Union[str, Sequence[str], None] = "step18_estoque_movimentos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cost_allocations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("production_unit_id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("operation_execution_id", sa.Uuid(), nullable=True),
        sa.Column("inventory_movement_id", sa.Uuid(), nullable=True),
        sa.Column("fin_rateio_id", sa.Uuid(), nullable=True),
        sa.Column("cost_category", sa.String(32), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default=sa.text("'BRL'")),
        sa.Column("allocation_date", sa.Date(), nullable=False),
        sa.Column("allocation_method", sa.String(24), nullable=False, server_default=sa.text("'DIRECT'")),
        sa.Column("allocation_basis", sa.Numeric(18, 6), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_cost_allocations_tenant_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_unit_id"], ["production_units.id"], name="fk_cost_allocations_production_unit_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["operation_execution_id"],
            ["operacoes_execucoes.id"],
            name="fk_cost_allocations_operation_execution_id",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["inventory_movement_id"],
            ["estoque_movimentos.id"],
            name="fk_cost_allocations_inventory_movement_id",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["fin_rateio_id"], ["fin_rateios.id"], name="fk_cost_allocations_fin_rateio_id", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("amount <> 0", name="ck_cost_allocations_amount_nonzero"),
        sa.CheckConstraint(
            "source IN ('OPERATION_EXECUTION','INVENTORY_MOVEMENT','FIN_RATEIO','MANUAL')",
            name="ck_cost_allocations_source",
        ),
        sa.CheckConstraint(
            "cost_category IN ('INSUMO','MAO_OBRA','MAQUINARIO','SERVICO','DESPESA_FINANCEIRA','OUTROS')",
            name="ck_cost_allocations_category",
        ),
        sa.CheckConstraint(
            "allocation_method IN ('DIRECT','PERCENTAGE','AREA_HA','YIELD_SC')",
            name="ck_cost_allocations_method",
        ),
        sa.CheckConstraint(
            "(source = 'OPERATION_EXECUTION' AND operation_execution_id IS NOT NULL) OR source <> 'OPERATION_EXECUTION'",
            name="ck_cost_allocations_source_operation_execution",
        ),
        sa.CheckConstraint(
            "(source = 'INVENTORY_MOVEMENT' AND inventory_movement_id IS NOT NULL) OR source <> 'INVENTORY_MOVEMENT'",
            name="ck_cost_allocations_source_inventory_movement",
        ),
        sa.CheckConstraint(
            "(source = 'FIN_RATEIO' AND fin_rateio_id IS NOT NULL) OR source <> 'FIN_RATEIO'",
            name="ck_cost_allocations_source_fin_rateio",
        ),
    )

    op.create_index(
        "ix_cost_allocations_tenant_pu_category",
        "cost_allocations",
        ["tenant_id", "production_unit_id", "cost_category"],
    )
    op.create_index("ix_cost_allocations_tenant_source", "cost_allocations", ["tenant_id", "source", "source_id"])
    op.create_index("ix_cost_allocations_tenant_date", "cost_allocations", ["tenant_id", "allocation_date"])
    op.create_index("ix_cost_allocations_operation_execution", "cost_allocations", ["operation_execution_id"])
    op.create_index("ix_cost_allocations_inventory_movement", "cost_allocations", ["inventory_movement_id"])
    op.create_index("ix_cost_allocations_fin_rateio", "cost_allocations", ["fin_rateio_id"])

    op.execute(
        """
        INSERT INTO cost_allocations (
          id, tenant_id, production_unit_id,
          source, source_id, operation_execution_id,
          cost_category, amount, allocation_date,
          allocation_method, allocation_basis
        )
        SELECT
          gen_random_uuid(),
          oe.tenant_id,
          oe.production_unit_id,
          'OPERATION_EXECUTION',
          oe.id,
          oe.id,
          'OUTROS',
          oe.custo_real,
          oe.data_execucao,
          'DIRECT',
          oe.area_ha_executada
        FROM operacoes_execucoes oe
        WHERE oe.production_unit_id IS NOT NULL
          AND oe.custo_real IS NOT NULL
          AND oe.custo_real <> 0
          AND NOT EXISTS (
            SELECT 1
              FROM cost_allocations ca
             WHERE ca.source = 'OPERATION_EXECUTION'
               AND ca.source_id = oe.id
               AND ca.production_unit_id = oe.production_unit_id
          )
        """
    )

    op.execute(
        """
        WITH candidatos AS (
          SELECT
            r.id AS rateio_id,
            r.tenant_id,
            r.valor_rateado::numeric AS valor_rateado,
            r.safra_id,
            r.talhao_id,
            d.cultivo_id,
            COALESCE(d.competencia, d.data_pagamento, d.data_emissao) AS allocation_date,
            pu.id AS production_unit_id,
            pu.area_ha::numeric AS area_ha
          FROM fin_rateios r
          JOIN fin_despesas d
            ON d.id = r.despesa_id
           AND d.tenant_id = r.tenant_id
          JOIN production_units pu
            ON pu.tenant_id = r.tenant_id
           AND pu.safra_id = r.safra_id
           AND pu.status <> 'CANCELADA'
           AND (r.talhao_id IS NULL OR pu.area_id = r.talhao_id)
           AND (d.cultivo_id IS NULL OR pu.cultivo_id = d.cultivo_id)
          WHERE r.safra_id IS NOT NULL
            AND r.valor_rateado <> 0
        ),
        ponderado AS (
          SELECT
            c.*,
            SUM(c.area_ha) OVER (PARTITION BY c.rateio_id) AS total_area,
            COUNT(*) OVER (PARTITION BY c.rateio_id) AS qtd_pus
          FROM candidatos c
        )
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
        """
    )


def downgrade() -> None:
    op.drop_index("ix_cost_allocations_fin_rateio", table_name="cost_allocations")
    op.drop_index("ix_cost_allocations_inventory_movement", table_name="cost_allocations")
    op.drop_index("ix_cost_allocations_operation_execution", table_name="cost_allocations")
    op.drop_index("ix_cost_allocations_tenant_date", table_name="cost_allocations")
    op.drop_index("ix_cost_allocations_tenant_source", table_name="cost_allocations")
    op.drop_index("ix_cost_allocations_tenant_pu_category", table_name="cost_allocations")
    op.drop_table("cost_allocations")
