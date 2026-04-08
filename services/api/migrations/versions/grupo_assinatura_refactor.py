"""grupo_assinatura_refactor

Revision ID: grupo_assinatura_refactor
Revises: rh_colaborador_nome_cpf
Create Date: 2026-04-04

Mudanças:
- assinaturas_tenant.grupo_fazendas_id: nullable=True → NOT NULL
- assinaturas_tenant.tipo_assinatura: default PRINCIPAL → GRUPO
- UniqueConstraint (grupo_fazendas_id, tipo_assinatura) — 1 assinatura GRUPO por grupo
- tenants.modulos_ativos: nullable=True (deprecado)
- tenants.max_usuarios_simultaneos: nullable=True (deprecado)
"""
from alembic import op
import sqlalchemy as sa

revision = 'grupo_assinatura_refactor'
down_revision = 'rh_colaborador_nome_cpf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Remover assinaturas órfãs (sem grupo) antes de tornar NOT NULL
    op.execute("""
        DELETE FROM assinaturas_tenant
        WHERE grupo_fazendas_id IS NULL
    """)

    # 2. grupo_fazendas_id NOT NULL
    op.alter_column(
        'assinaturas_tenant', 'grupo_fazendas_id',
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=False
    )

    # 3. Atualizar tipo_assinatura PRINCIPAL → GRUPO
    op.execute("""
        UPDATE assinaturas_tenant
        SET tipo_assinatura = 'GRUPO'
        WHERE tipo_assinatura = 'PRINCIPAL'
    """)

    # 4. UniqueConstraint: 1 assinatura GRUPO por grupo
    op.create_unique_constraint(
        'uq_assinatura_grupo_tipo',
        'assinaturas_tenant',
        ['grupo_fazendas_id', 'tipo_assinatura']
    )

    # 5. Deprecar campos no tenant (tornar nullable)
    op.alter_column('tenants', 'modulos_ativos', nullable=True)
    op.alter_column('tenants', 'max_usuarios_simultaneos', nullable=True)

    # 6. Zerar os campos deprecated
    op.execute("UPDATE tenants SET modulos_ativos = NULL, max_usuarios_simultaneos = NULL")


def downgrade() -> None:
    op.drop_constraint('uq_assinatura_grupo_tipo', 'assinaturas_tenant', type_='unique')

    op.execute("""
        UPDATE assinaturas_tenant
        SET tipo_assinatura = 'PRINCIPAL'
        WHERE tipo_assinatura = 'GRUPO'
    """)

    op.alter_column(
        'assinaturas_tenant', 'grupo_fazendas_id',
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=True
    )

    op.alter_column('tenants', 'modulos_ativos', nullable=False,
                    server_default=sa.text("'[]'::json"))
    op.alter_column('tenants', 'max_usuarios_simultaneos', nullable=False,
                    server_default='5')
