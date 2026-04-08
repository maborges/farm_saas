"""merge_all_heads

Revision ID: 1795966a0c0a
Revises: 001_notas_fiscais, 035, fase3_sankhya, rh_colaborador_nome_cpf
Create Date: 2026-04-02 02:43:52.140274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1795966a0c0a'
down_revision: Union[str, Sequence[str], None] = ('001_notas_fiscais', '035', 'fase3_sankhya', 'rh_colaborador_nome_cpf')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
