import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, Date, Integer
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

    # Relacionamento com tokens de recuperação de senha
    tokens_recuperacao: Mapped[list["TokenRecuperacaoSenha"]] = relationship("TokenRecuperacaoSenha", back_populates="usuario", lazy="select")


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


class TokenRecuperacaoSenha(Base):
    """
    Token de recuperação de senha com expiração de 1 hora.
    
    Usado para implementar recuperação de senha por e-mail:
    - Geração de token único e seguro
    - Expiração automática após 1 hora
    - Invalidação após uso (single-use)
    - Rastreamento de IP de criação e uso
    """
    __tablename__ = "tokens_recuperacao_senha"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    utilizado: Mapped[bool] = mapped_column(Boolean, default=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    data_expiracao: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_utilizacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    ip_origem: Mapped[str | None] = mapped_column(String(45))  # IPv6 max = 45 chars
    ip_utilizacao: Mapped[str | None] = mapped_column(String(45))
    
    # Relacionamento
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="tokens_recuperacao")


class TentativaLogin(Base):
    """
    Registro de tentativas de login para rate limiting e segurança.

    Usado para implementar:
    - Rate limiting: 5 tentativas por 15 minutos
    - Bloqueio automático após 5 falhas
    - Prevenção de brute-force attacks
    """
    __tablename__ = "login_tentativas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(45))  # IPv6 max = 45 chars
    user_agent: Mapped[str | None] = mapped_column(String(500))

    sucesso: Mapped[bool] = mapped_column(Boolean, default=False)
    motivo_falha: Mapped[str | None] = mapped_column(String(100))  # SENHA_INVALIDA, USUARIO_INATIVO, USUARIO_NAO_ENCONTRADO

    tentativas_count: Mapped[int] = mapped_column(Integer, default=1)

    # Bloqueio automático após 5 falhas
    bloqueado: Mapped[bool] = mapped_column(Boolean, default=False)
    data_bloqueio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_desbloqueio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # Automático após 15 min

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
