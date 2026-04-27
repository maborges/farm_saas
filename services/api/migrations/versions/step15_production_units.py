"""step15: ProductionUnit + status_consorcio_area (read model + gate seletivo)

Revision ID: step15_pu
Revises: step14_uom
Create Date: 2026-04-24

Cria as fundações do núcleo operacional da safra:
  - Tabela `production_units` (mantida em inglês — exceção documentada; colide
    semanticamente com `unidades_produtivas` = Fazenda).
  - Tabela `status_consorcio_area` (read model + gate seletivo; fonte de verdade
    permanece em production_units.percentual_participacao).
  - Partial unique `WHERE status <> 'CANCELADA'` — permite recriação após cancelar.
  - Function + CONSTRAINT TRIGGER DEFERRABLE INITIALLY DEFERRED para validar
    SUM(percentual_participacao) ≤ 100 por (tenant, safra, area) no COMMIT.
  - Function + TRIGGER AFTER INSERT/UPDATE/DELETE para refresh do read model.
  - Backfill idempotente a partir de `cultivo_areas` (triggers desabilitadas
    durante backfill em massa; rebuild de status_consorcio_area ao final).

Decisões aprovadas (ver docs/agro/treinamento/step15-desenho-conceitual.md):
  1. Unicidade partial (WHERE status <> 'CANCELADA')
  2. area_ha é snapshot da safra
  3. PU é first-class (backfill + API + sync explícito via service)
  4. status_consorcio_area = read model + gate seletivo
  5. PU é o centro de custo agrícola canônico (sem tabela externa)
  6. Rateio é responsabilidade do Step 19 (não da PU)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = "step15_pu"
down_revision: Union[str, Sequence[str], None] = "step14_uom"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Tabela production_units
    # ------------------------------------------------------------------
    op.create_table(
        "production_units",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("safra_id", sa.Uuid(), nullable=False),
        sa.Column("cultivo_id", sa.Uuid(), nullable=False),
        sa.Column("area_id", sa.Uuid(), nullable=False),
        sa.Column(
            "cultivo_area_id",
            sa.Uuid(),
            nullable=True,
            comment="Rastreia origem quando a PU nasce via backfill ou sync de CultivoArea.",
        ),
        sa.Column(
            "percentual_participacao",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default=sa.text("100.00"),
            comment="Participação relativa entre PUs da mesma (safra, area). Soma <= 100 por (safra, area).",
        ),
        sa.Column(
            "area_ha",
            sa.Numeric(precision=12, scale=4),
            nullable=False,
            comment="SNAPSHOT da safra — não recalcula se AreaRural.area_ha mudar depois.",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'ATIVA'"),
        ),
        sa.Column("data_inicio", sa.Date(), nullable=True),
        sa.Column("data_fim", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], ondelete="CASCADE", name="fk_production_units_tenant_id"
        ),
        sa.ForeignKeyConstraint(
            ["safra_id"], ["safras.id"], ondelete="CASCADE", name="fk_production_units_safra_id"
        ),
        sa.ForeignKeyConstraint(
            ["cultivo_id"], ["cultivos.id"], ondelete="CASCADE", name="fk_production_units_cultivo_id"
        ),
        sa.ForeignKeyConstraint(
            ["area_id"],
            ["cadastros_areas_rurais.id"],
            ondelete="CASCADE",
            name="fk_production_units_area_id",
        ),
        sa.ForeignKeyConstraint(
            ["cultivo_area_id"],
            ["cultivo_areas.id"],
            ondelete="SET NULL",
            name="fk_production_units_cultivo_area_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "percentual_participacao > 0 AND percentual_participacao <= 100",
            name="ck_production_units_percentual_participacao",
        ),
        sa.CheckConstraint(
            "area_ha > 0",
            name="ck_production_units_area_ha_positiva",
        ),
        sa.CheckConstraint(
            "status IN ('ATIVA','ENCERRADA','CANCELADA')",
            name="ck_production_units_status",
        ),
        sa.CheckConstraint(
            "data_fim IS NULL OR data_inicio IS NULL OR data_fim >= data_inicio",
            name="ck_production_units_datas_ordenadas",
        ),
    )

    # Índices
    op.create_index(
        "ix_production_units_tenant_safra",
        "production_units",
        ["tenant_id", "safra_id"],
        unique=False,
    )
    op.create_index(
        "ix_production_units_tenant_cultivo",
        "production_units",
        ["tenant_id", "cultivo_id"],
        unique=False,
    )
    op.create_index(
        "ix_production_units_tenant_area",
        "production_units",
        ["tenant_id", "area_id"],
        unique=False,
    )
    op.create_index(
        "ix_production_units_tenant_status",
        "production_units",
        ["tenant_id", "status"],
        unique=False,
    )

    # Partial unique: 1 PU ativa/encerrada por cruzamento. Canceladas não colidem.
    op.execute(
        """
        CREATE UNIQUE INDEX uq_production_units_ativa
          ON production_units (tenant_id, safra_id, cultivo_id, area_id)
          WHERE status <> 'CANCELADA'
        """
    )

    # Índice parcial para rastreio de origem
    op.execute(
        """
        CREATE INDEX ix_production_units_cultivo_area
          ON production_units (cultivo_area_id)
          WHERE cultivo_area_id IS NOT NULL
        """
    )

    # ------------------------------------------------------------------
    # 2. Tabela status_consorcio_area (read model + gate seletivo)
    # ------------------------------------------------------------------
    op.create_table(
        "status_consorcio_area",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("safra_id", sa.Uuid(), nullable=False),
        sa.Column("area_id", sa.Uuid(), nullable=False),
        sa.Column(
            "soma_participacao",
            sa.Numeric(precision=6, scale=2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "qtd_unidades",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            comment="VAZIO | INCOMPLETO | VALIDO | INCONSISTENTE",
        ),
        sa.Column(
            "calculado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
            name="fk_status_consorcio_area_tenant_id",
        ),
        sa.ForeignKeyConstraint(
            ["safra_id"],
            ["safras.id"],
            ondelete="CASCADE",
            name="fk_status_consorcio_area_safra_id",
        ),
        sa.ForeignKeyConstraint(
            ["area_id"],
            ["cadastros_areas_rurais.id"],
            ondelete="CASCADE",
            name="fk_status_consorcio_area_area_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "safra_id",
            "area_id",
            name="uq_status_consorcio_area_safra_area",
        ),
        sa.CheckConstraint(
            "status IN ('VAZIO','INCOMPLETO','VALIDO','INCONSISTENTE')",
            name="ck_status_consorcio_area_status",
        ),
    )

    op.create_index(
        "ix_status_consorcio_area_tenant_status",
        "status_consorcio_area",
        ["tenant_id", "status"],
        unique=False,
    )

    # ------------------------------------------------------------------
    # 3. Function + CONSTRAINT TRIGGER DEFERRED (validação soma <= 100)
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_production_units_valida_soma()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
          v_soma NUMERIC(6,2);
        BEGIN
          -- Para CONSTRAINT TRIGGER DEFERRED, o trigger dispara no COMMIT;
          -- a tabela já contém o estado final, então SUM vê todas as linhas.
          SELECT COALESCE(SUM(percentual_participacao), 0)
            INTO v_soma
            FROM production_units
           WHERE tenant_id = NEW.tenant_id
             AND safra_id  = NEW.safra_id
             AND area_id   = NEW.area_id
             AND status <> 'CANCELADA';

          IF v_soma > 100.01 THEN
            RAISE EXCEPTION
              'soma de percentual_participacao excede 100 em (tenant=%, safra=%, area=%): soma=% — verifique PUs de consórcio',
              NEW.tenant_id, NEW.safra_id, NEW.area_id, v_soma
              USING ERRCODE = 'check_violation';
          END IF;

          RETURN NULL;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER tg_production_units_valida_soma
          AFTER INSERT OR UPDATE ON production_units
          DEFERRABLE INITIALLY DEFERRED
          FOR EACH ROW
          EXECUTE FUNCTION fn_production_units_valida_soma()
        """
    )

    # ------------------------------------------------------------------
    # 4. Function + TRIGGER de refresh do read model
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_production_units_refresh_status()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
          v_tenant_id UUID;
          v_safra_id  UUID;
          v_area_id   UUID;
          v_soma      NUMERIC(6,2);
          v_qtd       INTEGER;
          v_status    VARCHAR(20);
        BEGIN
          IF TG_OP = 'DELETE' THEN
            v_tenant_id := OLD.tenant_id;
            v_safra_id  := OLD.safra_id;
            v_area_id   := OLD.area_id;
          ELSE
            v_tenant_id := NEW.tenant_id;
            v_safra_id  := NEW.safra_id;
            v_area_id   := NEW.area_id;
          END IF;

          SELECT COALESCE(SUM(percentual_participacao), 0), COUNT(*)
            INTO v_soma, v_qtd
            FROM production_units
           WHERE tenant_id = v_tenant_id
             AND safra_id  = v_safra_id
             AND area_id   = v_area_id
             AND status <> 'CANCELADA';

          IF v_qtd = 0 THEN
            v_status := 'VAZIO';
          ELSIF v_soma < 99.99 THEN
            v_status := 'INCOMPLETO';
          ELSIF v_soma <= 100.01 THEN
            v_status := 'VALIDO';
          ELSE
            v_status := 'INCONSISTENTE';
          END IF;

          INSERT INTO status_consorcio_area
            (id, tenant_id, safra_id, area_id,
             soma_participacao, qtd_unidades, status, calculado_em)
          VALUES
            (gen_random_uuid(), v_tenant_id, v_safra_id, v_area_id,
             v_soma, v_qtd, v_status, now())
          ON CONFLICT (tenant_id, safra_id, area_id) DO UPDATE SET
            soma_participacao = EXCLUDED.soma_participacao,
            qtd_unidades      = EXCLUDED.qtd_unidades,
            status            = EXCLUDED.status,
            calculado_em      = EXCLUDED.calculado_em;

          -- UPDATE que mude as chaves (tenant, safra, area) precisa refrescar
          -- também a área antiga. Chaves não deveriam mudar, mas é defensivo.
          IF TG_OP = 'UPDATE' AND (
               OLD.tenant_id <> NEW.tenant_id
            OR OLD.safra_id  <> NEW.safra_id
            OR OLD.area_id   <> NEW.area_id
          ) THEN
            SELECT COALESCE(SUM(percentual_participacao), 0), COUNT(*)
              INTO v_soma, v_qtd
              FROM production_units
             WHERE tenant_id = OLD.tenant_id
               AND safra_id  = OLD.safra_id
               AND area_id   = OLD.area_id
               AND status <> 'CANCELADA';

            IF v_qtd = 0 THEN
              v_status := 'VAZIO';
            ELSIF v_soma < 99.99 THEN
              v_status := 'INCOMPLETO';
            ELSIF v_soma <= 100.01 THEN
              v_status := 'VALIDO';
            ELSE
              v_status := 'INCONSISTENTE';
            END IF;

            INSERT INTO status_consorcio_area
              (id, tenant_id, safra_id, area_id,
               soma_participacao, qtd_unidades, status, calculado_em)
            VALUES
              (gen_random_uuid(), OLD.tenant_id, OLD.safra_id, OLD.area_id,
               v_soma, v_qtd, v_status, now())
            ON CONFLICT (tenant_id, safra_id, area_id) DO UPDATE SET
              soma_participacao = EXCLUDED.soma_participacao,
              qtd_unidades      = EXCLUDED.qtd_unidades,
              status            = EXCLUDED.status,
              calculado_em      = EXCLUDED.calculado_em;
          END IF;

          RETURN NULL;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER tg_production_units_refresh_status
          AFTER INSERT OR UPDATE OR DELETE ON production_units
          FOR EACH ROW
          EXECUTE FUNCTION fn_production_units_refresh_status()
        """
    )

    # ------------------------------------------------------------------
    # 5. Backfill idempotente a partir de cultivo_areas
    #    Triggers desabilitadas durante backfill em massa.
    # ------------------------------------------------------------------
    op.execute(
        "ALTER TABLE production_units DISABLE TRIGGER tg_production_units_valida_soma"
    )
    op.execute(
        "ALTER TABLE production_units DISABLE TRIGGER tg_production_units_refresh_status"
    )

    # Inserir 1 PU por cultivo_areas existente.
    # - Cultivo não-consorciado: percentual = 100
    # - Cultivo consorciado: percentual proporcional a area_ha em (safra, area)
    op.execute(
        """
        INSERT INTO production_units (
          id, tenant_id, safra_id, cultivo_id, area_id, cultivo_area_id,
          percentual_participacao, area_ha, status
        )
        SELECT
          gen_random_uuid(),
          ca.tenant_id,
          c.safra_id,
          ca.cultivo_id,
          ca.area_id,
          ca.id,
          CASE
            WHEN c.consorciado = false THEN 100.00
            ELSE ROUND(
              (ca.area_ha / SUM(ca.area_ha) OVER (
                PARTITION BY ca.tenant_id, c.safra_id, ca.area_id
              ) * 100)::numeric,
              2
            )
          END,
          ca.area_ha,
          'ATIVA'
        FROM cultivo_areas ca
        JOIN cultivos c ON c.id = ca.cultivo_id
        ON CONFLICT (tenant_id, safra_id, cultivo_id, area_id)
          WHERE status <> 'CANCELADA'
          DO NOTHING
        """
    )

    # Rebuild inicial do status_consorcio_area (trigger estava desabilitado)
    op.execute(
        """
        INSERT INTO status_consorcio_area (
          id, tenant_id, safra_id, area_id,
          soma_participacao, qtd_unidades, status, calculado_em
        )
        SELECT
          gen_random_uuid(),
          tenant_id,
          safra_id,
          area_id,
          SUM(percentual_participacao),
          COUNT(*),
          CASE
            WHEN COUNT(*) = 0 THEN 'VAZIO'
            WHEN SUM(percentual_participacao) < 99.99 THEN 'INCOMPLETO'
            WHEN SUM(percentual_participacao) <= 100.01 THEN 'VALIDO'
            ELSE 'INCONSISTENTE'
          END,
          now()
        FROM production_units
        WHERE status <> 'CANCELADA'
        GROUP BY tenant_id, safra_id, area_id
        ON CONFLICT (tenant_id, safra_id, area_id) DO NOTHING
        """
    )

    # Reabilitar triggers
    op.execute(
        "ALTER TABLE production_units ENABLE TRIGGER tg_production_units_refresh_status"
    )
    op.execute(
        "ALTER TABLE production_units ENABLE TRIGGER tg_production_units_valida_soma"
    )


def downgrade() -> None:
    """Downgrade intencionalmente não implementado.

    Step 15 cria `production_units` que é referenciado por steps 16–19
    (FKs `production_unit_id`). Reverter apenas o DDL aqui deixaria ambientes
    intermediários com FKs órfãs ou triggers apontando para funções removidas.
    Reversão deve ser feita via restore de backup do ponto pré-step15.

    Em caso de necessidade de rollback cirúrgico (apenas se nenhum step
    posterior foi aplicado), seguir procedimento documentado em
    docs/agro/treinamento/step15-plano.md §5.2.
    """
    raise NotImplementedError(
        "Downgrade de step15 não suportado. Reverter via restore de backup."
    )
