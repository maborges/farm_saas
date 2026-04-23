"""step13 — analise_solo upgrade: micronutrientes, irrigacao, manejo, cultura, validade

Revision ID: step13_analise_solo_upgrade
Revises: step12_safra_tarefas
Create Date: 2026-04-21
"""

from alembic import op
import sqlalchemy as sa

revision = "step13_analise_solo_upgrade"
down_revision = "step12_safra_tarefas"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("analises_solo", schema="farms") as batch_op:
        # Micronutrientes
        batch_op.add_column(sa.Column("zinco_zn",    sa.Numeric(8, 3), nullable=True, comment="mg/dm³"))
        batch_op.add_column(sa.Column("boro_b",      sa.Numeric(8, 3), nullable=True, comment="mg/dm³"))
        batch_op.add_column(sa.Column("ferro_fe",    sa.Numeric(8, 3), nullable=True, comment="mg/dm³"))
        batch_op.add_column(sa.Column("manganes_mn", sa.Numeric(8, 3), nullable=True, comment="mg/dm³"))

        # Saturação por Alumínio (m%)
        batch_op.add_column(sa.Column("saturacao_al_m_pct", sa.Numeric(5, 2), nullable=True, comment="m% = Al / CTC × 100"))

        # Contexto agronômico
        batch_op.add_column(sa.Column("tipo_irrigacao",  sa.String(20),  nullable=True, comment="SEQUEIRO | GOTEJAMENTO | PIVO_CENTRAL | ASPERSAO | SULCO"))
        batch_op.add_column(sa.Column("sistema_manejo",  sa.String(20),  nullable=True, comment="PLANTIO_DIRETO | CONVENCIONAL | MINIMO"))
        batch_op.add_column(sa.Column("cultura_nome",    sa.String(100), nullable=True, comment="Nome da cultura vinculada à análise"))
        batch_op.add_column(sa.Column("cultura_anterior",sa.String(100), nullable=True, comment="Cultura plantada anteriormente no talhão"))

        # Validade
        batch_op.add_column(sa.Column("validade_meses", sa.Integer(), nullable=True, server_default="12", comment="Meses de validade da análise"))

        # Observações do agrônomo
        batch_op.add_column(sa.Column("observacoes", sa.Text(), nullable=True))

    op.execute("COMMIT")


def downgrade():
    with op.batch_alter_table("analises_solo", schema="farms") as batch_op:
        for col in [
            "zinco_zn", "boro_b", "ferro_fe", "manganes_mn",
            "saturacao_al_m_pct", "tipo_irrigacao", "sistema_manejo",
            "cultura_nome", "cultura_anterior", "validade_meses", "observacoes",
        ]:
            batch_op.drop_column(col)
