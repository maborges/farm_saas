"""add_conciliacao_bancaria

Revision ID: 14332b81c8b9
Revises: cd26bb50a28e
Create Date: 2026-03-23 09:28:18.477978

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14332b81c8b9'
down_revision: Union[str, Sequence[str], None] = 'cd26bb50a28e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'fin_contas_bancarias',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('fazenda_id', sa.Uuid(), nullable=True),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('banco', sa.String(50), nullable=True),
        sa.Column('agencia', sa.String(20), nullable=True),
        sa.Column('conta', sa.String(30), nullable=True),
        sa.Column('tipo', sa.String(20), nullable=False, server_default='CORRENTE'),
        sa.Column('ativa', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fin_contas_bancarias_tenant_id', 'fin_contas_bancarias', ['tenant_id'])

    op.create_table(
        'fin_lancamentos_bancarios',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('conta_id', sa.Uuid(), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('valor', sa.Numeric(15, 2), nullable=False),
        sa.Column('descricao', sa.String(500), nullable=True),
        sa.Column('id_ofx', sa.String(100), nullable=True),
        sa.Column('tipo', sa.String(10), nullable=False),
        sa.Column('status_conciliacao', sa.String(20), nullable=False, server_default='NAO_CONCILIADO'),
        sa.Column('despesa_id', sa.Uuid(), nullable=True),
        sa.Column('receita_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conta_id'], ['fin_contas_bancarias.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['despesa_id'], ['fin_despesas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['receita_id'], ['fin_receitas.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fin_lancamentos_bancarios_tenant_id', 'fin_lancamentos_bancarios', ['tenant_id'])
    op.create_index('ix_fin_lancamentos_bancarios_conta_id', 'fin_lancamentos_bancarios', ['conta_id'])
    op.create_index('ix_fin_lancamentos_bancarios_id_ofx', 'fin_lancamentos_bancarios', ['id_ofx'])


def downgrade() -> None:
    op.drop_index('ix_fin_lancamentos_bancarios_id_ofx', 'fin_lancamentos_bancarios')
    op.drop_index('ix_fin_lancamentos_bancarios_conta_id', 'fin_lancamentos_bancarios')
    op.drop_index('ix_fin_lancamentos_bancarios_tenant_id', 'fin_lancamentos_bancarios')
    op.drop_table('fin_lancamentos_bancarios')
    op.drop_index('ix_fin_contas_bancarias_tenant_id', 'fin_contas_bancarias')
    op.drop_table('fin_contas_bancarias')
