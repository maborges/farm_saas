"""cadastro_propriedade_completo

Revision ID: 574378e90967
Revises: add_arquivos_geo
Create Date: 2026-04-04 04:05:14.906403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '574378e90967'
down_revision: Union[str, Sequence[str], None] = 'add_arquivos_geo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renomear cnpj → cpf_cnpj
    op.alter_column('fazendas', 'cnpj', new_column_name='cpf_cnpj')

    # Adicionar campos fiscais/geográficos
    op.add_column('fazendas', sa.Column('codigo_car', sa.String(50), nullable=True))
    op.add_column('fazendas', sa.Column('nirf', sa.String(20), nullable=True))
    op.add_column('fazendas', sa.Column('uf', sa.String(2), nullable=True))
    op.add_column('fazendas', sa.Column('municipio', sa.String(100), nullable=True))
    op.add_column('fazendas', sa.Column('area_aproveitavel_ha', sa.Numeric(12, 4), nullable=True))
    op.add_column('fazendas', sa.Column('area_app_ha', sa.Numeric(12, 4), nullable=True))
    op.add_column('fazendas', sa.Column('area_rl_ha', sa.Numeric(12, 4), nullable=True))

    # Converter area_total_ha de Float para Numeric
    op.alter_column(
        'fazendas', 'area_total_ha',
        type_=sa.Numeric(12, 4),
        postgresql_using='area_total_ha::numeric(12,4)',
        existing_type=sa.Float(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.drop_column('fazendas', 'area_rl_ha')
    op.drop_column('fazendas', 'area_app_ha')
    op.drop_column('fazendas', 'area_aproveitavel_ha')
    op.drop_column('fazendas', 'municipio')
    op.drop_column('fazendas', 'uf')
    op.drop_column('fazendas', 'nirf')
    op.drop_column('fazendas', 'codigo_car')
    op.alter_column('fazendas', 'cpf_cnpj', new_column_name='cnpj')
    op.alter_column(
        'fazendas', 'area_total_ha',
        type_=sa.Float(),
        existing_type=sa.Numeric(12, 4),
        existing_nullable=True,
    )
