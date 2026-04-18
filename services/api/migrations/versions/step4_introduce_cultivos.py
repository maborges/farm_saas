"""step4: Introduce Cultivos architecture — supports multiple crops per safra

Revision ID: step4_cultivos_intro
Revises: step3_fix_prescricoes_vra_talhao
Create Date: 2026-04-17

Cria a arquitetura de Cultivos que permite múltiplos cultivos por safra:
  - Tabela `cultivos` — unidade de negócio dentro de uma safra
  - Tabela `cultivo_areas` — associação N:N entre cultivo e talhão (AreaRural)
  - Adiciona `cultivo_id` (nullable) em operacoes, romaneios, etc para referência
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "step4_cultivos_intro"
down_revision = "add_estoque_benef_fk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Criar tabela cultivos
    op.create_table(
        'cultivos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('safra_id', sa.Uuid(), nullable=False),
        sa.Column('cultura', sa.String(50), nullable=False),
        sa.Column('cultivar_id', sa.Uuid(), nullable=True),
        sa.Column('cultivar_nome', sa.String(100), nullable=True),
        sa.Column('commodity_id', sa.Uuid(), nullable=True),
        sa.Column('sistema_plantio', sa.String(30), nullable=True),
        sa.Column('populacao_prevista', sa.Integer(), nullable=True),
        sa.Column('populacao_real', sa.Integer(), nullable=True),
        sa.Column('espacamento_cm', sa.Integer(), nullable=True),
        sa.Column('data_plantio_prevista', sa.Date(), nullable=True),
        sa.Column('data_plantio_real', sa.Date(), nullable=True),
        sa.Column('data_colheita_prevista', sa.Date(), nullable=True),
        sa.Column('data_colheita_real', sa.Date(), nullable=True),
        sa.Column('produtividade_meta_sc_ha', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('produtividade_real_sc_ha', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('preco_venda_previsto', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('custo_previsto_ha', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('custo_realizado_ha', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='PLANEJADO'),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['commodity_id'], ['cadastros_commodities.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['cultivar_id'], ['cadastros_culturas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['safra_id'], ['safras.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cultivos_safra_id'), 'cultivos', ['safra_id'], unique=False)
    op.create_index(op.f('ix_cultivos_tenant_id'), 'cultivos', ['tenant_id'], unique=False)

    # 2. Criar tabela cultivo_areas
    op.create_table(
        'cultivo_areas',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('cultivo_id', sa.Uuid(), nullable=False),
        sa.Column('area_id', sa.Uuid(), nullable=False),
        sa.Column('area_ha', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['area_id'], ['cadastros_areas_rurais.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cultivo_id'], ['cultivos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cultivo_areas_cultivo_id'), 'cultivo_areas', ['cultivo_id'], unique=False)
    op.create_index(op.f('ix_cultivo_areas_tenant_id'), 'cultivo_areas', ['tenant_id'], unique=False)

    # 3. Adicionar cultivo_id (nullable) em operacoes_agricolas
    op.add_column('operacoes_agricolas', sa.Column('cultivo_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_operacoes_agricolas_cultivo_id',
        'operacoes_agricolas',
        'cultivos',
        ['cultivo_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 4. Adicionar cultivo_id em romaneios_colheita
    op.add_column('romaneios_colheita', sa.Column('cultivo_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_romaneios_colheita_cultivo_id',
        'romaneios_colheita',
        'cultivos',
        ['cultivo_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 5. Adicionar cultivo_id em agricola_produtos_colhidos
    op.add_column('agricola_produtos_colhidos', sa.Column('cultivo_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_agricola_produtos_colhidos_cultivo_id',
        'agricola_produtos_colhidos',
        'cultivos',
        ['cultivo_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 6. Adicionar cultivo_id em cafe_lotes_beneficiamento
    op.add_column('cafe_lotes_beneficiamento', sa.Column('cultivo_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_cafe_lotes_beneficiamento_cultivo_id',
        'cafe_lotes_beneficiamento',
        'cultivos',
        ['cultivo_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 7. Adicionar cultivo_id em itens_orcamento_safra
    # NOTE: Tabela será adicionada em próxima migration se necessário
    # op.add_column('itens_orcamento_safra', sa.Column('cultivo_id', sa.Uuid(), nullable=True))


def downgrade() -> None:
    # Remover FKs nas tabelas dependentes
    op.drop_constraint('fk_cafe_lotes_beneficiamento_cultivo_id', 'cafe_lotes_beneficiamento', type_='foreignkey')
    op.drop_column('cafe_lotes_beneficiamento', 'cultivo_id')

    op.drop_constraint('fk_agricola_produtos_colhidos_cultivo_id', 'agricola_produtos_colhidos', type_='foreignkey')
    op.drop_column('agricola_produtos_colhidos', 'cultivo_id')

    op.drop_constraint('fk_romaneios_colheita_cultivo_id', 'romaneios_colheita', type_='foreignkey')
    op.drop_column('romaneios_colheita', 'cultivo_id')

    op.drop_constraint('fk_operacoes_agricolas_cultivo_id', 'operacoes_agricolas', type_='foreignkey')
    op.drop_column('operacoes_agricolas', 'cultivo_id')

    # Remover tabelasCultivo_areas
    op.drop_index(op.f('ix_cultivo_areas_tenant_id'), table_name='cultivo_areas')
    op.drop_index(op.f('ix_cultivo_areas_cultivo_id'), table_name='cultivo_areas')
    op.drop_table('cultivo_areas')

    # Remover tabela Cultivos
    op.drop_index(op.f('ix_cultivos_tenant_id'), table_name='cultivos')
    op.drop_index(op.f('ix_cultivos_safra_id'), table_name='cultivos')
    op.drop_table('cultivos')
