import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, JSON, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from core.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    documento: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )  # CPF/CNPJ
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Controle de SaaS e Billing
    modulos_ativos: Mapped[list[str]] = mapped_column(
        JSON, default=list
    )  # Ex: ["CORE", "A1", "A2", "O1", "P1"]
    max_usuarios_simultaneos: Mapped[int] = mapped_column(default=5)

    # Storage
    storage_usado_mb: Mapped[int] = mapped_column(Integer, default=0)
    storage_limite_mb: Mapped[int] = mapped_column(Integer, default=10240)  # 10GB padrão

    # Último acesso
    data_ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Contato
    email_responsavel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone_responsavel: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Branding e White-Label
    slug: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    dominio_customizado: Mapped[str | None] = mapped_column(
        String(150), unique=True, index=True
    )
    
    # Onboarding — token de ativação enviado por email após conversão de lead
    activation_token: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    activation_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Guarda o JSON de cores, logo e tema do cliente
    branding: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Configurações de e-mail próprias do produtor (White-label SMTP)
    smtp_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Idioma default configurado para o Tenant (Fallback se os usuarios não definirem)
    idioma_padrao: Mapped[str] = mapped_column(String(10), default="pt-BR")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relacionamentos (Evitar load automático para não inflar queries)
    # fazendas: Mapped[list["Fazenda"]] = relationship("Fazenda", back_populates="tenant")
