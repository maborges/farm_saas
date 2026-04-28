"""step27: rename insumos_operacao.insumo_id to produto_id

Revision ID: step27_rename_insumo_id
Revises: step26_produto_canonico
Create Date: 2026-04-28
"""
import sqlalchemy as sa
from alembic import op

revision = "step27_rename_insumo_id"
down_revision = "step26_produto_canonico"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("insumos_operacao", "insumo_id", new_column_name="produto_id")

    # Recriar índice com nome canônico
    op.drop_index("ix_insumos_operacao_insumo_id", table_name="insumos_operacao", if_exists=True)
    op.create_index("ix_insumos_operacao_produto_id", "insumos_operacao", ["produto_id"])


def downgrade():
    op.drop_index("ix_insumos_operacao_produto_id", table_name="insumos_operacao")
    op.create_index("ix_insumos_operacao_insumo_id", "insumos_operacao", ["produto_id"])
    op.alter_column("insumos_operacao", "produto_id", new_column_name="insumo_id")
