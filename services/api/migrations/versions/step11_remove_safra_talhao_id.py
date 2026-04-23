"""remove talhao_id legado de safras

Revision ID: step11_remove_safra_talhao_id
Revises: step10_cultivo_area_analise_solo
Create Date: 2026-04-20
"""
from alembic import op
import sqlalchemy as sa

revision = "step11_remove_safra_talhao_id"
down_revision = "step10_cultivo_area_analise_solo"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("safras") as batch_op:
        batch_op.drop_constraint("safras_talhao_id_fkey", type_="foreignkey")
        batch_op.drop_index("ix_safras_talhao_id")
        batch_op.drop_column("talhao_id")


def downgrade():
    with op.batch_alter_table("safras") as batch_op:
        batch_op.add_column(
            sa.Column("talhao_id", sa.UUID(), nullable=True)
        )
        batch_op.create_index("ix_safras_talhao_id", ["talhao_id"])
        batch_op.create_foreign_key(
            "safras_talhao_id_fkey",
            "cadastros_areas_rurais",
            ["talhao_id"],
            ["id"],
            ondelete="CASCADE",
        )
