"""
ComercializacaoCommodity — contratos de venda de commodities.

Fecha o ciclo: Produção → Classificação → Padronização → Comercialização

Cada comercialização:
- Reserva ProdutoColhido do estoque
- Gera conta a receber no financeiro (quando confirmada)
- Rastreia entrega e pagamento
"""
import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Date, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class ComercializacaoCommodity(Base):
    """
    Contrato de venda de commodity.

    Status flow:
        RASCUNHO → CONFIRMADO → EM_TRANSITO → ENTREGUE → FINALIZADO
        Qualquer status → CANCELADO
    """
    __tablename__ = "financeiro_comercializacoes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identificação
    numero_contrato: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True, comment="Número do contrato / nota")

    # O que está sendo vendido
    commodity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_commodities.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Quem está comprando
    comprador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="RESTRICT"), nullable=False, index=True,
        comment="Pessoa/empresa compradora"
    )

    # Quantidade e preço
    quantidade: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, comment="Quantidade na unidade da commodity")
    unidade: Mapped[str] = mapped_column(String(20), nullable=False, comment="Unidade de medida (herdada da commodity)")
    preco_unitario: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, comment="Preço por unidade")
    moeda: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")

    # Valor total (calculado)
    valor_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, comment="quantidade × preco_unitario")

    # Condições de pagamento
    forma_pagamento: Mapped[str | None] = mapped_column(
        String(30), nullable=True,
        comment="A_VISTA | PRAZO | BOLETO | PIX | TRANSFERENCIA"
    )
    data_pagamento: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Entrega
    data_entrega_prevista: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_entrega_real: Mapped[date | None] = mapped_column(Date, nullable=True)
    local_entrega: Mapped[str | None] = mapped_column(
        String(200), nullable=True,
        comment="Endereço/local de entrega"
    )
    frete_por_conta: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
        comment="COMPRADOR | VENDEDOR | CIF | FOB"
    )

    # Origem (rastreabilidade)
    # Vínculo com ProdutoColhido para baixa de estoque
    produto_colhido_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agricola_produtos_colhidos.id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="Lote de produto colhido vinculado (para rastreabilidade e baixa)"
    )

    # NF-e
    nf_numero: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Número da NF-e")
    nf_serie: Mapped[str | None] = mapped_column(String(10), nullable=True)
    nf_chave: Mapped[str | None] = mapped_column(String(44), nullable=True, comment="Chave de acesso NF-e")

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="RASCUNHO",
        comment="RASCUNHO | CONFIRMADO | EM_TRANSITO | ENTREGUE | FINALIZADO | CANCELADO"
    )

    # Observações
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Financeiro (vínculo com contas a receber)
    receita_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True,
        comment="ID da Receita gerada no financeiro"
    )

    # Audit
    criado_por: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    # Relacionamentos
    # commodity: Mapped["Commodity"] = relationship(back_populates="comercializacoes", lazy="noload")
    # comprador: Mapped["Pessoa"] = relationship(back_populates="comercializacoes", lazy="noload")
