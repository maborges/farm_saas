import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class SessaoAtiva(Base):
    """
    Controle de sessões ativas para limite de usuários simultâneos.

    Implementa o controle de usuários simultâneos conforme o plano contratado,
    permitindo que múltiplas fazendas de um grupo compartilhem o mesmo limite.

    Funcionalidades:
    - Validação de limite de usuários por plano
    - Compartilhamento de limite entre fazendas do mesmo grupo
    - Expiração automática de sessões inativas
    - Auditoria de acessos

    Exemplo:
        Plano PRO: 10 usuários simultâneos
        Grupo "Sul" (3 fazendas) compartilha esse limite
        → Se 7 usuários estão conectados, restam 3 slots disponíveis
    """
    __tablename__ = "sessoes_ativas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Contexto da sessão
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    grupo_fazendas_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grupos_fazendas.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Grupo ao qual a sessão pertence (para limite compartilhado)"
    )

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fazendas.id", ondelete="SET NULL"),
        nullable=True,
        comment="Fazenda ativa na sessão (pode mudar sem encerrar a sessão)"
    )

    # Token de sessão (hash SHA256 do JWT para validação)
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        comment="Hash SHA256 do JWT para identificação única da sessão"
    )

    # Informações de rede
    ip_address: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Endereço IP do cliente"
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="User agent do navegador/app"
    )

    # Controle temporal
    inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="Data/hora de início da sessão"
    )

    ultimo_heartbeat: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        comment="Última atividade do usuário (atualizado a cada requisição)"
    )

    expira_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        comment="Data/hora de expiração da sessão (inicio + 30min de inatividade)"
    )

    # Status: ATIVA, EXPIRADA, ENCERRADA
    status: Mapped[str] = mapped_column(
        String(20),
        default="ATIVA",
        index=True,
        comment="ATIVA (em uso), EXPIRADA (timeout), ENCERRADA (logout manual)"
    )

    # Índice composto para queries de limite de usuários
    __table_args__ = (
        Index(
            'idx_sessoes_limite_grupo',
            'tenant_id',
            'grupo_fazendas_id',
            'status',
            'expira_em'
        ),
        Index(
            'idx_sessoes_limpeza',
            'status',
            'expira_em'
        ),
    )
