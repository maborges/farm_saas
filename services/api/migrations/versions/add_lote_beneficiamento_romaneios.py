"""Add cafe_lote_beneficiamento_romaneios N:N table for multi-romaneio lotes

Revision ID: add_lote_benef_romaneios
Revises: benef_romaneio_perdas
Create Date: 2026-04-15

Permite que um LoteBeneficiamento seja formado por múltiplos Romaneios (blend).
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "add_lote_benef_romaneios"
down_revision = "benef_romaneio_perdas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cafe_lote_beneficiamento_romaneios",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column("tenant_id", PGUUID(as_uuid=True), nullable=False, index=True),
        sa.Column("lote_id", PGUUID(as_uuid=True), nullable=False, index=True),
        sa.Column("romaneio_id", PGUUID(as_uuid=True), nullable=False, index=True),
        sa.Column("peso_entrada_kg", sa.Numeric(12, 3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lote_id"], ["cafe_lotes_beneficiamento.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["romaneio_id"], ["romaneios_colheita.id"], ondelete="SET NULL"),
    )


def downgrade() -> None:
    op.drop_table("cafe_lote_beneficiamento_romaneios")
