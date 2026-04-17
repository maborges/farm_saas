import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, Float, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EspecieAnimal(str, enum.Enum):
    BOVINO      = "BOVINO"
    SUINO       = "SUINO"
    OVINO       = "OVINO"
    CAPRINO     = "CAPRINO"
    EQUINO      = "EQUINO"
    AVES        = "AVES"
    OUTRO       = "OUTRO"


class SexoAnimal(str, enum.Enum):
    MACHO       = "MACHO"
    FEMEA       = "FEMEA"
    CASTRADO    = "CASTRADO"


class CategoriaAnimal(str, enum.Enum):
    # Bovinos corte
    BEZERRO         = "BEZERRO"         # macho até desmame
    BEZERRA         = "BEZERRA"         # fêmea até desmame
    GARROTE         = "GARROTE"         # macho desmamado até 24m
    NOVILHA         = "NOVILHA"         # fêmea desmamada não parida
    BOI             = "BOI"             # castrado em engorda
    VACA_CORTE      = "VACA_CORTE"
    TOURO           = "TOURO"
    # Bovinos leite
    VACA_LEITE      = "VACA_LEITE"
    NOVILHA_LEITE   = "NOVILHA_LEITE"
    REPRODUTOR      = "REPRODUTOR"
    OUTRO           = "OUTRO"


class StatusAnimal(str, enum.Enum):
    ATIVO           = "ATIVO"
    VENDIDO         = "VENDIDO"
    ABATIDO         = "ABATIDO"
    MORTO           = "MORTO"
    TRANSFERIDO     = "TRANSFERIDO"     # saiu da fazenda para outra unidade


class TipoEvento(str, enum.Enum):
    # Entrada
    NASCIMENTO      = "NASCIMENTO"
    COMPRA          = "COMPRA"
    TRANSFERENCIA_ENTRADA = "TRANSFERENCIA_ENTRADA"

    # Produtivo
    PESAGEM         = "PESAGEM"
    DESMAME         = "DESMAME"
    CLASSIFICACAO   = "CLASSIFICACAO"   # mudança de categoria

    # Reprodutivo
    COBERTURA       = "COBERTURA"       # monta natural
    INSEMINACAO     = "INSEMINACAO"
    DIAGNOSTICO_PRENHEZ = "DIAGNOSTICO_PRENHEZ"
    PARTO           = "PARTO"
    ABORTO          = "ABORTO"

    # Sanitário
    VACINACAO       = "VACINACAO"
    MEDICACAO       = "MEDICACAO"
    EXAME           = "EXAME"
    VERMIFUGACAO    = "VERMIFUGACAO"
    BANHO_CARRAPATICIDA = "BANHO_CARRAPATICIDA"

    # Movimentação
    TRANSFERENCIA_LOTE    = "TRANSFERENCIA_LOTE"    # mudança de lote/piquete
    TRANSFERENCIA_SAIDA   = "TRANSFERENCIA_SAIDA"   # saída para outra fazenda

    # Saída
    VENDA           = "VENDA"
    ABATE           = "ABATE"
    MORTE           = "MORTE"


# ---------------------------------------------------------------------------
# LoteAnimal — agrupamento operacional de animais
# ---------------------------------------------------------------------------

class LoteAnimal(Base):
    """
    Agrupamento operacional de animais para manejo coletivo.
    Animais entram e saem do lote via EventoAnimal (TRANSFERENCIA_LOTE).

    Substitui: pec_lotes_bovinos (que misturava dados individuais com coletivos).

    piquete_id → cadastros_areas_rurais (tipo=PIQUETE)
    """
    __tablename__ = "pec_lotes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unidade_produtiva_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("unidades_produtivas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    area_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="Piquete ou pastagem atual (cadastros_areas_rurais)"
    )

    identificacao: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    especie: Mapped[str] = mapped_column(String(20), nullable=False, default="BOVINO")
    categoria: Mapped[str | None] = mapped_column(String(30), nullable=True)
    raca: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Contagem e peso calculados (desnormalizado para performance — atualizado por trigger/evento)
    quantidade_cabecas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    peso_medio_kg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    data_formacao: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    animais: Mapped[list["Animal"]] = relationship(back_populates="lote_atual", lazy="noload")


