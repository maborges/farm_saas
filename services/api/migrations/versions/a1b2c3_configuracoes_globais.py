"""configuracoes_globais: CategoriaCustom, ConfiguracaoFazenda, HistoricoConfiguracao, onboarding flag

Revision ID: a1b2c3configuracoes
Revises: 1795966a0c0a
Create Date: 2026-04-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'a1b2c3configuracoes'
down_revision = '1795966a0c0a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- categoria_custom ---
    op.create_table(
        'categoria_custom',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tipo', sa.Enum('despesa', 'receita', 'operacao', 'produto', 'insumo', name='tipocategoria'), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('parent_id', sa.Uuid(as_uuid=True), sa.ForeignKey('categoria_custom.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('ordem', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cor_hex', sa.String(7), nullable=True),
        sa.Column('icone', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_categoria_custom_tenant_id', 'categoria_custom', ['tenant_id'])
    op.create_index('ix_categoria_custom_tipo', 'categoria_custom', ['tipo'])
    op.create_index('ix_categoria_custom_slug', 'categoria_custom', ['slug'])
    op.create_index('ix_categoria_custom_tenant_tipo', 'categoria_custom', ['tenant_id', 'tipo'])

    # --- configuracao_fazenda ---
    op.create_table(
        'configuracao_fazenda',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('fazenda_id', sa.Uuid(as_uuid=True), sa.ForeignKey('fazendas.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overrides', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_configuracao_fazenda_fazenda_id', 'configuracao_fazenda', ['fazenda_id'])
    op.create_index('ix_configuracao_fazenda_tenant_id', 'configuracao_fazenda', ['tenant_id'])

    # --- historico_configuracao ---
    op.create_table(
        'historico_configuracao',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('campo_alterado', sa.String(100), nullable=False),
        sa.Column('valor_anterior', sa.JSON(), nullable=True),
        sa.Column('valor_novo', sa.JSON(), nullable=False),
        sa.Column('alterado_por', sa.Uuid(as_uuid=True), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('alterado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_historico_configuracao_tenant_id', 'historico_configuracao', ['tenant_id'])
    op.create_index('ix_historico_configuracao_alterado_em', 'historico_configuracao', ['alterado_em'])

    # --- tenants: flag onboarding ---
    op.add_column('tenants', sa.Column('onboarding_configuracao_completo', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('tenants', 'onboarding_configuracao_completo')
    op.drop_table('historico_configuracao')
    op.drop_table('configuracao_fazenda')
    op.drop_table('categoria_custom')
    op.execute("DROP TYPE IF EXISTS tipocategoria")
