"""drop tenant deprecated columns modulos_ativos max_usuarios_simultaneos

Revision ID: drop_tenant_deprecated_cols
Revises: 26b30d8e0daa
Create Date: 2026-04-09

These columns were deprecated in favour of AssinaturaTenant.modulos_inclusos
and AssinaturaTenant.usuarios_contratados. All reads/writes have been removed
from application code.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = 'drop_tenant_deprecated_cols'
down_revision: Union[str, None] = '26b30d8e0daa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('tenants') as batch_op:
        batch_op.drop_column('modulos_ativos')
        batch_op.drop_column('max_usuarios_simultaneos')


def downgrade() -> None:
    with op.batch_alter_table('tenants') as batch_op:
        batch_op.add_column(sa.Column(
            'modulos_ativos', sa.JSON(), nullable=True,
            comment='DEPRECATED: use AssinaturaTenant.modulos_inclusos via grupo'
        ))
        batch_op.add_column(sa.Column(
            'max_usuarios_simultaneos', sa.Integer(), nullable=True,
            comment='DEPRECATED: use AssinaturaTenant.usuarios_contratados via grupo'
        ))
