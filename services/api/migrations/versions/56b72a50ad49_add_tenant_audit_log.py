"""add_tenant_audit_log

Revision ID: 56b72a50ad49
Revises: c5f9761aaa6a
Create Date: 2026-04-03 15:54:07.981557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56b72a50ad49'
down_revision: Union[str, Sequence[str], None] = 'c5f9761aaa6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_audit_log",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("resource", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("payload_before", sa.JSON(), nullable=True),
        sa.Column("payload_after", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tenant_audit_log_tenant_id", "tenant_audit_log", ["tenant_id"])
    op.create_index("ix_tenant_audit_log_user_id", "tenant_audit_log", ["user_id"])
    op.create_index("ix_tenant_audit_log_action", "tenant_audit_log", ["action"])
    op.create_index("ix_tenant_audit_log_resource", "tenant_audit_log", ["resource"])
    op.create_index("ix_tenant_audit_log_created_at", "tenant_audit_log", ["created_at"])
    op.create_index("ix_tenant_audit_resource", "tenant_audit_log", ["tenant_id", "resource", "resource_id"])
    op.create_index("ix_tenant_audit_timeline", "tenant_audit_log", ["tenant_id", "created_at"])


def downgrade() -> None:
    op.drop_table("tenant_audit_log")
