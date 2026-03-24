import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class PlanoConta(Base):
    """
    Plano de Contas — categorias de receitas e despesas.

    Suporta estrutura hierárquica (pai/filho) via parent_id.
    Natureza SINTETICA = grupo (não aceita lançamentos diretos).
    Natureza ANALITICA = folha (aceita lançamentos).
    categoria_rfb mapeia para os grupos do Livro Caixa do Produtor Rural (RFB).
    is_sistema = True protege categorias padrão contra exclusão.
    """
    __tablename__ = "fin_planos_conta"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Hierarquia
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_planos_conta.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Conta pai (NULL = nível raiz)"
    )

    codigo: Mapped[str] = mapped_column(String(20), nullable=False, comment="Ex: 3.01.02")
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # RECEITA ou DESPESA
    tipo: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # SINTETICA (grupo) ou ANALITICA (folha — aceita lançamentos)
    natureza: Mapped[str] = mapped_column(String(10), default="ANALITICA", nullable=False)

    # Categoria RFB para Livro Caixa do Produtor Rural
    # Ex: "CUSTEIO", "INVESTIMENTO", "RECEITA_ATIVIDADE", "NAO_DEDUTIVEL"
    categoria_rfb: Mapped[str | None] = mapped_column(
        String(30), nullable=True,
        comment="Classificação RFB para Livro Caixa do Produtor Rural"
    )

    # Ordem de exibição dentro do mesmo nível
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Categorias de sistema não podem ser deletadas
    is_sistema: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
