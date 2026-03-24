import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class AdminUser(Base):
    """Usuários administrativos do SaaS (separado dos usuários dos tenants)."""
    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Perfil: super_admin, admin, suporte, financeiro, comercial
    role: Mapped[str] = mapped_column(String(20), nullable=False, default='admin')
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Preferências
    timezone: Mapped[str] = mapped_column(String(50), default='America/Sao_Paulo')
    locale: Mapped[str] = mapped_column(String(10), default='pt-BR')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def tem_permissao(self, permissao: str) -> bool:
        """Verifica se admin tem permissão."""
        from core.dependencies import ADMIN_PERMISSIONS
        user_perms = ADMIN_PERMISSIONS.get(self.role, [])

        if "*" in user_perms:
            return True

        if ":" not in permissao:
            return permissao in user_perms

        resource, action = permissao.split(":")
        return any(
            perm == permissao or perm == f"{resource}:*"
            for perm in user_perms
        )
