"""step1b: fix remaining FKs pointing to talhoes

Revision ID: step1b_fix_remaining_fks
Revises: step1_talhoes_consolidation
Create Date: 2026-04-06

Reponteira as FKs de frota_apontamentos_uso e relatorios_tecnicos
de talhoes.id para cadastros_areas_rurais.id.
"""

from alembic import op
import sqlalchemy as sa

revision = "step1b_fix_remaining_fks"
down_revision = "step1_talhoes_consolidation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # frota_apontamentos_uso
    op.drop_constraint("frota_apontamentos_uso_talhao_id_fkey", "frota_apontamentos_uso", type_="foreignkey")
    op.create_foreign_key(
        "frota_apontamentos_uso_talhao_id_fkey",
        "frota_apontamentos_uso", "cadastros_areas_rurais",
        ["talhao_id"], ["id"],
        ondelete="SET NULL",
    )

    # relatorios_tecnicos
    op.drop_constraint("relatorios_tecnicos_talhao_id_fkey", "relatorios_tecnicos", type_="foreignkey")
    op.create_foreign_key(
        "relatorios_tecnicos_talhao_id_fkey",
        "relatorios_tecnicos", "cadastros_areas_rurais",
        ["talhao_id"], ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("frota_apontamentos_uso_talhao_id_fkey", "frota_apontamentos_uso", type_="foreignkey")
    op.create_foreign_key(
        "frota_apontamentos_uso_talhao_id_fkey",
        "frota_apontamentos_uso", "talhoes",
        ["talhao_id"], ["id"],
        ondelete="SET NULL",
    )

    op.drop_constraint("relatorios_tecnicos_talhao_id_fkey", "relatorios_tecnicos", type_="foreignkey")
    op.create_foreign_key(
        "relatorios_tecnicos_talhao_id_fkey",
        "relatorios_tecnicos", "talhoes",
        ["talhao_id"], ["id"],
        ondelete="CASCADE",
    )
