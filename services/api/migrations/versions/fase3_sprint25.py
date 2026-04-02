"""Fase 3 Sprint 25: Integrações Contábeis

Revision ID: fase3_sprint25
Revises: fase2_completa
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'fase3_sprint25'
down_revision = 'fase2_completa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # SPRINT 25 - INTEGRAÇÕES CONTÁBEIS
    # ============================================
    
    op.create_table('integracoes_contabeis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('sistema', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('configuracoes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('credenciais', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('ultima_exportacao', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_integracoes_contabeis_id'), 'integracoes_contabeis', ['id'], unique=False)
    op.create_index(op.f('ix_integracoes_contabeis_tenant_id'), 'integracoes_contabeis', ['tenant_id'], unique=False)
    
    op.create_table('exportacoes_contabeis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('integracao_id', sa.Integer(), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('periodo_inicio', sa.Date(), nullable=False),
        sa.Column('periodo_fim', sa.Date(), nullable=False),
        sa.Column('arquivo_path', sa.String(length=500), nullable=True),
        sa.Column('arquivo_nome', sa.String(length=200), nullable=True),
        sa.Column('arquivo_formato', sa.String(length=20), nullable=True),
        sa.Column('arquivo_tamanho', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('registros_exportados', sa.Integer(), nullable=True),
        sa.Column('erro_mensagem', sa.Text(), nullable=True),
        sa.Column('agendada', sa.Boolean(), nullable=True),
        sa.Column('data_agendamento', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('processada_em', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['integracao_id'], ['integracoes_contabeis.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exportacoes_contabeis_id'), 'exportacoes_contabeis', ['id'], unique=False)
    op.create_index(op.f('ix_exportacoes_contabeis_tenant_id'), 'exportacoes_contabeis', ['tenant_id'], unique=False)
    
    op.create_table('lancamentos_contabeis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('data_lancamento', sa.Date(), nullable=False),
        sa.Column('documento', sa.String(length=50), nullable=True),
        sa.Column('historico', sa.Text(), nullable=False),
        sa.Column('valor_debito', sa.Float(), nullable=True),
        sa.Column('valor_credito', sa.Float(), nullable=True),
        sa.Column('conta_debito', sa.String(length=50), nullable=True),
        sa.Column('conta_credito', sa.String(length=50), nullable=True),
        sa.Column('centro_custo', sa.String(length=50), nullable=True),
        sa.Column('origem', sa.String(length=50), nullable=True),
        sa.Column('origem_id', sa.Integer(), nullable=True),
        sa.Column('exportado', sa.Boolean(), nullable=True),
        sa.Column('exportacao_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['exportacao_id'], ['exportacoes_contabeis.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lancamentos_contabeis_id'), 'lancamentos_contabeis', ['id'], unique=False)
    op.create_index(op.f('ix_lancamentos_contabeis_tenant_id'), 'lancamentos_contabeis', ['tenant_id'], unique=False)
    
    op.create_table('plano_contas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=True),
        sa.Column('natureza', sa.String(length=20), nullable=True),
        sa.Column('conta_pai_id', sa.Integer(), nullable=True),
        sa.Column('nivel', sa.Integer(), nullable=True),
        sa.Column('sistema_origem', sa.String(length=50), nullable=True),
        sa.Column('codigo_sistema', sa.String(length=50), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conta_pai_id'], ['plano_contas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plano_contas_id'), 'plano_contas', ['id'], unique=False)
    op.create_index(op.f('ix_plano_contas_tenant_id'), 'plano_contas', ['tenant_id'], unique=False)
    
    op.create_table('mapeamento_contabil',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('integracao_id', sa.Integer(), nullable=True),
        sa.Column('entidade_agrosaas', sa.String(length=50), nullable=False),
        sa.Column('campo_agrosaas', sa.String(length=100), nullable=False),
        sa.Column('valor_agrosaas', sa.String(length=100), nullable=True),
        sa.Column('conta_contabil', sa.String(length=50), nullable=True),
        sa.Column('centro_custo', sa.String(length=50), nullable=True),
        sa.Column('codigo_sistema', sa.String(length=50), nullable=True),
        sa.Column('tipo_operacao', sa.String(length=50), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['integracao_id'], ['integracoes_contabeis.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mapeamento_contabil_id'), 'mapeamento_contabil', ['id'], unique=False)
    op.create_index(op.f('ix_mapeamento_contabil_tenant_id'), 'mapeamento_contabil', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_mapeamento_contabil_tenant_id'), table_name='mapeamento_contabil')
    op.drop_index(op.f('ix_mapeamento_contabil_id'), table_name='mapeamento_contabil')
    op.drop_table('mapeamento_contabil')
    op.drop_index(op.f('ix_plano_contas_tenant_id'), table_name='plano_contas')
    op.drop_index(op.f('ix_plano_contas_id'), table_name='plano_contas')
    op.drop_table('plano_contas')
    op.drop_index(op.f('ix_lancamentos_contabeis_tenant_id'), table_name='lancamentos_contabeis')
    op.drop_index(op.f('ix_lancamentos_contabeis_id'), table_name='lancamentos_contabeis')
    op.drop_table('lancamentos_contabeis')
    op.drop_index(op.f('ix_exportacoes_contabeis_tenant_id'), table_name='exportacoes_contabeis')
    op.drop_index(op.f('ix_exportacoes_contabeis_id'), table_name='exportacoes_contabeis')
    op.drop_table('exportacoes_contabeis')
    op.drop_index(op.f('ix_integracoes_contabeis_tenant_id'), table_name='integracoes_contabeis')
    op.drop_index(op.f('ix_integracoes_contabeis_id'), table_name='integracoes_contabeis')
    op.drop_table('integracoes_contabeis')
