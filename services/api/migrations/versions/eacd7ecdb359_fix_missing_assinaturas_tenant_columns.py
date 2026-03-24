"""fix_missing_assinaturas_tenant_columns

Revision ID: eacd7ecdb359
Revises: 4492badc2748
Create Date: 2026-03-16 21:29:09.042278

Corrige colunas ausentes em assinaturas_tenant que deveriam ter sido
adicionadas pela migration 20240312_multi_sub mas não foram aplicadas.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eacd7ecdb359'
down_revision: Union[str, Sequence[str], None] = '4492badc2748'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona colunas grupo_fazendas_id e tipo_assinatura em assinaturas_tenant."""
    with op.batch_alter_table('assinaturas_tenant', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'grupo_fazendas_id',
                sa.UUID(as_uuid=True),
                sa.ForeignKey('grupos_fazendas.id', ondelete='CASCADE'),
                nullable=True,
                comment='Se NULL, assinatura principal do tenant. Se preenchido, assinatura específica do grupo.'
            )
        )
        batch_op.add_column(
            sa.Column(
                'tipo_assinatura',
                sa.String(20),
                nullable=False,
                server_default='PRINCIPAL',
                comment='PRINCIPAL (tenant inteiro), GRUPO (grupo específico), ADICIONAL (add-on de módulos)'
            )
        )


def downgrade() -> None:
    """Remove colunas adicionadas."""
    with op.batch_alter_table('assinaturas_tenant', schema=None) as batch_op:
        batch_op.drop_column('tipo_assinatura')
        batch_op.drop_column('grupo_fazendas_id')
