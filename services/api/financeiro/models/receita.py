import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Numeric, ForeignKey, Date, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class Receita(Base):
    """
    Receita Financeira / Contas a Receber.

    Suporta:
    - Vínculo com cliente/comprador cadastrado (pessoa_id) ou texto livre (cliente)
    - Parcelamento via grupo_parcela_id + numero_parcela/total_parcelas
    - Identificação fiscal (numero_nf, chave_nfe)
    - Competência fiscal para Livro Caixa
    """
    __tablename__ = "fin_receitas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unidade_produtiva_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("unidades_produtivas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plano_conta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fin_planos_conta.id", ondelete="RESTRICT"), nullable=False
    )

    # Vinculação com Pessoas (substitui campo texto livre cliente)
    pessoa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Cliente/comprador cadastrado. Se NULL, usar campo cliente (texto livre)"
    )

    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    valor_recebido: Mapped[float | None] = mapped_column(
        Numeric(14, 2), nullable=True,
        comment="Valor efetivamente recebido (pode ser parcial)"
    )

    data_emissao: Mapped[date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    data_recebimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    competencia: Mapped[date | None] = mapped_column(
        Date, nullable=True,
        comment="Mês/ano de competência fiscal para Livro Caixa (geralmente 1º dia do mês)"
    )

    # Status: A_RECEBER, RECEBIDO, RECEBIDO_PARCIAL, CANCELADO
    status: Mapped[str] = mapped_column(String(20), default="A_RECEBER", index=True)

    forma_recebimento: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
        comment="PIX, BOLETO, TRANSFERENCIA, DINHEIRO, CARTAO, CHEQUE"
    )

    # Parcelamento
    grupo_parcela_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True,
        comment="Agrupa todas as parcelas do mesmo lançamento parcelado"
    )
    numero_parcela: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_parcelas: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Fiscal
    numero_nf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    serie_nf: Mapped[str | None] = mapped_column(String(5), nullable=True)
    chave_nfe: Mapped[str | None] = mapped_column(String(44), nullable=True)

    # Legado (mantido por compatibilidade — preferir pessoa_id)
    cliente: Mapped[str | None] = mapped_column(String(150), nullable=True)
    nota_fiscal: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Rastreabilidade — origem do lançamento automático
    origem_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True,
        comment="ID do registro que gerou esta receita (ex: romaneios_colheita.id)"
    )
    origem_tipo: Mapped[str | None] = mapped_column(
        String(40), nullable=True,
        comment="Tipo da origem: ROMANEIO_COLHEITA, etc."
    )

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
