"""add password recovery token table

Revision ID: 20260403_pwd_recovery
Revises: 56b72a50ad49
Create Date: 2026-04-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260403_pwd_recovery'
down_revision = '56b72a50ad49'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tokens_recuperacao_senha table
    op.create_table(
        'tokens_recuperacao_senha',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('utilizado', sa.Boolean(), nullable=False, default=False),
        sa.Column('data_criacao', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data_expiracao', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data_utilizacao', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_origem', sa.String(45), nullable=True),
        sa.Column('ip_utilizacao', sa.String(45), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance and security
    op.create_index('ix_tokens_recuperacao_token', 'tokens_recuperacao_senha', ['token'], unique=True)
    op.create_index('ix_tokens_recuperacao_usuario_id', 'tokens_recuperacao_senha', ['usuario_id'])
    op.create_index('ix_tokens_recuperacao_utilizado', 'tokens_recuperacao_senha', ['utilizado'])


def downgrade() -> None:
    op.drop_index('ix_tokens_recuperacao_utilizado', table_name='tokens_recuperacao_senha')
    op.drop_index('ix_tokens_recuperacao_usuario_id', table_name='tokens_recuperacao_senha')
    op.drop_index('ix_tokens_recuperacao_token', table_name='tokens_recuperacao_senha')
    op.drop_table('tokens_recuperacao_senha')
