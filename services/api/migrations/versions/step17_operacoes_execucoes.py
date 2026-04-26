"""step17: operacoes_execucoes

Revision ID: step17_operacoes_execucoes
Revises: step16b_prescricoes_vra
Create Date: 2026-04-24

Introduces granular operation executions while preserving the legacy aggregate
columns in `operacoes_agricolas`.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "step17_operacoes_execucoes"
down_revision: Union[str, Sequence[str], None] = "step16b_prescricoes_vra"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "operacoes_execucoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("operacao_id", sa.Uuid(), nullable=False),
        sa.Column("production_unit_id", sa.Uuid(), nullable=True),
        sa.Column("data_execucao", sa.Date(), nullable=False),
        sa.Column("hora_execucao", sa.Time(), nullable=True),
        sa.Column("quantidade_planejada", sa.Numeric(18, 6), nullable=True),
        sa.Column("quantidade_executada", sa.Numeric(18, 6), nullable=False),
        sa.Column("quantidade_devolvida", sa.Numeric(18, 6), nullable=False, server_default=sa.text("0")),
        sa.Column("unidade_medida_id", sa.Uuid(), nullable=False),
        sa.Column("custo_real", sa.Numeric(15, 2), nullable=True),
        sa.Column("area_ha_executada", sa.Numeric(12, 4), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'REALIZADA'")),
        sa.Column("operador_id", sa.Uuid(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_operacoes_execucoes_tenant_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operacao_id"], ["operacoes_agricolas.id"], name="fk_operacoes_execucoes_operacao_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_unit_id"], ["production_units.id"], name="fk_operacoes_execucoes_production_unit_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["unidade_medida_id"], ["unidades_medida.id"], name="fk_operacoes_execucoes_unidade_medida_id", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operador_id"], ["cadastros_pessoas.id"], name="fk_operacoes_execucoes_operador_id", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("quantidade_executada >= 0", name="ck_operacoes_execucoes_quantidade_executada_nao_negativa"),
        sa.CheckConstraint("quantidade_devolvida >= 0", name="ck_operacoes_execucoes_quantidade_devolvida_nao_negativa"),
        sa.CheckConstraint("quantidade_devolvida <= quantidade_executada", name="ck_operacoes_execucoes_devolvida_lte_executada"),
        sa.CheckConstraint("area_ha_executada IS NULL OR area_ha_executada >= 0", name="ck_operacoes_execucoes_area_nao_negativa"),
        sa.CheckConstraint("status IN ('REALIZADA','DEVOLVIDA','CANCELADA')", name="ck_operacoes_execucoes_status"),
    )

    op.create_index("ix_operacoes_execucoes_tenant_operacao", "operacoes_execucoes", ["tenant_id", "operacao_id"])
    op.create_index(
        "ix_operacoes_execucoes_tenant_pu_data",
        "operacoes_execucoes",
        ["tenant_id", "production_unit_id", "data_execucao"],
    )
    op.create_index("ix_operacoes_execucoes_tenant_data", "operacoes_execucoes", ["tenant_id", "data_execucao"])

    # Backfill: one execution per legacy realized operation. The current
    # legacy model is single-area, so HA is the safest quantity proxy.
    op.execute(
        """
        INSERT INTO operacoes_execucoes (
          id, tenant_id, operacao_id, production_unit_id,
          data_execucao, hora_execucao,
          quantidade_planejada, quantidade_executada, quantidade_devolvida,
          unidade_medida_id, custo_real, area_ha_executada,
          status, operador_id, observacoes
        )
        SELECT
          gen_random_uuid(),
          oa.tenant_id,
          oa.id,
          oa.production_unit_id,
          oa.data_realizada,
          oa.hora_inicio,
          NULLIF(oa.area_aplicada_ha, 0),
          COALESCE(NULLIF(oa.area_aplicada_ha, 0), 1)::numeric,
          0,
          um.id,
          oa.custo_total,
          oa.area_aplicada_ha,
          'REALIZADA',
          oa.operador_id,
          oa.observacoes
        FROM operacoes_agricolas oa
        JOIN unidades_medida um
          ON um.tenant_id IS NULL
         AND um.codigo = 'HA'
         AND um.sistema = true
        WHERE oa.status = 'REALIZADA'
          AND NOT EXISTS (
            SELECT 1
              FROM operacoes_execucoes oe
             WHERE oe.operacao_id = oa.id
          )
        """
    )


def downgrade() -> None:
    op.drop_index("ix_operacoes_execucoes_tenant_data", table_name="operacoes_execucoes")
    op.drop_index("ix_operacoes_execucoes_tenant_pu_data", table_name="operacoes_execucoes")
    op.drop_index("ix_operacoes_execucoes_tenant_operacao", table_name="operacoes_execucoes")
    op.drop_table("operacoes_execucoes")
