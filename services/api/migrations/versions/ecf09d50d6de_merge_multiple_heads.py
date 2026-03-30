"""Merge multiple heads

Revision ID: ecf09d50d6de
Revises: 9f279111cf60, d3e4f5a6b7c8
Create Date: 2026-03-28 21:16:33.716039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecf09d50d6de'
down_revision: Union[str, Sequence[str], None] = ('9f279111cf60', 'd3e4f5a6b7c8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
