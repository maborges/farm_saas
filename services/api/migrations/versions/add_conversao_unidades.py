"""add_conversao_unidades

Adiciona tabela de conversão de unidades por commodity.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'conversao_unidade_v1'
down_revision: Union[str, Sequence[str], None] = 'comercializacao_v1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cadastros_conversao_unidades',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('commodity_id', sa.Uuid(), nullable=False),
        sa.Column('unidade_origem', sa.String(length=20), nullable=False),
        sa.Column('unidade_destino', sa.String(length=20), nullable=False),
        sa.Column('fator', sa.Float(), nullable=False, comment='destino = origem × fator'),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['commodity_id'], ['cadastros_commodities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('commodity_id', 'unidade_origem', 'unidade_destino', name='uq_conversao_commodity_origem_destino'),
    )
    with op.batch_alter_table('cadastros_conversao_unidades', schema=None) as batch_op:
        batch_op.create_index('ix_cadastros_conversao_unidades_commodity_id', ['commodity_id'], unique=False)

    # Seed de conversões padrão para commodities do sistema
    conversoes = [
        # SOJA
        ('SOJA', 'SACA_60KG', 'KG', 60.0, '1 saca de soja = 60 kg'),
        ('SOJA', 'SACA_60KG', 'TONELADA', 0.06, '1 saca de soja = 0.06 tonelada'),
        ('SOJA', 'KG', 'SACA_60KG', 1/60, '1 kg de soja = 1/60 saca'),
        ('SOJA', 'TONELADA', 'SACA_60KG', 1/0.06, '1 tonelada de soja = 16.67 sacas'),
        # MILHO
        ('MILHO', 'SACA_60KG', 'KG', 60.0, '1 saca de milho = 60 kg'),
        ('MILHO', 'SACA_60KG', 'TONELADA', 0.06, '1 saca de milho = 0.06 tonelada'),
        # TRIGO
        ('TRIGO', 'SACA_60KG', 'KG', 60.0, '1 saca de trigo = 60 kg'),
        # ALGODAO (saca de 15kg para algodão em pluma)
        ('ALGODAO', 'SACA_60KG', 'KG', 15.0, '1 saca de algodão em pluma = 15 kg'),
        ('ALGODAO', 'SACA_60KG', 'TONELADA', 0.015, '1 saca de algodão = 0.015 tonelada'),
        # ARROZ (saca de 50kg)
        ('ARROZ', 'SACA_60KG', 'KG', 50.0, '1 saca de arroz = 50 kg'),
        # CAFE
        ('CAFE_ARABICA', 'SACA_60KG', 'KG', 60.0, '1 saca de café = 60 kg'),
        ('CAFE_CONILON', 'SACA_60KG', 'KG', 60.0, '1 saca de café conilon = 60 kg'),
        # BOI_GORDO
        ('BOI_GORDO', 'ARROBA', 'KG', 15.0, '1 arroba = 15 kg'),
        ('BOI_GORDO', 'ARROBA', 'TONELADA', 0.015, '1 arroba = 0.015 tonelada'),
        # EUCALIPTO (m³)
        ('EUCALIPTO', 'M3', 'TONELADA', 0.55, '1 m³ de eucalipto ≈ 0.55 tonelada (densidade média)'),
    ]

    for codigo, origem, destino, fator, desc in conversoes:
        op.execute(sa.text("""
            INSERT INTO cadastros_conversao_unidades
                (id, commodity_id, unidade_origem, unidade_destino, fator, descricao, ativo, created_at)
            SELECT
                gen_random_uuid(),
                c.id, :origem, :destino, :fator, :desc, true, NOW()
            FROM cadastros_commodities c
            WHERE c.codigo = :codigo AND c.sistema = true
            ON CONFLICT (commodity_id, unidade_origem, unidade_destino) DO NOTHING
        """), {"codigo": codigo, "origem": origem, "destino": destino, "fator": fator, "desc": desc})

    # Atualizar alembic
    op.execute("UPDATE alembic_version SET version_num = 'conversao_unidade_v1'")


def downgrade() -> None:
    op.drop_table('cadastros_conversao_unidades')
