"""step14: Measurement Engine — unidades_medida + unidades_medida_conversoes

Revision ID: step14_uom
Revises: 0808ec16ef17
Create Date: 2026-04-24

Cria as fundações do Measurement Engine exigido pelo núcleo operacional da safra:
  - Tabela `unidades_medida` — unidades canônicas (massa, volume, area, tempo, etc.)
  - Tabela `unidades_medida_conversoes` — conversões não-lineares ou por cultura
  - Seed de unidades de sistema (tenant_id=NULL, sistema=true):
    KG, G, TON, SC60, SC50, L, ML, M3, HA, M2, HR_MAQ, HR_HOMEM, UN, BRL

Pré-requisito para steps 17 (operacoes_execucoes.unidade_medida_id) e 18
(estoque_movimentos.unidade_medida_id). Nenhuma mudança destrutiva.

Nomenclatura: snake_case pt-BR, prefixo de domínio `unidades_medida_`.
ProductionUnit (step15) permanece em inglês como exceção documentada.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = "step14_uom"
down_revision: Union[str, Sequence[str], None] = "0808ec16ef17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DIMENSOES_VALIDAS = (
    "massa",
    "volume",
    "area",
    "tempo",
    "contagem",
    "moeda",
    "hora_maquina",
    "hora_homem",
)


def upgrade() -> None:
    # 1. Tabela unidades_medida
    op.create_table(
        "unidades_medida",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            nullable=True,
            comment="NULL = unidade global de sistema; preenchido = customização por tenant",
        ),
        sa.Column("codigo", sa.String(length=16), nullable=False),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.Column(
            "dimensao",
            sa.String(length=24),
            nullable=False,
            comment="massa|volume|area|tempo|contagem|moeda|hora_maquina|hora_homem",
        ),
        sa.Column("codigo_canonico", sa.String(length=16), nullable=False),
        sa.Column(
            "fator_canonico",
            sa.Numeric(precision=18, scale=9),
            nullable=False,
            comment="Multiplicador para unidade canônica da dimensão. Ex: SC60 → 60.000000000",
        ),
        sa.Column(
            "sistema",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "ativo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "casas_decimais",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("2"),
            comment="Precisão de APRESENTAÇÃO (UI/máscaras). Não substitui a precisão de cálculo (NUMERIC).",
        ),
        sa.Column(
            "eh_canonica",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Marca explícita da unidade canônica da dimensão. Só true quando codigo=codigo_canonico e fator_canonico=1.",
        ),
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
            ["tenant_id"], ["tenants.id"], ondelete="CASCADE", name="fk_unidades_medida_tenant_id"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "fator_canonico > 0",
            name="ck_unidades_medida_fator_canonico_positivo",
        ),
        sa.CheckConstraint(
            "dimensao IN ('massa','volume','area','tempo','contagem','moeda','hora_maquina','hora_homem')",
            name="ck_unidades_medida_dimensao",
        ),
        sa.CheckConstraint(
            "casas_decimais BETWEEN 0 AND 9",
            name="ck_unidades_medida_casas_decimais_range",
        ),
        sa.CheckConstraint(
            "(eh_canonica = false) OR (codigo = codigo_canonico AND fator_canonico = 1)",
            name="ck_unidades_medida_canonica_coerencia",
        ),
    )

    # Índices não-únicos
    op.create_index(
        "ix_unidades_medida_dimensao",
        "unidades_medida",
        ["dimensao"],
        unique=False,
    )
    op.create_index(
        "ix_unidades_medida_tenant_ativo",
        "unidades_medida",
        ["tenant_id", "ativo"],
        unique=False,
    )

    # Partial unique indexes (PG nativo) — código único por escopo (global ou por tenant)
    op.execute(
        """
        CREATE UNIQUE INDEX uq_unidades_medida_codigo_global
          ON unidades_medida (codigo)
          WHERE tenant_id IS NULL
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_unidades_medida_codigo_tenant
          ON unidades_medida (tenant_id, codigo)
          WHERE tenant_id IS NOT NULL
        """
    )

    # Partial unique: apenas 1 canônica por dimensão (global + por tenant)
    op.execute(
        """
        CREATE UNIQUE INDEX uq_unidades_medida_canonica_global
          ON unidades_medida (dimensao)
          WHERE eh_canonica = true AND tenant_id IS NULL
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_unidades_medida_canonica_tenant
          ON unidades_medida (tenant_id, dimensao)
          WHERE eh_canonica = true AND tenant_id IS NOT NULL
        """
    )

    # 2. Tabela unidades_medida_conversoes
    op.create_table(
        "unidades_medida_conversoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
        sa.Column("unidade_origem_id", sa.Uuid(), nullable=False),
        sa.Column("unidade_destino_id", sa.Uuid(), nullable=False),
        sa.Column(
            "cultura",
            sa.String(length=50),
            nullable=True,
            comment="Ex: CAFE, SOJA — conversão específica por cultura",
        ),
        sa.Column("commodity_id", sa.Uuid(), nullable=True),
        sa.Column("fator", sa.Numeric(precision=18, scale=9), nullable=False),
        sa.Column(
            "percentual_tolerancia",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
            name="fk_unidades_medida_conversoes_tenant_id",
        ),
        sa.ForeignKeyConstraint(
            ["unidade_origem_id"],
            ["unidades_medida.id"],
            ondelete="RESTRICT",
            name="fk_unidades_medida_conversoes_origem",
        ),
        sa.ForeignKeyConstraint(
            ["unidade_destino_id"],
            ["unidades_medida.id"],
            ondelete="RESTRICT",
            name="fk_unidades_medida_conversoes_destino",
        ),
        sa.ForeignKeyConstraint(
            ["commodity_id"],
            ["cadastros_commodities.id"],
            ondelete="SET NULL",
            name="fk_unidades_medida_conversoes_commodity",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "fator > 0",
            name="ck_unidades_medida_conversoes_fator_positivo",
        ),
        sa.CheckConstraint(
            "unidade_origem_id <> unidade_destino_id",
            name="ck_unidades_medida_conversoes_unidades_distintas",
        ),
    )

    op.create_index(
        "ix_unidades_medida_conversoes_origem_destino",
        "unidades_medida_conversoes",
        ["tenant_id", "unidade_origem_id", "unidade_destino_id"],
        unique=False,
    )
    op.create_index(
        "ix_unidades_medida_conversoes_cultura",
        "unidades_medida_conversoes",
        ["cultura"],
        unique=False,
    )

    # Unique expression index para tratar NULLs como iguais (tenant_id, cultura, commodity_id)
    op.execute(
        """
        CREATE UNIQUE INDEX uq_unidades_medida_conversoes_escopo
          ON unidades_medida_conversoes (
            COALESCE(tenant_id, '00000000-0000-0000-0000-000000000000'::uuid),
            unidade_origem_id,
            unidade_destino_id,
            COALESCE(cultura, ''),
            COALESCE(commodity_id, '00000000-0000-0000-0000-000000000000'::uuid)
          )
        """
    )

    # 3. Seed de unidades de sistema (tenant_id=NULL, sistema=true)
    # Idempotente: ON CONFLICT DO NOTHING usa o partial unique uq_unidades_medida_codigo_global.
    # Colunas:
    #   codigo, nome, dimensao, codigo_canonico, fator_canonico, sistema, ativo,
    #   casas_decimais (precisão de apresentação), eh_canonica (marca da unidade-base)
    op.execute(
        """
        INSERT INTO unidades_medida
          (id, tenant_id, codigo, nome, dimensao, codigo_canonico, fator_canonico,
           sistema, ativo, casas_decimais, eh_canonica)
        VALUES
          (gen_random_uuid(), NULL, 'KG',       'Quilograma',       'massa',        'KG',      1.000000000,    true, true, 2, true),
          (gen_random_uuid(), NULL, 'G',        'Grama',            'massa',        'KG',      0.001000000,    true, true, 3, false),
          (gen_random_uuid(), NULL, 'TON',      'Tonelada',         'massa',        'KG',      1000.000000000, true, true, 4, false),
          (gen_random_uuid(), NULL, 'SC60',     'Saca 60 kg',       'massa',        'KG',      60.000000000,   true, true, 2, false),
          (gen_random_uuid(), NULL, 'SC50',     'Saca 50 kg',       'massa',        'KG',      50.000000000,   true, true, 2, false),
          (gen_random_uuid(), NULL, 'L',        'Litro',            'volume',       'L',       1.000000000,    true, true, 2, true),
          (gen_random_uuid(), NULL, 'ML',       'Mililitro',        'volume',       'L',       0.001000000,    true, true, 3, false),
          (gen_random_uuid(), NULL, 'M3',       'Metro cúbico',     'volume',       'L',       1000.000000000, true, true, 4, false),
          (gen_random_uuid(), NULL, 'HA',       'Hectare',          'area',         'HA',      1.000000000,    true, true, 2, true),
          (gen_random_uuid(), NULL, 'M2',       'Metro quadrado',   'area',         'HA',      0.000100000,    true, true, 0, false),
          (gen_random_uuid(), NULL, 'HR_MAQ',   'Hora de máquina',  'hora_maquina', 'HR_MAQ',  1.000000000,    true, true, 2, true),
          (gen_random_uuid(), NULL, 'HR_HOMEM', 'Hora homem',       'hora_homem',   'HR_HOMEM',1.000000000,    true, true, 2, true),
          (gen_random_uuid(), NULL, 'UN',       'Unidade',          'contagem',     'UN',      1.000000000,    true, true, 0, true),
          (gen_random_uuid(), NULL, 'BRL',      'Real brasileiro',  'moeda',        'BRL',     1.000000000,    true, true, 2, true)
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    """Downgrade intencionalmente não implementado.

    Este step introduz dados seed de sistema referenciados por steps futuros
    (17, 18). Reverter apenas o DDL deixaria referências órfãs nos ambientes
    que já avançaram. Reversão deve ser feita via restore de backup.
    """
    raise NotImplementedError(
        "Downgrade de step14 não suportado. Reverter via restore de backup."
    )
