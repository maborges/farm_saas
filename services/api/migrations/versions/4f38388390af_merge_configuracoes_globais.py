"""merge_configuracoes_globais

Revision ID: 4f38388390af
Revises: 20260403_pwd_recovery, a1b2c3configuracoes
Create Date: 2026-04-03 17:26:24.809206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f38388390af'
down_revision: Union[str, Sequence[str], None] = ('20260403_pwd_recovery', 'a1b2c3configuracoes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
