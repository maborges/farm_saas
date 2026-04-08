"""merge_heads_final

Revision ID: 24e6a080f3b3
Revises: 9fef33b8dd9f, add_is_default_to_plano
Create Date: 2026-04-05 17:00:32.896685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24e6a080f3b3'
down_revision: Union[str, Sequence[str], None] = ('9fef33b8dd9f', 'add_is_default_to_plano')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
