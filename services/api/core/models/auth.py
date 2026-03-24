import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base

class Usuario(Base):
    """Identidade global da pessoa na plataforma."""
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nome_completo: Mapped[str | None] = mapped_column(String(150))
    foto_perfil_url: Mapped[str | None] = mapped_column(String(500))
    senha_hash: Mapped[str | None] = mapped_column(String(255)) # Pode ser None se usar SSO
    
    # Feature flag para Operador Financeiro / Admin interno da AgroSaaS
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class PerfilAcesso(Base):
    """Representa um role (Padrão do sistema ou Customizado por Tenant)."""
    __tablename__ = "perfis_acesso"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Se tenant_id for NULL, é um perfil padrão do sistema global (admin, agronomo, peao)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)

    # Ex: {"agricola": "write", "financeiro": "read"}
    permissoes: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TenantUsuario(Base):
    """Vínculo de um usuário com um Tenant (Conta do Produtor/Gestor)."""
    __tablename__ = "tenant_usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    
    perfil_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("perfis_acesso.id"), nullable=True)
    
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False) # Owner não pode ser expulso
    status: Mapped[str] = mapped_column(String(20), default="ATIVO") # ATIVO, SUSPENSO
    data_validade_acesso: Mapped[date | None] = mapped_column(Date, nullable=True) # Data para prestadores temporários perderem acesso

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FazendaUsuario(Base):
    """
    Vínculo de usuário a fazendas específicas para segmentação de propriedades.

    Permite que um usuário tenha perfis diferentes por fazenda.
    Exemplo: João pode ser "financeiro" na Fazenda A e "agrônomo" na Fazenda B.
    """
    __tablename__ = "fazenda_usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    fazenda_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)

    # Perfil específico para esta fazenda (sobrescreve o perfil do TenantUsuario)
    perfil_fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("perfis_acesso.id", ondelete="SET NULL"),
        nullable=True,
        comment="Se NULL, usa o perfil do TenantUsuario. Se preenchido, sobrescreve para esta fazenda."
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ConviteAcesso(Base):
    """Convites enviados pelo assinante para membros se juntarem ao Tenant."""
    __tablename__ = "convites_acesso"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    email_convidado: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("perfis_acesso.id"), nullable=False)
    
    # JSON array de strings (uuid das fazendas)
    fazendas_ids: Mapped[list[str]] = mapped_column(JSON, default=list)

    token_convite: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDENTE") # PENDENTE, ACEITO, CANCElADO, EXPIRADO
    
    data_expiracao: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    data_validade_acesso: Mapped[date | None] = mapped_column(Date, nullable=True) # Definido já no convite

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
