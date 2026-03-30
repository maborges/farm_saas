"""add_plano_canais_comercializacao

Revision ID: b1c2d3e4f5a6
Revises: a0a58168bc5b
Create Date: 2026-03-28 00:00:00.000000

Adiciona controle independente de canal de comercialização em planos_assinatura:
- disponivel_site: visível no checkout/landing público
- disponivel_crm: visível no CRM para conversão de leads e ofertas personalizadas
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = 'a0a58168bc5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'planos_assinatura',
        sa.Column('disponivel_site', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column(
        'planos_assinatura',
        sa.Column('disponivel_crm', sa.Boolean(), nullable=False, server_default='true')
    )

    # Planos ativos existentes ficam disponíveis no CRM por padrão
    # disponivel_site permanece false — admin define manualmente quais vão ao site
    op.execute("""
        UPDATE planos_assinatura
        SET disponivel_crm = true
        WHERE ativo = true
    """)


def downgrade() -> None:
    op.drop_column('planos_assinatura', 'disponivel_crm')
    op.drop_column('planos_assinatura', 'disponivel_site')
