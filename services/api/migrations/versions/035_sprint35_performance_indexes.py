"""Sprint 35 - Performance Indexes

Revision ID: 035
Revises: fase3_sprints27_33_final
Create Date: 2026-03-31

Sprint 35: Performance - Otimização de Banco de Dados
Fase 4: Polimento e Lançamento

Índices criados baseados na análise de baseline:
- Identificar tabelas com muitas seq scans
- Otimizar queries de filtros por tenant
- Melhorar performance de joins e ordenações
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '035'
down_revision = 'fase3_sprints27_33_final'
branch_labels = None
depends_on = None


def upgrade():
    # ==========================================================================
    # CORE - Tenants e Usuários
    # ==========================================================================
    
    # Otimizar queries de listagem de tenants
    op.create_index(
        'ix_tenants_ativo',
        'tenants',
        ['ativo'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de busca de tenants por nome
    op.create_index(
        'ix_tenants_nome',
        'tenants',
        ['nome_fantasia'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de usuários por email (já existe, mas verificar)
    op.create_index(
        'ix_usuarios_tenant_id',
        'usuarios',
        ['tenant_id'],
        unique=False,
        if_not_exists=True
    )
    
    # ==========================================================================
    # FAZENDAS - Gestão de propriedades
    # ==========================================================================
    
    # Otimizar filtros por status e tenant
    op.create_index(
        'ix_fazendas_tenant_status',
        'fazendas',
        ['tenant_id', 'status'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries que buscam fazendas por grupo
    op.create_index(
        'ix_fazendas_grupo_fazendas_id',
        'fazendas',
        ['grupo_fazendas_id'],
        unique=False,
        if_not_exists=True
    )
    
    # ==========================================================================
    # CADASTROS - Produtos e Marcas
    # ==========================================================================
    
    # Otimizar queries de produtos por tipo
    op.create_index(
        'ix_cadastros_produtos_tipo_tenant',
        'cadastros_produtos',
        ['tenant_id', 'tipo'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de produtos por código
    op.create_index(
        'ix_cadastros_produtos_codigo',
        'cadastros_produtos',
        ['codigo'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de marcas por nome
    op.create_index(
        'ix_cadastros_marcas_nome',
        'cadastros_marcas',
        ['nome'],
        unique=False,
        if_not_exists=True
    )
    
    # ==========================================================================
    # CRM - Leads e Pipeline
    # ==========================================================================
    
    # Otimizar queries de leads por status
    op.create_index(
        'ix_crm_leads_status_tenant',
        'crm_leads',
        ['status', 'tenant_id'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de leads por pipeline
    op.create_index(
        'ix_crm_leads_pipeline',
        'crm_leads',
        ['pipeline_estagio_id'],
        unique=False,
        if_not_exists=True
    )
    
    # ==========================================================================
    # AGRÍCOLA - Safras e Operações
    # ==========================================================================
    
    # Otimizar queries de safras por ano
    op.create_index(
        'ix_safras_ano_safra',
        'safras',
        ['ano_safra'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de safras por talhão
    op.create_index(
        'ix_safras_talhao_id',
        'safras',
        ['talhao_id'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de operações por safra
    op.create_index(
        'ix_agricola_operacoes_safra_id',
        'agricola_operacoes',
        ['safra_id'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de operações por data
    op.create_index(
        'ix_agricola_operacoes_data',
        'agricola_operacoes',
        ['data_operacao'],
        unique=False,
        if_not_exists=True
    )
    
    # ==========================================================================
    # FINANCEIRO - Lançamentos
    # ==========================================================================
    
    # Otimizar queries de lançamentos por data de vencimento
    op.create_index(
        'ix_fin_lancamentos_vencimento',
        'financeiro_lancamentos',
        ['data_vencimento'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de lançamentos por categoria
    op.create_index(
        'ix_fin_lancamentos_categoria',
        'financeiro_lancamentos',
        ['categoria_id'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de lançamentos por status
    op.create_index(
        'ix_fin_lancamentos_status',
        'financeiro_lancamentos',
        ['status'],
        unique=False,
        if_not_exists=True
    )
    
    # ==========================================================================
    # PECUÁRIA - Animais
    # ==========================================================================
    
    # Otimizar queries de animais por categoria
    op.create_index(
        'ix_pecuaria_animais_categoria',
        'pecuaria_animais',
        ['categoria'],
        unique=False,
        if_not_exists=True
    )
    
    # Otimizar queries de animais por status
    op.create_index(
        'ix_pecuaria_animais_status',
        'pecuaria_animais',
        ['status'],
        unique=False,
        if_not_exists=True
    )
    
    # ==========================================================================
    # ÍNDICES COMPOSTOS PARA QUERIES CRÍTICAS
    # ==========================================================================
    
    # Dashboard financeiro: tenant + data + tipo
    op.create_index(
        'ix_fin_lancamentos_tenant_data_tipo',
        'financeiro_lancamentos',
        ['tenant_id', 'data_vencimento', 'tipo'],
        unique=False,
        if_not_exists=True
    )
    
    # Listagem de safras: tenant + status + ano
    op.create_index(
        'ix_safras_tenant_status_ano',
        'safras',
        ['tenant_id', 'status', 'ano_safra'],
        unique=False,
        if_not_exists=True
    )
    
    # Operações por safra com ordenação por data
    op.create_index(
        'ix_agricola_operacoes_safra_data',
        'agricola_operacoes',
        ['safra_id', 'data_operacao DESC'],
        unique=False,
        if_not_exists=True
    )
    
    print("✅ Índices de performance criados com sucesso!")
    print()
    print("Índices criados:")
    print("- Core: 3 índices")
    print("- Fazendas: 2 índices")
    print("- Cadastros: 3 índices")
    print("- CRM: 2 índices")
    print("- Agrícola: 4 índices")
    print("- Financeiro: 4 índices")
    print("- Pecuária: 2 índices")
    print("- Compostos: 3 índices")
    print()
    print("Total: 23 índices novos")


def downgrade():
    # Remover todos os índices criados na Sprint 35
    
    # Compostos
    op.drop_index('ix_fin_lancamentos_tenant_data_tipo', 'financeiro_lancamentos', if_exists=True)
    op.drop_index('ix_safras_tenant_status_ano', 'safras', if_exists=True)
    op.drop_index('ix_agricola_operacoes_safra_data', 'agricola_operacoes', if_exists=True)
    
    # Pecuária
    op.drop_index('ix_pecuaria_animais_status', 'pecuaria_animais', if_exists=True)
    op.drop_index('ix_pecuaria_animais_categoria', 'pecuaria_animais', if_exists=True)
    
    # Financeiro
    op.drop_index('ix_fin_lancamentos_status', 'financeiro_lancamentos', if_exists=True)
    op.drop_index('ix_fin_lancamentos_categoria', 'financeiro_lancamentos', if_exists=True)
    op.drop_index('ix_fin_lancamentos_vencimento', 'financeiro_lancamentos', if_exists=True)
    
    # Agrícola
    op.drop_index('ix_agricola_operacoes_data', 'agricola_operacoes', if_exists=True)
    op.drop_index('ix_agricola_operacoes_safra_id', 'agricola_operacoes', if_exists=True)
    op.drop_index('ix_safras_talhao_id', 'safras', if_exists=True)
    op.drop_index('ix_safras_ano_safra', 'safras', if_exists=True)
    
    # CRM
    op.drop_index('ix_crm_leads_pipeline', 'crm_leads', if_exists=True)
    op.drop_index('ix_crm_leads_status_tenant', 'crm_leads', if_exists=True)
    
    # Cadastros
    op.drop_index('ix_cadastros_marcas_nome', 'cadastros_marcas', if_exists=True)
    op.drop_index('ix_cadastros_produtos_codigo', 'cadastros_produtos', if_exists=True)
    op.drop_index('ix_cadastros_produtos_tipo_tenant', 'cadastros_produtos', if_exists=True)
    
    # Fazendas
    op.drop_index('ix_fazendas_grupo_fazendas_id', 'fazendas', if_exists=True)
    op.drop_index('ix_fazendas_tenant_status', 'fazendas', if_exists=True)
    
    # Core
    op.drop_index('ix_usuarios_tenant_id', 'usuarios', if_exists=True)
    op.drop_index('ix_tenants_nome', 'tenants', if_exists=True)
    op.drop_index('ix_tenants_ativo', 'tenants', if_exists=True)
    
    print("✅ Índices da Sprint 35 removidos com sucesso!")
