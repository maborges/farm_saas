"""add_financeiro_comercializacoes

Adiciona a tabela de comercialização de commodities (contratos de venda).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'comercializacao_v1'
down_revision: Union[str, Sequence[str], None] = 'merge_commodity_refactor'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'financeiro_comercializacoes',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('numero_contrato', sa.String(length=30), nullable=True, comment='Número do contrato / nota'),
        sa.Column('commodity_id', sa.Uuid(), nullable=False),
        sa.Column('comprador_id', sa.Uuid(), nullable=False, comment='Pessoa/empresa compradora'),
        sa.Column('quantidade', sa.Numeric(14, 3), nullable=False, comment='Quantidade na unidade da commodity'),
        sa.Column('unidade', sa.String(length=20), nullable=False, comment='Unidade de medida (herdada da commodity)'),
        sa.Column('preco_unitario', sa.Numeric(12, 4), nullable=False, comment='Preço por unidade'),
        sa.Column('moeda', sa.String(length=3), nullable=False, server_default='BRL'),
        sa.Column('valor_total', sa.Numeric(15, 2), nullable=False, comment='quantidade × preco_unitario'),
        sa.Column('forma_pagamento', sa.String(length=30), nullable=True, comment='A_VISTA | PRAZO | BOLETO | PIX | TRANSFERENCIA'),
        sa.Column('data_pagamento', sa.Date(), nullable=True),
        sa.Column('data_entrega_prevista', sa.Date(), nullable=True),
        sa.Column('data_entrega_real', sa.Date(), nullable=True),
        sa.Column('local_entrega', sa.String(length=200), nullable=True, comment='Endereço/local de entrega'),
        sa.Column('frete_por_conta', sa.String(length=20), nullable=True, comment='COMPRADOR | VENDEDOR | CIF | FOB'),
        sa.Column('produto_colhido_id', sa.Uuid(), nullable=True, comment='Lote de produto colhido vinculado'),
        sa.Column('nf_numero', sa.String(length=50), nullable=True, comment='Número da NF-e'),
        sa.Column('nf_serie', sa.String(length=10), nullable=True),
        sa.Column('nf_chave', sa.String(length=44), nullable=True, comment='Chave de acesso NF-e'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='RASCUNHO', comment='RASCUNHO | CONFIRMADO | EM_TRANSITO | ENTREGUE | FINALIZADO | CANCELADO'),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('dados_extras', postgresql.JSONB(), nullable=True),
        sa.Column('receita_id', sa.Uuid(), nullable=True, comment='ID da Receita gerada no financeiro'),
        sa.Column('criado_por', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['commodity_id'], ['cadastros_commodities.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['comprador_id'], ['cadastros_pessoas.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['produto_colhido_id'], ['agricola_produtos_colhidos.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )

    with op.batch_alter_table('financeiro_comercializacoes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_financeiro_comercializacoes_tenant_id'), ['tenant_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_financeiro_comercializacoes_commodity_id'), ['commodity_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_financeiro_comercializacoes_comprador_id'), ['comprador_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_financeiro_comercializacoes_produto_colhido_id'), ['produto_colhido_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_financeiro_comercializacoes_numero_contrato'), ['numero_contrato'], unique=False)
        batch_op.create_index(batch_op.f('ix_financeiro_comercializacoes_status'), ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('financeiro_comercializacoes')
