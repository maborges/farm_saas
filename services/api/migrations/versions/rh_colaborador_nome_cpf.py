"""rh_colaborador_add_nome_cpf_nullable_pessoa_id

Revision ID: rh_colaborador_nome_cpf
Revises: fcc3dc4b3800
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa

revision = 'rh_colaborador_nome_cpf'
down_revision = 'fcc3dc4b3800'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add nome and cpf columns to rh_colaboradores
    op.add_column('rh_colaboradores', sa.Column('nome', sa.String(200), nullable=True))
    op.add_column('rh_colaboradores', sa.Column('cpf', sa.String(14), nullable=True))

    # Backfill nome for existing rows (set a placeholder)
    op.execute("UPDATE rh_colaboradores SET nome = 'Colaborador' WHERE nome IS NULL")

    # Make nome NOT NULL after backfill
    op.alter_column('rh_colaboradores', 'nome', nullable=False)

    # Make pessoa_id nullable (was NOT NULL before)
    op.alter_column('rh_colaboradores', 'pessoa_id', nullable=True)

    # Add index on cpf
    op.create_index('ix_rh_colaboradores_cpf', 'rh_colaboradores', ['cpf'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_rh_colaboradores_cpf', table_name='rh_colaboradores')
    op.drop_column('rh_colaboradores', 'cpf')
    op.drop_column('rh_colaboradores', 'nome')
    op.alter_column('rh_colaboradores', 'pessoa_id', nullable=False)
