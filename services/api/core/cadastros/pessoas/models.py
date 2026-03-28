import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TipoPessoa(str, enum.Enum):
    PF = "PF"
    PJ = "PJ"


class BaseLegal(str, enum.Enum):
    CONTRATO            = "CONTRATO"           # Art. 7, V
    CONSENTIMENTO       = "CONSENTIMENTO"      # Art. 7, I
    INTERESSE_LEGITIMO  = "INTERESSE_LEGITIMO" # Art. 7, IX
    OBRIGACAO_LEGAL     = "OBRIGACAO_LEGAL"    # Art. 7, II
    EXECUCAO_POLITICAS  = "EXECUCAO_POLITICAS" # Art. 7, III


class TipoDocumento(str, enum.Enum):
    CPF        = "CPF"
    CNPJ       = "CNPJ"
    RG         = "RG"
    IE         = "IE"           # Inscrição Estadual
    PASSAPORTE = "PASSAPORTE"
    CNH        = "CNH"
    OUTRO      = "OUTRO"


class TipoContato(str, enum.Enum):
    CELULAR   = "CELULAR"
    TELEFONE  = "TELEFONE"
    EMAIL     = "EMAIL"
    WHATSAPP  = "WHATSAPP"
    SITE      = "SITE"
    OUTRO     = "OUTRO"


class TipoEndereco(str, enum.Enum):
    PRINCIPAL = "PRINCIPAL"
    ENTREGA   = "ENTREGA"
    COBRANCA  = "COBRANCA"
    RURAL     = "RURAL"


class TipoConta(str, enum.Enum):
    CORRENTE  = "CORRENTE"
    POUPANCA  = "POUPANCA"
    SALARIO   = "SALARIO"
    PIX       = "PIX"


# ---------------------------------------------------------------------------
# Pessoa — entidade base, dados NÃO sensíveis
# ---------------------------------------------------------------------------

class Pessoa(Base):
    """
    Entidade central: qualquer indivíduo ou organização relacionada ao tenant.
    Dados de identificação (PII) ficam em PessoaDocumento.
    Dados de contato ficam em PessoaContato.
    Papéis (fornecedor, funcionário, cliente...) ficam em PessoaRelacionamento.
    """
    __tablename__ = "cadastros_pessoas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tipo: Mapped[str] = mapped_column(String(2), nullable=False, comment="PF | PJ")
    nome_exibicao: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # LGPD — Art. 6 e 7
    base_legal: Mapped[str] = mapped_column(String(30), nullable=False, default="CONTRATO")
    reter_dados_ate: Mapped[date | None] = mapped_column(Date, nullable=True)
    anonimizado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="Atributos customizados por tenant")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    documentos: Mapped[list["PessoaDocumento"]] = relationship(back_populates="pessoa", lazy="noload", cascade="all, delete-orphan")
    contatos: Mapped[list["PessoaContato"]] = relationship(back_populates="pessoa", lazy="noload", cascade="all, delete-orphan")
    enderecos: Mapped[list["PessoaEndereco"]] = relationship(back_populates="pessoa", lazy="noload", cascade="all, delete-orphan")
    dados_bancarios: Mapped[list["PessoaBancario"]] = relationship(back_populates="pessoa", lazy="noload", cascade="all, delete-orphan")
    relacionamentos: Mapped[list["PessoaRelacionamento"]] = relationship(back_populates="pessoa", lazy="noload", cascade="all, delete-orphan")
    consentimentos: Mapped[list["PessoaConsentimento"]] = relationship(back_populates="pessoa", lazy="noload", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# PessoaDocumento — PII de identificação (1:N, cada doc é uma linha)
# ---------------------------------------------------------------------------

class PessoaDocumento(Base):
    """
    Documentos de identificação tipados.
    Separados da Pessoa para facilitar criptografia e anonimização seletiva (LGPD).
    Uma pessoa PJ pode ter CNPJ + IE; uma PF pode ter CPF + RG + CNH.
    """
    __tablename__ = "cadastros_pessoas_documentos"
    __table_args__ = (
        UniqueConstraint("pessoa_id", "tipo", name="uq_pessoa_documento_tipo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tipo: Mapped[str] = mapped_column(String(20), nullable=False, comment="CPF | CNPJ | RG | IE | PASSAPORTE | CNH | OUTRO")
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    orgao_emissor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    data_emissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_validade: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Dados complementares por tipo (PJ)
    razao_social: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="Apenas para CNPJ")
    nome_fantasia: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="Apenas para CNPJ")
    data_fundacao: Mapped[date | None] = mapped_column(Date, nullable=True, comment="Apenas para CNPJ")

    # Dados complementares por tipo (PF)
    nome_completo: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="Apenas para CPF")
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True, comment="Apenas para CPF")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    pessoa: Mapped["Pessoa"] = relationship(back_populates="documentos", lazy="noload")


# ---------------------------------------------------------------------------
# PessoaContato — telefones, emails, site (1:N, múltiplos por pessoa)
# ---------------------------------------------------------------------------

class PessoaContato(Base):
    """
    Contatos tipados. Uma pessoa pode ter vários contatos de tipos diferentes.
    O campo 'principal' marca o contato preferencial por tipo.
    """
    __tablename__ = "cadastros_pessoas_contatos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tipo: Mapped[str] = mapped_column(String(20), nullable=False, comment="CELULAR | TELEFONE | EMAIL | WHATSAPP | SITE | OUTRO")
    valor: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Ex: 'Contato financeiro', 'WhatsApp pessoal'")
    principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    pessoa: Mapped["Pessoa"] = relationship(back_populates="contatos", lazy="noload")


