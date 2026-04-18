"""add periodo ocupacao (data_inicio/data_fim) to cultivos

Revision ID: step6_add_periodo_ocupacao
Revises: step5_add_consorciado
Create Date: 2026-04-18 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "step6_add_periodo_ocupacao"
down_revision = "step5_add_consorciado"
branch_labels = None
depends_on = None


def upgrade():
    # Add data_inicio and data_fim columns to cultivos table
    with op.batch_alter_table("cultivos", schema=None) as batch_op:
        batch_op.add_column(sa.Column("data_inicio", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("data_fim", sa.Date(), nullable=True))
    op.execute("COMMIT")


def downgrade():
    # Remove data_inicio and data_fim columns from cultivos table
    with op.batch_alter_table("cultivos", schema=None) as batch_op:
        batch_op.drop_column("data_fim")
        batch_op.drop_column("data_inicio")
    op.execute("COMMIT")
