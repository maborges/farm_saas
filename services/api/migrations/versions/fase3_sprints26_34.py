"""Fase 3 Sprints 26-34: New Holland, Marketplace, Carbono, ESG, etc.

Revision ID: fase3_sprints26_34
Revises: fase3_sprint25
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'fase3_sprints26_34'
down_revision = 'fase3_sprint25'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # SPRINT 26 - NEW HOLLAND, MARKETPLACE, CARBONO
    # ============================================
    
    op.create_table('integracao_new_holland',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('client_id', sa.String(length=200), nullable=True),
        sa.Column('client_secret', sa.String(length=200), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('ultimo_sync', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_integracao_new_holland_id'), 'integracao_new_holland', ['id'], unique=False)
    op.create_index(op.f('ix_integracao_new_holland_tenant_id'), 'integracao_new_holland', ['tenant_id'], unique=False)
    
    op.create_table('maquinas_new_holland',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integracao_id', sa.Integer(), nullable=False),
        sa.Column('nh_id', sa.String(length=100), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=True),
        sa.Column('modelo', sa.String(length=100), nullable=True),
        sa.Column('marca', sa.String(length=100), nullable=True),
        sa.Column('ano', sa.Integer(), nullable=True),
        sa.Column('numero_serie', sa.String(length=100), nullable=True),
        sa.Column('horas_uso', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('ultima_atualizacao', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['integracao_id'], ['integracao_new_holland.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maquinas_new_holland_id'), 'maquinas_new_holland', ['id'], unique=False)
    
    op.create_table('marketplace_integracoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('descricao_curta', sa.String(length=200), nullable=True),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('subcategoria', sa.String(length=50), nullable=True),
        sa.Column('fornecedor', sa.String(length=100), nullable=True),
        sa.Column('fornecedor_logo', sa.String(length=500), nullable=True),
        sa.Column('site_fornecedor', sa.String(length=500), nullable=True),
        sa.Column('suporte_email', sa.String(length=200), nullable=True),
        sa.Column('ativa', sa.Boolean(), nullable=True),
        sa.Column('oficial', sa.Boolean(), nullable=True),
        sa.Column('versao', sa.String(length=20), nullable=True),
        sa.Column('requisitos', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('configuracoes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('total_instalacoes', sa.Integer(), nullable=True),
        sa.Column('avaliacao_media', sa.Float(), nullable=True),
        sa.Column('total_avaliacoes', sa.Integer(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('screenshots', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('documentacao_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_marketplace_integracoes_id'), 'marketplace_integracoes', ['id'], unique=False)
    
    op.create_table('tenant_integracoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('integracao_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('configuracoes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('credenciais', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('webhook_secret', sa.String(length=200), nullable=True),
        sa.Column('ultima_sincronizacao', sa.DateTime(), nullable=True),
        sa.Column('total_sincronizacoes', sa.Integer(), nullable=True),
        sa.Column('installed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['integracao_id'], ['marketplace_integracoes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenant_integracoes_id'), 'tenant_integracoes', ['id'], unique=False)
    op.create_index(op.f('ix_tenant_integracoes_tenant_id'), 'tenant_integracoes', ['tenant_id'], unique=False)
    
    op.create_table('marketplace_avaliacoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integracao_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('nota', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=True),
        sa.Column('comentario', sa.Text(), nullable=True),
        sa.Column('aprovada', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['integracao_id'], ['marketplace_integracoes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_marketplace_avaliacoes_id'), 'marketplace_avaliacoes', ['id'], unique=False)
    
    op.create_table('carbono_emissoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('escopo', sa.Integer(), nullable=False),
        sa.Column('categoria', sa.String(length=100), nullable=False),
        sa.Column('fonte', sa.String(length=200), nullable=True),
        sa.Column('atividade', sa.String(length=200), nullable=True),
        sa.Column('quantidade', sa.Float(), nullable=False),
        sa.Column('unidade', sa.String(length=50), nullable=False),
        sa.Column('fator_emissao', sa.Float(), nullable=True),
        sa.Column('fator_emissao_referencia', sa.String(length=200), nullable=True),
        sa.Column('total_co2e', sa.Float(), nullable=True),
        sa.Column('data_referencia', sa.DateTime(), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('arquivo_comprovante', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_carbono_emissoes_id'), 'carbono_emissoes', ['id'], unique=False)
    op.create_index(op.f('ix_carbono_emissoes_tenant_id'), 'carbono_emissoes', ['tenant_id'], unique=False)
    
    op.create_table('carbono_projetos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('metodologia', sa.String(length=100), nullable=True),
        sa.Column('area_ha', sa.Float(), nullable=False),
        sa.Column('geometria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('creditos_estimados', sa.Float(), nullable=True),
        sa.Column('creditos_verificados', sa.Float(), nullable=True),
        sa.Column('creditos_vendidos', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('data_inicio', sa.Date(), nullable=True),
        sa.Column('data_verificacao', sa.Date(), nullable=True),
        sa.Column('data_certificacao', sa.Date(), nullable=True),
        sa.Column('certificador', sa.String(length=200), nullable=True),
        sa.Column('numero_registro', sa.String(length=100), nullable=True),
        sa.Column('padrao', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_carbono_projetos_id'), 'carbono_projetos', ['id'], unique=False)
    
    op.create_table('carbono_relatorios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('periodo_inicio', sa.DateTime(), nullable=False),
        sa.Column('periodo_fim', sa.DateTime(), nullable=False),
        sa.Column('escopo_1_total', sa.Float(), nullable=True),
        sa.Column('escopo_2_total', sa.Float(), nullable=True),
        sa.Column('escopo_3_total', sa.Float(), nullable=True),
        sa.Column('total_geral', sa.Float(), nullable=True),
        sa.Column('creditos_gerados', sa.Float(), nullable=True),
        sa.Column('saldo_liquido', sa.Float(), nullable=True),
        sa.Column('intensidade_carbono', sa.Float(), nullable=True),
        sa.Column('unidade_producao', sa.String(length=50), nullable=True),
        sa.Column('total_produzido', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('arquivo_pdf', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_carbono_relatorios_id'), 'carbono_relatorios', ['id'], unique=False)
    op.create_index(op.f('ix_carbono_relatorios_tenant_id'), 'carbono_relatorios', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_carbono_relatorios_tenant_id'), table_name='carbono_relatorios')
    op.drop_index(op.f('ix_carbono_relatorios_id'), table_name='carbono_relatorios')
    op.drop_table('carbono_relatorios')
    op.drop_index(op.f('ix_carbono_projetos_id'), table_name='carbono_projetos')
    op.drop_table('carbono_projetos')
    op.drop_index(op.f('ix_carbono_emissoes_tenant_id'), table_name='carbono_emissoes')
    op.drop_index(op.f('ix_carbono_emissoes_id'), table_name='carbono_emissoes')
    op.drop_table('carbono_emissoes')
    op.drop_index(op.f('ix_marketplace_avaliacoes_id'), table_name='marketplace_avaliacoes')
    op.drop_table('marketplace_avaliacoes')
    op.drop_index(op.f('ix_tenant_integracoes_tenant_id'), table_name='tenant_integracoes')
    op.drop_index(op.f('ix_tenant_integracoes_id'), table_name='tenant_integracoes')
    op.drop_table('tenant_integracoes')
    op.drop_index(op.f('ix_marketplace_integracoes_id'), table_name='marketplace_integracoes')
    op.drop_table('marketplace_integracoes')
    op.drop_index(op.f('ix_maquinas_new_holland_id'), table_name='maquinas_new_holland')
    op.drop_table('maquinas_new_holland')
    op.drop_index(op.f('ix_integracao_new_holland_tenant_id'), table_name='integracao_new_holland')
    op.drop_index(op.f('ix_integracao_new_holland_id'), table_name='integracao_new_holland')
    op.drop_table('integracao_new_holland')
