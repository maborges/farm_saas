"""add_propriedade_exploracao_rural

Revision ID: add_propriedade_exploracao_rural
Revises: 8c2e891d6ba9
Create Date: 2026-04-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_propriedade_exploracao_rural'
down_revision: Union[str, None] = '8c2e891d6ba9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. CREATE TABLE cadastros_propriedades
    op.create_table(
        'cadastros_propriedades',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('nome', sa.String(200), nullable=False),
        sa.Column('cpf_cnpj', sa.String(18), nullable=True),
        sa.Column('inscricao_estadual', sa.String(50), nullable=True),
        sa.Column('ie_isento', sa.Boolean, default=False),
        sa.Column('email', sa.String(200), nullable=True),
        sa.Column('telefone', sa.String(30), nullable=True),
        sa.Column('nome_fantasia', sa.String(200), nullable=True),
        sa.Column('regime_tributario', sa.String(30), nullable=True),
        sa.Column('cor', sa.String(7), nullable=True),
        sa.Column('icone', sa.String(50), nullable=True),
        sa.Column('ordem', sa.Integer, default=0),
        sa.Column('ativo', sa.Boolean, default=True),
        sa.Column('observacoes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Index('ix_propriedades_tenant', 'tenant_id'),
    )

    # 2. CREATE TABLE cadastros_exploracoes_rurais
    op.create_table(
        'cadastros_exploracoes_rurais',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('propriedade_id', sa.Uuid(as_uuid=True), sa.ForeignKey('cadastros_propriedades.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('fazenda_id', sa.Uuid(as_uuid=True), sa.ForeignKey('fazendas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('natureza', sa.String(30), nullable=False, server_default='propria'),
        sa.Column('data_inicio', sa.Date, nullable=False),
        sa.Column('data_fim', sa.Date, nullable=True),
        sa.Column('numero_contrato', sa.String(100), nullable=True),
        sa.Column('valor_anual', sa.Float, nullable=True),
        sa.Column('percentual_producao', sa.Float, nullable=True),
        sa.Column('area_explorada_ha', sa.Float, nullable=True),
        sa.Column('documento_s3_key', sa.String(512), nullable=True),
        sa.Column('documento_tipo', sa.String(20), nullable=True),
        sa.Column('ativo', sa.Boolean, default=True),
        sa.Column('observacoes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Index('ix_exploracoes_tenant', 'tenant_id'),
        sa.Index('ix_exploracoes_vigencia', 'data_inicio', 'data_fim'),
    )

    # 3. CREATE TABLE cadastros_documentos_exploracao
    op.create_table(
        'cadastros_documentos_exploracao',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.Uuid(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('exploracao_id', sa.Uuid(as_uuid=True), sa.ForeignKey('cadastros_exploracoes_rurais.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('tipo', sa.String(50), nullable=False),
        sa.Column('nome_arquivo', sa.String(255), nullable=False),
        sa.Column('storage_path', sa.String(512), nullable=False),
        sa.Column('storage_backend', sa.String(10), nullable=False, server_default='local'),
        sa.Column('tamanho_bytes', sa.Integer, nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('data_emissao', sa.Date, nullable=True),
        sa.Column('data_validade', sa.Date, nullable=True),
        sa.Column('numero_documento', sa.String(100), nullable=True),
        sa.Column('orgao_expedidor', sa.String(100), nullable=True),
        sa.Column('observacoes', sa.Text, nullable=True),
        sa.Column('ativo', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 4. Migração de dados (opcional - se houver dados em grupos_fazendas)
    # Esta parte depende da existência da tabela grupos_fazendas
    # Se existir, descomentar:
    #
    # from sqlalchemy.sql import table, column
    # grupos_fazendas = table('grupos_fazendas', 
    #     column('id', sa.Uuid), column('tenant_id', sa.Uuid), 
    #     column('nome', sa.String), column('descricao', sa.Text),
    #     column('cor', sa.String), column('icone', sa.String),
    #     column('ordem', sa.Integer), column('ativo', sa.Boolean),
    #     column('created_at', sa.DateTime), column('updated_at', sa.DateTime)
    # )
    # 
    # connection = op.get_bind()
    # resultados = connection.execute(sa.select(grupos_fazendas))
    # for row in resultados:
    #     connection.execute(
    #         sa.text("""
    #             INSERT INTO cadastros_propriedades 
    #             (id, tenant_id, nome, descricao, cor, icone, ordem, ativo, created_at, updated_at)
    #             VALUES (:id, :tenant_id, :nome, :descricao, :cor, :icone, :ordem, :ativo, :created_at, :updated_at)
    #         """),
    #         {
    #             'id': row.id, 'tenant_id': row.tenant_id, 'nome': row.nome,
    #             'descricao': row.descricao, 'cor': row.cor, 'icone': row.icone,
    #             'ordem': row.ordem, 'ativo': row.ativo, 
    #             'created_at': row.created_at, 'updated_at': row.updated_at
    #         }
    #     )

    # 5. Adicionar coluna exploracao_id em fazendas (se necessário)
    # Esta parte é opcional e depende da estrutura real de fazendas
    # op.add_column(
    #     'fazendas',
    #     sa.Column('exploracao_id', sa.Uuid(as_uuid=True), nullable=True)
    # )


def downgrade() -> None:
    # Ordem inversa: remover colunas adicionadas, depois tabelas
    # op.drop_column('fazendas', 'exploracao_id')
    
    op.drop_table('cadastros_documentos_exploracao')
    op.drop_table('cadastros_exploracoes_rurais')
    op.drop_table('cadastros_propriedades')
