"""Add romaneio_id and detailed loss fields to cafe_lotes_beneficiamento

Revision ID: add_beneficiamento_romaneio_perdas
Revises: step3_fix_prescricoes_vra
Create Date: 2026-04-15

Adiciona campos para rastreabilidade e rendimento detalhado:
- romaneio_id: FK para romaneios_colheita
- perda_secagem_kg: Perda durante secagem
- perda_quebra_kg: Grãos quebrados
- perda_defeito_kg: Grãos defeituosos
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "benef_romaneio_perdas"
down_revision = ("add_fornecedor_fields", "add_planejada_pulv")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cafe_lotes_beneficiamento",
        sa.Column(
            "romaneio_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("romaneios_colheita.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
            comment="FK para rastreabilidade: qual romaneio originou este lote"
        )
    )
    op.add_column(
        "cafe_lotes_beneficiamento",
        sa.Column(
            "perda_secagem_kg",
            sa.Numeric(10, 3),
            nullable=True,
            comment="Perda de peso durante secagem (kg)"
        )
    )
    op.add_column(
        "cafe_lotes_beneficiamento",
        sa.Column(
            "perda_quebra_kg",
            sa.Numeric(10, 3),
            nullable=True,
            comment="Grãos quebrados descartados (kg)"
        )
    )
    op.add_column(
        "cafe_lotes_beneficiamento",
        sa.Column(
            "perda_defeito_kg",
            sa.Numeric(10, 3),
            nullable=True,
            comment="Grãos defeituosos descartados (kg)"
        )
    )


def downgrade() -> None:
    op.drop_column("cafe_lotes_beneficiamento", "perda_defeito_kg")
    op.drop_column("cafe_lotes_beneficiamento", "perda_quebra_kg")
    op.drop_column("cafe_lotes_beneficiamento", "perda_secagem_kg")
    op.drop_column("cafe_lotes_beneficiamento", "romaneio_id")
