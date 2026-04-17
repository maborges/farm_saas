"""Allow PULVERIZAÇÃO in PLANEJADA phase

Revision ID: add_planejada_pulv
Revises: f6e6c0c83f72
Create Date: 2026-04-14 12:00:00.000000

Permite operações de PULVERIZAÇÃO (pulverizações) na fase PLANEJADA,
além das fases já permitidas DESENVOLVIMENTO e COLHEITA.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_planejada_pulv'
down_revision: Union[str, Sequence[str], None] = 'f6e6c0c83f72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add PLANEJADA to PULVERIZAÇÃO fases_permitidas."""
    op.execute("""
        UPDATE agricola_operacao_tipo_fase
        SET fases_permitidas = '["PLANEJADA", "DESENVOLVIMENTO", "COLHEITA"]'::jsonb
        WHERE tipo_operacao = 'PULVERIZAÇÃO'
    """)


def downgrade() -> None:
    """Remove PLANEJADA from PULVERIZAÇÃO fases_permitidas."""
    op.execute("""
        UPDATE agricola_operacao_tipo_fase
        SET fases_permitidas = '["DESENVOLVIMENTO", "COLHEITA"]'::jsonb
        WHERE tipo_operacao = 'PULVERIZAÇÃO'
    """)
