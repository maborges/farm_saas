"""seed_operacao_tipo_fase

Revision ID: f6e6c0c83f72
Revises: de8f5829583c
Create Date: 2026-04-14 17:27:24.640967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6e6c0c83f72'
down_revision: Union[str, Sequence[str], None] = 'de8f5829583c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
