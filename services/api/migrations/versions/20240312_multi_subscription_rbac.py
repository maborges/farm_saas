"""Multi-subscription support and RBAC enhancements (SQLite compatible)

Revision ID: 20240312_multi_sub
Revises: 7aec82540f16
Create Date: 2024-03-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers
revision = '20240312_multi_sub'
down_revision = '7aec82540f16'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========== 1. CREATE TABLE: grupos_fazendas ==========
    op.create_table(
        'grupos_fazendas',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('nome', sa.String(150), nullable=False),
        sa.Column('descricao', sa.Text, nullable=True),
        sa.Column('cor', sa.String(7), nullable=True),
        sa.Column('icone', sa.String(50), nullable=True),
        sa.Column('ordem', sa.Integer, default=0),
        sa.Column('ativo', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_grupos_fazendas_tenant', 'grupos_fazendas', ['tenant_id'])

    # ========== 2. ALTER TABLE: fazendas - ADD grupo_id ==========
    with op.batch_alter_table('fazendas') as batch_op:
        batch_op.add_column(sa.Column('grupo_id', sa.String(36), nullable=True))

    # ========== 3. ALTER TABLE: assinaturas_tenant ==========
    with op.batch_alter_table('assinaturas_tenant') as batch_op:
        # Remove unique constraint
        try:
            batch_op.drop_constraint('assinaturas_tenant_tenant_id_key', type_='unique')
        except:
            pass

        # Add new columns
        batch_op.add_column(sa.Column('grupo_fazendas_id', sa.String(36), nullable=True))
        batch_op.add_column(sa.Column('tipo_assinatura', sa.String(20), server_default='PRINCIPAL'))

    # ========== 4. ALTER TABLE: fazenda_usuarios - ADD perfil_fazenda_id ==========
    with op.batch_alter_table('fazenda_usuarios') as batch_op:
        batch_op.add_column(sa.Column('perfil_fazenda_id', sa.String(36), nullable=True))

    # ========== 5. CREATE TABLE: sessoes_ativas ==========
    op.create_table(
        'sessoes_ativas',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('grupo_fazendas_id', sa.String(36), nullable=True),
        sa.Column('usuario_id', sa.String(36), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fazenda_id', sa.String(36), nullable=True),
        sa.Column('token_hash', sa.String(64), unique=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('inicio', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('ultimo_heartbeat', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expira_em', sa.DateTime, nullable=False),
        sa.Column('status', sa.String(20), default='ATIVA'),
    )
    op.create_index('idx_sessoes_tenant', 'sessoes_ativas', ['tenant_id'])
    op.create_index('idx_sessoes_usuario', 'sessoes_ativas', ['usuario_id'])
    op.create_index('idx_sessoes_status', 'sessoes_ativas', ['status', 'expira_em'])

    # ========== 6. CREATE TABLE: admin_impersonations ==========
    op.create_table(
        'admin_impersonations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('admin_user_id', sa.String(36), sa.ForeignKey('admin_users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fazenda_id', sa.String(36), nullable=True),
        sa.Column('motivo', sa.Text, nullable=False),
        sa.Column('categoria', sa.String(50), server_default='SUPORTE'),
        sa.Column('inicio', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('fim', sa.DateTime, nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('acoes_realizadas', sa.JSON, server_default='[]'),
        sa.Column('meta_info', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_impersonation_admin', 'admin_impersonations', ['admin_user_id'])
    op.create_index('idx_impersonation_tenant', 'admin_impersonations', ['tenant_id'])


def downgrade() -> None:
    # Reverse order
    op.drop_table('admin_impersonations')
    op.drop_table('sessoes_ativas')

    with op.batch_alter_table('fazenda_usuarios') as batch_op:
        batch_op.drop_column('perfil_fazenda_id')

    with op.batch_alter_table('assinaturas_tenant') as batch_op:
        batch_op.drop_column('tipo_assinatura')
        batch_op.drop_column('grupo_fazendas_id')
        # Restore unique
        try:
            batch_op.create_unique_constraint('assinaturas_tenant_tenant_id_key', ['tenant_id'])
        except:
            pass

    with op.batch_alter_table('fazendas') as batch_op:
        batch_op.drop_column('grupo_id')

    op.drop_table('grupos_fazendas')
