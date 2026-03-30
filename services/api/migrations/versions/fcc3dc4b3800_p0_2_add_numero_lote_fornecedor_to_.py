"""P0.2: Add numero_lote_fornecedor to ItemRecebimento for supplier batch tracking

Revision ID: fcc3dc4b3800
Revises: f0a1b2c3d4e5
Create Date: 2026-03-30 20:31:26.611363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcc3dc4b3800'
down_revision: Union[str, Sequence[str], None] = 'f0a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('compras_recebimentos_itens', sa.Column('numero_lote_fornecedor', sa.String(100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('compras_recebimentos_itens', 'numero_lote_fornecedor')
