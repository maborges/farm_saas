"""Fase 3 - Integração ERP Sankhya

Revision ID: fase3_sankhya
Revises: fase3_sprints27_33_final
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'fase3_sankhya'
down_revision = 'fase3_sprints27_33_final'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # INTEGRAÇÃO SANKHYA
    # ============================================
    
    op.create_table('sankhya_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('ws_url', sa.String(length=500), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=200), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('ultimo_teste', sa.DateTime(), nullable=True),
        sa.Column('teste_status', sa.String(length=50), nullable=True),
        sa.Column('sync_interval', sa.Integer(), nullable=True),
        sa.Column('ultimo_sync', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id')
    )
    op.create_index(op.f('ix_sankhya_config_id'), 'sankhya_config', ['id'], unique=False)
    op.create_index(op.f('ix_sankhya_config_tenant_id'), 'sankhya_config', ['tenant_id'], unique=False)
    
    op.create_table('sankhya_sync_logs',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('operacao', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('registros_processados', sa.Integer(), nullable=True),
        sa.Column('registros_sucesso', sa.Integer(), nullable=True),
        sa.Column('registros_erro', sa.Integer(), nullable=True),
        sa.Column('erro_mensagem', sa.Text(), nullable=True),
        sa.Column('tempo_execucao_ms', sa.Float(), nullable=True),
        sa.Column('periodo_inicio', sa.DateTime(), nullable=True),
        sa.Column('periodo_fim', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['config_id'], ['sankhya_config.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sankhya_sync_logs_id'), 'sankhya_sync_logs', ['id'], unique=False)
    op.create_index(op.f('ix_sankhya_sync_logs_tenant_id'), 'sankhya_sync_logs', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_sankhya_sync_logs_created_at'), 'sankhya_sync_logs', ['created_at'], unique=False)
    
    op.create_table('sankhya_pessoas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('sankhya_id', sa.String(length=50), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=True),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('nome_fantasia', sa.String(length=200), nullable=True),
        sa.Column('cpf', sa.String(length=14), nullable=True),
        sa.Column('cnpj', sa.String(length=18), nullable=True),
        sa.Column('ie', sa.String(length=20), nullable=True),
        sa.Column('im', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('celular', sa.String(length=20), nullable=True),
        sa.Column('endereco', sa.String(length=200), nullable=True),
        sa.Column('numero', sa.String(length=20), nullable=True),
        sa.Column('complemento', sa.String(length=50), nullable=True),
        sa.Column('bairro', sa.String(length=100), nullable=True),
        sa.Column('cidade', sa.String(length=100), nullable=True),
        sa.Column('uf', sa.String(length=2), nullable=True),
        sa.Column('cep', sa.String(length=10), nullable=True),
        sa.Column('pais', sa.String(length=100), nullable=True),
        sa.Column('codigo_sankhya', sa.String(length=50), nullable=True),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('sincronizado_em', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sankhya_pessoas_id'), 'sankhya_pessoas', ['id'], unique=False)
    op.create_index(op.f('ix_sankhya_pessoas_tenant_id'), 'sankhya_pessoas', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_sankhya_pessoas_sankhya_id'), 'sankhya_pessoas', ['sankhya_id'], unique=True)
    
    op.create_table('sankhya_produtos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('sankhya_id', sa.String(length=50), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('ncm', sa.String(length=8), nullable=True),
        sa.Column('cest', sa.String(length=7), nullable=True),
        sa.Column('cfop', sa.String(length=5), nullable=True),
        sa.Column('origem', sa.String(length=2), nullable=True),
        sa.Column('unidade', sa.String(length=10), nullable=True),
        sa.Column('preco_custo', sa.Float(), nullable=True),
        sa.Column('preco_venda', sa.Float(), nullable=True),
        sa.Column('controle_estoque', sa.Boolean(), nullable=True),
        sa.Column('controle_serial', sa.Boolean(), nullable=True),
        sa.Column('codigo_sankhya', sa.String(length=50), nullable=True),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('sincronizado_em', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sankhya_produtos_id'), 'sankhya_produtos', ['id'], unique=False)
    op.create_index(op.f('ix_sankhya_produtos_tenant_id'), 'sankhya_produtos', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_sankhya_produtos_sankhya_id'), 'sankhya_produtos', ['sankhya_id'], unique=True)
    
    op.create_table('sankhya_nfe',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('sankhya_id', sa.String(length=50), nullable=True),
        sa.Column('tipo_operacao', sa.String(length=20), nullable=True),
        sa.Column('numero', sa.String(length=20), nullable=False),
        sa.Column('serie', sa.String(length=10), nullable=True),
        sa.Column('modelo', sa.String(length=10), nullable=True),
        sa.Column('chave_acesso', sa.String(length=44), nullable=True),
        sa.Column('cnpj_emitente', sa.String(length=18), nullable=True),
        sa.Column('cnpj_destinatario', sa.String(length=18), nullable=True),
        sa.Column('valor_total', sa.Float(), nullable=True),
        sa.Column('valor_produtos', sa.Float(), nullable=True),
        sa.Column('valor_frete', sa.Float(), nullable=True),
        sa.Column('valor_seguro', sa.Float(), nullable=True),
        sa.Column('valor_desconto', sa.Float(), nullable=True),
        sa.Column('valor_ipi', sa.Float(), nullable=True),
        sa.Column('valor_icms', sa.Float(), nullable=True),
        sa.Column('valor_pis', sa.Float(), nullable=True),
        sa.Column('valor_cofins', sa.Float(), nullable=True),
        sa.Column('data_emissao', sa.Date(), nullable=True),
        sa.Column('data_saida', sa.Date(), nullable=True),
        sa.Column('data_entrada', sa.Date(), nullable=True),
        sa.Column('status_sankhya', sa.String(length=50), nullable=True),
        sa.Column('protocolo_sankhya', sa.String(length=50), nullable=True),
        sa.Column('exportado_sankhya', sa.Boolean(), nullable=True),
        sa.Column('importado_sankhya', sa.Boolean(), nullable=True),
        sa.Column('sincronizado_em', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sankhya_nfe_id'), 'sankhya_nfe', ['id'], unique=False)
    op.create_index(op.f('ix_sankhya_nfe_tenant_id'), 'sankhya_nfe', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_sankhya_nfe_sankhya_id'), 'sankhya_nfe', ['sankhya_id'], unique=True)
    op.create_index(op.f('ix_sankhya_nfe_chave_acesso'), 'sankhya_nfe', ['chave_acesso'], unique=True)
    
    op.create_table('sankhya_lancamentos_financeiros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('sankhya_id', sa.String(length=50), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=True),
        sa.Column('numero_documento', sa.String(length=50), nullable=True),
        sa.Column('valor', sa.Float(), nullable=False),
        sa.Column('valor_saldo', sa.Float(), nullable=True),
        sa.Column('data_lancamento', sa.Date(), nullable=True),
        sa.Column('data_vencimento', sa.Date(), nullable=True),
        sa.Column('data_pagamento', sa.Date(), nullable=True),
        sa.Column('historico', sa.String(length=500), nullable=True),
        sa.Column('rateio', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('exportado_sankhya', sa.Boolean(), nullable=True),
        sa.Column('importado_sankhya', sa.Boolean(), nullable=True),
        sa.Column('sincronizado_em', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sankhya_lancamentos_financeiros_id'), 'sankhya_lancamentos_financeiros', ['id'], unique=False)
    op.create_index(op.f('ix_sankhya_lancamentos_financeiros_tenant_id'), 'sankhya_lancamentos_financeiros', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_sankhya_lancamentos_financeiros_sankhya_id'), 'sankhya_lancamentos_financeiros', ['sankhya_id'], unique=True)
    
    op.create_table('sankhya_tabelas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('codigo', sa.String(length=20), nullable=False),
        sa.Column('descricao', sa.String(length=500), nullable=False),
        sa.Column('complemento', sa.String(length=200), nullable=True),
        sa.Column('dados_adicionais', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('sincronizado_em', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sankhya_tabelas_id'), 'sankhya_tabelas', ['id'], unique=False)
    op.create_index(op.f('ix_sankhya_tabelas_tenant_id'), 'sankhya_tabelas', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sankhya_tabelas_tenant_id'), table_name='sankhya_tabelas')
    op.drop_index(op.f('ix_sankhya_tabelas_id'), table_name='sankhya_tabelas')
    op.drop_table('sankhya_tabelas')
    op.drop_index(op.f('ix_sankhya_lancamentos_financeiros_sankhya_id'), table_name='sankhya_lancamentos_financeiros')
    op.drop_index(op.f('ix_sankhya_lancamentos_financeiros_tenant_id'), table_name='sankhya_lancamentos_financeiros')
    op.drop_index(op.f('ix_sankhya_lancamentos_financeiros_id'), table_name='sankhya_lancamentos_financeiros')
    op.drop_table('sankhya_lancamentos_financeiros')
    op.drop_index(op.f('ix_sankhya_nfe_chave_acesso'), table_name='sankhya_nfe')
    op.drop_index(op.f('ix_sankhya_nfe_sankhya_id'), table_name='sankhya_nfe')
    op.drop_index(op.f('ix_sankhya_nfe_tenant_id'), table_name='sankhya_nfe')
    op.drop_index(op.f('ix_sankhya_nfe_id'), table_name='sankhya_nfe')
    op.drop_table('sankhya_nfe')
    op.drop_index(op.f('ix_sankhya_produtos_sankhya_id'), table_name='sankhya_produtos')
    op.drop_index(op.f('ix_sankhya_produtos_tenant_id'), table_name='sankhya_produtos')
    op.drop_index(op.f('ix_sankhya_produtos_id'), table_name='sankhya_produtos')
    op.drop_table('sankhya_produtos')
    op.drop_index(op.f('ix_sankhya_pessoas_sankhya_id'), table_name='sankhya_pessoas')
    op.drop_index(op.f('ix_sankhya_pessoas_tenant_id'), table_name='sankhya_pessoas')
    op.drop_index(op.f('ix_sankhya_pessoas_id'), table_name='sankhya_pessoas')
    op.drop_table('sankhya_pessoas')
    op.drop_index(op.f('ix_sankhya_sync_logs_created_at'), table_name='sankhya_sync_logs')
    op.drop_index(op.f('ix_sankhya_sync_logs_tenant_id'), table_name='sankhya_sync_logs')
    op.drop_index(op.f('ix_sankhya_sync_logs_id'), table_name='sankhya_sync_logs')
    op.drop_table('sankhya_sync_logs')
    op.drop_index(op.f('ix_sankhya_config_tenant_id'), table_name='sankhya_config')
    op.drop_index(op.f('ix_sankhya_config_id'), table_name='sankhya_config')
    op.drop_table('sankhya_config')
