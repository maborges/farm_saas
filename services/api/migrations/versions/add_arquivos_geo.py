"""add_arquivos_geo

Revision ID: add_arquivos_geo
Revises: add_infraestruturas
Create Date: 2026-04-04

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_arquivos_geo'
down_revision = 'add_infraestruturas'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cadastros_arquivos_geo',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('area_rural_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('uploaded_by', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('nome_arquivo', sa.String(255), nullable=False),
        sa.Column('formato', sa.String(10), nullable=False),
        sa.Column('tamanho_bytes', sa.Integer, nullable=False),
        sa.Column('storage_backend', sa.String(10), nullable=False),
        sa.Column('storage_path', sa.String(512), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDENTE'),
        sa.Column('poligonos_extraidos', sa.Integer, nullable=True),
        sa.Column('area_ha_extraida', sa.Numeric(12, 4), nullable=True),
        sa.Column('erro_msg', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['area_rural_id'], ['cadastros_areas_rurais.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_arquivos_geo_tenant_area', 'cadastros_arquivos_geo', ['tenant_id', 'area_rural_id'])
    op.create_index('ix_arquivos_geo_tenant_status', 'cadastros_arquivos_geo', ['tenant_id', 'status'])


def downgrade() -> None:
    op.drop_index('ix_arquivos_geo_tenant_status', table_name='cadastros_arquivos_geo')
    op.drop_index('ix_arquivos_geo_tenant_area', table_name='cadastros_arquivos_geo')
    op.drop_table('cadastros_arquivos_geo')
