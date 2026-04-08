"""merge_heads

Revision ID: 48126310bfd6
Revises: 4f38388390af, grupo_assinatura_refactor
Create Date: 2026-04-04 03:21:57.627205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48126310bfd6'
down_revision: Union[str, Sequence[str], None] = ('4f38388390af', 'grupo_assinatura_refactor')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
