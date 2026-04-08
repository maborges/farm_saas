"""merge_heads

Revision ID: c5f9761aaa6a
Revises: grupo_usuario_mandatory_grupo, imoveis_rurais_init, 20260402_add_login_rate_limiting
Create Date: 2026-04-03 09:36:16.606728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5f9761aaa6a'
down_revision: Union[str, Sequence[str], None] = ('grupo_usuario_mandatory_grupo', 'imoveis_rurais_init', '20260402_add_login_rate_limiting')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
