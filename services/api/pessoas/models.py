import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class Pessoa(Base):
    """
    Cadastro centralizado de pessoas (física ou jurídica) vinculadas ao tenant.

    Unifica fornecedores, clientes, funcionários e parceiros em uma única entidade.
    Múltiplos tipos podem ser atribuídos via campo JSON 'tipos' para casos onde
    a mesma pessoa é, por exemplo, fornecedor E cliente.

    Usado por: Financeiro (lançamentos), Compras (pedidos), RH (folha).
    """
    __tablename__ = "pessoas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Classificação
    tipo_principal: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="FORNECEDOR, CLIENTE, FUNCIONARIO, PARCEIRO, PRESTADOR, OUTRO"
    )
    tipos: Mapped[list] = mapped_column(
        JSON,
        default=list,
        comment="Lista de todos os tipos aplicáveis (ex: ['FORNECEDOR', 'CLIENTE'])"
    )

    # Identificação
    tipo_pessoa: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="PJ",
        comment="PF (pessoa física) ou PJ (pessoa jurídica)"
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cpf_cnpj: Mapped[str | None] = mapped_column(String(18), nullable=True, index=True)
    rg_ie: Mapped[str | None] = mapped_column(
        String(30), nullable=True,
        comment="RG (PF) ou Inscrição Estadual (PJ)"
    )

    # Contato
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    celular: Mapped[str | None] = mapped_column(String(20), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Endereço (desnormalizado para simplicidade)
    cep: Mapped[str | None] = mapped_column(String(9), nullable=True)
    logradouro: Mapped[str | None] = mapped_column(String(200), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    complemento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # Dados bancários (para funcionários e parceiros)
    banco_codigo: Mapped[str | None] = mapped_column(String(10), nullable=True)
    banco_agencia: Mapped[str | None] = mapped_column(String(10), nullable=True)
    banco_conta: Mapped[str | None] = mapped_column(String(20), nullable=True)
    banco_tipo_conta: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
        comment="CORRENTE, POUPANCA, PIX"
    )
    banco_chave_pix: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Metadados
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
