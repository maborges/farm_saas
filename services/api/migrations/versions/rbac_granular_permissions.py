"""Converter formato JSON de permissoes para formato granular {"granted": [...]}

Revision ID: rbac_granular_permissions
Revises: rh_colaborador_nome_cpf
Create Date: 2026-04-02

"""
import json
from alembic import op
from sqlalchemy import text

revision = "rbac_granular_permissions"
down_revision = "rh_colaborador_nome_cpf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Buscar perfis customizados com formato legado {"modulo": "write/read/none"}
    rows = conn.execute(
        text("SELECT id, permissoes FROM perfis_acesso WHERE is_custom = TRUE AND permissoes IS NOT NULL")
    ).fetchall()

    for row in rows:
        perfil_id, permissoes = row
        if not isinstance(permissoes, dict):
            continue

        # Já está no novo formato — pular
        if "granted" in permissoes or "permissions" in permissoes:
            continue

        # Converter formato legado para granular
        granted = []
        for module, level in permissoes.items():
            if level == "none":
                continue
            if level in ("write", "*"):
                granted.append(f"{module}:*")
            elif level == "read":
                granted.extend([
                    f"{module}:*:view",
                    f"{module}:*:list",
                    f"{module}:*:export",
                ])

        novo = json.dumps({"granted": granted})
        conn.execute(
            text("UPDATE perfis_acesso SET permissoes = :p::jsonb WHERE id = :id"),
            {"p": novo, "id": str(perfil_id)}
        )


def downgrade() -> None:
    # Não há rollback determinístico seguro para conversão de dados
    pass
