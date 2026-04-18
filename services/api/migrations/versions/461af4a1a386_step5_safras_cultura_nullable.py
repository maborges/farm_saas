"""step5_safras_cultura_nullable

Revision ID: 461af4a1a386
Revises: step4_cultivos_intro
Create Date: 2026-04-18 06:49:07.833315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '461af4a1a386'
down_revision: Union[str, Sequence[str], None] = 'step4_cultivos_intro'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Torna safras.cultura nullable — campo foi movido para a entidade Cultivo."""
    op.alter_column('safras', 'cultura', existing_type=sa.String(length=100), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE safras SET cultura = 'DESCONHECIDA' WHERE cultura IS NULL")
    op.alter_column('safras', 'cultura', existing_type=sa.String(length=100), nullable=False)
