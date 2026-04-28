"""step24: permitir origem LEGADO em estoque_movimentos

Revision ID: step24_legado_estoque
Revises: b2c4d6e8f001
Create Date: 2026-04-28
"""

from typing import Sequence, Union

from alembic import op


revision: str = "step24_legado_estoque"
down_revision: Union[str, Sequence[str], None] = "b2c4d6e8f001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_estoque_movimentos_origem", "estoque_movimentos", type_="check")
    op.create_check_constraint(
        "ck_estoque_movimentos_origem",
        "estoque_movimentos",
        "origem IN ('OPERACAO_EXECUCAO','COMPRA','COLHEITA','AJUSTE','MANUAL','TRANSFERENCIA','LEGADO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_estoque_movimentos_origem", "estoque_movimentos", type_="check")
    op.create_check_constraint(
        "ck_estoque_movimentos_origem",
        "estoque_movimentos",
        "origem IN ('OPERACAO_EXECUCAO','COMPRA','COLHEITA','AJUSTE','MANUAL','TRANSFERENCIA')",
    )
