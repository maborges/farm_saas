"""step16b: restore prescricoes_vra table with production_unit_id

Revision ID: step16b_prescricoes_vra
Revises: step16_pu_fks
Create Date: 2026-04-24

Some environments reached Step 16 without the optional `prescricoes_vra` table,
although the application still exposes its model/router. This migration makes
the schema explicit again and includes the Step 16 `production_unit_id` FK.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID


revision: str = "step16b_prescricoes_vra"
down_revision: Union[str, Sequence[str], None] = "step16_pu_fks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def upgrade() -> None:
    if not _table_exists("prescricoes_vra"):
        op.create_table(
            "prescricoes_vra",
            sa.Column("id", sa.Integer(), primary_key=True, index=True, autoincrement=True),
            sa.Column("tenant_id", sa.String(50), nullable=False, index=True),
            sa.Column("production_unit_id", PGUUID(as_uuid=True), nullable=True),
            sa.Column("unidade_produtiva_id", PGUUID(as_uuid=True), nullable=False),
            sa.Column("talhao_id", PGUUID(as_uuid=True), nullable=True),
            sa.Column("safra_id", PGUUID(as_uuid=True), nullable=True),
            sa.Column("tipo", sa.String(50), nullable=False),
            sa.Column("elemento", sa.String(50), nullable=True),
            sa.Column("dose_media", sa.Float(), nullable=True),
            sa.Column("dose_minima", sa.Float(), nullable=True),
            sa.Column("dose_maxima", sa.Float(), nullable=True),
            sa.Column("unidade", sa.String(20), server_default="kg/ha", nullable=True),
            sa.Column("caminho_isoxml", sa.String(500), nullable=True),
            sa.Column("caminho_shapefile", sa.String(500), nullable=True),
            sa.Column("caminho_geojson", sa.String(500), nullable=True),
            sa.Column("grid_tamanho_m", sa.Float(), nullable=True),
            sa.Column("total_pontos", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(50), server_default="rascunho", nullable=True),
            sa.Column("aprovada_por", PGUUID(as_uuid=True), nullable=True),
            sa.Column("aprovada_em", sa.DateTime(), nullable=True),
            sa.Column("responsavel_tecnico", sa.String(200), nullable=True),
            sa.Column("crt", sa.String(100), nullable=True),
            sa.Column("observacoes", sa.Text(), nullable=True),
            sa.Column("criada_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=True),
            sa.Column("atualizada_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=True),
            sa.ForeignKeyConstraint(
                ["production_unit_id"],
                ["production_units.id"],
                name="fk_prescricoes_vra_production_unit_id",
                ondelete="SET NULL",
            ),
            sa.ForeignKeyConstraint(
                ["unidade_produtiva_id"],
                ["unidades_produtivas.id"],
                name="fk_prescricoes_vra_unidade_produtiva_id",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["talhao_id"],
                ["cadastros_areas_rurais.id"],
                name="fk_prescricoes_vra_talhao_id",
                ondelete="SET NULL",
            ),
            sa.ForeignKeyConstraint(
                ["safra_id"],
                ["safras.id"],
                name="fk_prescricoes_vra_safra_id",
                ondelete="SET NULL",
            ),
        )
        op.create_index("ix_prescricoes_vra_tenant_pu", "prescricoes_vra", ["tenant_id", "production_unit_id"])
        return

    if not _column_exists("prescricoes_vra", "production_unit_id"):
        op.add_column("prescricoes_vra", sa.Column("production_unit_id", PGUUID(as_uuid=True), nullable=True))
        op.create_foreign_key(
            "fk_prescricoes_vra_production_unit_id",
            "prescricoes_vra",
            "production_units",
            ["production_unit_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index("ix_prescricoes_vra_tenant_pu", "prescricoes_vra", ["tenant_id", "production_unit_id"])


def downgrade() -> None:
    if not _table_exists("prescricoes_vra"):
        return
    op.drop_index("ix_prescricoes_vra_tenant_pu", table_name="prescricoes_vra")
    op.drop_table("prescricoes_vra")
