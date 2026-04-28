"""add unique partial index on compras_fornecedores tenant+pessoa

Revision ID: b2c4d6e8f001
Revises: 7d9b6a1c2f30
Create Date: 2026-04-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c4d6e8f001"
down_revision: Union[str, Sequence[str], None] = "7d9b6a1c2f30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_compras_fornecedores_tenant_pessoa",
        "compras_fornecedores",
        ["tenant_id", "pessoa_id"],
        unique=True,
        schema="farms",
        postgresql_where=sa.text("pessoa_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_compras_fornecedores_tenant_pessoa",
        table_name="compras_fornecedores",
        schema="farms",
    )
