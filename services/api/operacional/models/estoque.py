import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, JSON, Float, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from sqlalchemy import Uuid as UUID
from core.database import Base

class Deposito(Base):
    """Armazéns, galpões ou tanques de combustível."""
    __tablename__ = "estoque_depositos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    unidade_produtiva_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("unidades_produtivas.id"), index=True)
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), default="GERAL") # GERAL, COMBUSTIVEL, DEFENSIVOS, PECAS
    localizacao_desc: Mapped[str | None] = mapped_column(String(200))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

class SaldoEstoque(Base):
    """Ponte entre Produto e Depósito para controle de quantidade atual."""
    __tablename__ = "estoque_saldos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deposito_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_depositos.id", ondelete="CASCADE"), index=True)
    produto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_produtos.id", ondelete="CASCADE"), index=True)
    
    quantidade_atual: Mapped[float] = mapped_column(Float, default=0.0)
    quantidade_reservada: Mapped[float] = mapped_column(Float, default=0.0)
    ultima_atualizacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class LoteEstoque(Base):
    """Rastreabilidade por lote de produto (defensivos, sementes, ração)."""
    __tablename__ = "estoque_lotes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_produtos.id", ondelete="CASCADE"), index=True)
    deposito_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_depositos.id", ondelete="CASCADE"), index=True)

    numero_lote: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    data_fabricacao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_validade: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    quantidade_inicial: Mapped[float] = mapped_column(Float, default=0.0)
    quantidade_atual: Mapped[float] = mapped_column(Float, default=0.0)
    custo_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    nota_fiscal_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ATIVO, VENCIDO, ESGOTADO, BLOQUEADO
    status: Mapped[str] = mapped_column(String(20), default="ATIVO")
    lote_beneficiamento_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True, comment="FK rastreabilidade: qual lote beneficiamento originou este estoque")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RequisicaoMaterial(Base):
    """Solicitação interna de material ao almoxarifado."""
    __tablename__ = "estoque_requisicoes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    unidade_produtiva_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("unidades_produtivas.id"), index=True)
    solicitante_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    aprovador_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    data_solicitacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    data_necessidade: Mapped[date | None] = mapped_column(Date, nullable=True)
    # PENDENTE, APROVADA, SEPARANDO, ENTREGUE, RECUSADA, CANCELADA
    status: Mapped[str] = mapped_column(String(20), default="PENDENTE")
    # ORDEM_SERVICO, MANUTENCAO, PRODUCAO, OUTRO
    origem_tipo: Mapped[str] = mapped_column(String(30), default="OUTRO")
    origem_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(500), nullable=True)


class ItemRequisicao(Base):
    __tablename__ = "estoque_requisicoes_itens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requisicao_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_requisicoes.id", ondelete="CASCADE"))
    produto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_produtos.id"))
    deposito_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_depositos.id"), nullable=True)
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_lotes.id"), nullable=True)
    quantidade_solicitada: Mapped[float] = mapped_column(Float, nullable=False)
    quantidade_aprovada: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantidade_entregue: Mapped[float | None] = mapped_column(Float, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ReservaEstoque(Base):
    """Bloqueio de saldo para uso futuro garantido (OS, safra, pedido)."""
    __tablename__ = "estoque_reservas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    produto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_produtos.id", ondelete="CASCADE"), index=True)
    deposito_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_depositos.id", ondelete="CASCADE"), index=True)
    criado_por_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    motivo: Mapped[str] = mapped_column(String(255), nullable=False)
    # ORDEM_SERVICO, PEDIDO_COMPRA, SAFRA, REQUISICAO, MANUAL
    referencia_tipo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    referencia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    # ATIVA, CONSUMIDA, CANCELADA
    status: Mapped[str] = mapped_column(String(20), default="ATIVA", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EstoqueMovimento(Base):
    """Ledger append-only de estoque. Correções são novos movimentos via ajuste_de."""
    __tablename__ = "estoque_movimentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    data_movimento: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    tipo_movimento: Mapped[str] = mapped_column(String(24), nullable=False)

    produto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_produtos.id", ondelete="RESTRICT"), nullable=False, index=True)
    deposito_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_depositos.id", ondelete="SET NULL"), nullable=True, index=True)
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("estoque_lotes.id", ondelete="SET NULL"), nullable=True, index=True)

    quantidade: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    unidade_medida_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("unidades_medida.id", ondelete="RESTRICT"), nullable=False)
    custo_unitario: Mapped[float | None] = mapped_column(Numeric(15, 6), nullable=True)
    custo_total: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    origem: Mapped[str] = mapped_column(String(32), nullable=False)
    origem_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    operacao_execucao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("operacoes_execucoes.id", ondelete="SET NULL"), nullable=True
    )
    production_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production_units.id", ondelete="SET NULL"), nullable=True
    )
    numero_lote: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ajuste_de: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("estoque_movimentos.id", ondelete="SET NULL"), nullable=True
    )
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Compatibilidade com o nomeado antigo usado em serviços/routers legados.
    data_movimentacao = synonym("data_movimento")
    tipo = synonym("tipo_movimento")
    origem_tipo = synonym("origem")
    motivo = synonym("observacoes")

    def __init__(self, **kwargs):
        legacy_to_current = {
            "data_movimentacao": "data_movimento",
            "tipo": "tipo_movimento",
            "origem_tipo": "origem",
            "motivo": "observacoes",
        }
        for legacy_key, current_key in legacy_to_current.items():
            if legacy_key in kwargs and current_key not in kwargs:
                kwargs[current_key] = kwargs.pop(legacy_key)

        # Chamadas legadas ainda passam usuario_id, mas o ledger atual não usa esse campo.
        kwargs.pop("usuario_id", None)

        super().__init__(**kwargs)
