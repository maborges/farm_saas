"""
Add imóveis rurais module - cadastro, documentos legais, arrendamentos

Revision ID: imoveis_rurais_init
Revises: fcc3dc4b3800
Create Date: 2026-04-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'imoveis_rurais_init'
down_revision = '1795966a0c0a'  # Latest migration
branch_labels = None
depends_on = None

# Use JSON for SQLite compatibility (PostgreSQL will auto-convert to JSONB)
def get_json_type():
    try:
        return postgresql.JSONB(astext_type=sa.Text())
    except:
        return sa.JSON()


def _create_enum_if_not_exists(bind, values: list, name: str) -> None:
    """Create a PostgreSQL enum type only if it doesn't already exist."""
    bind.execute(sa.text(
        f"DO $$ BEGIN "
        f"  CREATE TYPE {name} AS ENUM ({', '.join(repr(v) for v in values)}); "
        f"EXCEPTION WHEN duplicate_object THEN NULL; "
        f"END $$;"
    ))


def upgrade() -> None:
    bind = op.get_bind()
    # Create enum types (idempotent — safe to re-run)
    _create_enum_if_not_exists(bind, ['rural', 'particular', 'devoluta', 'posse'], 'tipoimovel')
    _create_enum_if_not_exists(bind, ['regular', 'pendente', 'irregular'], 'situacaoimovel')
    _create_enum_if_not_exists(bind, ['CCIR', 'ITR_DITR', 'CAR', 'ESCRITURA', 'MATRICULA', 'GEOREFERENCIAMENTO', 'OUTRO'], 'tipodocumento')
    _create_enum_if_not_exists(bind, ['ATIVO', 'SUBSTITUIDO', 'VENCIDO', 'CANCELADO'], 'statusdocumento')
    _create_enum_if_not_exists(bind, ['ARRENDAMENTO', 'PARCERIA'], 'tipocontrato')
    _create_enum_if_not_exists(bind, ['PESSOA_FISICA', 'PESSOA_JURIDICA', 'FAZENDA_TENANT'], 'tipoarrendatario')
    _create_enum_if_not_exists(bind, ['FIXO_BRL', 'FIXO_SACAS', 'PERCENTUAL'], 'valormodalidade')
    _create_enum_if_not_exists(bind, ['MENSAL', 'SEMESTRAL', 'ANUAL', 'SAFRA'], 'periodicidade')
    _create_enum_if_not_exists(bind, ['ATIVO', 'ENCERRADO', 'RESCINDIDO', 'SUSPENSO'], 'statuscontrato')
    _create_enum_if_not_exists(bind, ['PREVISTA', 'PAGA', 'CANCELADA', 'VENCIDA'], 'statusparcela')

    # Create table: imoveis_cartorios
    op.create_table('imoveis_cartorios',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('comarca', sa.String(100), nullable=False),
        sa.Column('uf', sa.String(2), nullable=False),
        sa.Column('codigo_censec', sa.String(20), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('endereco', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )

    # Create table: imoveis_rurais
    op.create_table('imoveis_rurais',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('fazenda_id', sa.Uuid(as_uuid=True), sa.ForeignKey('fazendas.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('cartorio_id', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_cartorios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('numero_matricula', sa.String(100), nullable=True),
        sa.Column('nirf', sa.String(20), nullable=True, index=True),
        sa.Column('car_numero', sa.String(50), nullable=True, index=True),
        sa.Column('ccir_numero', sa.String(50), nullable=True),
        sa.Column('area_total_ha', sa.Numeric(12, 4), nullable=False),
        sa.Column('area_aproveitavel_ha', sa.Numeric(12, 4), nullable=True),
        sa.Column('area_app_ha', sa.Numeric(12, 4), nullable=True),
        sa.Column('area_rl_ha', sa.Numeric(12, 4), nullable=True),
        sa.Column('modulos_fiscais', sa.Numeric(6, 2), nullable=True),
        sa.Column('municipio', sa.String(100), nullable=False),
        sa.Column('uf', sa.String(2), nullable=False),
        sa.Column('codigo_municipio_ibge', sa.String(10), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('tipo', sa.Enum('rural', 'particular', 'devoluta', 'posse', name='tipoimovel', create_type=False), nullable=False),
        sa.Column('situacao', sa.Enum('regular', 'pendente', 'irregular', name='situacaoimovel', create_type=False), nullable=False),
        sa.Column('geometria', get_json_type(), nullable=True),
        sa.Column('observacao', sa.Text(), nullable=True),
        sa.Column('motivo_alteracao_area', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Uuid(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, index=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['cartorio_id'], ['imoveis_cartorios.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['usuarios.id']),
        sa.UniqueConstraint('nirf', name='uq_imovel_nirf'),
        sa.UniqueConstraint('tenant_id', 'cartorio_id', 'numero_matricula', name='uq_imovel_matricula'),
    )

    # Create table: imoveis_matriculas
    op.create_table('imoveis_matriculas',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('imovel_id', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_rurais.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('cartorio_id', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_cartorios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('numero_matricula', sa.String(50), nullable=False),
        sa.Column('cartorio_nome', sa.String(200), nullable=True),
        sa.Column('area_matricula_ha', sa.Numeric(12, 4), nullable=False),
        sa.Column('data_transmissao', sa.Date(), nullable=True),
        sa.Column('tipo_transmissao', sa.String(50), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['imovel_id'], ['imoveis_rurais.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cartorio_id'], ['imoveis_cartorios.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('tenant_id', 'cartorio_id', 'numero_matricula', name='uq_matricula_unica'),
    )

    # Create table: imoveis_benfeitorias
    op.create_table('imoveis_benfeitorias',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('imovel_id', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_rurais.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('tipo', sa.String(50), nullable=True),
        sa.Column('area_construida', sa.Numeric(10, 2), nullable=True),
        sa.Column('capacidade', sa.Numeric(12, 2), nullable=True),
        sa.Column('unidade_capacidade', sa.String(20), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('valor_estimado', sa.Numeric(12, 2), nullable=True),
        sa.Column('ano_construcao', sa.Integer(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['imovel_id'], ['imoveis_rurais.id'], ondelete='CASCADE'),
    )

    # Create table: imoveis_documentos
    op.create_table('imoveis_documentos',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('imovel_id', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_rurais.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('tipo', sa.Enum('CCIR', 'ITR_DITR', 'CAR', 'ESCRITURA', 'MATRICULA', 'GEOREFERENCIAMENTO', 'OUTRO', name='tipodocumento', create_type=False), nullable=False, index=True),
        sa.Column('descricao', sa.String(255), nullable=True),
        sa.Column('numero_documento', sa.String(100), nullable=True),
        sa.Column('data_emissao', sa.Date(), nullable=True),
        sa.Column('data_vencimento', sa.Date(), nullable=True, index=True),
        sa.Column('status', sa.Enum('ATIVO', 'SUBSTITUIDO', 'VENCIDO', 'CANCELADO', name='statusdocumento', create_type=False), nullable=False),
        sa.Column('versao', sa.Integer(), nullable=False),
        sa.Column('substituido_por', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_documentos.id', ondelete='SET NULL'), nullable=True),
        sa.Column('path_storage', sa.String(512), nullable=False),
        sa.Column('nome_arquivo', sa.String(255), nullable=False),
        sa.Column('tamanho_bytes', sa.Integer(), nullable=False),
        sa.Column('hash_conteudo', sa.String(64), nullable=True),
        sa.Column('restrito', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_by', sa.Uuid(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['imovel_id'], ['imoveis_rurais.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['substituido_por'], ['imoveis_documentos.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('tenant_id', 'imovel_id', 'tipo', 'versao', name='uq_documento_tipo_versao'),
    )

    # Create table: imoveis_documentos_historico
    op.create_table('imoveis_documentos_historico',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('documento_id', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_documentos.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('usuario_id', sa.Uuid(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('acao', sa.String(50), nullable=False),
        sa.Column('dados_acao', get_json_type(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['documento_id'], ['imoveis_documentos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id']),
    )

    # Create table: imoveis_arrendamentos
    op.create_table('imoveis_arrendamentos',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('imovel_id', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_rurais.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('fazenda_id', sa.Uuid(as_uuid=True), sa.ForeignKey('fazendas.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('tipo', sa.Enum('ARRENDAMENTO', 'PARCERIA', name='tipocontrato', create_type=False), nullable=False),
        sa.Column('arrendatario_tipo', sa.Enum('PESSOA_FISICA', 'PESSOA_JURIDICA', 'FAZENDA_TENANT', name='tipoarrendatario', create_type=False), nullable=False),
        sa.Column('arrendatario_pessoa_id', sa.Uuid(as_uuid=True), sa.ForeignKey('pessoas.id', ondelete='SET NULL'), nullable=True),
        sa.Column('arrendatario_fazenda_id', sa.Uuid(as_uuid=True), sa.ForeignKey('fazendas.id', ondelete='SET NULL'), nullable=True),
        sa.Column('area_arrendada_ha', sa.Numeric(12, 4), nullable=False),
        sa.Column('valor_modalidade', sa.Enum('FIXO_BRL', 'FIXO_SACAS', 'PERCENTUAL', name='valormodalidade', create_type=False), nullable=False),
        sa.Column('valor', sa.Numeric(12, 2), nullable=False),
        sa.Column('commodity_referencia', sa.String(50), nullable=True),
        sa.Column('periodicidade', sa.Enum('MENSAL', 'SEMESTRAL', 'ANUAL', 'SAFRA', name='periodicidade', create_type=False), nullable=False),
        sa.Column('data_inicio', sa.Date(), nullable=False),
        sa.Column('data_fim', sa.Date(), nullable=False),
        sa.Column('dia_vencimento', sa.Integer(), nullable=True),
        sa.Column('indice_reajuste', sa.String(20), nullable=True),
        sa.Column('data_reajuste_anual', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('ATIVO', 'ENCERRADO', 'RESCINDIDO', 'SUSPENSO', name='statuscontrato', create_type=False), nullable=False),
        sa.Column('motivo_rescisao', sa.Text(), nullable=True),
        sa.Column('path_contrato_pdf', sa.String(512), nullable=True),
        sa.Column('registro_cartorio', sa.String(100), nullable=True),
        sa.Column('clausulas_observacoes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Uuid(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['imovel_id'], ['imoveis_rurais.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['arrendatario_pessoa_id'], ['pessoas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['arrendatario_fazenda_id'], ['fazendas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['usuarios.id']),
    )

    # Create table: imoveis_arrendamento_parcelas
    op.create_table('imoveis_arrendamento_parcelas',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('contrato_id', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_arrendamentos.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('numero_parcela', sa.Integer(), nullable=False),
        sa.Column('data_vencimento', sa.Date(), nullable=False, index=True),
        sa.Column('valor_centavos', sa.Integer(), nullable=False),
        sa.Column('valor_sacas', sa.Numeric(10, 2), nullable=True),
        sa.Column('status', sa.Enum('PREVISTA', 'PAGA', 'CANCELADA', 'VENCIDA', name='statusparcela', create_type=False), nullable=False),
        sa.Column('lancamento_financeiro_id', sa.Uuid(as_uuid=True), sa.ForeignKey('lancamentos.id', ondelete='SET NULL'), nullable=True),
        sa.Column('data_pagamento', sa.Date(), nullable=True),
        sa.Column('indice_aplicado', sa.Numeric(10, 4), nullable=True),
        sa.Column('observacao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contrato_id'], ['imoveis_arrendamentos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lancamento_financeiro_id'], ['lancamentos.id'], ondelete='SET NULL'),
    )

    # Create table: imoveis_arrendamento_reajustes
    op.create_table('imoveis_arrendamento_reajustes',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('contrato_id', sa.Uuid(as_uuid=True), sa.ForeignKey('imoveis_arrendamentos.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('data_reajuste', sa.Date(), nullable=False),
        sa.Column('indice_nome', sa.String(50), nullable=False),
        sa.Column('indice_valor', sa.Numeric(10, 4), nullable=False),
        sa.Column('valor_anterior', sa.Numeric(12, 2), nullable=False),
        sa.Column('valor_novo', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_by', sa.Uuid(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contrato_id'], ['imoveis_arrendamentos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['usuarios.id']),
    )


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('imoveis_arrendamento_reajustes')
    op.drop_table('imoveis_arrendamento_parcelas')
    op.drop_table('imoveis_arrendamentos')
    op.drop_table('imoveis_documentos_historico')
    op.drop_table('imoveis_documentos')
    op.drop_table('imoveis_benfeitorias')
    op.drop_table('imoveis_matriculas')
    op.drop_table('imoveis_rurais')
    op.drop_table('imoveis_cartorios')

    # Drop enum types
    sa.Enum(name='statusparcela').drop(op.get_bind())
    sa.Enum(name='statuscontrato').drop(op.get_bind())
    sa.Enum(name='periodicidade').drop(op.get_bind())
    sa.Enum(name='valormodalidade').drop(op.get_bind())
    sa.Enum(name='tipoarrendatario').drop(op.get_bind())
    sa.Enum(name='tipocontrato').drop(op.get_bind())
    sa.Enum(name='statusdocumento').drop(op.get_bind())
    sa.Enum(name='tipodocumento').drop(op.get_bind())
    sa.Enum(name='situacaoimovel').drop(op.get_bind())
    sa.Enum(name='tipoimovel').drop(op.get_bind())
