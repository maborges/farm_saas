"""tenant_activation_token

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-03-28 00:01:00.000000

Adiciona campos de ativação de conta ao tenant (fluxo de conversão de lead):
- activation_token: token único enviado por email ao assinante
- activation_expires_at: expiração do token (48h após envio)
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'tenants',
        sa.Column('activation_token', sa.String(100), nullable=True)
    )
    op.add_column(
        'tenants',
        sa.Column('activation_expires_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_tenants_activation_token', 'tenants', ['activation_token'])


def downgrade() -> None:
    op.drop_index('ix_tenants_activation_token', table_name='tenants')
    op.drop_column('tenants', 'activation_expires_at')
    op.drop_column('tenants', 'activation_token')
