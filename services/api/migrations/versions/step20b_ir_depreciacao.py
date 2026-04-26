"""step20b: IR e depreciação nos cenários de safra

Revision ID: step20b_ir_depreciacao
Revises: step20_safra_cenarios
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa

revision = "step20b_ir_depreciacao"
down_revision = "step20_safra_cenarios"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # safra_cenarios — campos de IR e depreciação a nível de cenário
    with op.batch_alter_table("safra_cenarios") as batch:
        batch.add_column(sa.Column("depreciacao_total", sa.Numeric(18, 2), nullable=True))
        batch.add_column(sa.Column("ir_aliquota_pct", sa.Numeric(5, 2), nullable=True))
        batch.add_column(sa.Column("ir_valor_total", sa.Numeric(18, 2), nullable=True))

    # safra_cenarios_unidades — depreciação e IR por unidade produtiva
    with op.batch_alter_table("safra_cenarios_unidades") as batch:
        batch.add_column(sa.Column("depreciacao_ha", sa.Numeric(14, 2), nullable=True))
        batch.add_column(sa.Column("depreciacao_total", sa.Numeric(18, 2), nullable=True))
        batch.add_column(sa.Column("ir_valor", sa.Numeric(18, 2), nullable=True))

    op.execute("COMMIT")


def downgrade() -> None:
    with op.batch_alter_table("safra_cenarios_unidades") as batch:
        batch.drop_column("ir_valor")
        batch.drop_column("depreciacao_total")
        batch.drop_column("depreciacao_ha")

    with op.batch_alter_table("safra_cenarios") as batch:
        batch.drop_column("ir_valor_total")
        batch.drop_column("ir_aliquota_pct")
        batch.drop_column("depreciacao_total")
