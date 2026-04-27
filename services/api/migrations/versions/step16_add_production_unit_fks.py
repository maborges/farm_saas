"""step16: add production_unit_id nullable FKs to legacy operational tables

Revision ID: step16_pu_fks
Revises: step15_pu
Create Date: 2026-04-24

Adds optional references to `production_units` without removing legacy
`cultivo_id`, `talhao_id` or `cultivo_area_id` links. Backfill is deliberately
conservative: only rows with an unambiguous ProductionUnit are updated.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "step16_pu_fks"
down_revision: Union[str, Sequence[str], None] = "step15_pu"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = (
    ("operacoes_agricolas", "fk_operacoes_agricolas_production_unit_id", "ix_operacoes_agricolas_tenant_pu"),
    ("safra_tarefas", "fk_safra_tarefas_production_unit_id", "ix_safra_tarefas_tenant_pu"),
    ("romaneios_colheita", "fk_romaneios_colheita_production_unit_id", "ix_romaneios_colheita_tenant_pu"),
    ("cafe_lotes_beneficiamento", "fk_cafe_lotes_beneficiamento_production_unit_id", "ix_cafe_lotes_beneficiamento_tenant_pu"),
    ("agricola_orcamento_itens", "fk_agricola_orcamento_itens_production_unit_id", "ix_agricola_orcamento_itens_tenant_pu"),
    ("prescricoes_vra", "fk_prescricoes_vra_production_unit_id", "ix_prescricoes_vra_tenant_pu"),
    ("analises_solo", "fk_analises_solo_production_unit_id", "ix_analises_solo_tenant_pu"),
)


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def upgrade() -> None:
    existing_tables = {table_name for table_name, _, _ in TABLES if _table_exists(table_name)}

    for table_name, fk_name, index_name in TABLES:
        if table_name not in existing_tables:
            continue
        op.add_column(table_name, sa.Column("production_unit_id", sa.Uuid(), nullable=True))
        op.create_foreign_key(
            fk_name,
            table_name,
            "production_units",
            ["production_unit_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index(index_name, table_name, ["tenant_id", "production_unit_id"], unique=False)

    # Operações e romaneios têm a chave completa: tenant + safra + cultivo + talhão(area).
    if "operacoes_agricolas" in existing_tables:
        op.execute(
            """
            UPDATE operacoes_agricolas oa
               SET production_unit_id = pu.id
              FROM production_units pu
             WHERE oa.production_unit_id IS NULL
               AND oa.cultivo_id IS NOT NULL
               AND pu.tenant_id = oa.tenant_id
               AND pu.safra_id = oa.safra_id
               AND pu.cultivo_id = oa.cultivo_id
               AND pu.area_id = oa.talhao_id
               AND pu.status <> 'CANCELADA'
            """
        )

    if "romaneios_colheita" in existing_tables:
        op.execute(
            """
            UPDATE romaneios_colheita rc
               SET production_unit_id = pu.id
              FROM production_units pu
             WHERE rc.production_unit_id IS NULL
               AND rc.cultivo_id IS NOT NULL
               AND pu.tenant_id = rc.tenant_id
               AND pu.safra_id = rc.safra_id
               AND pu.cultivo_id = rc.cultivo_id
               AND pu.area_id = rc.talhao_id
               AND pu.status <> 'CANCELADA'
            """
        )

    if "cafe_lotes_beneficiamento" in existing_tables:
        op.execute(
            """
            UPDATE cafe_lotes_beneficiamento lb
               SET production_unit_id = pu.id
              FROM production_units pu
             WHERE lb.production_unit_id IS NULL
               AND lb.cultivo_id IS NOT NULL
               AND lb.talhao_id IS NOT NULL
               AND pu.tenant_id = lb.tenant_id
               AND pu.safra_id = lb.safra_id
               AND pu.cultivo_id = lb.cultivo_id
               AND pu.area_id = lb.talhao_id
               AND pu.status <> 'CANCELADA'
            """
        )

    # Tarefas resolvem pela origem cultivo_area_id quando disponível.
    if "safra_tarefas" in existing_tables:
        op.execute(
            """
            UPDATE safra_tarefas st
               SET production_unit_id = pu.id
              FROM production_units pu
             WHERE st.production_unit_id IS NULL
               AND st.cultivo_area_id IS NOT NULL
               AND pu.tenant_id = st.tenant_id
               AND pu.safra_id = st.safra_id
               AND pu.cultivo_area_id = st.cultivo_area_id
               AND (st.talhao_id IS NULL OR pu.area_id = st.talhao_id)
               AND pu.status <> 'CANCELADA'
            """
        )

    # agricola_orcamento_itens, prescricoes_vra e analises_solo não têm hoje
    # área+cultivo+safra suficientes para backfill sem inferência ambígua.


def downgrade() -> None:
    for table_name, fk_name, index_name in reversed(TABLES):
        if not _table_exists(table_name):
            continue
        op.drop_index(index_name, table_name=table_name)
        op.drop_constraint(fk_name, table_name, type_="foreignkey")
        op.drop_column(table_name, "production_unit_id")
