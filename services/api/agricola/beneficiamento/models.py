import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Boolean, Date, Text, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUIDCol
from core.database import Base


class LoteBeneficiamento(Base):
    """
    Lote de beneficiamento pós-colheita de café.

    Rastreia o processamento desde o recebimento do café cereja/coco
    até a saída como café beneficiado/ensacado.

    Métodos suportados:
    - NATURAL:    Seca com casca (cereja) — maior corpo, doçura
    - LAVADO:     Despolpa → fermenta → lava → seca — acidez limpa
    - HONEY:      Despolpa sem lavagem → seca com mucilagem — equilíbrio
    - DESCASCADO: Remove casca, mantém mucilagem (CD/pulped natural)
    """
    __tablename__ = "cafe_lotes_beneficiamento"

    id: Mapped[uuid.UUID] = mapped_column(UUIDCol(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUIDCol(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    safra_id: Mapped[uuid.UUID] = mapped_column(
        UUIDCol(as_uuid=True), ForeignKey("safras.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    talhao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDCol(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="SET NULL"),
        nullable=True, index=True
    )

    # Identificação do lote
    numero_lote: Mapped[str] = mapped_column(String(30), nullable=False)
    metodo: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="NATURAL, LAVADO, HONEY, DESCASCADO"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="RECEBIMENTO",
        comment="RECEBIMENTO, SECAGEM, CLASSIFICACAO, ARMAZENADO, VENDIDO"
    )

    # Entrada (café cereja/coco — alta umidade)
    data_entrada: Mapped[date] = mapped_column(Date, nullable=False)
    peso_entrada_kg: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    umidade_entrada_pct: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="Umidade na entrada: cereja ~55-65%, coco ~30-40%"
    )

    # Secagem
    local_secagem: Mapped[str | None] = mapped_column(
        String(30), nullable=True,
        comment="TERREIRO_CIMENTO, TERREIRO_SUSPENSO, SECADOR_MECANICO, MISTO"
    )
    data_inicio_secagem: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_fim_secagem: Mapped[date | None] = mapped_column(Date, nullable=True)
    dias_secagem: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Saída (café beneficiado/seco)
    data_saida: Mapped[date | None] = mapped_column(Date, nullable=True)
    peso_saida_kg: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    umidade_saida_pct: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="Umidade final: padrão MAPA = 12%"
    )

    # Calculados automaticamente
    fator_reducao: Mapped[float | None] = mapped_column(
        Numeric(6, 3), nullable=True,
        comment="Relação entrada/saída. Ex: 4.8 = 4,8 kg cereja → 1 kg beneficiado"
    )
    sacas_beneficiadas: Mapped[float | None] = mapped_column(
        Numeric(10, 3), nullable=True,
        comment="Sacas de 60 kg de café beneficiado"
    )
    perda_pct: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="% de perda no processamento vs. esperado"
    )

    # Classificação e qualidade
    peneira_principal: Mapped[str | None] = mapped_column(
        String(10), nullable=True,
        comment="Peneira predominante: 17+, 15/16, 13/14, etc."
    )
    bebida: Mapped[str | None] = mapped_column(
        String(30), nullable=True,
        comment="Classificação ABIC: ESTRITAMENTE_MOLE, MOLE, APENAS_MOLE, DURA, RIADA, RIO"
    )
    pontuacao_scaa: Mapped[float | None] = mapped_column(
        Numeric(4, 2), nullable=True,
        comment="Pontuação SCA (0-100). ≥ 80 = specialty coffee"
    )
    defeitos_intrinsecos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defeitos_extrinsecos: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Armazenagem
    armazem_id: Mapped[uuid.UUID | None] = mapped_column(UUIDCol(as_uuid=True), nullable=True)
    saca_inicio: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Nº da primeira saca")
    saca_fim: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Nº da última saca")

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow
    )
