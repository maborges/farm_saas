"""step25: drop legacy estoque_movimentacoes table

Revision ID: step25_drop_movimentacoes
Revises: step24_legado_estoque
Create Date: 2026-04-28
"""
from alembic import op

revision = "step25_drop_movimentacoes"
down_revision = "step24_legado_estoque"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("estoque_movimentacoes")


def downgrade():
    pass  # Tabela legada removida intencionalmente — não restaurar
