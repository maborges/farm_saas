import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base

class Fornecedor(Base):
    __tablename__ = "compras_fornecedores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    
    nome_fantasia: Mapped[str] = mapped_column(String(150), nullable=False)
    razao_social: Mapped[str | None] = mapped_column(String(150))
    cnpj_cpf: Mapped[str | None] = mapped_column(String(20), index=True)
    email: Mapped[str | None] = mapped_column(String(100))
    telefone: Mapped[str | None] = mapped_column(String(20))

class PedidoCompra(Base):
    """Solicitação de compra interna ou cotação."""
    __tablename__ = "compras_pedidos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    usuario_solicitante_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    
    data_pedido: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # ABERTO, COTACAO, APROVADO, EM_RECEBIMENTO, RECEBIDO, RECEBIDO_PARCIAL, CANCELADO
    status: Mapped[str] = mapped_column(String(30), default="ABERTO")

    deposito_destino_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_depositos.id"), nullable=True)
    data_recebimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(500))

class ItemPedidoCompra(Base):
    __tablename__ = "compras_itens_pedido"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pedido_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compras_pedidos.id", ondelete="CASCADE"))
    produto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_produtos.id"))

    quantidade_solicitada: Mapped[float] = mapped_column(Float, nullable=False)
    preco_estimado_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    quantidade_recebida: Mapped[float] = mapped_column(Float, default=0.0)
    preco_real_unitario: Mapped[float | None] = mapped_column(Float, nullable=True)
    # PENDENTE, PARCIAL, COMPLETO, CANCELADO
    status_item: Mapped[str] = mapped_column(String(20), default="PENDENTE")

class RecebimentoParcial(Base):
    """Registro de um recebimento (total ou parcial) de um pedido de compra."""
    __tablename__ = "compras_recebimentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pedido_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compras_pedidos.id", ondelete="CASCADE"), index=True)
    data_recebimento: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    numero_nf: Mapped[str | None] = mapped_column(String(50), nullable=True)
    chave_nfe: Mapped[str | None] = mapped_column(String(60), nullable=True)
    recebido_por_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(500), nullable=True)


class ItemRecebimento(Base):
    __tablename__ = "compras_recebimentos_itens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recebimento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compras_recebimentos.id", ondelete="CASCADE"))
    item_pedido_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compras_itens_pedido.id"))
    quantidade_recebida: Mapped[float] = mapped_column(Float, nullable=False)
    preco_real_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_lotes.id"), nullable=True)


class DevolucaoFornecedor(Base):
    """Devolução de mercadoria ao fornecedor."""
    __tablename__ = "compras_devolucoes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    pedido_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("compras_pedidos.id"), nullable=True)
    fornecedor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compras_fornecedores.id"))
    data_devolucao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # DEFEITO, QUANTIDADE_ERRADA, FORA_SPEC, VENCIDO, OUTRO
    motivo: Mapped[str] = mapped_column(String(30), nullable=False)
    # ABERTA, ENVIADA, CONCLUIDA, RECUSADA
    status: Mapped[str] = mapped_column(String(20), default="ABERTA")
    numero_nf_devolucao: Mapped[str | None] = mapped_column(String(50), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(500), nullable=True)


class ItemDevolucao(Base):
    __tablename__ = "compras_devolucoes_itens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    devolucao_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compras_devolucoes.id", ondelete="CASCADE"))
    produto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_produtos.id"))
    deposito_origem_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_depositos.id"))
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_lotes.id"), nullable=True)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    custo_unitario: Mapped[float] = mapped_column(Float, default=0.0)


class CotacaoFornecedor(Base):
    """Resposta de um fornecedor a um pedido de compra."""
    __tablename__ = "compras_cotacoes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pedido_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compras_pedidos.id", ondelete="CASCADE"))
    fornecedor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("compras_fornecedores.id"))
    
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    prazo_entrega_dias: Mapped[int | None] = mapped_column(Integer)
    condicoes_pagamento: Mapped[str | None] = mapped_column(String(200))
    vencimento_cotacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    selecionada: Mapped[bool] = mapped_column(Boolean, default=False)
