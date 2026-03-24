import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class AdminImpersonation(Base):
    """
    Log de quando admin do SaaS acessa conta de assinante (impersonation).

    Registra todas as vezes que um administrador do SaaS assume o contexto
    de um assinante para suporte, demonstração ou auditoria.

    Segurança:
    - Requer permissão específica (backoffice:impersonate)
    - Registra motivo obrigatório
    - Log completo de ações realizadas
    - Auditável e rastreável

    Exemplo de uso:
        Admin "João Silva" acessa conta do tenant "Fazenda Santa Cruz"
        para configurar integração de e-mail (suporte técnico).
    """
    __tablename__ = "admin_impersonations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Admin que está fazendo impersonation
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Tenant sendo acessado
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Fazenda específica (opcional)
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fazendas.id", ondelete="SET NULL"),
        nullable=True,
        comment="Fazenda específica sendo acessada (NULL = contexto geral do tenant)"
    )

    # Justificativa obrigatória
    motivo: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Motivo do acesso (ex: 'Suporte técnico - configuração SMTP')"
    )

    # Categoria do motivo
    categoria: Mapped[str] = mapped_column(
        String(50),
        default="SUPORTE",
        comment="SUPORTE, AUDITORIA, DEMONSTRACAO, MIGRACAO, EMERGENCIA"
    )

    # Controle temporal
    inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        comment="Início da sessão de impersonation"
    )

    fim: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fim da sessão (NULL = ainda ativa)"
    )

    # Informações de rede
    ip_address: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="IP do admin durante o acesso"
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # Log de ações realizadas durante o impersonation
    acoes_realizadas: Mapped[list[dict]] = mapped_column(
        JSON,
        default=list,
        comment="""
        Array de objetos com as ações realizadas:
        [{
            "timestamp": "2024-03-12T10:30:00Z",
            "acao": "UPDATE",
            "recurso": "configuracoes.smtp",
            "detalhes": {"campo": "smtp_host", "valor_anterior": "...", "valor_novo": "..."}
        }]
        """
    )

    # Metadados adicionais (metadata é palavra reservada no SQLAlchemy)
    meta_info: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Informações adicionais (ticket de suporte, aprovação, etc)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
