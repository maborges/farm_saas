"""step20: safra_cenarios e safra_cenarios_unidades

Revision ID: step20_safra_cenarios
Revises: step19_cost_allocations
Create Date: 2026-04-24

Tabelas de análise de cenários econômicos por ProductionUnit.
Sem backfill automático — cenários BASE são criados on-demand pelo service.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "step20_safra_cenarios"
down_revision: Union[str, Sequence[str], None] = "step19_cost_allocations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "safra_cenarios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("safra_id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("tipo", sa.String(20), nullable=False, server_default=sa.text("'CUSTOM'")),
        sa.Column("eh_base", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'ATIVO'")),
        sa.Column("unidade_medida_id", sa.Uuid(), nullable=True),
        sa.Column("produtividade_default", sa.Numeric(10, 3), nullable=True),
        sa.Column("preco_default", sa.Numeric(14, 4), nullable=True),
        sa.Column("custo_ha_default", sa.Numeric(14, 2), nullable=True),
        sa.Column("fator_custo_pct", sa.Numeric(6, 4), nullable=True),
        sa.Column("area_total_ha", sa.Numeric(12, 4), nullable=True),
        sa.Column("receita_bruta_total", sa.Numeric(18, 2), nullable=True),
        sa.Column("custo_total", sa.Numeric(18, 2), nullable=True),
        sa.Column("margem_contribuicao_total", sa.Numeric(18, 2), nullable=True),
        sa.Column("resultado_liquido_total", sa.Numeric(18, 2), nullable=True),
        sa.Column("ponto_equilibrio_sc_ha", sa.Numeric(10, 3), nullable=True),
        sa.Column("calculado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_safra_cenarios_tenant_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["safra_id"], ["safras.id"], name="fk_safra_cenarios_safra_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["unidade_medida_id"], ["unidades_medida.id"], name="fk_safra_cenarios_unidade_medida_id", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "safra_id", "nome", name="uq_safra_cenarios_tenant_safra_nome"),
        sa.CheckConstraint("tipo IN ('BASE','OTIMISTA','PESSIMISTA','CUSTOM')", name="ck_safra_cenarios_tipo"),
        sa.CheckConstraint("status IN ('ATIVO','ARQUIVADO')", name="ck_safra_cenarios_status"),
        sa.CheckConstraint(
            "fator_custo_pct IS NULL OR (fator_custo_pct > 0 AND fator_custo_pct <= 2.0)",
            name="ck_safra_cenarios_fator_custo",
        ),
    )
    op.create_index("ix_safra_cenarios_tenant_safra", "safra_cenarios", ["tenant_id", "safra_id"])
    op.create_index(
        "uq_safra_cenarios_base_por_safra",
        "safra_cenarios",
        ["tenant_id", "safra_id"],
        unique=True,
        postgresql_where=sa.text("eh_base = true"),
    )

    op.create_table(
        "safra_cenarios_unidades",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("cenario_id", sa.Uuid(), nullable=False),
        sa.Column("production_unit_id", sa.Uuid(), nullable=False),
        sa.Column("unidade_medida_id", sa.Uuid(), nullable=True),
        sa.Column("cultivo_nome", sa.String(100), nullable=True),
        sa.Column("area_nome", sa.String(200), nullable=True),
        sa.Column("area_ha", sa.Numeric(12, 4), nullable=False),
        sa.Column("percentual_participacao", sa.Numeric(5, 2), nullable=False),
        sa.Column("produtividade_simulada", sa.Numeric(10, 3), nullable=True),
        sa.Column("preco_simulado", sa.Numeric(14, 4), nullable=True),
        sa.Column("custo_total_simulado_ha", sa.Numeric(14, 2), nullable=True),
        sa.Column("custo_base_fonte", sa.String(20), nullable=True),
        sa.Column("produtividade_efetiva", sa.Numeric(10, 3), nullable=True),
        sa.Column("preco_efetivo", sa.Numeric(14, 4), nullable=True),
        sa.Column("custo_ha_efetivo", sa.Numeric(14, 2), nullable=True),
        sa.Column("producao_total", sa.Numeric(14, 3), nullable=True),
        sa.Column("receita_bruta", sa.Numeric(18, 2), nullable=True),
        sa.Column("custo_total", sa.Numeric(18, 2), nullable=True),
        sa.Column("margem_contribuicao", sa.Numeric(18, 2), nullable=True),
        sa.Column("margem_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("resultado_liquido", sa.Numeric(18, 2), nullable=True),
        sa.Column("ponto_equilibrio", sa.Numeric(10, 3), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_safra_cenarios_unidades_tenant_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cenario_id"], ["safra_cenarios.id"], name="fk_safra_cenarios_unidades_cenario_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_unit_id"], ["production_units.id"], name="fk_safra_cenarios_unidades_pu_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["unidade_medida_id"], ["unidades_medida.id"], name="fk_safra_cenarios_unidades_uom_id", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cenario_id", "production_unit_id", name="uq_safra_cenarios_unidades_cenario_pu"),
        sa.CheckConstraint("area_ha > 0", name="ck_safra_cenarios_unidades_area_ha"),
        sa.CheckConstraint(
            "percentual_participacao > 0 AND percentual_participacao <= 100",
            name="ck_safra_cenarios_unidades_participacao",
        ),
        sa.CheckConstraint(
            "produtividade_simulada IS NULL OR produtividade_simulada > 0",
            name="ck_safra_cenarios_unidades_produtividade",
        ),
        sa.CheckConstraint(
            "preco_simulado IS NULL OR preco_simulado > 0",
            name="ck_safra_cenarios_unidades_preco",
        ),
        sa.CheckConstraint(
            "custo_total_simulado_ha IS NULL OR custo_total_simulado_ha >= 0",
            name="ck_safra_cenarios_unidades_custo",
        ),
        sa.CheckConstraint(
            "custo_base_fonte IS NULL OR custo_base_fonte IN ('REALIZADO','ORCADO','MANUAL')",
            name="ck_safra_cenarios_unidades_custo_fonte",
        ),
    )
    op.create_index("ix_safra_cenarios_unidades_cenario", "safra_cenarios_unidades", ["cenario_id"])
    op.create_index("ix_safra_cenarios_unidades_pu", "safra_cenarios_unidades", ["production_unit_id"])
    op.create_index("ix_safra_cenarios_unidades_tenant", "safra_cenarios_unidades", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("safra_cenarios_unidades")
    op.drop_table("safra_cenarios")
