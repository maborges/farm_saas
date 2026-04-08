"""step3: fix prescricoes_vra talhao_id type and FK

Revision ID: step3_fix_prescricoes_vra
Revises: step2_drop_talhoes
Create Date: 2026-04-06

Corrige talhao_id em prescricoes_vra:
- Muda tipo de Integer para UUID
- Adiciona FK para cadastros_areas_rurais.id
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "step3_fix_prescricoes_vra"
down_revision = "step2_drop_talhoes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import text
    conn = op.get_bind()

    exists = conn.execute(text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'prescricoes_vra')"
    )).scalar()

    if exists:
        conn.execute(text("ALTER TABLE prescricoes_vra ALTER COLUMN talhao_id DROP NOT NULL"))
        conn.execute(text("ALTER TABLE prescricoes_vra ALTER COLUMN talhao_id TYPE UUID USING NULL"))
        op.create_foreign_key(
            "prescricoes_vra_talhao_id_fkey",
            "prescricoes_vra", "cadastros_areas_rurais",
            ["talhao_id"], ["id"],
            ondelete="SET NULL",
        )
    else:
        op.create_table(
            "prescricoes_vra",
            sa.Column("id", sa.Integer(), primary_key=True, index=True, autoincrement=True),
            sa.Column("tenant_id", sa.String(50), nullable=False, index=True),
            sa.Column("fazenda_id", PGUUID(as_uuid=True), sa.ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False),
            sa.Column("talhao_id", PGUUID(as_uuid=True), sa.ForeignKey("cadastros_areas_rurais.id", ondelete="SET NULL"), nullable=True),
            sa.Column("safra_id", PGUUID(as_uuid=True), sa.ForeignKey("safras.id", ondelete="SET NULL"), nullable=True),
            sa.Column("tipo", sa.String(50), nullable=False),
            sa.Column("elemento", sa.String(50)),
            sa.Column("dose_media", sa.Float()),
            sa.Column("dose_minima", sa.Float()),
            sa.Column("dose_maxima", sa.Float()),
            sa.Column("unidade", sa.String(20), server_default="kg/ha"),
            sa.Column("caminho_isoxml", sa.String(500)),
            sa.Column("caminho_shapefile", sa.String(500)),
            sa.Column("caminho_geojson", sa.String(500)),
            sa.Column("grid_tamanho_m", sa.Float()),
            sa.Column("total_pontos", sa.Integer()),
            sa.Column("status", sa.String(50), server_default="rascunho"),
            sa.Column("aprovada_por", PGUUID(as_uuid=True), nullable=True),
            sa.Column("aprovada_em", sa.DateTime()),
            sa.Column("responsavel_tecnico", sa.String(200)),
            sa.Column("crt", sa.String(100)),
            sa.Column("observacoes", sa.Text()),
            sa.Column("criada_em", sa.DateTime(), server_default=sa.text("NOW()")),
            sa.Column("atualizada_em", sa.DateTime(), server_default=sa.text("NOW()")),
        )


def downgrade() -> None:
    op.drop_table("prescricoes_vra")
