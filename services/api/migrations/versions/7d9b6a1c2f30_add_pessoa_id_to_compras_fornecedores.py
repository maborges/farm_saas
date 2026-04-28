"""add pessoa_id to compras_fornecedores

Revision ID: 7d9b6a1c2f30
Revises: 39df121d9a4b
Create Date: 2026-04-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d9b6a1c2f30"
down_revision: Union[str, Sequence[str], None] = "39df121d9a4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("compras_fornecedores", schema=None) as batch_op:
        batch_op.add_column(sa.Column("pessoa_id", sa.Uuid(), nullable=True))
        batch_op.create_index(batch_op.f("ix_compras_fornecedores_pessoa_id"), ["pessoa_id"], unique=False)
        batch_op.create_foreign_key(
            batch_op.f("fk_compras_fornecedores_pessoa_id_cadastros_pessoas"),
            "cadastros_pessoas",
            ["pessoa_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("compras_fornecedores", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_compras_fornecedores_pessoa_id_cadastros_pessoas"),
            type_="foreignkey",
        )
        batch_op.drop_index(batch_op.f("ix_compras_fornecedores_pessoa_id"))
        batch_op.drop_column("pessoa_id")
