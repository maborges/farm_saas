"""add_produto_colhido_and_romaneio_commodity_id

Adiciona:
- Tabela agricola_produtos_colhidos
- Campo commodity_id em romaneios_colheita
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'produto_colhido_v1'
down_revision: Union[str, Sequence[str], None] = 'commodity_refactor_v1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------------
    # 1. commodity_id em romaneios_colheita
    # ---------------------------------------------------------------
    with op.batch_alter_table('romaneios_colheita', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'commodity_id', sa.Uuid(), nullable=True,
            comment="Commodity colhida (derivada de safra.commodity_id, mas explícito para queries)"
        ))
        batch_op.create_foreign_key(
            'fk_romaneio_commodity',
            'cadastros_commodities',
            ['commodity_id'],
            ['id'],
            ondelete='SET NULL'
        )
        batch_op.create_index(batch_op.f('ix_romaneios_colheita_commodity_id'), ['commodity_id'], unique=False)

    # Popular commodity_id a partir da safra
    op.execute("""
        UPDATE romaneios_colheita
        SET commodity_id = (SELECT commodity_id FROM safras WHERE safras.id = romaneios_colheita.safra_id)
        WHERE commodity_id IS NULL
    """)

    # ---------------------------------------------------------------
    # 2. Tabela agricola_produtos_colhidos
    # ---------------------------------------------------------------
    op.create_table(
        'agricola_produtos_colhidos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('safra_id', sa.Uuid(), nullable=False),
        sa.Column('talhao_id', sa.Uuid(), nullable=False),
        sa.Column('romaneio_id', sa.Uuid(), nullable=True, comment="Romaneio de colheita que originou este lote"),
        sa.Column('commodity_id', sa.Uuid(), nullable=False),
        sa.Column('classificacao_id', sa.Uuid(), nullable=True, comment="Classificação de mercado atribuída"),
        sa.Column('quantidade', sa.Numeric(14, 3), nullable=False, comment="Quantidade na unidade da commodity"),
        sa.Column('unidade', sa.String(length=20), nullable=False, comment="Unidade de medida (herdada da commodity)"),
        sa.Column('peso_liquido_kg', sa.Numeric(14, 3), nullable=False, comment="Peso líquido real em kg"),
        sa.Column('umidade_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('impureza_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('avariados_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('ardidos_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('quebrados_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('destino', sa.String(length=30), nullable=True, comment="ARMAZEM | TERCEIRO | VENDIDO | TRANSITO"),
        sa.Column('armazem_id', sa.Uuid(), nullable=True, comment="Depósito/armazém onde está fisicamente"),
        sa.Column('data_entrada', sa.Date(), nullable=False),
        sa.Column('data_saida_prevista', sa.Date(), nullable=True),
        sa.Column('nf_origem', sa.String(length=50), nullable=True, comment="NF de origem se veio de terceiro"),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('dados_extras', sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='ARMAZENADO', comment="ARMAZENADO | RESERVADO | EM_TRANSITO | VENDIDO | PERDA"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['safra_id'], ['safras.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['talhao_id'], ['cadastros_areas_rurais.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['romaneio_id'], ['romaneios_colheita.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['commodity_id'], ['cadastros_commodities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['classificacao_id'], ['cadastros_commodities_classificacoes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('agricola_produtos_colhidos', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_agricola_produtos_colhidos_tenant_id'), ['tenant_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_agricola_produtos_colhidos_safra_id'), ['safra_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_agricola_produtos_colhidos_talhao_id'), ['talhao_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_agricola_produtos_colhidos_romaneio_id'), ['romaneio_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_agricola_produtos_colhidos_commodity_id'), ['commodity_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_agricola_produtos_colhidos_classificacao_id'), ['classificacao_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_agricola_produtos_colhidos_status'), ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table('romaneios_colheita', schema=None) as batch_op:
        batch_op.drop_constraint('fk_romaneio_commodity', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_romaneios_colheita_commodity_id'))
        batch_op.drop_column('commodity_id')

    op.drop_table('agricola_produtos_colhidos')
