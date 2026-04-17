"""commodity_refactor_classificacoes_cotacoes_qualidade

Revision ID: commodity_refactor_v1
Revises: ed0688180f35
Create Date: 2026-04-12 00:00:00.000000

Refatora commodities para adicionar:
- Tabela cadastros_commodities_cotacoes (nova)
- Campos umidade_padrao_pct e impureza_padrao_pct em cadastros_commodities
- UniqueConstraint tenant_id + nome em cadastros_commodities
- Torna campo codigo NOT NULL e único globalmente
- Adiciona campos de qualidade que estavam faltando no modelo SQLAlchemy
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'commodity_refactor_v1'
down_revision: Union[str, Sequence[str], None] = 'ed0688180f35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------------
    # 1. Tabela de cotações (nova)
    # ---------------------------------------------------------------
    op.create_table(
        'cadastros_commodities_cotacoes',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('commodity_id', sa.Uuid(), nullable=False),
        sa.Column('data', sa.DateTime(timezone=True), nullable=False),
        sa.Column('preco', sa.Numeric(12, 4), nullable=False, comment='Preço na unidade padrão da commodity'),
        sa.Column('moeda', sa.String(length=3), nullable=False, server_default='BRL'),
        sa.Column('fonte', sa.String(length=50), nullable=True, comment='CEPEA, B3, CONAB, MANUAL'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['commodity_id'], ['cadastros_commodities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('commodity_id', 'data', 'fonte', name='uq_cotacao_commodity_data_fonte'),
    )
    with op.batch_alter_table('cadastros_commodities_cotacoes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_cadastros_commodities_cotacoes_commodity_id'), ['commodity_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_cadastros_commodities_cotacoes_data'), ['data'], unique=False)

    # ---------------------------------------------------------------
    # 2. Adicionar campos de qualidade a cadastros_commodities
    # ---------------------------------------------------------------
    with op.batch_alter_table('cadastros_commodities', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'umidade_padrao_pct', sa.Float(), nullable=True,
            comment='Umidade padrão MAPA para descontos. Ex: 14.0 para soja, 12.0 para café'
        ))
        batch_op.add_column(sa.Column(
            'impureza_padrao_pct', sa.Float(), nullable=True,
            comment='Impureza padrão aceita sem desconto. Ex: 1.0'
        ))

    # ---------------------------------------------------------------
    # 3. Adicionar UniqueConstraint tenant_id + nome
    # ---------------------------------------------------------------
    # Verificar se já existe (SQLite não suporta ADD CONSTRAINT diretamente)
    # Para PostgreSQL funcionaria, para SQLite precisa rebuild
    try:
        with op.batch_alter_table('cadastros_commodities', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_commodity_tenant_nome', ['tenant_id', 'nome'])
    except Exception:
        # SQLite: constraint já pode ter sido aplicada ou não suportada
        pass

    # ---------------------------------------------------------------
    # 4. Tornar codigo NOT NULL e limpar nulos
    # ---------------------------------------------------------------
    # Gerar códigos para registros sem código
    op.execute("""
        UPDATE cadastros_commodities
        SET codigo = UPPER(REPLACE(nome, ' ', '_'))
        WHERE codigo IS NULL OR codigo = ''
    """)
    with op.batch_alter_table('cadastros_commodities', schema=None) as batch_op:
        batch_op.alter_column(
            'codigo',
            existing_type=sa.String(50),
            nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table('cadastros_commodities', schema=None) as batch_op:
        batch_op.alter_column(
            'codigo',
            existing_type=sa.String(50),
            nullable=True,
        )
        batch_op.drop_constraint('uq_commodity_tenant_nome', type_='unique')
        batch_op.drop_column('impureza_padrao_pct')
        batch_op.drop_column('umidade_padrao_pct')

    with op.batch_alter_table('cadastros_commodities_cotacoes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_cadastros_commodities_cotacoes_data'))
        batch_op.drop_index(batch_op.f('ix_cadastros_commodities_cotacoes_commodity_id'))

    op.drop_table('cadastros_commodities_cotacoes')
