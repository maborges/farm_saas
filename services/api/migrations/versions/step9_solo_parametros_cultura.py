"""step9: add v_meta_pct_padrao to cadastros_culturas + create solo_parametros_cultura

Revision ID: step9_solo_parametros_cultura
Revises: step8_add_cultivo_to_harvest_processing
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa

revision = "step9_solo_parametros_cultura"
down_revision = "step8_add_cultivo_to_harvest"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Campo v_meta_pct_padrao em cadastros_culturas
    with op.batch_alter_table("cadastros_culturas") as batch:
        batch.add_column(sa.Column("v_meta_pct_padrao", sa.Numeric(5, 1), nullable=True,
                                   comment="V% meta padrão para calagem desta cultura"))

    # 2. Nova tabela solo_parametros_cultura
    op.create_table(
        "solo_parametros_cultura",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("cultura_id", sa.Uuid(), sa.ForeignKey("cadastros_culturas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True,
                  comment="NULL = padrão do sistema"),
        sa.Column("regiao", sa.String(50), nullable=True,
                  comment="CERRADO | SUL | NORDESTE | SUDESTE | NORTE | null=geral"),
        sa.Column("parametro", sa.String(20), nullable=False,
                  comment="FOSFORO | POTASSIO | PH | NITROGENIO | CALCARIO"),
        sa.Column("faixa_min", sa.Numeric(8, 2), nullable=False),
        sa.Column("faixa_max", sa.Numeric(8, 2), nullable=True,
                  comment="NULL = sem limite superior"),
        sa.Column("classificacao", sa.String(20), nullable=False,
                  comment="MUITO_BAIXO | BAIXO | MEDIO | ALTO | MUITO_ALTO"),
        sa.Column("rec_dose_kg_ha", sa.Numeric(8, 2), nullable=True),
        sa.Column("obs", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    op.create_index(
        "ix_solo_params_cultura_lookup",
        "solo_parametros_cultura",
        ["cultura_id", "tenant_id", "parametro", "regiao"],
    )


def downgrade():
    op.drop_table("solo_parametros_cultura")
    with op.batch_alter_table("cadastros_culturas") as batch:
        batch.drop_column("v_meta_pct_padrao")
