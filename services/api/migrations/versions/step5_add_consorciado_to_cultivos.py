"""add consorciado field to cultivos

Revision ID: step5_add_consorciado
Revises: step4_introduce_cultivos
Create Date: 2026-04-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "step5_add_consorciado"
down_revision = "step4_introduce_cultivos"
branch_labels = None
depends_on = None


def upgrade():
    # Add consorciado column to cultivos table
    with op.batch_alter_table("cultivos", schema=None) as batch_op:
        batch_op.add_column(sa.Column("consorciado", sa.Boolean(), nullable=False, server_default="false"))
    op.execute("COMMIT")


def downgrade():
    # Remove consorciado column from cultivos table
    with op.batch_alter_table("cultivos", schema=None) as batch_op:
        batch_op.drop_column("consorciado")
    op.execute("COMMIT")
