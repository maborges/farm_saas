"""add_is_default_to_plano_assinatura

Revision ID: add_is_default_to_plano
Revises: b1c2d3e4f5a6
Create Date: 2026-04-04 00:00:00.000000

Adiciona campo is_default à tabela planos_assinatura.
Apenas um plano pode ser padrão por vez.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_default_to_plano'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar coluna is_default com valor padrão false
    op.add_column(
        'planos_assinatura',
        sa.Column(
            'is_default',
            sa.Boolean(),
            nullable=False,
            server_default='false',
            comment='Plano padrão para onboarding. Apenas um plano pode ser default=True.'
        )
    )

    # Se ainda não existe nenhum plano padrão, marcar o primeiro plano ativo como padrão
    # Isso garante que sempre haverá um plano padrão
    op.execute("""
        UPDATE planos_assinatura
        SET is_default = true
        WHERE id = (
            SELECT id FROM planos_assinatura
            WHERE ativo = true
            ORDER BY created_at ASC
            LIMIT 1
        )
        AND NOT EXISTS (
            SELECT 1 FROM planos_assinatura WHERE is_default = true
        )
    """)


def downgrade() -> None:
    op.drop_column('planos_assinatura', 'is_default')
