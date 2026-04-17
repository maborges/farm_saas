"""culturas_tenant_nullable_sistema_column

Revision ID: de8f5829583c
Revises: conversao_unidade_v1
Create Date: 2026-04-13 17:09:05.583516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de8f5829583c'
down_revision: Union[str, Sequence[str], None] = 'conversao_unidade_v1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
