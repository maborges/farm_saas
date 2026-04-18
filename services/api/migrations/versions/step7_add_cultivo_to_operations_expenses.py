"""add cultivo_id to operacoes_agricolas and fin_despesas for cost tracking

Revision ID: step7_add_cultivo_to_operations
Revises: step6_add_periodo_ocupacao
Create Date: 2026-04-18 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "step7_add_cultivo_to_operations"
down_revision = "step6_add_periodo_ocupacao"
branch_labels = None
depends_on = None


def upgrade():
    # Add cultivo_id to operacoes_agricolas table
    with op.batch_alter_table("operacoes_agricolas", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cultivo_id", sa.Uuid(), nullable=True, index=True))
        batch_op.create_foreign_key(
            "fk_operacoes_agricolas_cultivo",
            "cultivos",
            ["cultivo_id"],
            ["id"],
            ondelete="CASCADE"
        )
    op.execute("COMMIT")

    # Add cultivo_id to fin_despesas table
    with op.batch_alter_table("fin_despesas", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cultivo_id", sa.Uuid(), nullable=True, index=True))
        batch_op.create_foreign_key(
            "fk_fin_despesas_cultivo",
            "cultivos",
            ["cultivo_id"],
            ["id"],
            ondelete="SET NULL"
        )
    op.execute("COMMIT")


def downgrade():
    # Remove cultivo_id from fin_despesas table
    with op.batch_alter_table("fin_despesas", schema=None) as batch_op:
        batch_op.drop_constraint("fk_fin_despesas_cultivo", type_="foreignkey")
        batch_op.drop_column("cultivo_id")

    # Remove cultivo_id from operacoes_agricolas table
    with op.batch_alter_table("operacoes_agricolas", schema=None) as batch_op:
        batch_op.drop_constraint("fk_operacoes_agricolas_cultivo", type_="foreignkey")
        batch_op.drop_column("cultivo_id")

    op.execute("COMMIT")
