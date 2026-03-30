"""assinatura_stripe_subscription_id

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-03-28 00:02:00.000000

Adiciona stripe_subscription_id em assinaturas_tenant para rastrear
a assinatura recorrente no Stripe após pagamento confirmado via webhook.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd3e4f5a6b7c8'
down_revision: Union[str, None] = 'c2d3e4f5a6b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'assinaturas_tenant',
        sa.Column('stripe_subscription_id', sa.String(100), nullable=True)
    )
    op.create_index(
        'ix_assinaturas_tenant_stripe_subscription_id',
        'assinaturas_tenant',
        ['stripe_subscription_id']
    )


def downgrade() -> None:
    op.drop_index('ix_assinaturas_tenant_stripe_subscription_id', table_name='assinaturas_tenant')
    op.drop_column('assinaturas_tenant', 'stripe_subscription_id')
