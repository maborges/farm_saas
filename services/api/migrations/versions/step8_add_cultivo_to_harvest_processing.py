"""add cultivo_id to romaneios_colheita and cafe_lotes_beneficiamento for production tracking

Revision ID: step8_add_cultivo_to_harvest
Revises: step7_add_cultivo_to_operations
Create Date: 2026-04-18 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "step8_add_cultivo_to_harvest"
down_revision = "step7_add_cultivo_to_operations"
branch_labels = None
depends_on = None


def upgrade():
    # Add cultivo_id to romaneios_colheita table
    with op.batch_alter_table("romaneios_colheita", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cultivo_id", sa.Uuid(), nullable=True, index=True))
        batch_op.create_foreign_key(
            "fk_romaneios_colheita_cultivo",
            "cultivos",
            ["cultivo_id"],
            ["id"],
            ondelete="CASCADE"
        )
    op.execute("COMMIT")

    # Add cultivo_id to cafe_lotes_beneficiamento table
    with op.batch_alter_table("cafe_lotes_beneficiamento", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cultivo_id", sa.Uuid(), nullable=True, index=True))
        batch_op.create_foreign_key(
            "fk_cafe_lotes_beneficiamento_cultivo",
            "cultivos",
            ["cultivo_id"],
            ["id"],
            ondelete="SET NULL"
        )
    op.execute("COMMIT")


def downgrade():
    # Remove cultivo_id from cafe_lotes_beneficiamento table
    with op.batch_alter_table("cafe_lotes_beneficiamento", schema=None) as batch_op:
        batch_op.drop_constraint("fk_cafe_lotes_beneficiamento_cultivo", type_="foreignkey")
        batch_op.drop_column("cultivo_id")

    # Remove cultivo_id from romaneios_colheita table
    with op.batch_alter_table("romaneios_colheita", schema=None) as batch_op:
        batch_op.drop_constraint("fk_romaneios_colheita_cultivo", type_="foreignkey")
        batch_op.drop_column("cultivo_id")

    op.execute("COMMIT")
