import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class ProdutoCatalogo(Base):
    """
    Catálogo unificado de produtos/insumos do tenant.
    Usado por múltiplos módulos: estoque, compras, agrícola, pecuária.
    """
    __tablename__ = "cadastros_produtos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)

    nome: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    # Tipos: INSUMO_AGRICOLA | SEMENTE | DEFENSIVO | FERTILIZANTE | COMBUSTIVEL |
    #        PECA_MAQUINARIO | MATERIAL_GERAL | RACAO_ANIMAL | MEDICAMENTO_ANIMAL | SERVICO | OUTROS
    tipo: Mapped[str] = mapped_column(String(30), default="OUTROS", nullable=False, index=True)
    unidade_medida: Mapped[str] = mapped_column(String(20), default="UN")  # L, KG, UN, SACA, M3, T
    codigo_interno: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    sku: Mapped[str | None] = mapped_column(String(100), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Campos cross-cutting (usados por estoque E agrícola)
    estoque_minimo: Mapped[float] = mapped_column(Float, default=0.0)
    preco_medio: Mapped[float] = mapped_column(Float, default=0.0)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ProdutoAgricolaDetalhe(Base):
    """Extensão para produtos de uso agrícola (insumos, defensivos, sementes)."""
    __tablename__ = "cadastros_produtos_agricola"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastros_produtos.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    # Defensivos / receituário
    registro_mapa: Mapped[str | None] = mapped_column(String(50), nullable=True)
    classe_agronomica: Mapped[str | None] = mapped_column(String(50), nullable=True)  # HERBICIDA, FUNGICIDA...
    principio_ativo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    formulacao: Mapped[str | None] = mapped_column(String(50), nullable=True)  # CE, SC, WG...
    periodo_carencia_dias: Mapped[int | None] = mapped_column(nullable=True)

    # Sementes
    cultivar: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cultura: Mapped[str | None] = mapped_column(String(50), nullable=True)  # SOJA, MILHO, TRIGO...


class ProdutoEstoqueDetalhe(Base):
    """Extensão para produtos de controle de estoque físico."""
    __tablename__ = "cadastros_produtos_estoque"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastros_produtos.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    # Controle físico
    localizacao_default: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Prateleira, setor
    peso_unitario_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_unitario_l: Mapped[float | None] = mapped_column(Float, nullable=True)
    perecivel: Mapped[bool] = mapped_column(Boolean, default=False)
    prazo_validade_dias: Mapped[int | None] = mapped_column(nullable=True)
    ncm: Mapped[str | None] = mapped_column(String(10), nullable=True)
