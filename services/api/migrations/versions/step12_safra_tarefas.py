"""create safra_tarefas table

Revision ID: step12_safra_tarefas
Revises: step11_remove_safra_talhao_id
Create Date: 2026-04-21
"""
from alembic import op
import sqlalchemy as sa

revision = "step12_safra_tarefas"
down_revision = "step11_remove_safra_talhao_id"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "safra_tarefas",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("safra_id", sa.UUID(), nullable=False),
        sa.Column("talhao_id", sa.UUID(), nullable=True),
        sa.Column("cultivo_area_id", sa.UUID(), nullable=True),
        sa.Column("analise_solo_id", sa.UUID(), nullable=True),
        sa.Column("origem", sa.String(20), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("descricao", sa.String(300), nullable=False),
        sa.Column("obs", sa.Text(), nullable=True),
        sa.Column("prioridade", sa.String(10), nullable=False, server_default="MEDIA"),
        sa.Column("status", sa.String(25), nullable=False, server_default="PENDENTE_APROVACAO"),
        sa.Column("dose_estimada_kg_ha", sa.Numeric(12, 4), nullable=True),
        sa.Column("quantidade_total_estimada_kg", sa.Numeric(14, 2), nullable=True),
        sa.Column("area_ha", sa.Numeric(10, 2), nullable=True),
        sa.Column("custo_estimado", sa.Numeric(15, 2), nullable=True),
        sa.Column("data_prevista", sa.Date(), nullable=True),
        sa.Column("aprovado_por", sa.UUID(), nullable=True),
        sa.Column("aprovado_em", sa.DateTime(), nullable=True),
        sa.Column("operacao_id", sa.UUID(), nullable=True),
        sa.Column("concluida_em", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["safra_id"], ["safras.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["talhao_id"], ["cadastros_areas_rurais.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["cultivo_area_id"], ["cultivo_areas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["analise_solo_id"], ["analises_solo.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["operacao_id"], ["operacoes_agricolas.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_safra_tarefas_tenant_id", "safra_tarefas", ["tenant_id"])
    op.create_index("ix_safra_tarefas_safra_id", "safra_tarefas", ["safra_id"])
    op.create_index("ix_safra_tarefas_status", "safra_tarefas", ["status"])
    op.create_index("ix_safra_tarefas_talhao", "safra_tarefas", ["talhao_id"])
    op.create_index("ix_safra_tarefas_tenant_safra_status", "safra_tarefas", ["tenant_id", "safra_id", "status"])

    # Adicionar tarefa_id em operacoes_agricolas
    op.add_column("operacoes_agricolas", sa.Column("tarefa_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_operacoes_tarefa_id",
        "operacoes_agricolas", "safra_tarefas",
        ["tarefa_id"], ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint("fk_operacoes_tarefa_id", "operacoes_agricolas", type_="foreignkey")
    op.drop_column("operacoes_agricolas", "tarefa_id")
    op.drop_index("ix_safra_tarefas_tenant_safra_status", "safra_tarefas")
    op.drop_index("ix_safra_tarefas_talhao", "safra_tarefas")
    op.drop_index("ix_safra_tarefas_status", "safra_tarefas")
    op.drop_index("ix_safra_tarefas_safra_id", "safra_tarefas")
    op.drop_index("ix_safra_tarefas_tenant_id", "safra_tarefas")
    op.drop_table("safra_tarefas")
