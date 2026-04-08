"""Add grupos_usuarios table and make fazendas.grupo_id NOT NULL

Revision ID: grupo_usuario_mandatory_grupo
Revises: rbac_granular_permissions
Create Date: 2026-04-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "grupo_usuario_mandatory_grupo"
down_revision = "rbac_granular_permissions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Create grupos_usuarios table
    op.create_table(
        "grupos_usuarios",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("grupo_id", sa.Uuid(as_uuid=True), sa.ForeignKey("grupos_fazendas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("perfil_id", sa.Uuid(as_uuid=True), sa.ForeignKey("perfis_acesso.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("grupo_id", "user_id", name="uq_grupo_usuario"),
    )

    # 2. For each tenant that has fazendas with grupo_id=NULL, create a "Principal" group
    #    and assign those fazendas to it, then set NOT NULL.
    #
    # Step 2a: find tenants with ungrouped fazendas
    result = conn.execute(sa.text(
        "SELECT DISTINCT tenant_id FROM fazendas WHERE grupo_id IS NULL"
    ))
    tenant_ids = [row[0] for row in result]

    for tenant_id in tenant_ids:
        # Create a "Principal" grupo for this tenant
        grupo_id = conn.execute(sa.text(
            """
            INSERT INTO grupos_fazendas (id, tenant_id, nome, descricao, ativo, created_at, updated_at, ordem)
            VALUES (gen_random_uuid(), :tenant_id, 'Principal', 'Grupo padrão criado automaticamente', true, now(), now(), 0)
            RETURNING id
            """
        ), {"tenant_id": tenant_id}).scalar()

        # Assign all ungrouped fazendas of this tenant to this grupo
        conn.execute(sa.text(
            "UPDATE fazendas SET grupo_id = :grupo_id WHERE tenant_id = :tenant_id AND grupo_id IS NULL"
        ), {"grupo_id": grupo_id, "tenant_id": tenant_id})

        # Link the tenant owner (is_owner=true) to this grupo
        owner_result = conn.execute(sa.text(
            """
            SELECT usuario_id, perfil_id FROM tenant_usuarios
            WHERE tenant_id = :tenant_id AND is_owner = true
            LIMIT 1
            """
        ), {"tenant_id": tenant_id})
        owner_row = owner_result.fetchone()
        if owner_row:
            conn.execute(sa.text(
                """
                INSERT INTO grupos_usuarios (id, tenant_id, grupo_id, user_id, perfil_id, created_at)
                VALUES (gen_random_uuid(), :tenant_id, :grupo_id, :user_id, :perfil_id, now())
                ON CONFLICT (grupo_id, user_id) DO NOTHING
                """
            ), {
                "tenant_id": tenant_id,
                "grupo_id": grupo_id,
                "user_id": owner_row[0],
                "perfil_id": owner_row[1],
            })

    # 3. Now set grupo_id NOT NULL
    op.alter_column("fazendas", "grupo_id", nullable=False)

    # 4. Change FK ondelete from SET NULL to RESTRICT
    # Drop existing FK constraint (name may vary, use IF EXISTS via raw SQL)
    try:
        op.drop_constraint("fazendas_grupo_id_fkey", "fazendas", type_="foreignkey")
    except Exception:
        pass  # constraint name may differ in some envs
    op.create_foreign_key(
        "fazendas_grupo_id_fkey",
        "fazendas", "grupos_fazendas",
        ["grupo_id"], ["id"],
        ondelete="RESTRICT"
    )


def downgrade() -> None:
    # Revert grupo_id back to nullable with SET NULL
    op.drop_constraint("fazendas_grupo_id_fkey", "fazendas", type_="foreignkey")
    op.create_foreign_key(
        "fazendas_grupo_id_fkey",
        "fazendas", "grupos_fazendas",
        ["grupo_id"], ["id"],
        ondelete="SET NULL"
    )
    op.alter_column("fazendas", "grupo_id", nullable=True)
    op.drop_table("grupos_usuarios")
