"""step1: migrate talhoes data to cadastros_areas_rurais

Revision ID: step1_talhoes_consolidation
Revises: rh_colaborador_nome_cpf
Create Date: 2026-04-06

Estratégia Expand/Contract — Passo 1:
  - Copia registros da tabela legada `talhoes` para `cadastros_areas_rurais` (tipo=TALHAO)
  - Preserva os mesmos UUIDs para evitar remapeamento de FKs em operacoes/rastreabilidade
  - Skipa registros que já existem (idempotente)
  - NÃO dropa `talhoes` ainda — isso é o step2
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "step1_talhoes_consolidation"
down_revision = "rh_colaborador_nome_cpf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Verifica se a tabela legada ainda existe
    result = conn.execute(text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_name = 'talhoes')"
    ))
    if not result.scalar():
        print("Tabela 'talhoes' não existe — nada a migrar.")
        return

    # Copia talhoes → cadastros_areas_rurais preservando IDs
    # Skipa IDs que já existem (idempotente em re-run)
    conn.execute(text("""
        INSERT INTO cadastros_areas_rurais (
            id,
            tenant_id,
            fazenda_id,
            parent_id,
            tipo,
            nome,
            codigo,
            descricao,
            area_hectares,
            area_hectares_manual,
            geometria,
            centroide_lat,
            centroide_lng,
            dados_extras,
            ativo,
            created_at,
            updated_at
        )
        SELECT
            t.id,
            t.tenant_id,
            t.fazenda_id,
            NULL AS parent_id,
            'TALHAO' AS tipo,
            t.nome,
            t.codigo,
            NULL AS descricao,
            t.area_ha AS area_hectares,
            t.area_ha_manual AS area_hectares_manual,
            t.geometria,
            CASE
                WHEN t.centroide IS NOT NULL
                THEN (t.centroide->>'lat')::float
                ELSE NULL
            END AS centroide_lat,
            CASE
                WHEN t.centroide IS NOT NULL
                THEN (t.centroide->>'lng')::float
                ELSE NULL
            END AS centroide_lng,
            jsonb_build_object(
                'tipo_solo', t.tipo_solo,
                'classe_solo', t.classe_solo,
                'textura_solo', t.textura_solo,
                'relevo', t.relevo,
                'irrigado', t.irrigado,
                'sistema_irrigacao', t.sistema_irrigacao,
                'historico_culturas', t.historico_culturas,
                'migrado_de', 'talhoes_legado'
            ) AS dados_extras,
            t.ativo,
            t.created_at,
            t.updated_at
        FROM talhoes t
        WHERE NOT EXISTS (
            SELECT 1 FROM cadastros_areas_rurais ar WHERE ar.id = t.id
        )
    """))

    migrated = conn.execute(text(
        "SELECT COUNT(*) FROM cadastros_areas_rurais WHERE dados_extras->>'migrado_de' = 'talhoes_legado'"
    )).scalar()
    print(f"✓ {migrated} talhões migrados para cadastros_areas_rurais")

    # Cria índice para queries por tipo+fazenda (se não existir)
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_areas_rurais_talhao_fazenda
        ON cadastros_areas_rurais (fazenda_id, tipo)
        WHERE tipo = 'TALHAO'
    """))
    print("✓ Índice idx_areas_rurais_talhao_fazenda criado")


def downgrade() -> None:
    conn = op.get_bind()

    # Remove apenas os registros migrados (marcados com dados_extras)
    conn.execute(text(
        "DELETE FROM cadastros_areas_rurais WHERE dados_extras->>'migrado_de' = 'talhoes_legado'"
    ))

    conn.execute(text(
        "DROP INDEX IF EXISTS idx_areas_rurais_talhao_fazenda"
    ))