# ---------------------------------------------------------------------------
# PessoaEndereco — endereços múltiplos e tipados (1:N)
# ---------------------------------------------------------------------------

class PessoaEndereco(Base):
    __tablename__ = "cadastros_pessoas_enderecos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tipo: Mapped[str] = mapped_column(String(20), default="PRINCIPAL", comment="PRINCIPAL | ENTREGA | COBRANCA | RURAL")
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
    principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    pessoa: Mapped["Pessoa"] = relationship(back_populates="enderecos", lazy="noload")


# ---------------------------------------------------------------------------
# PessoaBancario — dados bancários múltiplos (1:N)
# ---------------------------------------------------------------------------

class PessoaBancario(Base):
    """
    Contas bancárias e chaves PIX. PII de alto risco — candidato a criptografia.
    Uma pessoa pode ter múltiplas contas (ex: corrente + PIX + poupança).
    O campo 'principal' marca a conta padrão para pagamentos.
    """
    __tablename__ = "cadastros_pessoas_bancario"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tipo_conta: Mapped[str] = mapped_column(String(20), nullable=False, comment="CORRENTE | POUPANCA | SALARIO | PIX")
    banco_codigo: Mapped[str | None] = mapped_column(String(10), nullable=True)
    banco_nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    agencia: Mapped[str | None] = mapped_column(String(10), nullable=True)
    conta: Mapped[str | None] = mapped_column(String(20), nullable=True)
    chave_pix: Mapped[str | None] = mapped_column(String(150), nullable=True)

    # O titular pode ser diferente (ex: conta de empresa para pessoa física)
    titular_nome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    titular_cpf_cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True)

    principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    pessoa: Mapped["Pessoa"] = relationship(back_populates="dados_bancarios", lazy="noload")


# ---------------------------------------------------------------------------
# TipoRelacionamento — papéis configuráveis (sistema + por tenant)
# ---------------------------------------------------------------------------

class TipoRelacionamento(Base):
    """
    Catálogo de papéis que uma Pessoa pode assumir.
    Registros com tenant_id=NULL são padrão do sistema (não editáveis).
    Cada tenant pode criar seus próprios tipos adicionais.
    """
    __tablename__ = "cadastros_tipos_relacionamento"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True,
        comment="NULL = padrão do sistema"
    )

    codigo: Mapped[str] = mapped_column(String(50), nullable=False, index=True,
        comment="FORNECEDOR | CLIENTE | FUNCIONARIO | PRESTADOR | PARCEIRO | CONTADOR | OUTRO")
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cor: Mapped[str] = mapped_column(String(7), default="#6B7280")   # hex
    icone: Mapped[str] = mapped_column(String(50), default="user")   # lucide icon
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, comment="True = não editável pelo tenant")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


# ---------------------------------------------------------------------------
# PessoaRelacionamento — pivot pessoa ↔ papel ↔ fazenda (contexto)
# ---------------------------------------------------------------------------

class PessoaRelacionamento(Base):
    """
    Uma Pessoa pode ter múltiplos papéis, inclusive em fazendas diferentes.
    Ex: João é FUNCIONARIO na Fazenda A e PRESTADOR na Fazenda B.
    """
    __tablename__ = "cadastros_pessoa_relacionamentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_tipos_relacionamento.id"), nullable=False, index=True
    )
    fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id"), nullable=True, index=True
    )

    ativo_desde: Mapped[date | None] = mapped_column(Date, nullable=True)
    ativo_ate: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    pessoa: Mapped["Pessoa"] = relationship(back_populates="relacionamentos", lazy="noload")
    tipo: Mapped["TipoRelacionamento"] = relationship(lazy="noload")


# ---------------------------------------------------------------------------
# PessoaConsentimento — rastreio LGPD (append-only)
# ---------------------------------------------------------------------------

class PessoaConsentimento(Base):
    """Rastreio de consentimento LGPD — Art. 7, I + Art. 9. Nunca deletar."""
    __tablename__ = "cadastros_pessoas_consentimentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    finalidade: Mapped[str] = mapped_column(String(50), nullable=False, comment="OPERACIONAL | MARKETING | ANALYTICS")
    concedido: Mapped[bool] = mapped_column(Boolean, nullable=False)
    canal: Mapped[str] = mapped_column(String(20), default="WEB", comment="WEB | APP | PRESENCIAL | IMPORTACAO")
    ip_origem: Mapped[str | None] = mapped_column(String(45), nullable=True)
    versao_politica: Mapped[str | None] = mapped_column(String(20), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    pessoa: Mapped["Pessoa"] = relationship(back_populates="consentimentos", lazy="noload")


# ---------------------------------------------------------------------------
# PessoaAcessoLog — audit trail LGPD (append-only)
# ---------------------------------------------------------------------------

class PessoaAcessoLog(Base):
    """Audit trail para acesso a dados PII — LGPD Art. 37. Nunca deletar."""
    __tablename__ = "cadastros_pessoas_acesso_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    campos_acessados: Mapped[list | None] = mapped_column(JSON, nullable=True)
    motivo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# PessoaPII — dados sensíveis separados (backwards-compat)
# ---------------------------------------------------------------------------

class PessoaPII(Base):
    """Dados PII sensíveis separados para facilitar anonimização LGPD."""
    __tablename__ = "cadastros_pessoas_pii"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    # PF
    nome_completo: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rg: Mapped[str | None] = mapped_column(String(30), nullable=True)
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    nome_mae: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # PJ
    razao_social: Mapped[str | None] = mapped_column(String(200), nullable=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ie: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="Inscrição Estadual")
    data_fundacao: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
