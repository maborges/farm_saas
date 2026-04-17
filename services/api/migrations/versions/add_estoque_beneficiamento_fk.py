"""Add estoque-beneficiamento bidirectional foreign keys

Revision ID: add_estoque_benef_fk
Revises: add_lote_benef_romaneios
Create Date: 2026-04-15

Integração: quando um lote beneficiado é armazenado, cria LoteEstoque.
LoteBeneficiamento.lote_estoque_id aponta para o lote criado em estoque.
LoteEstoque.lote_beneficiamento_id aponta de volta para rastreabilidade.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "add_estoque_benef_fk"
down_revision = "add_lote_benef_romaneios"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adiciona lote_estoque_id em cafe_lotes_beneficiamento
    op.add_column(
        "cafe_lotes_beneficiamento",
        sa.Column(
            "lote_estoque_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("estoque_lotes.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
            comment="FK para LoteEstoque criado ao armazenar"
        )
    )

    # Adiciona lote_beneficiamento_id em estoque_lotes
    op.add_column(
        "estoque_lotes",
        sa.Column(
            "lote_beneficiamento_id",
            PGUUID(as_uuid=True),
            nullable=True,
            index=True,
            comment="FK rastreabilidade: qual lote beneficiamento originou este estoque"
        )
    )


def downgrade() -> None:
    op.drop_column("estoque_lotes", "lote_beneficiamento_id")
    op.drop_column("cafe_lotes_beneficiamento", "lote_estoque_id")
