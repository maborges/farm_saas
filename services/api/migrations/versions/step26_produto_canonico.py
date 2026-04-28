"""step26: add canonical product fields to insumos_operacao and pec_manejos_lote

Revision ID: step26_produto_canonico
Revises: step25_drop_movimentacoes
Create Date: 2026-04-28
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "step26_produto_canonico"
down_revision = "step25_drop_movimentacoes"
branch_labels = None
depends_on = None


def upgrade():
    # insumos_operacao — campos canônicos aditivos
    op.add_column(
        "insumos_operacao",
        sa.Column("lote_estoque_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "insumos_operacao",
        sa.Column("unidade_medida_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_insumos_operacao_lote_estoque",
        "insumos_operacao", "estoque_lotes",
        ["lote_estoque_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_insumos_operacao_unidade_medida",
        "insumos_operacao", "unidades_medida",
        ["unidade_medida_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_insumos_operacao_lote_estoque_id", "insumos_operacao", ["lote_estoque_id"])

    # pec_manejos_lote — vínculo ao catálogo de produtos
    op.add_column(
        "pec_manejos_lote",
        sa.Column("produto_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_pec_manejos_lote_produto",
        "pec_manejos_lote", "cadastros_produtos",
        ["produto_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_pec_manejos_lote_produto_id", "pec_manejos_lote", ["produto_id"])


def downgrade():
    op.drop_index("ix_pec_manejos_lote_produto_id", table_name="pec_manejos_lote")
    op.drop_constraint("fk_pec_manejos_lote_produto", "pec_manejos_lote", type_="foreignkey")
    op.drop_column("pec_manejos_lote", "produto_id")

    op.drop_index("ix_insumos_operacao_lote_estoque_id", table_name="insumos_operacao")
    op.drop_constraint("fk_insumos_operacao_unidade_medida", "insumos_operacao", type_="foreignkey")
    op.drop_constraint("fk_insumos_operacao_lote_estoque", "insumos_operacao", type_="foreignkey")
    op.drop_column("insumos_operacao", "unidade_medida_id")
    op.drop_column("insumos_operacao", "lote_estoque_id")
