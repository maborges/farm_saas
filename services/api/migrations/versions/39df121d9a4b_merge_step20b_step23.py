"""merge_step20b_step23

Revision ID: 39df121d9a4b
Revises: step20b_ir_depreciacao, step23_billing_hardening
Create Date: 2026-04-26 16:18:22.129665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39df121d9a4b'
down_revision: Union[str, Sequence[str], None] = ('step20b_ir_depreciacao', 'step23_billing_hardening')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
