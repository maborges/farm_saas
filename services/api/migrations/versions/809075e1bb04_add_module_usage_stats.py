"""add_module_usage_stats

Revision ID: 809075e1bb04
Revises: 574378e90967
Create Date: 2026-04-04 05:16:30.903088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '809075e1bb04'
down_revision: Union[str, Sequence[str], None] = '574378e90967'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "module_usage_stats",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module_id", sa.String(50), nullable=False),
        sa.Column("dia", sa.Date, nullable=False),
        sa.Column("total_requests", sa.Integer, nullable=False, server_default="1"),
    )
    op.create_index("ix_module_usage_tenant_id", "module_usage_stats", ["tenant_id"])
    op.create_index("ix_module_usage_module_id", "module_usage_stats", ["module_id"])
    op.create_index("ix_module_usage_dia", "module_usage_stats", ["dia"])
    op.create_index("ix_module_usage_tenant_dia", "module_usage_stats", ["tenant_id", "dia"])
    op.create_unique_constraint(
        "uq_module_usage_per_day",
        "module_usage_stats",
        ["tenant_id", "module_id", "dia"],
    )


def downgrade() -> None:
    op.drop_table("module_usage_stats")
