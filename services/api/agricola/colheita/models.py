"""
ProdutoColhido — entidade que representa o resultado da colheita já classificado.

Fluxo conceitual:
    Produção → Classificação → Padronização → Comercialização

ProdutoColhido fica entre a colheita (Romaneio) e a venda (Comercializacao futura).
Controla rastreabilidade: de qual safra/talhão veio, qual classificação recebeu,
qual qualidade foi medida no momento da entrada em armazém.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Date, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base


class ProdutoColhido(Base):
    """
    Lote de produto colhido classificado e padronizado.

    Representa a entrada real em estoque/armazém após a colheita,
    com qualidade medida e classificação de mercado atribuída.
    """
    __tablename__ = "agricola_produtos_colhidos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Origem
    safra_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    talhao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True
    )
    romaneio_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("romaneios_colheita.id", ondelete="SET NULL"), nullable=True, index=True,
        comment="Romaneio de colheita que originou este lote (pode ser null se entrada manual)"
    )

    # O que é
    commodity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_commodities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    classificacao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_commodities_classificacoes.id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="Classificação de mercado atribuída (TIPO_1, PREMIUM, etc.)"
    )

    # Quantidade
    quantidade: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, comment="Quantidade na unidade da commodity")
    unidade: Mapped[str] = mapped_column(String(20), nullable=False, comment="Unidade de medida (herdada da commodity)")
    peso_liquido_kg: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, comment="Peso líquido real em kg")

    # Qualidade medida no momento da entrada
    umidade_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    impureza_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    avariados_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    ardidos_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    quebrados_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Destino / localização
    destino: Mapped[str | None] = mapped_column(
        String(30), nullable=True,
        comment="ARMAZEM | TERCEIRO | VENDIDO | TRANSITO"
    )
    armazem_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="Depósito/armazém onde está fisicamente"
    )

    # Datas
    data_entrada: Mapped[date] = mapped_column(Date, nullable=False)
    data_saida_prevista: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Rastreabilidade extra
    nf_origem: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="NF de origem se veio de terceiro")
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Status do lote
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="ARMAZENADO",
        comment="ARMAZENADO | RESERVADO | EM_TRANSITO | VENDIDO | PERDA"
    )

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    # Relacionamentos (lazy=noload para evitar N+1)
    # safra: Mapped["Safra"] = relationship(back_populates="produtos_colhidos", lazy="noload")
    # commodity: Mapped["Commodity"] = relationship(back_populates="produtos_colhidos", lazy="noload")
    # classificacao: Mapped["CommodityClassificacao"] = relationship(back_populates="produtos_colhidos", lazy="noload")
