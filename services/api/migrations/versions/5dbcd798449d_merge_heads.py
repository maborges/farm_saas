"""merge heads

Revision ID: 5dbcd798449d
Revises: step13_analise_solo_upgrade, 461af4a1a386
Create Date: 2026-04-21 15:29:12.500177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dbcd798449d'
down_revision: Union[str, Sequence[str], None] = ('step13_analise_solo_upgrade', '461af4a1a386')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
