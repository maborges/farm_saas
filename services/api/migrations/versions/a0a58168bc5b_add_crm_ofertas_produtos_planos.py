"""add_crm_ofertas_produtos_planos

Revision ID: a0a58168bc5b
Revises: 0a0db412c2c8
Create Date: 2026-03-27 22:15:13.416439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0a58168bc5b'
down_revision: Union[str, Sequence[str], None] = '0a0db412c2c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Tabela de produtos
    op.create_table('crm_produtos',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=True),
    sa.Column('categoria', sa.String(length=50), nullable=False),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.Column('posicao', sa.Integer(), nullable=False),
    sa.Column('icone', sa.String(length=50), nullable=True),
    sa.Column('features', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome'),
    sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_crm_produtos_nome'), 'crm_produtos', ['nome'], unique=False)
    op.create_index(op.f('ix_crm_produtos_slug'), 'crm_produtos', ['slug'], unique=False)

    # Tabela de precificação
    op.create_table('crm_precificacao_modulo',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('modulo_oferta_id', sa.Uuid(), nullable=False),
    sa.Column('preco_mensal', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('preco_anual', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('vigencia_inicio', sa.DateTime(timezone=True), nullable=False),
    sa.Column('vigencia_fim', sa.DateTime(timezone=True), nullable=True),
    sa.Column('condicoes', sa.JSON(), nullable=True),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['modulo_oferta_id'], ['crm_produtos.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('modulo_oferta_id', 'vigencia_inicio', name='uq_modulo_vigencia')
    )
    op.create_index(op.f('ix_crm_precificacao_modulo_modulo_oferta_id'), 'crm_precificacao_modulo', ['modulo_oferta_id'], unique=False)

    # Tabela de planos comerciais
    op.create_table('crm_planos_comerciais',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=True),
    sa.Column('tipo_oferta', sa.String(length=50), nullable=False),
    sa.Column('modulos_inclusos', sa.JSON(), nullable=False),
    sa.Column('preco_mensal_padrao', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('preco_anual_padrao', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('público_alvo', sa.String(length=100), nullable=True),
    sa.Column('tier', sa.Integer(), nullable=False),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.Column('posicao', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome'),
    sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_crm_planos_comerciais_nome'), 'crm_planos_comerciais', ['nome'], unique=False)
    op.create_index(op.f('ix_crm_planos_comerciais_slug'), 'crm_planos_comerciais', ['slug'], unique=False)

    # Tabela de ofertas personalizadas
    op.create_table('crm_ofertas_personalizadas',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('lead_id', sa.Uuid(), nullable=False),
    sa.Column('tipo_oferta', sa.String(length=50), nullable=False),
    sa.Column('plano_base_id', sa.Uuid(), nullable=True),
    sa.Column('modulos_selecionados', sa.JSON(), nullable=True),
    sa.Column('preco_total_mensal', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('preco_total_anual', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('desconto_percentual', sa.Float(), nullable=False),
    sa.Column('justificativa', sa.Text(), nullable=True),
    sa.Column('vigencia_inicio', sa.DateTime(timezone=True), nullable=False),
    sa.Column('vigencia_fim', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('observacoes', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['lead_id'], ['crm_leads.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['plano_base_id'], ['crm_planos_comerciais.id']),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_ofertas_personalizadas_lead_id'), 'crm_ofertas_personalizadas', ['lead_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
