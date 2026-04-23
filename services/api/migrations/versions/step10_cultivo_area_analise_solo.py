"""step10: add analise_solo fields to cultivo_areas

Revision ID: step10_cultivo_area_analise_solo
Revises: step9_solo_parametros_cultura
Create Date: 2026-04-20
"""
from alembic import op
import sqlalchemy as sa

revision = "step10_cultivo_area_analise_solo"
down_revision = "step9_solo_parametros_cultura"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("cultivo_areas") as batch:
        batch.add_column(sa.Column(
            "analise_solo_id", sa.Uuid(), nullable=True,
            comment="FK para analise selecionada para este talhão/cultivo"
        ))
        batch.add_column(sa.Column(
            "regiao_analise", sa.String(50), nullable=True,
            comment="Região para lookup de parâmetros: CERRADO | SUL | NORDESTE | SUDESTE | NORTE"
        ))
        batch.add_column(sa.Column(
            "analise_status", sa.String(20), nullable=False,
            server_default="NAO_SELECIONADA",
            comment="NAO_SELECIONADA | SELECIONADA | REJEITADA"
        ))
        batch.create_foreign_key(
            "fk_cultivo_areas_analise_solo",
            "analises_solo",
            ["analise_solo_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_index(
        "ix_cultivo_areas_analise_solo_id",
        "cultivo_areas",
        ["tenant_id", "analise_solo_id"],
    )
    op.create_index(
        "ix_cultivo_areas_analise_status",
        "cultivo_areas",
        ["tenant_id", "analise_status"],
    )


def downgrade():
    op.drop_index("ix_cultivo_areas_analise_status", "cultivo_areas")
    op.drop_index("ix_cultivo_areas_analise_solo_id", "cultivo_areas")
    with op.batch_alter_table("cultivo_areas") as batch:
        batch.drop_constraint("fk_cultivo_areas_analise_solo", type_="foreignkey")
        batch.drop_column("analise_status")
        batch.drop_column("regiao_analise")
        batch.drop_column("analise_solo_id")
