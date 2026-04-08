"""remove limite_usuarios deprecated column

Revision ID: a1b2c3d4e5f7
Revises: add_is_default_to_plano_assinatura
Create Date: 2026-04-05
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f7'
down_revision = 'add_is_default_to_plano'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove o campo DEPRECATED limite_usuarios da tabela planos_assinatura."""
    with op.batch_alter_table('planos_assinatura', schema=None) as batch_op:
        batch_op.drop_column('limite_usuarios')


def downgrade() -> None:
    """Recria o campo limite_usuarios para rollback."""
    with op.batch_alter_table('planos_assinatura', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'limite_usuarios',
                sa.Integer(),
                nullable=True,
                comment='DEPRECATED: valor de referência apenas'
            )
        )
        # Preencher com valor padrão baseado no limite_usuarios_maximo
        op.execute(
            "UPDATE planos_assinatura SET limite_usuarios = "
            "COALESCE(limite_usuarios_maximo, 5) "
            "WHERE limite_usuarios IS NULL"
        )
        with op.batch_alter_table('planos_assinatura', schema=None) as batch_op:
            batch_op.alter_column('limite_usuarios', nullable=False)
