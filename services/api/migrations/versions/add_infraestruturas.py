"""add_infraestruturas

Revision ID: add_infraestruturas
Revises: 48126310bfd6
Create Date: 2026-04-04

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_infraestruturas'
down_revision = '48126310bfd6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cadastros_infraestruturas',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('area_rural_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False),
        sa.Column('capacidade', sa.Numeric(12, 2), nullable=True),
        sa.Column('unidade_capacidade', sa.String(20), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('observacoes', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['area_rural_id'], ['cadastros_areas_rurais.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_infraestruturas_tenant_area', 'cadastros_infraestruturas', ['tenant_id', 'area_rural_id'])
    op.create_index('ix_infraestruturas_tenant_tipo', 'cadastros_infraestruturas', ['tenant_id', 'tipo'])


def downgrade() -> None:
    op.drop_index('ix_infraestruturas_tenant_tipo', table_name='cadastros_infraestruturas')
    op.drop_index('ix_infraestruturas_tenant_area', table_name='cadastros_infraestruturas')
    op.drop_table('cadastros_infraestruturas')
