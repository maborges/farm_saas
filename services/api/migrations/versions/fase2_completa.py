"""Fase 2 - Sprints 19-23: NDVI, Irrigação, API Pública, Enterprise, Preditivo

Revision ID: fase2_completa
Revises: fase2_ia_iot
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'fase2_completa'
down_revision = 'fase2_ia_iot'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # SPRINT 19 - NDVI E IRRIGAÇÃO
    # ============================================
    
    op.create_table('imagens_satelite',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=False),
        sa.Column('talhao_id', sa.Integer(), nullable=True),
        sa.Column('satellite', sa.String(length=50), nullable=True),
        sa.Column('product_id', sa.String(length=100), nullable=True),
        sa.Column('acquisition_date', sa.DateTime(), nullable=False),
        sa.Column('cloud_coverage', sa.Float(), nullable=True),
        sa.Column('processing_level', sa.String(length=50), nullable=True),
        sa.Column('download_url', sa.String(length=500), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('local_path', sa.String(length=500), nullable=True),
        sa.Column('bandas', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sun_azimuth', sa.Float(), nullable=True),
        sa.Column('sun_elevation', sa.Float(), nullable=True),
        sa.Column('mean_solar_irradiance', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('processada_em', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.ForeignKeyConstraint(['talhao_id'], ['talhoes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_imagens_satelite_id'), 'imagens_satelite', ['id'], unique=False)
    op.create_index(op.f('ix_imagens_satelite_tenant_id'), 'imagens_satelite', ['tenant_id'], unique=False)
    
    op.create_table('ndvi_registros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=False),
        sa.Column('talhao_id', sa.Integer(), nullable=False),
        sa.Column('imagem_id', sa.Integer(), nullable=True),
        sa.Column('safra_id', sa.Integer(), nullable=True),
        sa.Column('ndvi_medio', sa.Float(), nullable=True),
        sa.Column('ndvi_minimo', sa.Float(), nullable=True),
        sa.Column('ndvi_maximo', sa.Float(), nullable=True),
        sa.Column('ndvi_desvio_padrao', sa.Float(), nullable=True),
        sa.Column('classificacao', sa.String(length=50), nullable=True),
        sa.Column('percentual_area', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('caminho_geojson', sa.String(length=500), nullable=True),
        sa.Column('caminho_raster', sa.String(length=500), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('data_aquisicao', sa.DateTime(), nullable=False),
        sa.Column('data_processamento', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['imagem_id'], ['imagens_satelite.id'], ),
        sa.ForeignKeyConstraint(['talhao_id'], ['talhoes.id'], ),
        sa.ForeignKeyConstraint(['safra_id'], ['safras.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ndvi_registros_id'), 'ndvi_registros', ['id'], unique=False)
    op.create_index(op.f('ix_ndvi_registros_tenant_id'), 'ndvi_registros', ['tenant_id'], unique=False)
    
    op.create_table('sistemas_irrigacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=False),
        sa.Column('talhao_id', sa.Integer(), nullable=True),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('tipo', sa.Enum('pivot_central', 'gotejamento', 'aspersao', 'inundacao', 'sulco', name='tiposistemairrigacao'), nullable=False),
        sa.Column('codigo_equipamento', sa.String(length=50), nullable=True),
        sa.Column('area_total_ha', sa.Float(), nullable=True),
        sa.Column('vazao_m3_h', sa.Float(), nullable=True),
        sa.Column('pressao_operacao_bar', sa.Float(), nullable=True),
        sa.Column('potencia_kw', sa.Float(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('geometria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('data_instalacao', sa.Date(), nullable=True),
        sa.Column('data_ultima_manutencao', sa.Date(), nullable=True),
        sa.Column('automatizado', sa.Boolean(), nullable=True),
        sa.Column('controlador_tipo', sa.String(length=100), nullable=True),
        sa.Column('controlador_modelo', sa.String(length=100), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.ForeignKeyConstraint(['talhao_id'], ['talhoes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sistemas_irrigacao_id'), 'sistemas_irrigacao', ['id'], unique=False)
    op.create_index(op.f('ix_sistemas_irrigacao_tenant_id'), 'sistemas_irrigacao', ['tenant_id'], unique=False)
    
    op.create_table('programacoes_irrigacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('sistema_id', sa.Integer(), nullable=False),
        sa.Column('talhao_id', sa.Integer(), nullable=True),
        sa.Column('data_inicio', sa.DateTime(), nullable=False),
        sa.Column('data_fim_prevista', sa.DateTime(), nullable=True),
        sa.Column('duracao_minutos', sa.Integer(), nullable=True),
        sa.Column('lamina_mm', sa.Float(), nullable=True),
        sa.Column('volume_m3', sa.Float(), nullable=True),
        sa.Column('turno_rega_dias', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('programada', 'em_andamento', 'concluida', 'cancelada', name='statusirrigacao'), nullable=True),
        sa.Column('automatico', sa.Boolean(), nullable=True),
        sa.Column('gatilho_umidade_solo', sa.Float(), nullable=True),
        sa.Column('gatilho_et0_acumulada', sa.Float(), nullable=True),
        sa.Column('responsavel_id', sa.Integer(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['sistema_id'], ['sistemas_irrigacao.id'], ),
        sa.ForeignKeyConstraint(['talhao_id'], ['talhoes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_programacoes_irrigacao_id'), 'programacoes_irrigacao', ['id'], unique=False)
    op.create_index(op.f('ix_programacoes_irrigacao_tenant_id'), 'programacoes_irrigacao', ['tenant_id'], unique=False)
    
    op.create_table('historico_irrigacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('sistema_id', sa.Integer(), nullable=False),
        sa.Column('programacao_id', sa.Integer(), nullable=True),
        sa.Column('talhao_id', sa.Integer(), nullable=True),
        sa.Column('data_inicio', sa.DateTime(), nullable=False),
        sa.Column('data_fim', sa.DateTime(), nullable=True),
        sa.Column('duracao_real_minutos', sa.Integer(), nullable=True),
        sa.Column('volume_m3', sa.Float(), nullable=True),
        sa.Column('lamina_mm', sa.Float(), nullable=True),
        sa.Column('eficiencia', sa.Float(), nullable=True),
        sa.Column('temperatura_media', sa.Float(), nullable=True),
        sa.Column('umidade_media', sa.Float(), nullable=True),
        sa.Column('vento_medio', sa.Float(), nullable=True),
        sa.Column('et0_dia', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('motivo_interrupcao', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['sistema_id'], ['sistemas_irrigacao.id'], ),
        sa.ForeignKeyConstraint(['programacao_id'], ['programacoes_irrigacao.id'], ),
        sa.ForeignKeyConstraint(['talhao_id'], ['talhoes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_historico_irrigacao_id'), 'historico_irrigacao', ['id'], unique=False)
    op.create_index(op.f('ix_historico_irrigacao_tenant_id'), 'historico_irrigacao', ['tenant_id'], unique=False)
    
    op.create_table('balanco_hidrico',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('talhao_id', sa.Integer(), nullable=False),
        sa.Column('safra_id', sa.Integer(), nullable=True),
        sa.Column('data_referencia', sa.Date(), nullable=False),
        sa.Column('precipitacao_mm', sa.Float(), nullable=True),
        sa.Column('irrigacao_mm', sa.Float(), nullable=True),
        sa.Column('orvalho_mm', sa.Float(), nullable=True),
        sa.Column('et0_mm', sa.Float(), nullable=True),
        sa.Column('et_cultura_mm', sa.Float(), nullable=True),
        sa.Column('percolacao_mm', sa.Float(), nullable=True),
        sa.Column('escoamento_mm', sa.Float(), nullable=True),
        sa.Column('saldo_mm', sa.Float(), nullable=True),
        sa.Column('agua_disponivel_mm', sa.Float(), nullable=True),
        sa.Column('capacidade_campo_mm', sa.Float(), nullable=True),
        sa.Column('ponto_murcha_mm', sa.Float(), nullable=True),
        sa.Column('agua_facilmente_disponivel_mm', sa.Float(), nullable=True),
        sa.Column('deficit_hidrico_mm', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('necessidade_irrigacao', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['talhao_id'], ['talhoes.id'], ),
        sa.ForeignKeyConstraint(['safra_id'], ['safras.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_balanco_hidrico_id'), 'balanco_hidrico', ['id'], unique=False)
    op.create_index(op.f('ix_balanco_hidrico_tenant_id'), 'balanco_hidrico', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_balanco_hidrico_data_referencia'), 'balanco_hidrico', ['data_referencia'], unique=False)
    
    op.create_table('estacoes_meteorologicas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('codigo_estacao', sa.String(length=50), nullable=True),
        sa.Column('fonte', sa.String(length=50), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('altitude_m', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('ultima_transmissao', sa.DateTime(), nullable=True),
        sa.Column('sensores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_estacoes_meteorologicas_id'), 'estacoes_meteorologicas', ['id'], unique=False)
    op.create_index(op.f('ix_estacoes_meteorologicas_tenant_id'), 'estacoes_meteorologicas', ['tenant_id'], unique=False)
    
    op.create_table('leituras_meteorologicas',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column('estacao_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('data_leitura', sa.DateTime(), nullable=False),
        sa.Column('temperatura_max', sa.Float(), nullable=True),
        sa.Column('temperatura_min', sa.Float(), nullable=True),
        sa.Column('temperatura_media', sa.Float(), nullable=True),
        sa.Column('umidade_max', sa.Float(), nullable=True),
        sa.Column('umidade_min', sa.Float(), nullable=True),
        sa.Column('umidade_media', sa.Float(), nullable=True),
        sa.Column('precipitacao_mm', sa.Float(), nullable=True),
        sa.Column('vento_velocidade_media', sa.Float(), nullable=True),
        sa.Column('vento_direcao', sa.Float(), nullable=True),
        sa.Column('vento_rajada_max', sa.Float(), nullable=True),
        sa.Column('radiacao_solar_mj_m2', sa.Float(), nullable=True),
        sa.Column('horas_brilho_solar', sa.Float(), nullable=True),
        sa.Column('pressao_atmosferica', sa.Float(), nullable=True),
        sa.Column('et0_mm', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['estacao_id'], ['estacoes_meteorologicas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leituras_meteorologicas_id'), 'leituras_meteorologicas', ['id'], unique=False)
    op.create_index(op.f('ix_leituras_meteorologicas_tenant_id'), 'leituras_meteorologicas', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_leituras_meteorologicas_data_leitura'), 'leituras_meteorologicas', ['data_leitura'], unique=False)
    
    # ============================================
    # SPRINT 21 - API PÚBLICA
    # ============================================
    
    op.create_table('api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('key_hash', sa.String(length=200), nullable=False),
        sa.Column('key_prefix', sa.String(length=10), nullable=False),
        sa.Column('escopos', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('rate_limit', sa.Integer(), nullable=True),
        sa.Column('rate_limit_period', sa.Integer(), nullable=True),
        sa.Column('ativa', sa.Boolean(), nullable=True),
        sa.Column('expira_em', sa.DateTime(), nullable=True),
        sa.Column('ultima_uso', sa.DateTime(), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('ip_whitelist', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_id'), 'api_keys', ['id'], unique=False)
    op.create_index(op.f('ix_api_keys_tenant_id'), 'api_keys', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=True)
    
    op.create_table('api_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('api_key_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('endpoint', sa.String(length=200), nullable=True),
        sa.Column('metodo', sa.String(length=10), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('tempo_resposta_ms', sa.Float(), nullable=True),
        sa.Column('ip_cliente', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('rate_limit_remaining', sa.Integer(), nullable=True),
        sa.Column('rate_limit_excedido', sa.Boolean(), nullable=True),
        sa.Column('erro_mensagem', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['api_key_id'], ['api_keys.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_logs_id'), 'api_logs', ['id'], unique=False)
    op.create_index(op.f('ix_api_logs_tenant_id'), 'api_logs', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_api_logs_created_at'), 'api_logs', ['created_at'], unique=False)
    
    op.create_table('api_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('versao', sa.String(length=20), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('ativa', sa.Boolean(), nullable=True),
        sa.Column('deprecated', sa.Boolean(), nullable=True),
        sa.Column('deprecation_date', sa.DateTime(), nullable=True),
        sa.Column('sunset_date', sa.DateTime(), nullable=True),
        sa.Column('changelog', sa.Text(), nullable=True),
        sa.Column('docs_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('versao')
    )
    op.create_index(op.f('ix_api_versions_id'), 'api_versions', ['id'], unique=False)
    
    op.create_table('sdks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('linguagem', sa.String(length=50), nullable=False),
        sa.Column('nome_pacote', sa.String(length=100), nullable=False),
        sa.Column('versao', sa.String(length=20), nullable=False),
        sa.Column('repositorio_url', sa.String(length=500), nullable=True),
        sa.Column('pacote_url', sa.String(length=500), nullable=True),
        sa.Column('docs_url', sa.String(length=500), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('oficial', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sdks_id'), 'sdks', ['id'], unique=False)
    
    # ============================================
    # SPRINT 22 - ENTERPRISE (SAP, POWER BI, BENCHMARKS)
    # ============================================
    
    op.create_table('sap_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('sap_host', sa.String(length=200), nullable=True),
        sa.Column('sap_system', sa.String(length=10), nullable=True),
        sa.Column('sap_client', sa.String(length=10), nullable=True),
        sa.Column('sap_user', sa.String(length=100), nullable=True),
        sa.Column('sap_password', sa.String(length=200), nullable=True),
        sa.Column('sap_language', sa.String(length=2), nullable=True),
        sa.Column('rfc_destination', sa.String(length=100), nullable=True),
        sa.Column('rfc_trace', sa.Integer(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('ultimo_teste', sa.DateTime(), nullable=True),
        sa.Column('teste_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id')
    )
    op.create_index(op.f('ix_sap_config_id'), 'sap_config', ['id'], unique=False)
    
    op.create_table('sap_sync_logs',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('operacao', sa.String(length=50), nullable=False),
        sa.Column('entidade', sa.String(length=50), nullable=False),
        sa.Column('bapi_function', sa.String(length=100), nullable=True),
        sa.Column('registro_id', sa.String(length=100), nullable=True),
        sa.Column('dados_enviados', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('dados_recebidos', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('erro_mensagem', sa.Text(), nullable=True),
        sa.Column('tempo_execucao_ms', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sap_sync_logs_id'), 'sap_sync_logs', ['id'], unique=False)
    op.create_index(op.f('ix_sap_sync_logs_tenant_id'), 'sap_sync_logs', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_sap_sync_logs_created_at'), 'sap_sync_logs', ['created_at'], unique=False)
    
    op.create_table('sap_mapping',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('entidade_agrosaas', sa.String(length=50), nullable=False),
        sa.Column('entidade_sap', sa.String(length=50), nullable=False),
        sa.Column('campo_agrosaas', sa.String(length=100), nullable=False),
        sa.Column('campo_sap', sa.String(length=100), nullable=False),
        sa.Column('tipo_conversao', sa.String(length=50), nullable=True),
        sa.Column('conversao_formula', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sap_mapping_id'), 'sap_mapping', ['id'], unique=False)
    
    op.create_table('powerbi_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('azure_tenant_id', sa.String(length=100), nullable=True),
        sa.Column('azure_client_id', sa.String(length=100), nullable=True),
        sa.Column('azure_client_secret', sa.String(length=200), nullable=True),
        sa.Column('authority_url', sa.String(length=200), nullable=True),
        sa.Column('workspace_id', sa.String(length=100), nullable=True),
        sa.Column('capacity_id', sa.String(length=100), nullable=True),
        sa.Column('embed_url', sa.String(length=500), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('ultimo_teste', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id')
    )
    op.create_index(op.f('ix_powerbi_config_id'), 'powerbi_config', ['id'], unique=False)
    
    op.create_table('powerbi_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('report_id', sa.String(length=100), nullable=False),
        sa.Column('report_name', sa.String(length=200), nullable=False),
        sa.Column('workspace_id', sa.String(length=100), nullable=True),
        sa.Column('dataset_id', sa.String(length=100), nullable=True),
        sa.Column('embed_url', sa.String(length=500), nullable=True),
        sa.Column('embed_token', sa.Text(), nullable=True),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('ordem', sa.Integer(), nullable=True),
        sa.Column('visivel', sa.Boolean(), nullable=True),
        sa.Column('filtros_padrao', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_powerbi_reports_id'), 'powerbi_reports', ['id'], unique=False)
    op.create_index(op.f('ix_powerbi_reports_tenant_id'), 'powerbi_reports', ['tenant_id'], unique=False)
    
    op.create_table('benchmarks_regionais',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('estado', sa.String(length=2), nullable=False),
        sa.Column('regiao', sa.String(length=100), nullable=True),
        sa.Column('cidade', sa.String(length=200), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('cultura', sa.String(length=50), nullable=False),
        sa.Column('safra', sa.String(length=9), nullable=False),
        sa.Column('produtividade_media', sa.Float(), nullable=True),
        sa.Column('produtividade_minima', sa.Float(), nullable=True),
        sa.Column('produtividade_maxima', sa.Float(), nullable=True),
        sa.Column('desvio_padrao', sa.Float(), nullable=True),
        sa.Column('area_plantada_ha', sa.Float(), nullable=True),
        sa.Column('area_colhida_ha', sa.Float(), nullable=True),
        sa.Column('fonte', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_benchmarks_regionais_id'), 'benchmarks_regionais', ['id'], unique=False)
    op.create_index(op.f('ix_benchmarks_regionais_cultura'), 'benchmarks_regionais', ['cultura'], unique=False)
    
    # ============================================
    # SPRINT 23 - PREDITIVO
    # ============================================
    
    op.create_table('modelos_preditivos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('algoritmo', sa.String(length=100), nullable=True),
        sa.Column('versao', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('acuracia', sa.Float(), nullable=True),
        sa.Column('precisao', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('rmse', sa.Float(), nullable=True),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('caminho_modelo', sa.String(length=500), nullable=True),
        sa.Column('caminho_scaler', sa.String(length=500), nullable=True),
        sa.Column('dados_treinamento', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('data_treinamento', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modelos_preditivos_id'), 'modelos_preditivos', ['id'], unique=False)
    op.create_index(op.f('ix_modelos_preditivos_tenant_id'), 'modelos_preditivos', ['tenant_id'], unique=False)
    
    op.create_table('previsoes_safra',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('talhao_id', sa.Integer(), nullable=True),
        sa.Column('safra_id', sa.Integer(), nullable=True),
        sa.Column('data_previsao', sa.DateTime(), nullable=False),
        sa.Column('data_colheita_prevista', sa.Date(), nullable=True),
        sa.Column('produtividade_prevista', sa.Float(), nullable=True),
        sa.Column('produtividade_minima', sa.Float(), nullable=True),
        sa.Column('produtividade_maxima', sa.Float(), nullable=True),
        sa.Column('confianca', sa.Float(), nullable=True),
        sa.Column('producao_total_prevista', sa.Float(), nullable=True),
        sa.Column('fatores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('produtividade_media_historica', sa.Float(), nullable=True),
        sa.Column('variacao_percentual', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('produtividade_real', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['talhao_id'], ['talhoes.id'], ),
        sa.ForeignKeyConstraint(['safra_id'], ['safras.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_previsoes_safra_id'), 'previsoes_safra', ['id'], unique=False)
    op.create_index(op.f('ix_previsoes_safra_tenant_id'), 'previsoes_safra', ['tenant_id'], unique=False)
    
    op.create_table('previsoes_climaticas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('tipo_evento', sa.String(length=50), nullable=False),
        sa.Column('severidade', sa.String(length=20), nullable=True),
        sa.Column('data_inicio_prevista', sa.DateTime(), nullable=False),
        sa.Column('data_fim_prevista', sa.DateTime(), nullable=True),
        sa.Column('probabilidade', sa.Float(), nullable=True),
        sa.Column('impacto_previsto', sa.Text(), nullable=True),
        sa.Column('recomendacoes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('area_afetada_ha', sa.Float(), nullable=True),
        sa.Column('geometria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('enviado_em', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_previsoes_climaticas_id'), 'previsoes_climaticas', ['id'], unique=False)
    op.create_index(op.f('ix_previsoes_climaticas_tenant_id'), 'previsoes_climaticas', ['tenant_id'], unique=False)
    
    op.create_table('alertas_epidemiologicos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('praga_doenca_id', sa.Integer(), nullable=True),
        sa.Column('nome_praga_doenca', sa.String(length=200), nullable=True),
        sa.Column('nivel_alerta', sa.String(length=20), nullable=False),
        sa.Column('temperatura_favoravel', sa.Boolean(), nullable=True),
        sa.Column('umidade_favoravel', sa.Boolean(), nullable=True),
        sa.Column('precipitacao_favoravel', sa.Boolean(), nullable=True),
        sa.Column('probabilidade_surtro', sa.Float(), nullable=True),
        sa.Column('data_inicio_risco', sa.DateTime(), nullable=False),
        sa.Column('data_fim_risco', sa.DateTime(), nullable=True),
        sa.Column('recomendacoes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tratamentos_preventivos', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('enviado_em', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.ForeignKeyConstraint(['praga_doenca_id'], ['pragas_doencas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alertas_epidemiologicos_id'), 'alertas_epidemiologicos', ['id'], unique=False)
    op.create_index(op.f('ix_alertas_epidemiologicos_tenant_id'), 'alertas_epidemiologicos', ['tenant_id'], unique=False)
    
    op.create_table('previsoes_preco_commodity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('commodity', sa.String(length=50), nullable=False),
        sa.Column('mercado', sa.String(length=50), nullable=True),
        sa.Column('data_previsao', sa.DateTime(), nullable=False),
        sa.Column('data_referencia', sa.Date(), nullable=False),
        sa.Column('preco_previsto', sa.Float(), nullable=True),
        sa.Column('preco_minimo', sa.Float(), nullable=True),
        sa.Column('preco_maximo', sa.Float(), nullable=True),
        sa.Column('confianca', sa.Float(), nullable=True),
        sa.Column('variacao_percentual', sa.Float(), nullable=True),
        sa.Column('tendencia', sa.String(length=20), nullable=True),
        sa.Column('fatores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_previsoes_preco_commodity_id'), 'previsoes_preco_commodity', ['id'], unique=False)
    op.create_index(op.f('ix_previsoes_preco_commodity_tenant_id'), 'previsoes_preco_commodity', ['tenant_id'], unique=False)
    
    op.create_table('programa_pontos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('regras', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('parceiros', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('premios', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_programa_pontos_id'), 'programa_pontos', ['id'], unique=False)
    op.create_index(op.f('ix_programa_pontos_tenant_id'), 'programa_pontos', ['tenant_id'], unique=False)
    
    op.create_table('pontos_saldo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('pessoa_id', sa.Integer(), nullable=True),
        sa.Column('saldo_atual', sa.Float(), nullable=True),
        sa.Column('pontos_acumulados', sa.Float(), nullable=True),
        sa.Column('pontos_resgatados', sa.Float(), nullable=True),
        sa.Column('pontos_expiram_em', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['pessoa_id'], ['pessoas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pontos_saldo_id'), 'pontos_saldo', ['id'], unique=False)
    
    op.create_table('pontos_transacoes',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('pessoa_id', sa.Integer(), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('pontos', sa.Float(), nullable=False),
        sa.Column('saldo_apos', sa.Float(), nullable=True),
        sa.Column('origem', sa.String(length=100), nullable=True),
        sa.Column('referencia_id', sa.String(length=100), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['pessoa_id'], ['pessoas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pontos_transacoes_id'), 'pontos_transacoes', ['id'], unique=False)
    op.create_index(op.f('ix_pontos_transacoes_created_at'), 'pontos_transacoes', ['created_at'], unique=False)


def downgrade() -> None:
    # Reverter todas as tabelas criadas
    op.drop_index(op.f('ix_pontos_transacoes_created_at'), table_name='pontos_transacoes')
    op.drop_index(op.f('ix_pontos_transacoes_id'), table_name='pontos_transacoes')
    op.drop_table('pontos_transacoes')
    op.drop_index(op.f('ix_pontos_saldo_id'), table_name='pontos_saldo')
    op.drop_table('pontos_saldo')
    op.drop_index(op.f('ix_programa_pontos_tenant_id'), table_name='programa_pontos')
    op.drop_index(op.f('ix_programa_pontos_id'), table_name='programa_pontos')
    op.drop_table('programa_pontos')
    op.drop_index(op.f('ix_previsoes_preco_commodity_tenant_id'), table_name='previsoes_preco_commodity')
    op.drop_index(op.f('ix_previsoes_preco_commodity_id'), table_name='previsoes_preco_commodity')
    op.drop_table('previsoes_preco_commodity')
    op.drop_index(op.f('ix_alertas_epidemiologicos_tenant_id'), table_name='alertas_epidemiologicos')
    op.drop_index(op.f('ix_alertas_epidemiologicos_id'), table_name='alertas_epidemiologicos')
    op.drop_table('alertas_epidemiologicos')
    op.drop_index(op.f('ix_previsoes_climaticas_tenant_id'), table_name='previsoes_climaticas')
    op.drop_index(op.f('ix_previsoes_climaticas_id'), table_name='previsoes_climaticas')
    op.drop_table('previsoes_climaticas')
    op.drop_index(op.f('ix_previsoes_safra_tenant_id'), table_name='previsoes_safra')
    op.drop_index(op.f('ix_previsoes_safra_id'), table_name='previsoes_safra')
    op.drop_table('previsoes_safra')
    op.drop_index(op.f('ix_modelos_preditivos_tenant_id'), table_name='modelos_preditivos')
    op.drop_index(op.f('ix_modelos_preditivos_id'), table_name='modelos_preditivos')
    op.drop_table('modelos_preditivos')
    op.drop_index(op.f('ix_benchmarks_regionais_cultura'), table_name='benchmarks_regionais')
    op.drop_index(op.f('ix_benchmarks_regionais_id'), table_name='benchmarks_regionais')
    op.drop_table('benchmarks_regionais')
    op.drop_index(op.f('ix_powerbi_reports_tenant_id'), table_name='powerbi_reports')
    op.drop_index(op.f('ix_powerbi_reports_id'), table_name='powerbi_reports')
    op.drop_table('powerbi_reports')
    op.drop_index(op.f('ix_powerbi_config_id'), table_name='powerbi_config')
    op.drop_table('powerbi_config')
    op.drop_index(op.f('ix_sap_mapping_id'), table_name='sap_mapping')
    op.drop_table('sap_mapping')
    op.drop_index(op.f('ix_sap_sync_logs_created_at'), table_name='sap_sync_logs')
    op.drop_index(op.f('ix_sap_sync_logs_tenant_id'), table_name='sap_sync_logs')
    op.drop_index(op.f('ix_sap_sync_logs_id'), table_name='sap_sync_logs')
    op.drop_table('sap_sync_logs')
    op.drop_index(op.f('ix_sap_config_id'), table_name='sap_config')
    op.drop_table('sap_config')
    op.drop_index(op.f('ix_sdks_id'), table_name='sdks')
    op.drop_table('sdks')
    op.drop_index(op.f('ix_api_versions_id'), table_name='api_versions')
    op.drop_table('api_versions')
    op.drop_index(op.f('ix_api_logs_created_at'), table_name='api_logs')
    op.drop_index(op.f('ix_api_logs_tenant_id'), table_name='api_logs')
    op.drop_index(op.f('ix_api_logs_id'), table_name='api_logs')
    op.drop_table('api_logs')
    op.drop_index(op.f('ix_api_keys_key_hash'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_tenant_id'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_id'), table_name='api_keys')
    op.drop_table('api_keys')
    op.drop_index(op.f('ix_leituras_meteorologicas_data_leitura'), table_name='leituras_meteorologicas')
    op.drop_index(op.f('ix_leituras_meteorologicas_tenant_id'), table_name='leituras_meteorologicas')
    op.drop_index(op.f('ix_leituras_meteorologicas_id'), table_name='leituras_meteorologicas')
    op.drop_table('leituras_meteorologicas')
    op.drop_index(op.f('ix_estacoes_meteorologicas_tenant_id'), table_name='estacoes_meteorologicas')
    op.drop_index(op.f('ix_estacoes_meteorologicas_id'), table_name='estacoes_meteorologicas')
    op.drop_table('estacoes_meteorologicas')
    op.drop_index(op.f('ix_balanco_hidrico_data_referencia'), table_name='balanco_hidrico')
    op.drop_index(op.f('ix_balanco_hidrico_tenant_id'), table_name='balanco_hidrico')
    op.drop_index(op.f('ix_balanco_hidrico_id'), table_name='balanco_hidrico')
    op.drop_table('balanco_hidrico')
    op.drop_index(op.f('ix_historico_irrigacao_tenant_id'), table_name='historico_irrigacao')
    op.drop_index(op.f('ix_historico_irrigacao_id'), table_name='historico_irrigacao')
    op.drop_table('historico_irrigacao')
    op.drop_index(op.f('ix_programacoes_irrigacao_tenant_id'), table_name='programacoes_irrigacao')
    op.drop_index(op.f('ix_programacoes_irrigacao_id'), table_name='programacoes_irrigacao')
    op.drop_table('programacoes_irrigacao')
    op.drop_index(op.f('ix_sistemas_irrigacao_tenant_id'), table_name='sistemas_irrigacao')
    op.drop_index(op.f('ix_sistemas_irrigacao_id'), table_name='sistemas_irrigacao')
    op.drop_table('sistemas_irrigacao')
    op.drop_index(op.f('ix_ndvi_registros_tenant_id'), table_name='ndvi_registros')
    op.drop_index(op.f('ix_ndvi_registros_id'), table_name='ndvi_registros')
    op.drop_table('ndvi_registros')
    op.drop_index(op.f('ix_imagens_satelite_tenant_id'), table_name='imagens_satelite')
    op.drop_index(op.f('ix_imagens_satelite_id'), table_name='imagens_satelite')
    op.drop_table('imagens_satelite')
    op.execute("DROP TYPE IF EXISTS tiposistemairrigacao")
    op.execute("DROP TYPE IF EXISTS statusirrigacao")
