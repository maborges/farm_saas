"""create notas_fiscais table

Revision ID: 001_notas_fiscais
Revises: 
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_notas_fiscais'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    sa.Enum('NFP-e', 'NF-e', 'NFC-e', name='tiponotafiscal').create(op.get_bind())
    sa.Enum('em_digitacao', 'assinada', 'transmitida', 'autorizada', 'cancelada', 'denegada', 'inutilizada', name='statussefaz').create(op.get_bind())
    
    # Create table
    op.create_table('notas_fiscais',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo', sa.Enum('NFP-e', 'NF-e', 'NFC-e', name='tiponotafiscal'), nullable=False, default='NFP-e'),
        sa.Column('numero', sa.Integer(), nullable=False),
        sa.Column('serie', sa.String(length=10), nullable=False, default='1'),
        sa.Column('data_emissao', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('data_saida_entrada', sa.DateTime(), nullable=True),
        sa.Column('data_autorizacao', sa.DateTime(), nullable=True),
        sa.Column('emitente_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('emitente_nome', sa.String(length=200), nullable=False),
        sa.Column('emitente_cnpj_cpf', sa.String(length=14), nullable=False),
        sa.Column('emitente_ie', sa.String(length=20), nullable=True),
        sa.Column('emitente_im', sa.String(length=20), nullable=True),
        sa.Column('destinatario_tipo', sa.String(length=10), nullable=False),
        sa.Column('destinatario_nome', sa.String(length=200), nullable=False),
        sa.Column('destinatario_documento', sa.String(length=14), nullable=False),
        sa.Column('destinatario_ie', sa.String(length=20), nullable=True),
        sa.Column('destinatario_email', sa.String(length=120), nullable=True),
        sa.Column('destinatario_telefone', sa.String(length=20), nullable=True),
        sa.Column('destinatario_logradouro', sa.String(length=200), nullable=True),
        sa.Column('destinatario_numero', sa.String(length=20), nullable=True),
        sa.Column('destinatario_complemento', sa.String(length=100), nullable=True),
        sa.Column('destinatario_bairro', sa.String(length=100), nullable=True),
        sa.Column('destinatario_municipio', sa.String(length=100), nullable=True),
        sa.Column('destinatario_uf', sa.String(length=2), nullable=True),
        sa.Column('destinatario_cep', sa.String(length=10), nullable=True),
        sa.Column('destinatario_pais', sa.String(length=50), nullable=True, default='Brasil'),
        sa.Column('destinatario_cod_municipio', sa.String(length=7), nullable=True),
        sa.Column('valor_total', sa.Float(), nullable=False, default=0.0),
        sa.Column('valor_produtos', sa.Float(), default=0.0),
        sa.Column('valor_frete', sa.Float(), default=0.0),
        sa.Column('valor_seguro', sa.Float(), default=0.0),
        sa.Column('valor_descontos', sa.Float(), default=0.0),
        sa.Column('valor_outras_despesas', sa.Float(), default=0.0),
        sa.Column('valor_tributos', sa.Float(), default=0.0),
        sa.Column('valor_pis', sa.Float(), default=0.0),
        sa.Column('valor_cofins', sa.Float(), default=0.0),
        sa.Column('valor_icms', sa.Float(), default=0.0),
        sa.Column('valor_ipi', sa.Float(), default=0.0),
        sa.Column('base_calculo_icms', sa.Float(), default=0.0),
        sa.Column('base_calculo_icms_st', sa.Float(), default=0.0),
        sa.Column('valor_icms_st', sa.Float(), default=0.0),
        sa.Column('modalidade_frete', sa.Integer(), nullable=True),
        sa.Column('transportadora_nome', sa.String(length=200), nullable=True),
        sa.Column('transportadora_cnpj_cpf', sa.String(length=14), nullable=True),
        sa.Column('transportadora_ie', sa.String(length=20), nullable=True),
        sa.Column('transportadora_endereco', sa.String(length=200), nullable=True),
        sa.Column('transportadora_municipio', sa.String(length=100), nullable=True),
        sa.Column('transportadora_uf', sa.String(length=2), nullable=True),
        sa.Column('veiculo_placa', sa.String(length=10), nullable=True),
        sa.Column('veiculo_uf', sa.String(length=2), nullable=True),
        sa.Column('veiculo_rntc', sa.String(length=20), nullable=True),
        sa.Column('itens', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=list),
        sa.Column('info_adicionais_fisco', sa.Text(), nullable=True),
        sa.Column('info_adicionais_contribuinte', sa.Text(), nullable=True),
        sa.Column('safra_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('codigo_agricultor', sa.String(length=20), nullable=True),
        sa.Column('chave_acesso', sa.String(length=44), nullable=True),
        sa.Column('status_sefaz', sa.Enum('em_digitacao', 'assinada', 'transmitida', 'autorizada', 'cancelada', 'denegada', 'inutilizada', name='statussefaz'), nullable=False, default='em_digitacao'),
        sa.Column('numero_recibo', sa.String(length=15), nullable=True),
        sa.Column('numero_protocolo', sa.String(length=15), nullable=True),
        sa.Column('motivo_cancelamento', sa.Text(), nullable=True),
        sa.Column('data_cancelamento', sa.DateTime(), nullable=True),
        sa.Column('xml', sa.Text(), nullable=True),
        sa.Column('xml_danfe', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['emitente_id'], ['fazendas.id'], ),
        sa.ForeignKeyConstraint(['safra_id'], ['safras.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'tipo', 'serie', 'numero', name='uq_nota_unica'),
        sa.UniqueConstraint('chave_acesso', name='uq_chave_acesso')
    )
    
    # Create indexes
    op.create_index('ix_notas_fiscais_tenant_id', 'notas_fiscais', ['tenant_id'])
    op.create_index('ix_notas_fiscais_chave_acesso', 'notas_fiscais', ['chave_acesso'])
    op.create_index('ix_notas_fiscais_numero', 'notas_fiscais', ['numero'])
    op.create_index('ix_notas_fiscais_status_sefaz', 'notas_fiscais', ['status_sefaz'])
    op.create_index('ix_notas_fiscais_data_emissao', 'notas_fiscais', ['data_emissao'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_notas_fiscais_data_emissao', table_name='notas_fiscais')
    op.drop_index('ix_notas_fiscais_status_sefaz', table_name='notas_fiscais')
    op.drop_index('ix_notas_fiscais_numero', table_name='notas_fiscais')
    op.drop_index('ix_notas_fiscais_chave_acesso', table_name='notas_fiscais')
    op.drop_index('ix_notas_fiscais_tenant_id', table_name='notas_fiscais')
    
    # Drop table
    op.drop_table('notas_fiscais')
    
    # Drop enum types
    sa.Enum(name='statussefaz').drop(op.get_bind())
    sa.Enum(name='tiponotafiscal').drop(op.get_bind())
