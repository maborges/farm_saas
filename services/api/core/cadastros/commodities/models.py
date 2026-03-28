import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TipoCommodity(str, enum.Enum):
    # Grãos e oleaginosas
    SOJA        = "SOJA"
    MILHO       = "MILHO"
    TRIGO       = "TRIGO"
    ARROZ       = "ARROZ"
    FEIJAO      = "FEIJAO"
    SORGO       = "SORGO"
    GIRASSOL    = "GIRASSOL"
    CANOLA      = "CANOLA"

    # Fibras
    ALGODAO     = "ALGODAO"
    SISAL       = "SISAL"

    # Frutas / horticultura
    CAFE        = "CAFE"
    CANA        = "CANA"
    LARANJA     = "LARANJA"
    OUTRO_FRUTA = "OUTRO_FRUTA"

    # Pecuária
    BOVINO_CORTE   = "BOVINO_CORTE"
    BOVINO_LEITE   = "BOVINO_LEITE"    # leite produzido
    SUINO          = "SUINO"
    AVES           = "AVES"
    OVINOS         = "OVINOS"

    OUTRO       = "OUTRO"


class UnidadeCommodity(str, enum.Enum):
    SACA_60KG   = "SACA_60KG"
    SACA_40KG   = "SACA_40KG"
    TONELADA    = "TONELADA"
    KG          = "KG"
    ARROBA      = "ARROBA"      # @ = 15kg
    LITRO       = "LITRO"       # leite
    CABECA      = "CABECA"      # animais
    CAIXA       = "CAIXA"


# ---------------------------------------------------------------------------
# Commodity — produto de SAÍDA (resultado da produção)
# ---------------------------------------------------------------------------

class Commodity(Base):
    """
    Produtos gerados pela atividade produtiva rural.
    Estes geram RECEITA ao serem vendidos.

    Diferente de Produto (insumo/almoxarifado):
      - Não entra via compra, entra via colheita / produção
      - Tem padrões de qualidade (umidade, impureza, classificação)
      - Preço é variável (cotação de mercado)
      - Estoque controlado em armazém, não almoxarifado

    Exemplos: soja colhida, milho, leite, boi gordo.
    """
    __tablename__ = "cadastros_commodities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True,
        comment="NULL = padrão do sistema"
    )
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, comment="True = não editável pelo tenant")

    nome: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    unidade_padrao: Mapped[str] = mapped_column(String(20), nullable=False, default="SACA_60KG")

    # Conversão de unidades (ex: 1 tonelada = 16.667 sacas)
    fator_conversao_kg: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Peso em KG de 1 unidade padrão. Ex: SACA_60KG=60, ARROBA=15"
    )

    # Padrões oficiais de qualidade (referência para classificação)
    umidade_padrao_pct: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Ex: 14.0 para soja")
    impureza_padrao_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    classificacoes: Mapped[list["CommodityClassificacao"]] = relationship(
        back_populates="commodity", lazy="noload", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# CommodityClassificacao — padrões de qualidade por classe/tipo
# ---------------------------------------------------------------------------

class CommodityClassificacao(Base):
    """
    Tabela de classificação de qualidade para uma commodity.
    Define os limites aceitos por classe (Tipo 1, Tipo 2, Fora de Tipo...).

    Baseado nas instruções normativas MAPA (ex: IN 11/2007 para soja,
    IN 60/2011 para milho).

    Usado por: romaneio_colheita, armazem_saldo, venda.
    """
    __tablename__ = "cadastros_commodities_classificacoes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commodity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_commodities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    classe: Mapped[str] = mapped_column(String(50), nullable=False, comment="TIPO_1 | TIPO_2 | FORA_TIPO | ESPECIAL | PREMIUM")
    descricao: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Limites de qualidade (máximos tolerados)
    umidade_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    impureza_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    avariados_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    ardidos_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    esverdeados_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    quebrados_max_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Desconto padrão aplicado por ponto excedente
    desconto_umidade_por_ponto: Mapped[float | None] = mapped_column(Float, nullable=True)
    desconto_impureza_por_ponto: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Outros parâmetros por commodity (ex: acidez para leite, PH para café)
    parametros_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    commodity: Mapped["Commodity"] = relationship(back_populates="classificacoes", lazy="noload")
