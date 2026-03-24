"""catalogo_produtos_unificado_migrate_fks

Revision ID: f1569f5e75f7
Revises: 0be54b7733cc
Create Date: 2026-03-23 23:33:43.623231

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = 'f1569f5e75f7'
down_revision: Union[str, Sequence[str], None] = '0be54b7733cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create unified catalog tables
    op.create_table('cadastros_produtos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('nome', sa.String(length=150), nullable=False),
        sa.Column('tipo', sa.String(length=30), nullable=False),
        sa.Column('unidade_medida', sa.String(length=20), nullable=False),
        sa.Column('codigo_interno', sa.String(length=50), nullable=True),
        sa.Column('sku', sa.String(length=100), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('estoque_minimo', sa.Float(), nullable=False),
        sa.Column('preco_medio', sa.Float(), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cadastros_produtos_codigo_interno', 'cadastros_produtos', ['codigo_interno'])
    op.create_index('ix_cadastros_produtos_nome', 'cadastros_produtos', ['nome'])
    op.create_index('ix_cadastros_produtos_tenant_id', 'cadastros_produtos', ['tenant_id'])
    op.create_index('ix_cadastros_produtos_tipo', 'cadastros_produtos', ['tipo'])

    op.create_table('cadastros_produtos_agricola',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('produto_id', sa.Uuid(), nullable=False),
        sa.Column('registro_mapa', sa.String(length=50), nullable=True),
        sa.Column('classe_agronomica', sa.String(length=50), nullable=True),
        sa.Column('principio_ativo', sa.String(length=200), nullable=True),
        sa.Column('formulacao', sa.String(length=50), nullable=True),
        sa.Column('periodo_carencia_dias', sa.Integer(), nullable=True),
        sa.Column('cultivar', sa.String(length=100), nullable=True),
        sa.Column('cultura', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['produto_id'], ['cadastros_produtos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cadastros_produtos_agricola_produto_id', 'cadastros_produtos_agricola', ['produto_id'], unique=True)

    op.create_table('cadastros_produtos_estoque',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('produto_id', sa.Uuid(), nullable=False),
        sa.Column('localizacao_default', sa.String(length=100), nullable=True),
        sa.Column('peso_unitario_kg', sa.Float(), nullable=True),
        sa.Column('volume_unitario_l', sa.Float(), nullable=True),
        sa.Column('perecivel', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('prazo_validade_dias', sa.Integer(), nullable=True),
        sa.Column('ncm', sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(['produto_id'], ['cadastros_produtos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cadastros_produtos_estoque_produto_id', 'cadastros_produtos_estoque', ['produto_id'], unique=True)

    # 2. Migrate existing products
    conn = op.get_bind()
    conn.execute(text("""
        INSERT INTO cadastros_produtos (id, tenant_id, nome, tipo, unidade_medida, codigo_interno, sku,
                                        descricao, estoque_minimo, preco_medio, ativo, created_at, updated_at)
        SELECT id, tenant_id, nome,
               CASE tipo_uso
                   WHEN 'INSUMO_AGRICOLA' THEN 'INSUMO_AGRICOLA'
                   WHEN 'COMBUSTIVEL'     THEN 'COMBUSTIVEL'
                   WHEN 'PECA'            THEN 'PECA_MAQUINARIO'
                   WHEN 'MATERIAL'        THEN 'MATERIAL_GERAL'
                   ELSE 'OUTROS'
               END,
               unidade_medida, codigo_interno, sku, NULL,
               estoque_minimo, preco_medio, ativo, NOW(), NOW()
        FROM estoque_produtos
        ON CONFLICT (id) DO NOTHING
    """))

    # 3. Repoint all FK constraints to cadastros_produtos
    for tbl, col, old_fk in [
        ('compras_devolucoes_itens', 'produto_id', 'compras_devolucoes_itens_produto_id_fkey'),
        ('compras_itens_pedido',     'produto_id', 'compras_itens_pedido_produto_id_fkey'),
        ('estoque_lotes',            'produto_id', 'estoque_lotes_produto_id_fkey'),
        ('estoque_movimentacoes',    'produto_id', 'estoque_movimentacoes_produto_id_fkey'),
        ('estoque_requisicoes_itens','produto_id', 'estoque_requisicoes_itens_produto_id_fkey'),
        ('estoque_reservas',         'produto_id', 'estoque_reservas_produto_id_fkey'),
        ('estoque_saldos',           'produto_id', 'estoque_saldos_produto_id_fkey'),
        ('frota_os_itens',           'produto_id', 'frota_os_itens_produto_id_fkey'),
        ('insumos_operacao',         'insumo_id',  'insumos_operacao_insumo_id_fkey'),
    ]:
        conn.execute(text(f'ALTER TABLE {tbl} DROP CONSTRAINT IF EXISTS "{old_fk}"'))
        conn.execute(text(f'ALTER TABLE {tbl} ADD CONSTRAINT {tbl}_{col}_fkey FOREIGN KEY ({col}) REFERENCES cadastros_produtos(id)'))

    # 4. Drop old tables (child before parent)
    op.drop_index('ix_estoque_produtos_nome', table_name='estoque_produtos')
    op.drop_index('ix_estoque_produtos_tenant_id', table_name='estoque_produtos')
    op.drop_table('estoque_produtos')
    op.drop_index('ix_estoque_categorias_tenant_id', table_name='estoque_categorias')
    op.drop_table('estoque_categorias')


def downgrade() -> None:
    # Recreate old tables
    op.create_table('estoque_categorias',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('tenant_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('nome', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='estoque_categorias_tenant_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='estoque_categorias_pkey'),
    )
    op.create_index('ix_estoque_categorias_tenant_id', 'estoque_categorias', ['tenant_id'])

    op.create_table('estoque_produtos',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('tenant_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('categoria_id', sa.UUID(), autoincrement=False, nullable=True),
        sa.Column('nome', sa.VARCHAR(length=150), autoincrement=False, nullable=False),
        sa.Column('unidade_medida', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('codigo_interno', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('sku', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column('estoque_minimo', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('preco_medio', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('tipo_uso', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('ativo', sa.Boolean(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['categoria_id'], ['estoque_categorias.id'], name='estoque_produtos_categoria_id_fkey'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='estoque_produtos_tenant_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='estoque_produtos_pkey'),
    )
    op.create_index('ix_estoque_produtos_tenant_id', 'estoque_produtos', ['tenant_id'])
    op.create_index('ix_estoque_produtos_nome', 'estoque_produtos', ['nome'])

    # Drop catalog tables
    op.drop_index('ix_cadastros_produtos_estoque_produto_id', table_name='cadastros_produtos_estoque')
    op.drop_table('cadastros_produtos_estoque')
    op.drop_index('ix_cadastros_produtos_agricola_produto_id', table_name='cadastros_produtos_agricola')
    op.drop_table('cadastros_produtos_agricola')
    op.drop_index('ix_cadastros_produtos_tipo', table_name='cadastros_produtos')
    op.drop_index('ix_cadastros_produtos_tenant_id', table_name='cadastros_produtos')
    op.drop_index('ix_cadastros_produtos_nome', table_name='cadastros_produtos')
    op.drop_index('ix_cadastros_produtos_codigo_interno', table_name='cadastros_produtos')
    op.drop_table('cadastros_produtos')
