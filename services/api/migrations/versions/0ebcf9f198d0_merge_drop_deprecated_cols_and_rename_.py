"""merge_drop_deprecated_cols_and_rename_fazendas

Revision ID: 0ebcf9f198d0
Revises: drop_tenant_deprecated_cols, rename_fazendas_unidades_prod
Create Date: 2026-04-09 12:34:32.520578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ebcf9f198d0'
down_revision: Union[str, Sequence[str], None] = ('drop_tenant_deprecated_cols', 'rename_fazendas_unidades_prod')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
