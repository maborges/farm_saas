"""step2: drop tabela talhoes legada e remover router

Revision ID: step2_drop_talhoes
Revises: step1_talhoes_consolidation
Create Date: 2026-04-06

Estratégia Expand/Contract — Passo 2 (Contract):
  - Valida que todos os talhões foram migrados (step1 deve ter rodado)
  - Dropa a tabela `talhoes` legada
  - Executar APÓS validar step1 em produção

ATENÇÃO: Rodar somente após:
  1. step1 ter sido executado e validado
  2. Router /talhoes ter sido removido de main.py
  3. Services que importam `from agricola.talhoes` terem sido atualizados
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "step2_drop_talhoes"
down_revision = "step1b_fix_remaining_fks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Verifica se tabela ainda existe
    result = conn.execute(text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'talhoes')"
    ))
    if not result.scalar():
        print("Tabela 'talhoes' já não existe — skip.")
        return

    # Segurança: valida que não há talhões sem correspondente em cadastros_areas_rurais
    orphans = conn.execute(text("""
        SELECT COUNT(*) FROM talhoes t
        WHERE NOT EXISTS (
            SELECT 1 FROM cadastros_areas_rurais ar WHERE ar.id = t.id
        )
    """)).scalar()

    if orphans > 0:
        raise Exception(
            f"ABORTADO: {orphans} talhão(ões) sem correspondente em cadastros_areas_rurais. "
            "Execute step1 primeiro e valide."
        )

    # Verifica FKs pendentes apontando para talhoes
    fk_check = conn.execute(text("""
        SELECT tc.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.referential_constraints rc
            ON tc.constraint_name = rc.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON rc.unique_constraint_name = ccu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND ccu.table_name = 'talhoes'
    """)).fetchall()

    if fk_check:
        tables = [(r[0], r[1]) for r in fk_check]
        raise Exception(
            f"ABORTADO: FK(s) ainda apontam para 'talhoes': {tables}. "
            "Atualize os models antes de dropar."
        )

    op.drop_table("talhoes")
    print("✓ Tabela 'talhoes' removida com sucesso")


def downgrade() -> None:
    # Recria a tabela talhoes (estrutura mínima para rollback de emergência)
    # Os dados precisam ser recopiados manualmente de cadastros_areas_rurais
    op.create_table(
        "talhoes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("fazenda_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("codigo", sa.String(20)),
        sa.Column("area_ha", sa.Numeric(12, 4)),
        sa.Column("area_ha_manual", sa.Numeric(12, 4)),
        sa.Column("geometria", sa.JSON()),
        sa.Column("centroide", sa.JSON()),
        sa.Column("tipo_solo", sa.String(50)),
        sa.Column("classe_solo", sa.String(10)),
        sa.Column("textura_solo", sa.String(20)),
        sa.Column("relevo", sa.String(20)),
        sa.Column("irrigado", sa.Boolean(), default=False),
        sa.Column("sistema_irrigacao", sa.String(50)),
        sa.Column("historico_culturas", sa.JSON(), default=list),
        sa.Column("ativo", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fazenda_id"], ["fazendas.id"], ondelete="CASCADE"),
    )
    print("⚠ Tabela 'talhoes' recriada (vazia). Repopule manualmente se necessário.")
