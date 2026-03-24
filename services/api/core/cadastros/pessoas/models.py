import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Text, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


class TipoPessoa(str, enum.Enum):
    PF = "PF"
    PJ = "PJ"


class BaseLegal(str, enum.Enum):
    CONTRATO = "CONTRATO"                        # Art. 7, V
    CONSENTIMENTO = "CONSENTIMENTO"              # Art. 7, I
    INTERESSE_LEGITIMO = "INTERESSE_LEGITIMO"    # Art. 7, IX
    OBRIGACAO_LEGAL = "OBRIGACAO_LEGAL"          # Art. 7, II
    EXECUCAO_POLITICAS = "EXECUCAO_POLITICAS"    # Art. 7, III


class CanalConsentimento(str, enum.Enum):
    WEB = "WEB"
    APP = "APP"
    PRESENCIAL = "PRESENCIAL"
    IMPORTACAO = "IMPORTACAO"


class TipoEndereco(str, enum.Enum):
    PRINCIPAL = "PRINCIPAL"
    ENTREGA = "ENTREGA"
    COBRANCA = "COBRANCA"
    RURAL = "RURAL"


class Pessoa(Base):
    """
    Entidade base — dados NÃO sensíveis.
    Dados PII ficam em PessoaPII (separados para facilitar anonimização LGPD).
    """
    __tablename__ = "cadastros_pessoas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)

    tipo: Mapped[str] = mapped_column(String(2), nullable=False)  # PF | PJ
    nome_exibicao: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # LGPD
    base_legal: Mapped[str] = mapped_column(String(30), nullable=False, default="CONTRATO")
    reter_dados_ate: Mapped[date | None] = mapped_column(Date, nullable=True)
    anonimizado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    relacionamentos: Mapped[list["PessoaRelacionamento"]] = relationship(
        "core.cadastros.pessoas.models.PessoaRelacionamento", back_populates="pessoa", lazy="noload"
    )


class PessoaPII(Base):
    """
    Dados pessoais identificáveis — tabela separada para anonimização seletiva.
    Em produção: colunas cpf/cnpj devem ser criptografadas (pgcrypto ou app-level).
    """
    __tablename__ = "cadastros_pessoas_pii"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), unique=True, index=True
    )

    # PF
    nome_completo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rg: Mapped[str | None] = mapped_column(String(30), nullable=True)
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)

    # PJ
    razao_social: Mapped[str | None] = mapped_column(String(200), nullable=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ie: Mapped[str | None] = mapped_column(String(30), nullable=True)  # Inscrição Estadual
    data_fundacao: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Contato (PF e PJ)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    celular: Mapped[str | None] = mapped_column(String(30), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class PessoaEndereco(Base):
    __tablename__ = "cadastros_pessoas_enderecos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), index=True
    )

    tipo: Mapped[str] = mapped_column(String(20), default="PRINCIPAL")
    cep: Mapped[str | None] = mapped_column(String(10), nullable=True)
    logradouro: Mapped[str | None] = mapped_column(String(200), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    complemento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(2), nullable=True)
    pais: Mapped[str] = mapped_column(String(3), default="BRA")
    lat: Mapped[float | None] = mapped_column(nullable=True)
    lng: Mapped[float | None] = mapped_column(nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


class TipoRelacionamento(Base):
    """
    Tipos de relacionamento: sistema (tenant_id=NULL) + personalizados por tenant.
    """
    __tablename__ = "cadastros_tipos_relacionamento"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )  # NULL = padrão do sistema

    codigo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cor: Mapped[str] = mapped_column(String(7), default="#6B7280")   # hex
    icone: Mapped[str] = mapped_column(String(50), default="user")   # lucide icon name
    sistema: Mapped[bool] = mapped_column(Boolean, default=False)     # True = não editável
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


class PessoaRelacionamento(Base):
    """Pivot: uma Pessoa pode ter múltiplos tipos de relacionamento, por fazenda."""
    __tablename__ = "cadastros_pessoa_relacionamentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), index=True
    )
    tipo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_tipos_relacionamento.id"), index=True
    )
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id"), nullable=True, index=True
    )

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo_desde: Mapped[date | None] = mapped_column(Date, nullable=True)
    ativo_ate: Mapped[date | None] = mapped_column(Date, nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    pessoa: Mapped["Pessoa"] = relationship(
        "core.cadastros.pessoas.models.Pessoa", back_populates="relacionamentos", lazy="noload"
    )
    tipo: Mapped["TipoRelacionamento"] = relationship(
        "core.cadastros.pessoas.models.TipoRelacionamento", lazy="noload"
    )


class PessoaConsentimento(Base):
    """Rastreio de consentimento LGPD — Art. 7, I + Art. 9."""
    __tablename__ = "cadastros_pessoas_consentimentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), index=True
    )

    finalidade: Mapped[str] = mapped_column(String(50), nullable=False)  # OPERACIONAL, MARKETING, ANALYTICS
    concedido: Mapped[bool] = mapped_column(Boolean, nullable=False)
    canal: Mapped[str] = mapped_column(String(20), default="WEB")
    ip_origem: Mapped[str | None] = mapped_column(String(45), nullable=True)
    versao_politica: Mapped[str | None] = mapped_column(String(20), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PessoaAcessoLog(Base):
    """Audit trail para acesso a dados PII — LGPD Art. 37."""
    __tablename__ = "cadastros_pessoas_acesso_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), index=True
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    campos_acessados: Mapped[list | None] = mapped_column(JSON, nullable=True)
    motivo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
