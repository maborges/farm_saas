"""Add fornecedor fields: email, telefone, condicoes_pagamento, prazo_entrega_dias, avaliacao

Revision ID: add_fornecedor_fields
Revises: step3_fix_prescricoes_vra
Create Date: 2026-04-14

Adiciona campos ao modelo Fornecedor:
- email
- telefone
- condicoes_pagamento
- prazo_entrega_dias
- avaliacao
"""

from alembic import op
import sqlalchemy as sa

revision = "add_fornecedor_fields"
down_revision = "step3_fix_prescricoes_vra"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('compras_fornecedores', sa.Column('email', sa.String(100), nullable=True))
    op.add_column('compras_fornecedores', sa.Column('telefone', sa.String(20), nullable=True))
    op.add_column('compras_fornecedores', sa.Column('condicoes_pagamento', sa.String(100), nullable=True))
    op.add_column('compras_fornecedores', sa.Column('prazo_entrega_dias', sa.Integer(), nullable=True))
    op.add_column('compras_fornecedores', sa.Column('avaliacao', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('compras_fornecedores', 'avaliacao')
    op.drop_column('compras_fornecedores', 'prazo_entrega_dias')
    op.drop_column('compras_fornecedores', 'condicoes_pagamento')
    op.drop_column('compras_fornecedores', 'telefone')
    op.drop_column('compras_fornecedores', 'email')
