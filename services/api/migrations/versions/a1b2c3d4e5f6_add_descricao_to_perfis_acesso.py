"""add_descricao_to_perfis_acesso

Revision ID: a1b2c3_perfis_acesso
Revises: eacd7ecdb359
Create Date: 2026-03-17 00:00:00.000000

Adiciona coluna descricao em perfis_acesso para armazenar
a descrição de perfis customizados dos tenants e perfis padrão do sistema.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3_perfis_acesso'
down_revision: Union[str, Sequence[str], None] = 'eacd7ecdb359'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('perfis_acesso', schema=None) as batch_op:
        batch_op.add_column(sa.Column('descricao', sa.String(500), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('perfis_acesso', schema=None) as batch_op:
        batch_op.drop_column('descricao')
