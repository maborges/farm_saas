"""step18: estoque_movimentos immutable ledger

Revision ID: step18_estoque_movimentos
Revises: step17_operacoes_execucoes
Create Date: 2026-04-24

Creates the append-only inventory ledger. Legacy stock tables remain in place;
opening balances are inserted by runbook/service, not by automatic backfill.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "step18_estoque_movimentos"
down_revision: Union[str, Sequence[str], None] = "step17_operacoes_execucoes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "estoque_movimentos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("data_movimento", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("tipo_movimento", sa.String(24), nullable=False),
        sa.Column("produto_id", sa.Uuid(), nullable=False),
        sa.Column("deposito_id", sa.Uuid(), nullable=True),
        sa.Column("lote_id", sa.Uuid(), nullable=True),
        sa.Column("quantidade", sa.Numeric(18, 6), nullable=False),
        sa.Column("unidade_medida_id", sa.Uuid(), nullable=False),
        sa.Column("custo_unitario", sa.Numeric(15, 6), nullable=True),
        sa.Column("custo_total", sa.Numeric(15, 2), nullable=True),
        sa.Column("origem", sa.String(32), nullable=False),
        sa.Column("origem_id", sa.Uuid(), nullable=True),
        sa.Column("operacao_execucao_id", sa.Uuid(), nullable=True),
        sa.Column("production_unit_id", sa.Uuid(), nullable=True),
        sa.Column("numero_lote", sa.String(100), nullable=True),
        sa.Column("ajuste_de", sa.Uuid(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_estoque_movimentos_tenant_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["produto_id"], ["cadastros_produtos.id"], name="fk_estoque_movimentos_produto_id", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["deposito_id"], ["estoque_depositos.id"], name="fk_estoque_movimentos_deposito_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lote_id"], ["estoque_lotes.id"], name="fk_estoque_movimentos_lote_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["unidade_medida_id"], ["unidades_medida.id"], name="fk_estoque_movimentos_unidade_medida_id", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operacao_execucao_id"], ["operacoes_execucoes.id"], name="fk_estoque_movimentos_operacao_execucao_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["production_unit_id"], ["production_units.id"], name="fk_estoque_movimentos_production_unit_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["ajuste_de"], ["estoque_movimentos.id"], name="fk_estoque_movimentos_ajuste_de", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("quantidade <> 0", name="ck_estoque_movimentos_quantidade_nao_zero"),
        sa.CheckConstraint(
            "tipo_movimento IN ('SALDO_INICIAL','ENTRADA','SAIDA','DEVOLUCAO','AJUSTE','TRANSFERENCIA')",
            name="ck_estoque_movimentos_tipo",
        ),
        sa.CheckConstraint(
            "origem IN ('OPERACAO_EXECUCAO','COMPRA','COLHEITA','AJUSTE','MANUAL','TRANSFERENCIA')",
            name="ck_estoque_movimentos_origem",
        ),
        sa.CheckConstraint(
            """
            (
              tipo_movimento IN ('SALDO_INICIAL','ENTRADA','DEVOLUCAO') AND quantidade > 0
            ) OR (
              tipo_movimento = 'SAIDA' AND quantidade < 0
            ) OR (
              tipo_movimento IN ('AJUSTE','TRANSFERENCIA') AND quantidade <> 0
            )
            """,
            name="ck_estoque_movimentos_sinal_por_tipo",
        ),
        sa.CheckConstraint(
            "(origem = 'OPERACAO_EXECUCAO' AND operacao_execucao_id IS NOT NULL) OR origem <> 'OPERACAO_EXECUCAO'",
            name="ck_estoque_movimentos_origem_operacao_execucao",
        ),
        sa.CheckConstraint(
            "(tipo_movimento = 'DEVOLUCAO' AND ajuste_de IS NOT NULL) OR tipo_movimento <> 'DEVOLUCAO'",
            name="ck_estoque_movimentos_devolucao_exige_ajuste_de",
        ),
        sa.CheckConstraint(
            "(tipo_movimento = 'SALDO_INICIAL' AND ajuste_de IS NULL) OR tipo_movimento <> 'SALDO_INICIAL'",
            name="ck_estoque_movimentos_saldo_inicial_sem_ajuste",
        ),
    )

    op.create_index("ix_estoque_movimentos_tenant_produto_data", "estoque_movimentos", ["tenant_id", "produto_id", "data_movimento"])
    op.create_index("ix_estoque_movimentos_tenant_deposito_produto", "estoque_movimentos", ["tenant_id", "deposito_id", "produto_id"])
    op.create_index("ix_estoque_movimentos_tenant_pu", "estoque_movimentos", ["tenant_id", "production_unit_id"])
    op.create_index("ix_estoque_movimentos_tenant_origem", "estoque_movimentos", ["tenant_id", "origem", "origem_id"])
    op.create_index("ix_estoque_movimentos_operacao_execucao", "estoque_movimentos", ["operacao_execucao_id"])
    op.create_index("ix_estoque_movimentos_lote", "estoque_movimentos", ["lote_id"])
    op.execute(
        """
        CREATE INDEX ix_estoque_movimentos_ajuste_de
          ON estoque_movimentos (ajuste_de)
          WHERE ajuste_de IS NOT NULL
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_estoque_movimentos_saldo_inicial
          ON estoque_movimentos (
            tenant_id,
            produto_id,
            COALESCE(deposito_id, '00000000-0000-0000-0000-000000000000'::uuid)
          )
          WHERE tipo_movimento = 'SALDO_INICIAL'
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_estoque_movimentos_append_only()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RAISE EXCEPTION
            'estoque_movimentos is append-only: use ajuste_de for corrections'
            USING ERRCODE = 'object_not_in_prerequisite_state';
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER tg_estoque_movimentos_append_only
          BEFORE UPDATE OR DELETE ON estoque_movimentos
          FOR EACH ROW
          EXECUTE FUNCTION fn_estoque_movimentos_append_only()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS tg_estoque_movimentos_append_only ON estoque_movimentos")
    op.execute("DROP FUNCTION IF EXISTS fn_estoque_movimentos_append_only()")
    op.execute("DROP INDEX IF EXISTS uq_estoque_movimentos_saldo_inicial")
    op.execute("DROP INDEX IF EXISTS ix_estoque_movimentos_ajuste_de")
    op.drop_index("ix_estoque_movimentos_lote", table_name="estoque_movimentos")
    op.drop_index("ix_estoque_movimentos_operacao_execucao", table_name="estoque_movimentos")
    op.drop_index("ix_estoque_movimentos_tenant_origem", table_name="estoque_movimentos")
    op.drop_index("ix_estoque_movimentos_tenant_pu", table_name="estoque_movimentos")
    op.drop_index("ix_estoque_movimentos_tenant_deposito_produto", table_name="estoque_movimentos")
    op.drop_index("ix_estoque_movimentos_tenant_produto_data", table_name="estoque_movimentos")
    op.drop_table("estoque_movimentos")
