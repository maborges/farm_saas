import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class GrupoFazendas(Base):
    """
    Grupo de fazendas que compartilham recursos de uma assinatura.

    Permite que um tenant organize suas fazendas em grupos e atribua
    assinaturas específicas para cada grupo, possibilitando:
    - Múltiplas assinaturas por tenant
    - Limites de usuários compartilhados por grupo
    - Gestão separada de módulos por grupo

    Exemplo:
        Tenant "Agro Corp" pode ter:
        - Grupo "Fazendas Região Sul" (3 fazendas) → Assinatura PRO
        - Grupo "Fazendas Região Norte" (2 fazendas) → Assinatura BASIC
    """
    __tablename__ = "grupos_fazendas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Ex: 'Fazendas Região Sul', 'Unidades Pecuária'"
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descrição detalhada do grupo"
    )

    # Customização visual para UI
    cor: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
        comment="Cor HEX para identificação visual (ex: '#3B82F6')"
    )

    icone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Nome do ícone para UI (ex: 'MapPin', 'Building2')"
    )

    # Ordem de exibição
    ordem: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Ordem de exibição na listagem"
    )

    # Status
    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Grupos inativos são ocultados mas mantém histórico"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
