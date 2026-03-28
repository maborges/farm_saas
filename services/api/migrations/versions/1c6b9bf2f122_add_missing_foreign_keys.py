"""add_missing_foreign_keys

Revision ID: 1c6b9bf2f122
Revises: 08262413a4e2
Create Date: 2026-03-26 14:34:24.749648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c6b9bf2f122'
down_revision: Union[str, Sequence[str], None] = '08262413a4e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona foreign keys faltantes identificadas na auditoria."""

    # 1. frota_abastecimentos.fornecedor_id -> cadastros_pessoas.id
    with op.batch_alter_table('frota_abastecimentos', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'frota_abastecimentos_fornecedor_id_fkey',
            'cadastros_pessoas',
            ['fornecedor_id'],
            ['id'],
            ondelete='SET NULL'
        )

    # 2. frota_apontamentos_uso.talhao_id -> talhoes.id
    with op.batch_alter_table('frota_apontamentos_uso', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'frota_apontamentos_uso_talhao_id_fkey',
            'talhoes',
            ['talhao_id'],
            ['id'],
            ondelete='SET NULL'
        )

    # 3. frota_apontamentos_uso.operacao_id -> operacoes_agricolas.id
    # Nota: A tabela é operacoes_agricolas, não operacoes
    with op.batch_alter_table('frota_apontamentos_uso', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'frota_apontamentos_uso_operacao_id_fkey',
            'operacoes_agricolas',
            ['operacao_id'],
            ['id'],
            ondelete='SET NULL'
        )

    # 4. operacoes_agricolas.operador_id -> cadastros_pessoas.id
    with op.batch_alter_table('operacoes_agricolas', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'operacoes_agricolas_operador_id_fkey',
            'cadastros_pessoas',
            ['operador_id'],
            ['id'],
            ondelete='SET NULL'
        )

    # 5. rh_empreitadas.safra_id -> safras.id
    with op.batch_alter_table('rh_empreitadas', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'rh_empreitadas_safra_id_fkey',
            'safras',
            ['safra_id'],
            ['id'],
            ondelete='CASCADE'
        )

    # 6. rh_lancamentos_diarias.safra_id -> safras.id
    with op.batch_alter_table('rh_lancamentos_diarias', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'rh_lancamentos_diarias_safra_id_fkey',
            'safras',
            ['safra_id'],
            ['id'],
            ondelete='CASCADE'
        )

    # 7. romaneios_colheita.operador_id -> cadastros_pessoas.id
    with op.batch_alter_table('romaneios_colheita', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'romaneios_colheita_operador_id_fkey',
            'cadastros_pessoas',
            ['operador_id'],
            ['id'],
            ondelete='SET NULL'
        )


def downgrade() -> None:
    """Remove foreign keys adicionadas."""

    # Remove na ordem inversa
    with op.batch_alter_table('romaneios_colheita', schema=None) as batch_op:
        batch_op.drop_constraint('romaneios_colheita_operador_id_fkey', type_='foreignkey')

    with op.batch_alter_table('rh_lancamentos_diarias', schema=None) as batch_op:
        batch_op.drop_constraint('rh_lancamentos_diarias_safra_id_fkey', type_='foreignkey')

    with op.batch_alter_table('rh_empreitadas', schema=None) as batch_op:
        batch_op.drop_constraint('rh_empreitadas_safra_id_fkey', type_='foreignkey')

    with op.batch_alter_table('operacoes_agricolas', schema=None) as batch_op:
        batch_op.drop_constraint('operacoes_agricolas_operador_id_fkey', type_='foreignkey')

    with op.batch_alter_table('frota_apontamentos_uso', schema=None) as batch_op:
        batch_op.drop_constraint('frota_apontamentos_uso_operacao_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('frota_apontamentos_uso_talhao_id_fkey', type_='foreignkey')

    with op.batch_alter_table('frota_abastecimentos', schema=None) as batch_op:
        batch_op.drop_constraint('frota_abastecimentos_fornecedor_id_fkey', type_='foreignkey')
