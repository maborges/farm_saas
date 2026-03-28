"""notificacoes_table

Revision ID: ab2e515b14fe
Revises: 9be54904b80e
Create Date: 2026-03-25 23:16:23.289383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab2e515b14fe'
down_revision: Union[str, Sequence[str], None] = '9be54904b80e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notificacoes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("tipo", sa.String(60), nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("mensagem", sa.String(1000), nullable=False),
        sa.Column("lida", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notificacoes_tenant_id", "notificacoes", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_notificacoes_tenant_id", table_name="notificacoes")
    op.drop_table("notificacoes")
