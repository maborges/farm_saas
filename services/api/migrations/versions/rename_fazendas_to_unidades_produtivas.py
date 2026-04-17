"""rename fazendas to unidades_produtivas and remove grupos_fazendas

Revision ID: rename_fazendas_unidades_prod
Revises:
Create Date: 2026-04-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'rename_fazendas_unidades_prod'
down_revision = 'fase2_ia_iot'
branch_labels = None
depends_on = None


def _rename_column_if_exists(table: str, old: str, new: str) -> None:
    """Rename column only if it exists (safe for re-runs)."""
    op.execute(f"""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = '{table}'
                  AND column_name = '{old}'
            ) THEN
                ALTER TABLE "{table}" RENAME COLUMN "{old}" TO "{new}";
            END IF;
        END $$;
    """)


def _drop_column_if_exists(table: str, column: str) -> None:
    op.execute(f"""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = '{table}'
                  AND column_name = '{column}'
            ) THEN
                ALTER TABLE "{table}" DROP COLUMN "{column}";
            END IF;
        END $$;
    """)


def _drop_table_if_exists_cascade(table: str) -> None:
    op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')


def _rename_table_if_exists(old: str, new: str) -> None:
    op.execute(f"""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = current_schema()
                  AND table_name = '{old}'
            ) THEN
                ALTER TABLE "{old}" RENAME TO "{new}";
            END IF;
        END $$;
    """)


def upgrade():
    # 1. Drop grupos_usuarios e grupos_fazendas com CASCADE
    _drop_table_if_exists_cascade("grupos_usuarios")
    _drop_table_if_exists_cascade("grupos_fazendas")

    # 2. Remover colunas órfãs que sobram após o CASCADE
    _drop_column_if_exists("assinaturas_tenant", "grupo_fazendas_id")
    _drop_column_if_exists("sessoes_ativas", "grupo_fazendas_id")
    _drop_column_if_exists("fazendas", "grupo_id")

    # 3. Rename fazendas → unidades_produtivas
    _rename_table_if_exists("fazendas", "unidades_produtivas")

    # 4. Rename fazenda_usuarios → unidade_produtiva_usuarios
    _rename_table_if_exists("fazenda_usuarios", "unidade_produtiva_usuarios")

    # 5. Rename fazenda_id → unidade_produtiva_id em todas as tabelas
    tables_with_fazenda_id = [
        "unidade_produtiva_usuarios",
        "sessoes_ativas",
        "configuracao_fazenda",
        "cadastros_areas_rurais",
        "cadastros_equipamentos",
        "cadastros_pessoas_relacionamento",
        "pec_lotes",
        "pec_animais",
        "pec_piquetes",
        "pec_producao_leite",
        "rh_colaboradores",
        "rh_lancamentos_diaria",
        "rh_empreitadas",
        "op_depositos",
        "op_saldo_estoque",
        "op_apontamentos",
        "agr_registros_climaticos",
        "agr_rastreabilidade_lotes",
        "fin_despesas",
        "fin_receitas",
        "fin_notas_fiscais",
        "imoveis_imovel",
    ]

    for table in tables_with_fazenda_id:
        _rename_column_if_exists(table, "fazenda_id", "unidade_produtiva_id")


def downgrade():
    tables_with_unidade_id = [
        "unidade_produtiva_usuarios",
        "configuracao_fazenda",
        "cadastros_areas_rurais",
        "cadastros_equipamentos",
        "cadastros_pessoas_relacionamento",
        "pec_lotes",
        "pec_animais",
        "pec_piquetes",
        "pec_producao_leite",
        "rh_colaboradores",
        "rh_lancamentos_diaria",
        "rh_empreitadas",
        "op_depositos",
        "op_saldo_estoque",
        "op_apontamentos",
        "agr_registros_climaticos",
        "agr_rastreabilidade_lotes",
        "fin_despesas",
        "fin_receitas",
        "fin_notas_fiscais",
        "imoveis_imovel",
    ]

    for table in tables_with_unidade_id:
        _rename_column_if_exists(table, "unidade_produtiva_id", "fazenda_id")

    _rename_table_if_exists("unidade_produtiva_usuarios", "fazenda_usuarios")
    _rename_table_if_exists("unidades_produtivas", "fazendas")