# ---------------------------------------------------------------------------
# Animal — entidade viva individual (ativo biológico — IAS 41 / CPC 29)
# ---------------------------------------------------------------------------

class Animal(Base):
    """
    Entidade central da pecuária. Representa um indivíduo vivo.

    Animal ≠ Produto. É um ativo biológico com:
      - Identidade única (brinco, microchip)
      - Genealogia (pai, mãe)
      - Ciclo de vida completo via EventoAnimal
      - Valor biológico variável

    Peso atual e status são desnormalizados para performance.
    O histórico completo está em EventoAnimal.
    """
    __tablename__ = "pec_animais"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unidade_produtiva_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("unidades_produtivas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lote_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_lotes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Identificação
    numero_brinco: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    numero_sisbov: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True, comment="SISBOV/Rastreabilidade bovina")
    microchip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nome: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Nome do animal (opcional, comum em reprodutores)")

    # Classificação
    especie: Mapped[str] = mapped_column(String(20), nullable=False, default="BOVINO")
    categoria: Mapped[str] = mapped_column(String(30), nullable=False)
    raca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sexo: Mapped[str] = mapped_column(String(10), nullable=False)
    pelagem: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Datas
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_entrada: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    # Genealogia (auto-referencial)
    pai_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_animais.id", ondelete="SET NULL"), nullable=True
    )
    mae_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_animais.id", ondelete="SET NULL"), nullable=True
    )

    # Estado atual (desnormalizado — atualizado pelo último evento relevante)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ATIVO")
    peso_atual_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_ultima_pesagem: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Valor patrimonial
    valor_aquisicao: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_atual: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Valor de mercado estimado")

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    lote_atual: Mapped["LoteAnimal | None"] = relationship(back_populates="animais", lazy="noload")
    eventos: Mapped[list["EventoAnimal"]] = relationship(back_populates="animal", lazy="noload", cascade="all, delete-orphan")
    pai: Mapped["Animal | None"] = relationship("Animal", foreign_keys=[pai_id], lazy="noload", remote_side=[id])
    mae: Mapped["Animal | None"] = relationship("Animal", foreign_keys=[mae_id], lazy="noload", remote_side=[id])


# ---------------------------------------------------------------------------
# EventoAnimal — registro imutável (append-only) de tudo que acontece
# ---------------------------------------------------------------------------

class EventoAnimal(Base):
    """
    Linha do tempo completa de um animal. Append-only — nunca deletar.

    Cada tipo de evento usa campos específicos + dados_extras JSONB:
      PESAGEM:      peso_kg
      VACINACAO:    produto_id, dose_ml, via_aplicacao
      INSEMINACAO:  reprodutor_id (ou touro externo), semen_partida
      PARTO:        quantidade_crias, crias_vivas, peso_cria_kg
      VENDA:        valor_total, comprador_id (pessoa), destino
      MORTE:        causa_morte, laudo_veterinario
      COMPRA:       valor_total, origem, vendedor_id (pessoa)
    """
    __tablename__ = "pec_eventos_animal"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    animal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_animais.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tipo: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    data_evento: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Campos comuns a múltiplos tipos
    peso_kg: Mapped[float | None] = mapped_column(Float, nullable=True, comment="PESAGEM, NASCIMENTO, COMPRA, VENDA, ABATE")
    valor: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Valor financeiro do evento (COMPRA, VENDA, MEDICACAO...)")
    lote_destino_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pec_lotes.id", ondelete="SET NULL"), nullable=True,
        comment="TRANSFERENCIA_LOTE: lote destino"
    )
    area_destino_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="SET NULL"), nullable=True,
        comment="Piquete/pastagem destino em transferências"
    )
    pessoa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"), nullable=True,
        comment="COMPRA: vendedor | VENDA: comprador | MEDICACAO: veterinário"
    )
    produto_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_produtos.id", ondelete="SET NULL"), nullable=True,
        comment="VACINACAO | MEDICACAO | VERMIFUGACAO: produto utilizado"
    )
    responsavel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    animal: Mapped["Animal"] = relationship(back_populates="eventos", lazy="noload")
