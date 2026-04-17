"""add_area_rural_type_reorganize_hierarchy

Revision ID: a1b2c3d4e5f6
Revises: 9069070a48f7
Create Date: 2026-04-10 16:00:00.000000

Adiciona o tipo AREA_RURAL ao enum TipoArea e reorganiza a hierarquia:
- Cria nós AREA_RURAL e INFRAESTRUTURA raiz para cada UnidadeProdutiva existente
- Move GLEBAs raiz para debaixo do nó AREA_RURAL correspondente
"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '9069070a48f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Adicionar AREA_RURAL ao enum (PostgreSQL)
    try:
        conn.execute(text("ALTER TYPE tipoarea ADD VALUE IF NOT EXISTS 'AREA_RURAL'"))
    except Exception:
        pass  # SQLite ou enum já existente

    # 2. Para cada UnidadeProdutiva com áreas, garantir nó AREA_RURAL raiz
    ups = conn.execute(text(
        "SELECT DISTINCT unidade_produtiva_id, tenant_id FROM areas_rurais WHERE parent_id IS NULL"
    )).fetchall()

    for row in ups:
        up_id = str(row[0])
        tenant_id = str(row[1])

        # --- AREA_RURAL ---
        existing_ar = conn.execute(text(
            "SELECT id FROM areas_rurais WHERE unidade_produtiva_id = :up AND tipo = 'AREA_RURAL' AND parent_id IS NULL LIMIT 1"
        ), {"up": up_id}).fetchone()

        if existing_ar:
            area_rural_id = str(existing_ar[0])
        else:
            area_rural_id = str(uuid.uuid4())
            now = "NOW()"
            conn.execute(text(
                """INSERT INTO areas_rurais (id, tenant_id, unidade_produtiva_id, tipo, nome, ativo, parent_id, created_at, updated_at)
                   VALUES (:id, :tenant, :up, 'AREA_RURAL', 'Área Rural', true, NULL, NOW(), NOW())"""
            ), {"id": area_rural_id, "tenant": tenant_id, "up": up_id})

        # Move GLEBAs raiz para debaixo do nó AREA_RURAL
        conn.execute(text(
            """UPDATE areas_rurais
               SET parent_id = :ar_id, updated_at = NOW()
               WHERE unidade_produtiva_id = :up
                 AND tipo = 'GLEBA'
                 AND parent_id IS NULL"""
        ), {"ar_id": area_rural_id, "up": up_id})

        # --- INFRAESTRUTURA (garante que existe) ---
        existing_infra = conn.execute(text(
            "SELECT id FROM areas_rurais WHERE unidade_produtiva_id = :up AND tipo = 'INFRAESTRUTURA' AND parent_id IS NULL LIMIT 1"
        ), {"up": up_id}).fetchone()

        if not existing_infra:
            infra_id = str(uuid.uuid4())
            conn.execute(text(
                """INSERT INTO areas_rurais (id, tenant_id, unidade_produtiva_id, tipo, nome, ativo, parent_id, created_at, updated_at)
                   VALUES (:id, :tenant, :up, 'INFRAESTRUTURA', 'Infraestrutura', true, NULL, NOW(), NOW())"""
            ), {"id": infra_id, "tenant": tenant_id, "up": up_id})


def downgrade() -> None:
    conn = op.get_bind()

    # Move GLEBAs de volta para raiz
    conn.execute(text(
        """UPDATE areas_rurais SET parent_id = NULL, updated_at = NOW()
           WHERE tipo = 'GLEBA'
             AND parent_id IN (SELECT id FROM areas_rurais WHERE tipo = 'AREA_RURAL')"""
    ))

    # Remove nós AREA_RURAL criados automaticamente
    conn.execute(text(
        "DELETE FROM areas_rurais WHERE tipo = 'AREA_RURAL' AND nome = 'Área Rural'"
    ))
