"""merge commodity refactor into main

Merge das duas branches de migration:
- a1b2c3_perfis_acesso (main)
- commodity_refactor_v1 → produto_colhido_v1 (commodities)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'merge_commodity_refactor'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3_perfis_acesso', 'produto_colhido_v1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
