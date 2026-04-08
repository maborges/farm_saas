"""add login rate limiting table

Revision ID: 20260402_add_login_rate_limiting
Revises: fase3_sprints27_33_final
Create Date: 2026-04-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260402_add_login_rate_limiting'
down_revision = 'fase3_sprints27_33_final'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create login_tentativas table
    op.create_table(
        'login_tentativas',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('sucesso', sa.Boolean(), nullable=False, default=False),
        sa.Column('motivo_falha', sa.String(100), nullable=True),
        sa.Column('tentativas_count', sa.Integer(), nullable=False, default=1),
        sa.Column('bloqueado', sa.Boolean(), nullable=False, default=False),
        sa.Column('data_bloqueio', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_desbloqueio', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('ix_login_tentativas_email', 'login_tentativas', ['email'])
    op.create_index('ix_login_tentativas_created_at', 'login_tentativas', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_login_tentativas_created_at', table_name='login_tentativas')
    op.drop_index('ix_login_tentativas_email', table_name='login_tentativas')
    op.drop_table('login_tentativas')
