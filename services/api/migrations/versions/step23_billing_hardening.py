"""step23: billing hardening — grace_period_days, trial_expires_at em assinaturas_tenant

Revision ID: step23_billing_hardening
Revises: step20_safra_cenarios
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa

revision = "step23_billing_hardening"
down_revision = "step20_safra_cenarios"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("assinaturas_tenant") as batch:
        batch.add_column(sa.Column(
            "grace_period_days",
            sa.Integer(),
            nullable=False,
            server_default="3",
            comment="Dias de carência após vencimento antes de suspender. Default: 3.",
        ))
        batch.add_column(sa.Column(
            "trial_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Data de expiração do trial. NULL = sem trial ou já convertido.",
        ))

    op.execute("COMMIT")


def downgrade():
    with op.batch_alter_table("assinaturas_tenant") as batch:
        batch.drop_column("grace_period_days")
        batch.drop_column("trial_expires_at")
