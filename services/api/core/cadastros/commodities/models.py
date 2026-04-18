import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    String, Boolean, DateTime, Float, ForeignKey, Text, JSON,
    UniqueConstraint, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TipoCommodity(str, enum.Enum):
    AGRICOLA = "AGRICOLA"
    PECUARIA = "PECUARIA"
    FLORESTAL = "FLORESTAL"


# Unidades com peso fixo (devem ter peso_unidade preenchido)
UNIDADES_PESO_FIXO = {"SACA_60KG", "TONELADA", "KG", "ARROBA"}

# Unidades sem peso fixo (peso_unidade deve ser None)
UNIDADES_SEM_PESO_FIXO = {"CABECA", "LITRO", "M3", "UNIDADE"}


class UnidadeCommodity(str, enum.Enum):
    SACA_60KG = "SACA_60KG"
    TONELADA = "TONELADA"
    KG = "KG"
    ARROBA = "ARROBA"
    CABECA = "CABECA"
    LITRO = "LITRO"
    M3 = "M3"
    UNIDADE = "UNIDADE"


# ---------------------------------------------------------------------------
# Commodity — padrão de mercado para comercialização
# ---------------------------------------------------------------------------

class Commodity(Base):
    """
    Commodity é uma categoria padronizada de mercado utilizada para comercialização.
    NÃO é o resultado da safra — define como o produto é NEGOCIADO, não como é produzido.

    Regras:
    - peso_unidade só pode ser usado em unidades fixas (SACA_60KG, TONELADA, KG, ARROBA)
    - nome deve ser único por tenant
    - codigo deve ser único globalmente
    """
    __tablename__ = "cadastros_commodities"
    __table_args__ = (
        UniqueConstraint("tenant_id", "nome", name="uq_commodity_tenant_nome"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    sistema: Mapped[bool] = mapped_column(Boolean, default=False)

    # Identificação
    nome: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Classificação
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    unidade_padrao: Mapped[str] = mapped_column(String(20), nullable=False)
    peso_unidade: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Peso em kg da unidade padrão. Obrigatório para SACA_60KG, TONELADA, KG, ARROBA. Null para CABECA, LITRO, etc."
    )

    # Parâmetros de qualidade padrão (para cálculos de romaneio)
    umidade_padrao_pct: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Umidade padrão MAPA para descontos. Ex: 14.0 para soja, 12.0 para café"
    )
    impureza_padrao_pct: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Impureza padrão aceita sem desconto. Ex: 1.0"
    )

    # Cotação de mercado
    possui_cotacao: Mapped[bool] = mapped_column(Boolean, default=False)
    bolsa_referencia: Mapped[str | None] = mapped_column(String(100), nullable=True)
    codigo_bolsa: Mapped[str | None] = mapped_column(String(100), nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos
    classificacoes: Mapped[list["CommodityClassificacao"]] = relationship(
        back_populates="commodity", lazy="noload", cascade="all, delete-orphan"
    )
    cotacoes: Mapped[list["CotacaoCommodity"]] = relationship(
        back_populates="commodity", lazy="noload", cascade="all, delete-orphan"
    )
    conversoes: Mapped[list["ConversaoUnidade"]] = relationship(
        back_populates="commodity", lazy="noload", cascade="all, delete-orphan"
    )
    # safras: Mapped[list["Safra"]] = relationship(back_populates="commodity", lazy="noload")


# Importação no final para registrar ConversaoUnidade no mapper registry sem circular import
from core.cadastros.commodities.conversao import ConversaoUnidade as ConversaoUnidade  # noqa: E402, F401


# ---------------------------------------------------------------------------
# CommodityClassificacao — classes de qualidade por commodity
# ---------------------------------------------------------------------------

class CommodityClassificacao(Base):
    """
    Classes de qualidade para uma commodity.
    Ex: TIPO_1, TIPO_2, FORA_TIPO, ESPECIAL, PREMIUM.

    Define limites máximos para umidade, impureza, avariados, etc.
    Pertence à commodity — NÃO ao produto colhido.
    """
    __tablename__ = "cadastros_commodities_classificacoes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commodity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_commodities.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    classe: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="TIPO_1 | TIPO_2 | FORA_TIPO | ESPECIAL | PREMIUM"
    )
    descricao: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Limites máximos por classe
    umidade_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    impureza_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    avariados_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    ardidos_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    esverdeados_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    quebrados_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Descontos por ponto fora do padrão
    desconto_umidade_por_ponto: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Desconto % por ponto de umidade acima do máximo"
    )
    desconto_impureza_por_ponto: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Desconto % por ponto de impureza acima do máximo"
    )

    parametros_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relacionamentos
    commodity: Mapped["Commodity"] = relationship(back_populates="classificacoes", lazy="noload")


# ---------------------------------------------------------------------------
# CotacaoCommodity — histórico de cotações de mercado
# ---------------------------------------------------------------------------

class CotacaoCommodity(Base):
    """
    Histórico de cotações diárias para commodities com preço de mercado.
    Usado para cálculo de receita, projeções e integração financeira.
    """
    __tablename__ = "cadastros_commodities_cotacoes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commodity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_commodities.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    data: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    preco: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, comment="Preço na unidade padrão da commodity")
    moeda: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")
    fonte: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Fonte da cotação: CEPEA, B3, CONAB, MANUAL"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    commodity: Mapped["Commodity"] = relationship(back_populates="cotacoes", lazy="noload")

    __table_args__ = (
        UniqueConstraint("commodity_id", "data", "fonte", name="uq_cotacao_commodity_data_fonte"),
    )
