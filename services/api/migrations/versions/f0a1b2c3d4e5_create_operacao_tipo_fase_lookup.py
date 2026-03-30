"""Create lookup table: agricola_operacao_tipo_fase

Revision ID: f0a1b2c3d4e5
Revises: ecf09d50d6de
Create Date: 2026-03-30 18:45:00.000000

Cria tabela de lookup para validar que operação agrícola só é permitida em fases específicas.
Exemplo:
- PLANTIO → permitido em [PLANTIO, DESENVOLVIMENTO]
- COLHEITA → permitido em [COLHEITA]

Usa campos genéricos origem_id + origem_tipo já existentes em fin_despesas e fin_receitas.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = 'ecf09d50d6de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create agricola_operacao_tipo_fase lookup table."""

    op.create_table('agricola_operacao_tipo_fase',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tipo_operacao', sa.String(length=30), nullable=False, unique=True),
        sa.Column('fases_permitidas', sa.JSON(), nullable=False, comment='Lista de fases permitidas: ["PLANTIO", "DESENVOLVIMENTO"]'),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tipo_operacao')
    )

    op.create_index(
        'idx_operacao_tipo_fase_tipo',
        'agricola_operacao_tipo_fase',
        ['tipo_operacao'],
        unique=True
    )

    # Seed inicial de dados (tipos de operação comuns)
    op.execute("""
        INSERT INTO agricola_operacao_tipo_fase (id, tipo_operacao, fases_permitidas, descricao)
        VALUES
            (gen_random_uuid(), 'PLANTIO', '["PLANTIO", "DESENVOLVIMENTO"]'::jsonb, 'Semeadura e plantio'),
            (gen_random_uuid(), 'ADUBAÇÃO', '["PREPARO_SOLO", "DESENVOLVIMENTO"]'::jsonb, 'Adubação de cobertura'),
            (gen_random_uuid(), 'PULVERIZAÇÃO', '["DESENVOLVIMENTO", "COLHEITA"]'::jsonb, 'Aplicação de defensivos'),
            (gen_random_uuid(), 'COLHEITA', '["COLHEITA"]'::jsonb, 'Colheita manual ou mecanizada'),
            (gen_random_uuid(), 'OPERAÇÃO_MECANIZADA', '["PLANTIO", "DESENVOLVIMENTO"]'::jsonb, 'Operações gerais de máquina'),
            (gen_random_uuid(), 'PREPARO_SOLO', '["PREPARO_SOLO"]'::jsonb, 'Aração, gradagem, subsolagem'),
            (gen_random_uuid(), 'CALAGEM', '["PREPARO_SOLO"]'::jsonb, 'Aplicação de calcário'),
            (gen_random_uuid(), 'IRRIGAÇÃO', '["DESENVOLVIMENTO", "COLHEITA"]'::jsonb, 'Sistema de irrigação')
    """)


def downgrade() -> None:
    """Revert: drop table."""

    op.drop_index('idx_operacao_tipo_fase_tipo', table_name='agricola_operacao_tipo_fase')
    op.drop_table('agricola_operacao_tipo_fase')
