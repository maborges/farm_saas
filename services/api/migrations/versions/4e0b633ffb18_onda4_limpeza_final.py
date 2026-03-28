"""onda4_limpeza_final

Revision ID: 4e0b633ffb18
Revises: 3a5b2924aad1
Create Date: 2026-03-24 23:20:32.789504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e0b633ffb18'
down_revision: Union[str, Sequence[str], None] = '3a5b2924aad1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # rh_colaboradores — nova estrutura normalizada (pessoa_id FK, sem nome/cpf)
    op.create_table('rh_colaboradores',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('tenant_id', sa.Uuid(), nullable=False),
    sa.Column('fazenda_id', sa.Uuid(), nullable=True),
    sa.Column('pessoa_id', sa.Uuid(), nullable=False),
    sa.Column('cargo', sa.String(length=100), nullable=True),
    sa.Column('tipo_contrato', sa.String(length=20), nullable=False, comment='CLT | DIARISTA | EMPREITEIRO | TERCEIRO | PJ'),
    sa.Column('valor_diaria', sa.Float(), nullable=True),
    sa.Column('valor_hora', sa.Float(), nullable=True),
    sa.Column('data_admissao', sa.Date(), nullable=True),
    sa.Column('data_demissao', sa.Date(), nullable=True),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.Column('observacoes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['pessoa_id'], ['cadastros_pessoas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('rh_colaboradores', schema=None) as batch_op:
        batch_op.create_index('ix_rh_colaboradores_fazenda_id', ['fazenda_id'], unique=False)
        batch_op.create_index('ix_rh_colaboradores_pessoa_id', ['pessoa_id'], unique=False)
        batch_op.create_index('ix_rh_colaboradores_tenant_id', ['tenant_id'], unique=False)

    op.create_table('rh_lancamentos_diarias',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('tenant_id', sa.Uuid(), nullable=False),
    sa.Column('colaborador_id', sa.Uuid(), nullable=False),
    sa.Column('fazenda_id', sa.Uuid(), nullable=True),
    sa.Column('safra_id', sa.Uuid(), nullable=True),
    sa.Column('data', sa.Date(), nullable=False),
    sa.Column('horas_trabalhadas', sa.Float(), nullable=False),
    sa.Column('atividade', sa.String(length=100), nullable=False, comment='PLANTIO | COLHEITA | CAPINA | MANUTENCAO | IRRIGACAO | GERAL'),
    sa.Column('valor_diaria', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False, comment='PENDENTE | PAGO'),
    sa.Column('data_pagamento', sa.Date(), nullable=True),
    sa.Column('observacoes', sa.String(length=300), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['colaborador_id'], ['rh_colaboradores.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('rh_lancamentos_diarias', schema=None) as batch_op:
        batch_op.create_index('ix_rh_lancamentos_diarias_colaborador_id', ['colaborador_id'], unique=False)
        batch_op.create_index('ix_rh_lancamentos_diarias_tenant_id', ['tenant_id'], unique=False)

    op.create_table('rh_empreitadas',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('tenant_id', sa.Uuid(), nullable=False),
    sa.Column('colaborador_id', sa.Uuid(), nullable=False),
    sa.Column('fazenda_id', sa.Uuid(), nullable=True),
    sa.Column('safra_id', sa.Uuid(), nullable=True),
    sa.Column('descricao', sa.String(length=300), nullable=False),
    sa.Column('unidade', sa.String(length=30), nullable=False, comment='HECTARE | SACA | HORA | UNIDADE | METRO'),
    sa.Column('quantidade', sa.Float(), nullable=False),
    sa.Column('valor_unitario', sa.Float(), nullable=False),
    sa.Column('valor_total', sa.Float(), nullable=False),
    sa.Column('data_inicio', sa.Date(), nullable=False),
    sa.Column('data_fim', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False, comment='ABERTA | CONCLUIDA | PAGA | CANCELADA'),
    sa.Column('data_pagamento', sa.Date(), nullable=True),
    sa.Column('observacoes', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['colaborador_id'], ['rh_colaboradores.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['fazenda_id'], ['fazendas.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('rh_empreitadas', schema=None) as batch_op:
        batch_op.create_index('ix_rh_empreitadas_colaborador_id', ['colaborador_id'], unique=False)
        batch_op.create_index('ix_rh_empreitadas_tenant_id', ['tenant_id'], unique=False)

    # Migrar dados de talhoes → cadastros_areas_rurais antes de recriar FKs
    op.execute("""
        INSERT INTO cadastros_areas_rurais (
            id, tenant_id, fazenda_id, tipo, nome, codigo,
            area_hectares, area_hectares_manual, geometria,
            ativo, created_at, updated_at
        )
        SELECT
            id, tenant_id, fazenda_id,
            'TALHAO' AS tipo,
            nome, codigo,
            area_ha AS area_hectares,
            area_ha_manual AS area_hectares_manual,
            geometria::jsonb AS geometria,
            ativo, created_at, updated_at
        FROM talhoes
        ON CONFLICT (id) DO NOTHING
    """)

    with op.batch_alter_table('fin_rateios', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fin_rateios_talhao_id_fkey'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'cadastros_areas_rurais', ['talhao_id'], ['id'], ondelete='SET NULL')

    with op.batch_alter_table('monitoramento_pragas', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('monitoramento_pragas_talhao_id_fkey'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'cadastros_areas_rurais', ['talhao_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('operacoes_agricolas', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('operacoes_agricolas_talhao_id_fkey'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'cadastros_areas_rurais', ['talhao_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('previsoes_produtividade', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('previsoes_produtividade_talhao_id_fkey'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'cadastros_areas_rurais', ['talhao_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('romaneios_colheita', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('romaneios_colheita_talhao_id_fkey'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'cadastros_areas_rurais', ['talhao_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('safras', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('safras_talhao_id_fkey'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'cadastros_areas_rurais', ['talhao_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('safras', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('safras_talhao_id_fkey'), 'talhoes', ['talhao_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('romaneios_colheita', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('romaneios_colheita_talhao_id_fkey'), 'talhoes', ['talhao_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('previsoes_produtividade', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('previsoes_produtividade_talhao_id_fkey'), 'talhoes', ['talhao_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('operacoes_agricolas', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('operacoes_agricolas_talhao_id_fkey'), 'talhoes', ['talhao_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('monitoramento_pragas', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('monitoramento_pragas_talhao_id_fkey'), 'talhoes', ['talhao_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('fin_rateios', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fin_rateios_talhao_id_fkey'), 'talhoes', ['talhao_id'], ['id'], ondelete='SET NULL')

    with op.batch_alter_table('rh_lancamentos_diarias', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_rh_lancamentos_diarias_tenant_id'))
        batch_op.drop_index(batch_op.f('ix_rh_lancamentos_diarias_colaborador_id'))

    op.drop_table('rh_lancamentos_diarias')
    with op.batch_alter_table('rh_empreitadas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_rh_empreitadas_tenant_id'))
        batch_op.drop_index(batch_op.f('ix_rh_empreitadas_colaborador_id'))

    op.drop_table('rh_empreitadas')
    with op.batch_alter_table('rh_colaboradores', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_rh_colaboradores_tenant_id'))
        batch_op.drop_index(batch_op.f('ix_rh_colaboradores_pessoa_id'))
        batch_op.drop_index(batch_op.f('ix_rh_colaboradores_fazenda_id'))

    op.drop_table('rh_colaboradores')
    # ### end Alembic commands ###
