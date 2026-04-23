"""add_cancellation_fields_to_tarefas

Revision ID: 6d3bbf58bcc7
Revises: 3e5cb19a3727
Create Date: 2026-04-22 22:39:43.976422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d3bbf58bcc7'
down_revision: Union[str, Sequence[str], None] = '3e5cb19a3727'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('safra_tarefas', sa.Column('cancelado_por', sa.UUID(), nullable=True))
    op.add_column('safra_tarefas', sa.Column('cancelado_em', sa.DateTime(), nullable=True))
    op.add_column('safra_tarefas', sa.Column('motivo_cancelamento', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('safra_tarefas', 'motivo_cancelamento')
    op.drop_column('safra_tarefas', 'cancelado_em')
    op.drop_column('safra_tarefas', 'cancelado_por')
