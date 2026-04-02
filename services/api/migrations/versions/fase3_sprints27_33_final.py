"""Fase 3 - Sprints 27-33: MRV, ESG, Piscicultura, Confinamento, Genética, Hedging, IoT, ILPF

Revision ID: fase3_sprints27_33_final
Revises: fase3_sprints26_34
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'fase3_sprints27_33_final'
down_revision = 'fase3_sprints26_34'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # SPRINT 27 - MRV
    # ============================================
    op.create_table('mrv_projetos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('carbono_projeto_id', sa.Integer(), nullable=True),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('metodologia', sa.String(length=100), nullable=True),
        sa.Column('padrao', sa.String(length=50), nullable=True),
        sa.Column('area_ha', sa.Float(), nullable=True),
        sa.Column('geometria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('monitoramento_ativo', sa.Boolean(), nullable=True),
        sa.Column('ultimo_relatorio', sa.DateTime(), nullable=True),
        sa.Column('proxima_verificacao', sa.Date(), nullable=True),
        sa.Column('creditos_gerados', sa.Float(), nullable=True),
        sa.Column('creditos_verificados', sa.Float(), nullable=True),
        sa.Column('creditos_vendidos', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mrv_projetos_id'), 'mrv_projetos', ['id'], unique=False)
    
    op.create_table('mrv_relatorios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('projeto_id', sa.Integer(), nullable=True),
        sa.Column('periodo_inicio', sa.Date(), nullable=False),
        sa.Column('periodo_fim', sa.Date(), nullable=False),
        sa.Column('remocoes_co2e', sa.Float(), nullable=True),
        sa.Column('emissoes_evitadas', sa.Float(), nullable=True),
        sa.Column('total_creditos', sa.Float(), nullable=True),
        sa.Column('verificado', sa.Boolean(), nullable=True),
        sa.Column('verificador', sa.String(length=200), nullable=True),
        sa.Column('data_verificacao', sa.Date(), nullable=True),
        sa.Column('arquivo_pdf', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['projeto_id'], ['mrv_projetos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mrv_relatorios_id'), 'mrv_relatorios', ['id'], unique=False)
    
    # ============================================
    # SPRINT 28 - ESG
    # ============================================
    op.create_table('esg_indicadores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('categoria', sa.String(length=10), nullable=False),
        sa.Column('subcategoria', sa.String(length=50), nullable=True),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('valor', sa.Float(), nullable=True),
        sa.Column('unidade', sa.String(length=50), nullable=True),
        sa.Column('meta', sa.Float(), nullable=True),
        sa.Column('periodo_referencia', sa.String(length=20), nullable=True),
        sa.Column('padrao_gri', sa.String(length=50), nullable=True),
        sa.Column('padrao_sasb', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_esg_indicadores_id'), 'esg_indicadores', ['id'], unique=False)
    
    op.create_table('esg_relatorios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('ano_referencia', sa.Integer(), nullable=False),
        sa.Column('score_ambiental', sa.Float(), nullable=True),
        sa.Column('score_social', sa.Float(), nullable=True),
        sa.Column('score_governanca', sa.Float(), nullable=True),
        sa.Column('score_total', sa.Float(), nullable=True),
        sa.Column('emissao_co2e', sa.Float(), nullable=True),
        sa.Column('consumo_agua', sa.Float(), nullable=True),
        sa.Column('residuos_reciclados', sa.Float(), nullable=True),
        sa.Column('acidentes_trabalho', sa.Integer(), nullable=True),
        sa.Column('diversidade_genero', sa.Float(), nullable=True),
        sa.Column('rotatividade', sa.Float(), nullable=True),
        sa.Column('publicado', sa.Boolean(), nullable=True),
        sa.Column('arquivo_pdf', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_esg_relatorios_id'), 'esg_relatorios', ['id'], unique=False)
    
    # ============================================
    # SPRINT 28 - PISCICULTURA
    # ============================================
    op.create_table('tanques_rede',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=True),
        sa.Column('volume_m3', sa.Float(), nullable=True),
        sa.Column('area_m2', sa.Float(), nullable=True),
        sa.Column('profundidade_m', sa.Float(), nullable=True),
        sa.Column('formato', sa.String(length=50), nullable=True),
        sa.Column('especie', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('data_povoamento', sa.Date(), nullable=True),
        sa.Column('data_colheita_prevista', sa.Date(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tanques_rede_id'), 'tanques_rede', ['id'], unique=False)
    
    op.create_table('arracoamentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('tanque_id', sa.Integer(), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('hora', sa.DateTime(), nullable=True),
        sa.Column('quantidade_razao', sa.Float(), nullable=True),
        sa.Column('tipo_racao', sa.String(length=100), nullable=True),
        sa.Column('responsavel_id', sa.Integer(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tanque_id'], ['tanques_rede.id'], ),
        sa.ForeignKeyConstraint(['responsavel_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_arracoamentos_id'), 'arracoamentos', ['id'], unique=False)
    
    op.create_table('pesagens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('tanque_id', sa.Integer(), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('total_peixes', sa.Integer(), nullable=True),
        sa.Column('peso_total_kg', sa.Float(), nullable=True),
        sa.Column('peso_medio_g', sa.Float(), nullable=True),
        sa.Column('biomassa_estimada_kg', sa.Float(), nullable=True),
        sa.Column('taxa_arracoamento', sa.Float(), nullable=True),
        sa.Column('responsavel_id', sa.Integer(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tanque_id'], ['tanques_rede.id'], ),
        sa.ForeignKeyConstraint(['responsavel_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pesagens_id'), 'pesagens', ['id'], unique=False)
    
    # ============================================
    # SPRINT 29 - CONFINAMENTO
    # ============================================
    op.create_table('confinamento_lotes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('safra', sa.String(length=20), nullable=True),
        sa.Column('total_animais', sa.Integer(), nullable=True),
        sa.Column('peso_inicial_kg', sa.Float(), nullable=True),
        sa.Column('peso_inicial_total_kg', sa.Float(), nullable=True),
        sa.Column('data_entrada', sa.Date(), nullable=False),
        sa.Column('data_saida_prevista', sa.Date(), nullable=True),
        sa.Column('data_saida_real', sa.Date(), nullable=True),
        sa.Column('peso_saida_kg', sa.Float(), nullable=True),
        sa.Column('ganho_medio_diario', sa.Float(), nullable=True),
        sa.Column('conversao_alimentar', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_confinamento_lotes_id'), 'confinamento_lotes', ['id'], unique=False)
    
    op.create_table('racoes_tmr',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=True),
        sa.Column('ingredientes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('proteina_bruta', sa.Float(), nullable=True),
        sa.Column('ndt', sa.Float(), nullable=True),
        sa.Column('energia_liquida', sa.Float(), nullable=True),
        sa.Column('custo_por_tonelada', sa.Float(), nullable=True),
        sa.Column('ativa', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_racoes_tmr_id'), 'racoes_tmr', ['id'], unique=False)
    
    op.create_table('cochos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('lote_id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('comprimento_m', sa.Float(), nullable=True),
        sa.Column('racao_fornecida_kg', sa.Float(), nullable=True),
        sa.Column('sobra_kg', sa.Float(), nullable=True),
        sa.Column('consumo_kg', sa.Float(), nullable=True),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('turno', sa.String(length=20), nullable=True),
        sa.Column('responsavel_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['lote_id'], ['confinamento_lotes.id'], ),
        sa.ForeignKeyConstraint(['responsavel_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cochos_id'), 'cochos', ['id'], unique=False)
    
    # ============================================
    # SPRINT 30 - GENÉTICA
    # ============================================
    op.create_table('racas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('especie', sa.String(length=50), nullable=True),
        sa.Column('origem', sa.String(length=100), nullable=True),
        sa.Column('peso_adulto_macho', sa.Float(), nullable=True),
        sa.Column('peso_adulto_femea', sa.Float(), nullable=True),
        sa.Column('cor_padrao', sa.String(length=50), nullable=True),
        sa.Column('dep_ganho_peso', sa.Float(), nullable=True),
        sa.Column('dep_area_olho_lombo', sa.Float(), nullable=True),
        sa.Column('dep_gordura_subcutanea', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_racas_id'), 'racas', ['id'], unique=False)
    
    op.create_table('sugestoes_acasalamento',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('matriz_id', sa.Integer(), nullable=False),
        sa.Column('reprodutor_id', sa.Integer(), nullable=False),
        sa.Column('dep_esperado', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('score_complementaridade', sa.Float(), nullable=True),
        sa.Column('realizado', sa.Boolean(), nullable=True),
        sa.Column('data_acasalamento', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sugestoes_acasalamento_id'), 'sugestoes_acasalamento', ['id'], unique=False)
    
    # ============================================
    # SPRINT 31 - HEDGING
    # ============================================
    op.create_table('contratos_futuros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('commodity', sa.String(length=50), nullable=False),
        sa.Column('mercado', sa.String(length=50), nullable=True),
        sa.Column('codigo_contrato', sa.String(length=50), nullable=True),
        sa.Column('mes_vencimento', sa.String(length=7), nullable=True),
        sa.Column('tipo_posicao', sa.String(length=10), nullable=True),
        sa.Column('quantidade', sa.Float(), nullable=True),
        sa.Column('unidade', sa.String(length=20), nullable=True),
        sa.Column('preco_contratado', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('data_liquidacao', sa.Date(), nullable=True),
        sa.Column('preco_liquidacao', sa.Float(), nullable=True),
        sa.Column('resultado', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contratos_futuros_id'), 'contratos_futuros', ['id'], unique=False)
    
    op.create_table('hedge_registros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('contrato_id', sa.Integer(), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=True),
        sa.Column('quantidade', sa.Float(), nullable=True),
        sa.Column('preco', sa.Float(), nullable=True),
        sa.Column('cotacao_mercado', sa.Float(), nullable=True),
        sa.Column('base', sa.Float(), nullable=True),
        sa.Column('resultado_papel', sa.Float(), nullable=True),
        sa.Column('resultado_fisico', sa.Float(), nullable=True),
        sa.Column('resultado_liquido', sa.Float(), nullable=True),
        sa.Column('data_operacao', sa.Date(), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contrato_id'], ['contratos_futuros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hedge_registros_id'), 'hedge_registros', ['id'], unique=False)
    
    # ============================================
    # SPRINT 32 - IOT SENSORES
    # ============================================
    op.create_table('sensores_iot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=True),
        sa.Column('protocolo', sa.String(length=20), nullable=True),
        sa.Column('endpoint', sa.String(length=200), nullable=True),
        sa.Column('topic_mqtt', sa.String(length=200), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('ultima_leitura', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensores_iot_id'), 'sensores_iot', ['id'], unique=False)
    
    op.create_table('sensores_leituras',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column('sensor_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('valor', sa.Float(), nullable=False),
        sa.Column('unidade', sa.String(length=20), nullable=True),
        sa.Column('qualidade', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['sensor_id'], ['sensores_iot.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensores_leituras_id'), 'sensores_leituras', ['id'], unique=False)
    op.create_index(op.f('ix_sensores_leituras_timestamp'), 'sensores_leituras', ['timestamp'], unique=False)
    
    # ============================================
    # SPRINT 33 - ILPF
    # ============================================
    op.create_table('ilpf_modulos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('fazenda_id', sa.Integer(), nullable=True),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=True),
        sa.Column('tipo_ilpf', sa.String(length=20), nullable=True),
        sa.Column('area_ha', sa.Float(), nullable=False),
        sa.Column('geometria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('cultura', sa.String(length=100), nullable=True),
        sa.Column('especie_florestal', sa.String(length=100), nullable=True),
        sa.Column('spacing_arvores', sa.String(length=50), nullable=True),
        sa.Column('data_inicio', sa.Date(), nullable=True),
        sa.Column('ano_implantacao', sa.Integer(), nullable=True),
        sa.Column('carbono_sequestrado', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ilpf_modulos_id'), 'ilpf_modulos', ['id'], unique=False)
    
    # ============================================
    # SPRINT 33 - APP COLABORADORES
    # ============================================
    op.create_table('colaborador_apontamentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('colaborador_id', sa.Integer(), nullable=True),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('horas_trabalhadas', sa.Float(), nullable=True),
        sa.Column('atividade', sa.String(length=200), nullable=True),
        sa.Column('talhao_id', sa.Integer(), nullable=True),
        sa.Column('maquina_id', sa.Integer(), nullable=True),
        sa.Column('quantidade_produzida', sa.Float(), nullable=True),
        sa.Column('unidade', sa.String(length=20), nullable=True),
        sa.Column('aprovado', sa.Boolean(), nullable=True),
        sa.Column('aprovado_por', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_colaborador_apontamentos_id'), 'colaborador_apontamentos', ['id'], unique=False)


def downgrade() -> None:
    # Reverter todas as tabelas na ordem inversa
    op.drop_index(op.f('ix_colaborador_apontamentos_id'), table_name='colaborador_apontamentos')
    op.drop_table('colaborador_apontamentos')
    op.drop_index(op.f('ix_ilpf_modulos_id'), table_name='ilpf_modulos')
    op.drop_table('ilpf_modulos')
    op.drop_index(op.f('ix_sensores_leituras_timestamp'), table_name='sensores_leituras')
    op.drop_index(op.f('ix_sensores_leituras_id'), table_name='sensores_leituras')
    op.drop_table('sensores_leituras')
    op.drop_index(op.f('ix_sensores_iot_id'), table_name='sensores_iot')
    op.drop_table('sensores_iot')
    op.drop_index(op.f('ix_hedge_registros_id'), table_name='hedge_registros')
    op.drop_table('hedge_registros')
    op.drop_index(op.f('ix_contratos_futuros_id'), table_name='contratos_futuros')
    op.drop_table('contratos_futuros')
    op.drop_index(op.f('ix_sugestoes_acasalamento_id'), table_name='sugestoes_acasalamento')
    op.drop_table('sugestoes_acasalamento')
    op.drop_index(op.f('ix_racas_id'), table_name='racas')
    op.drop_table('racas')
    op.drop_index(op.f('ix_cochos_id'), table_name='cochos')
    op.drop_table('cochos')
    op.drop_index(op.f('ix_racoes_tmr_id'), table_name='racoes_tmr')
    op.drop_table('racoes_tmr')
    op.drop_index(op.f('ix_confinamento_lotes_id'), table_name='confinamento_lotes')
    op.drop_table('confinamento_lotes')
    op.drop_index(op.f('ix_pesagens_id'), table_name='pesagens')
    op.drop_table('pesagens')
    op.drop_index(op.f('ix_arracoamentos_id'), table_name='arracoamentos')
    op.drop_table('arracoamentos')
    op.drop_index(op.f('ix_tanques_rede_id'), table_name='tanques_rede')
    op.drop_table('tanques_rede')
    op.drop_index(op.f('ix_esg_relatorios_id'), table_name='esg_relatorios')
    op.drop_table('esg_relatorios')
    op.drop_index(op.f('ix_esg_indicadores_id'), table_name='esg_indicadores')
    op.drop_table('esg_indicadores')
    op.drop_index(op.f('ix_mrv_relatorios_id'), table_name='mrv_relatorios')
    op.drop_table('mrv_relatorios')
    op.drop_index(op.f('ix_mrv_projetos_id'), table_name='mrv_projetos')
    op.drop_table('mrv_projetos')
