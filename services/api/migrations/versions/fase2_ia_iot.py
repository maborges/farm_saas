"""Fase 2 - IA Diagnostico e IoT Integracao

Revision ID: fase2_ia_iot
Revises: previous_revision
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fase2_ia_iot'
down_revision = '001_notas_fiscais'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # IA DIAGNÓSTICO - PRAGAS E DOENÇAS
    # ============================================
    op.create_table('pragas_doencas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('nome_cientifico', sa.String(length=200), nullable=True),
        sa.Column('tipo', sa.Enum('praga', 'doenca', 'nutricional', 'outro', name='tipodiagnostico'), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('sintomas', sa.Text(), nullable=True),
        sa.Column('culturas_afetadas', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('imagem_referencia', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pragas_doencas_id'), 'pragas_doencas', ['id'], unique=False)
    op.create_index(op.f('ix_pragas_doencas_nome'), 'pragas_doencas', ['nome'], unique=False)

    op.create_table('tratamentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('praga_doenca_id', sa.Integer(), nullable=False),
        sa.Column('nome_comercial', sa.String(length=200), nullable=False),
        sa.Column('principio_ativo', sa.String(length=200), nullable=True),
        sa.Column('dosagem', sa.String(length=100), nullable=True),
        sa.Column('unidade', sa.String(length=50), nullable=True),
        sa.Column('carencia_dias', sa.Integer(), nullable=True),
        sa.Column('aplicacoes_maximas', sa.Integer(), nullable=True),
        sa.Column('descricao_aplicacao', sa.Text(), nullable=True),
        sa.Column('precaucoes', sa.Text(), nullable=True),
        sa.Column('custo_estimado', sa.Float(), nullable=True),
        sa.Column('disponivel', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['praga_doenca_id'], ['pragas_doencas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tratamentos_id'), 'tratamentos', ['id'], unique=False)

    op.create_table('diagnosticos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('talhao_id', sa.Integer(), nullable=True),
        sa.Column('praga_doenca_id', sa.Integer(), nullable=True),
        sa.Column('imagem_path', sa.String(length=500), nullable=True),
        sa.Column('confianca', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('diagnosticado_por', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('confirmed_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['praga_doenca_id'], ['pragas_doencas.id'], ),
        sa.ForeignKeyConstraint(['talhao_id'], ['talhoes.id'], ),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnosticos_id'), 'diagnosticos', ['id'], unique=False)
    op.create_index(op.f('ix_diagnosticos_tenant_id'), 'diagnosticos', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_diagnosticos_created_at'), 'diagnosticos', ['created_at'], unique=False)

    op.create_table('recomendacoes_diagnostico',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('diagnostico_id', sa.Integer(), nullable=False),
        sa.Column('tratamento_id', sa.Integer(), nullable=True),
        sa.Column('prioridade', sa.Integer(), nullable=True),
        sa.Column('dosagem_recomendada', sa.String(length=100), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['diagnostico_id'], ['diagnosticos.id'], ),
        sa.ForeignKeyConstraint(['tratamento_id'], ['tratamentos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recomendacoes_diagnostico_id'), 'recomendacoes_diagnostico', ['id'], unique=False)

    op.create_table('modelos_ml',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('versao', sa.String(length=50), nullable=False),
        sa.Column('arquitetura', sa.String(length=100), nullable=True),
        sa.Column('acuracia', sa.Float(), nullable=True),
        sa.Column('precisao', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('caminho_modelo', sa.String(length=500), nullable=True),
        sa.Column('dataset_tamanho', sa.Integer(), nullable=True),
        sa.Column('classes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('trained_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modelos_ml_id'), 'modelos_ml', ['id'], unique=False)

    # ============================================
    # IOT - JOHN DEERE
    # ============================================
    op.create_table('integracao_john_deere',
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
    op.create_index(op.f('ix_integracao_john_deere_id'), 'integracao_john_deere', ['id'], unique=False)
    op.create_index(op.f('ix_integracao_john_deere_tenant_id'), 'integracao_john_deere', ['tenant_id'], unique=False)

    op.create_table('maquinas_john_deere',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integracao_id', sa.Integer(), nullable=False),
        sa.Column('jd_id', sa.String(length=100), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=True),
        sa.Column('modelo', sa.String(length=100), nullable=True),
        sa.Column('marca', sa.String(length=100), nullable=True),
        sa.Column('ano', sa.Integer(), nullable=True),
        sa.Column('numero_serie', sa.String(length=100), nullable=True),
        sa.Column('horas_uso', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('ultima_atualizacao', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['integracao_id'], ['integracao_john_deere.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maquinas_john_deere_id'), 'maquinas_john_deere', ['id'], unique=False)

    op.create_table('telemetria_maquina',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column('maquina_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('velocidade', sa.Float(), nullable=True),
        sa.Column('combustivel_nivel', sa.Float(), nullable=True),
        sa.Column('combustivel_consumo', sa.Float(), nullable=True),
        sa.Column('temperatura_motor', sa.Float(), nullable=True),
        sa.Column('pressao_oleo', sa.Float(), nullable=True),
        sa.Column('rpm_motor', sa.Integer(), nullable=True),
        sa.Column('horas_motor', sa.Float(), nullable=True),
        sa.Column('carga_motor', sa.Float(), nullable=True),
        sa.Column('velocidade_solo', sa.Float(), nullable=True),
        sa.Column('area_trabalhada', sa.Float(), nullable=True),
        sa.Column('status_operacao', sa.String(length=50), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['maquina_id'], ['maquinas_john_deere.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telemetria_maquina_id'), 'telemetria_maquina', ['id'], unique=False)
    op.create_index(op.f('ix_telemetria_maquina_tenant_id'), 'telemetria_maquina', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_telemetria_maquina_timestamp'), 'telemetria_maquina', ['timestamp'], unique=False)

    op.create_table('operacoes_campo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('maquina_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('talhao_id', sa.Integer(), nullable=True),
        sa.Column('jd_operation_id', sa.String(length=100), nullable=True),
        sa.Column('tipo_operacao', sa.String(length=50), nullable=True),
        sa.Column('data_inicio', sa.DateTime(), nullable=True),
        sa.Column('data_fim', sa.DateTime(), nullable=True),
        sa.Column('area_trabalhada', sa.Float(), nullable=True),
        sa.Column('produtividade_media', sa.Float(), nullable=True),
        sa.Column('umidade_media', sa.Float(), nullable=True),
        sa.Column('velocidade_media', sa.Float(), nullable=True),
        sa.Column('geometria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('dados_colheita', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['maquina_id'], ['maquinas_john_deere.id'], ),
        sa.ForeignKeyConstraint(['talhao_id'], ['talhoes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_operacoes_campo_id'), 'operacoes_campo', ['id'], unique=False)
    op.create_index(op.f('ix_operacoes_campo_tenant_id'), 'operacoes_campo', ['tenant_id'], unique=False)

    # ============================================
    # IOT - CASE IH
    # ============================================
    op.create_table('integracao_case_ih',
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
    op.create_index(op.f('ix_integracao_case_ih_id'), 'integracao_case_ih', ['id'], unique=False)
    op.create_index(op.f('ix_integracao_case_ih_tenant_id'), 'integracao_case_ih', ['tenant_id'], unique=False)

    op.create_table('maquinas_case_ih',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integracao_id', sa.Integer(), nullable=False),
        sa.Column('afs_id', sa.String(length=100), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=True),
        sa.Column('modelo', sa.String(length=100), nullable=True),
        sa.Column('marca', sa.String(length=100), nullable=True),
        sa.Column('ano', sa.Integer(), nullable=True),
        sa.Column('numero_serie', sa.String(length=100), nullable=True),
        sa.Column('horas_uso', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('ultima_atualizacao', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['integracao_id'], ['integracao_case_ih.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maquinas_case_ih_id'), 'maquinas_case_ih', ['id'], unique=False)

    op.create_table('telemetria_case_ih',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column('maquina_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('velocidade', sa.Float(), nullable=True),
        sa.Column('combustivel_nivel', sa.Float(), nullable=True),
        sa.Column('combustivel_consumo', sa.Float(), nullable=True),
        sa.Column('temperatura_motor', sa.Float(), nullable=True),
        sa.Column('rpm_motor', sa.Integer(), nullable=True),
        sa.Column('horas_motor', sa.Float(), nullable=True),
        sa.Column('status_operacao', sa.String(length=50), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['maquina_id'], ['maquinas_case_ih.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telemetria_case_ih_id'), 'telemetria_case_ih', ['id'], unique=False)
    op.create_index(op.f('ix_telemetria_case_ih_tenant_id'), 'telemetria_case_ih', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_telemetria_case_ih_timestamp'), 'telemetria_case_ih', ['timestamp'], unique=False)

    # ============================================
    # WHATSAPP
    # ============================================
    op.create_table('configuracao_whatsapp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('account_sid', sa.String(length=200), nullable=True),
        sa.Column('auth_token', sa.String(length=200), nullable=True),
        sa.Column('phone_number_id', sa.String(length=100), nullable=True),
        sa.Column('telefone_whatsapp', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('verify_token', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_configuracao_whatsapp_id'), 'configuracao_whatsapp', ['id'], unique=False)
    op.create_index(op.f('ix_configuracao_whatsapp_tenant_id'), 'configuracao_whatsapp', ['tenant_id'], unique=False)

    op.create_table('templates_whatsapp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('idioma', sa.String(length=10), nullable=True),
        sa.Column('template_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('corpo_mensagem', sa.Text(), nullable=True),
        sa.Column('variaveis', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_templates_whatsapp_id'), 'templates_whatsapp', ['id'], unique=False)

    op.create_table('alertas_whatsapp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('destinatario', sa.String(length=50), nullable=False),
        sa.Column('mensagem', sa.Text(), nullable=True),
        sa.Column('variaveis', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('sid_mensagem', sa.String(length=100), nullable=True),
        sa.Column('erro', sa.Text(), nullable=True),
        sa.Column('enviado_em', sa.DateTime(), nullable=True),
        sa.Column('entregue_em', sa.DateTime(), nullable=True),
        sa.Column('lido_em', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['templates_whatsapp.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alertas_whatsapp_id'), 'alertas_whatsapp', ['id'], unique=False)
    op.create_index(op.f('ix_alertas_whatsapp_tenant_id'), 'alertas_whatsapp', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_alertas_whatsapp_created_at'), 'alertas_whatsapp', ['created_at'], unique=False)

    # ============================================
    # COMPARADOR DE PREÇOS
    # ============================================
    op.create_table('comparador_preco_regional',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('commodity', sa.String(length=100), nullable=False),
        sa.Column('regiao', sa.String(length=100), nullable=False),
        sa.Column('cidade', sa.String(length=200), nullable=True),
        sa.Column('estado', sa.String(length=2), nullable=False),
        sa.Column('preco', sa.Float(), nullable=False),
        sa.Column('unidade', sa.String(length=20), nullable=True),
        sa.Column('variacao_dia', sa.Float(), nullable=True),
        sa.Column('variacao_semana', sa.Float(), nullable=True),
        sa.Column('variacao_mes', sa.Float(), nullable=True),
        sa.Column('fonte', sa.String(length=200), nullable=True),
        sa.Column('data_coleta', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comparador_preco_regional_id'), 'comparador_preco_regional', ['id'], unique=False)
    op.create_index(op.f('ix_comparador_preco_regional_commodity'), 'comparador_preco_regional', ['commodity'], unique=False)
    op.create_index(op.f('ix_comparador_preco_regional_data_coleta'), 'comparador_preco_regional', ['data_coleta'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_comparador_preco_regional_data_coleta'), table_name='comparador_preco_regional')
    op.drop_index(op.f('ix_comparador_preco_regional_commodity'), table_name='comparador_preco_regional')
    op.drop_index(op.f('ix_comparador_preco_regional_id'), table_name='comparador_preco_regional')
    op.drop_table('comparador_preco_regional')
    op.drop_index(op.f('ix_alertas_whatsapp_created_at'), table_name='alertas_whatsapp')
    op.drop_index(op.f('ix_alertas_whatsapp_tenant_id'), table_name='alertas_whatsapp')
    op.drop_index(op.f('ix_alertas_whatsapp_id'), table_name='alertas_whatsapp')
    op.drop_table('alertas_whatsapp')
    op.drop_index(op.f('ix_templates_whatsapp_id'), table_name='templates_whatsapp')
    op.drop_table('templates_whatsapp')
    op.drop_index(op.f('ix_configuracao_whatsapp_tenant_id'), table_name='configuracao_whatsapp')
    op.drop_index(op.f('ix_configuracao_whatsapp_id'), table_name='configuracao_whatsapp')
    op.drop_table('configuracao_whatsapp')
    op.drop_index(op.f('ix_telemetria_case_ih_timestamp'), table_name='telemetria_case_ih')
    op.drop_index(op.f('ix_telemetria_case_ih_tenant_id'), table_name='telemetria_case_ih')
    op.drop_index(op.f('ix_telemetria_case_ih_id'), table_name='telemetria_case_ih')
    op.drop_table('telemetria_case_ih')
    op.drop_index(op.f('ix_maquinas_case_ih_id'), table_name='maquinas_case_ih')
    op.drop_table('maquinas_case_ih')
    op.drop_index(op.f('ix_integracao_case_ih_tenant_id'), table_name='integracao_case_ih')
    op.drop_index(op.f('ix_integracao_case_ih_id'), table_name='integracao_case_ih')
    op.drop_table('integracao_case_ih')
    op.drop_index(op.f('ix_operacoes_campo_tenant_id'), table_name='operacoes_campo')
    op.drop_index(op.f('ix_operacoes_campo_id'), table_name='operacoes_campo')
    op.drop_table('operacoes_campo')
    op.drop_index(op.f('ix_telemetria_maquina_timestamp'), table_name='telemetria_maquina')
    op.drop_index(op.f('ix_telemetria_maquina_tenant_id'), table_name='telemetria_maquina')
    op.drop_index(op.f('ix_telemetria_maquina_id'), table_name='telemetria_maquina')
    op.drop_table('telemetria_maquina')
    op.drop_index(op.f('ix_maquinas_john_deere_id'), table_name='maquinas_john_deere')
    op.drop_table('maquinas_john_deere')
    op.drop_index(op.f('ix_integracao_john_deere_tenant_id'), table_name='integracao_john_deere')
    op.drop_index(op.f('ix_integracao_john_deere_id'), table_name='integracao_john_deere')
    op.drop_table('integracao_john_deere')
    op.drop_index(op.f('ix_modelos_ml_id'), table_name='modelos_ml')
    op.drop_table('modelos_ml')
    op.drop_index(op.f('ix_recomendacoes_diagnostico_id'), table_name='recomendacoes_diagnostico')
    op.drop_table('recomendacoes_diagnostico')
    op.drop_index(op.f('ix_diagnosticos_created_at'), table_name='diagnosticos')
    op.drop_index(op.f('ix_diagnosticos_tenant_id'), table_name='diagnosticos')
    op.drop_index(op.f('ix_diagnosticos_id'), table_name='diagnosticos')
    op.drop_table('diagnosticos')
    op.drop_index(op.f('ix_tratamentos_id'), table_name='tratamentos')
    op.drop_table('tratamentos')
    op.drop_index(op.f('ix_pragas_doencas_nome'), table_name='pragas_doencas')
    op.drop_index(op.f('ix_pragas_doencas_id'), table_name='pragas_doencas')
    op.drop_table('pragas_doencas')
    op.execute("DROP TYPE IF EXISTS tipodiagnostico")
