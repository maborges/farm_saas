import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TipoArea(str, enum.Enum):
    # Administrativo / legal
    PROPRIEDADE       = "PROPRIEDADE"       # Imóvel rural (nível topo, tem matrícula)
    GLEBA             = "GLEBA"             # Parcela legal com matrícula própria

    # Produtivo
    UNIDADE_PRODUTIVA = "UNIDADE_PRODUTIVA" # Agrupamento administrativo sem geometria
    AREA              = "AREA"              # Subdivisão genérica de unidade produtiva
    TALHAO            = "TALHAO"            # Unidade de plantio (polígono)
    PASTAGEM          = "PASTAGEM"          # Área de pastagem (polígono)
    PIQUETE           = "PIQUETE"           # Subdivisão de pastagem para rotação

    # Ambiental / legal
    APP               = "APP"              # Área de Preservação Permanente
    RESERVA_LEGAL     = "RESERVA_LEGAL"    # Reserva Legal (Código Florestal)

    # Infraestrutura (sem geometria obrigatória)
    ARMAZEM           = "ARMAZEM"          # Armazém / silo / galpão
    SEDE              = "SEDE"             # Sede administrativa / moradia
    INFRAESTRUTURA    = "INFRAESTRUTURA"   # Curral, aviário, pocilga, etc.


# ---------------------------------------------------------------------------
# AreaRural — entidade hierárquica central
# ---------------------------------------------------------------------------

class AreaRural(Base):
    """
    Modelo hierárquico unificado para toda subdivisão espacial de uma fazenda.

    Substitui: talhoes, pec_piquetes, imoveis_rurais, imoveis_benfeitorias.

    Hierarquia de exemplo:
        PROPRIEDADE (Fazenda São João)
        ├── GLEBA (Matrícula 1234)
        │   ├── APP (Rio das Pedras)
        │   └── RESERVA_LEGAL
        ├── UNIDADE_PRODUTIVA (Bloco Norte)
        │   ├── TALHAO (T-01)
        │   ├── TALHAO (T-02)
        │   └── PASTAGEM (P-01)
        │       └── PIQUETE (PQ-01)
        ├── ARMAZEM (Armazém Central)
        └── SEDE

    Geometria: opcional — tipos administrativos (SEDE, ARMAZEM, UNIDADE_PRODUTIVA)
    podem não ter polígono. Tipos produtivos (TALHAO, PIQUETE) normalmente têm.
    Geometria armazenada como GeoJSON dict; em produção com PostGIS usar Geometry.
    """
    __tablename__ = "cadastros_areas_rurais"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fazenda_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Hierarquia (self-referencial)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastros_areas_rurais.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Identificação
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Código interno (ex: T-01, P-01)")
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Dimensões
    area_hectares: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Calculado do polígono ou preenchido manualmente"
    )
    area_hectares_manual: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Override manual quando não há geometria"
    )

    # Geometria (GeoJSON — substituir por Geometry(PostGIS) em produção)
    geometria: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment="GeoJSON Polygon/MultiPolygon. Nulo para tipos administrativos."
    )
    centroide_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    centroide_lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Dados específicos por tipo (evita tabelas extras para atributos simples)
    # Exemplos:
    #   TALHAO:    {"cultura_atual": "SOJA", "tipo_solo": "LATOSSOLO", "irrigado": true}
    #   PIQUETE:   {"capacidade_ua": 45, "forrageira": "BRAQUIARIA", "possui_aguada": true}
    #   ARMAZEM:   {"capacidade_sacas": 50000, "tipo_piso": "CIMENTO", "possui_termometria": true}
    #   APP:       {"curso_dagua": "Rio das Pedras", "largura_buffer_metros": 30}
    #   TALHAO agr: {"declividade_pct": 3.2, "classe_solo": "LVd", "textura_solo": "ARGILOSA"}
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    filhos: Mapped[list["AreaRural"]] = relationship(
        "AreaRural",
        back_populates="pai",
        foreign_keys=[parent_id],
        lazy="noload"
    )
    pai: Mapped["AreaRural | None"] = relationship(
        "AreaRural",
        back_populates="filhos",
        remote_side=[id],
        lazy="noload"
    )
    matriculas: Mapped[list["MatriculaImovel"]] = relationship(
        back_populates="area", lazy="noload", cascade="all, delete-orphan"
    )
    registros_ambientais: Mapped[list["RegistroAmbiental"]] = relationship(
        back_populates="area", lazy="noload", cascade="all, delete-orphan"
    )
    valores_patrimoniais: Mapped[list["ValorPatrimonial"]] = relationship(
        back_populates="area", lazy="noload", cascade="all, delete-orphan",
        order_by="ValorPatrimonial.data_avaliacao.desc()"
    )


# ---------------------------------------------------------------------------
# MatriculaImovel — documentação cartorial de PROPRIEDADE ou GLEBA
# ---------------------------------------------------------------------------

class MatriculaImovel(Base):
    """
    Matrículas cartoriais vinculadas a uma AreaRural tipo PROPRIEDADE ou GLEBA.
    Inclui dados fundiários: CAR, NIRF, INCRA.
    Uma propriedade pode ter múltiplas matrículas (remembramento/desmembramento).
    """
    __tablename__ = "cadastros_areas_matriculas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    numero_matricula: Mapped[str] = mapped_column(String(100), nullable=False)
    cartorio: Mapped[str | None] = mapped_column(String(200), nullable=True)
    comarca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area_matricula_ha: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Dados cartoriais completos
    livro: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Livro do registro cartorial")
    folha: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Folha do registro cartorial")
    data_registro: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Data do registro em cartório")

    # Registros fundiários
    car_numero: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Cadastro Ambiental Rural")
    nirf: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="Número do Imóvel na Receita Federal")
    incra: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="Código INCRA do imóvel")
    ccir: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="Certificado de Cadastro de Imóvel Rural")
    sncr: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="Sistema Nacional de Cadastro Rural (INCRA)")
    itr_numero: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Número do processo ITR na Receita Federal")

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    area: Mapped["AreaRural"] = relationship(back_populates="matriculas", lazy="noload")


# ---------------------------------------------------------------------------
# RegistroAmbiental — dados de APP, Reserva Legal, licenças
# ---------------------------------------------------------------------------

class RegistroAmbiental(Base):
    """
    Informações ambientais e licenças vinculadas a áreas preservadas.
    Aplicável a tipos: APP, RESERVA_LEGAL.
    """
    __tablename__ = "cadastros_areas_registros_ambientais"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    tipo_registro: Mapped[str] = mapped_column(String(50), nullable=False,
        comment="CAR_APP | CAR_RL | LICENCA_IBAMA | AIA | OUTORGA_AGUA | OUTRO")
    numero: Mapped[str | None] = mapped_column(String(100), nullable=True)
    orgao: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data_emissao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    data_validade: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    link_documento: Mapped[str | None] = mapped_column(String(500), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    area: Mapped["AreaRural"] = relationship(back_populates="registros_ambientais", lazy="noload")


# ---------------------------------------------------------------------------
# ValorPatrimonial — histórico de avaliações para fins contábeis/patrimoniais
# ---------------------------------------------------------------------------

class MetodoAvaliacao(str, enum.Enum):
    MERCADO   = "MERCADO"    # Valor de mercado (comparativo)
    CUSTO     = "CUSTO"      # Valor de custo de reposição
    RENDA     = "RENDA"      # Capitalização da renda esperada
    DECLARADO = "DECLARADO"  # Valor declarado pelo proprietário (ex: ITR)
    LAUDO     = "LAUDO"      # Laudo técnico de avaliação


class ValorPatrimonial(Base):
    """
    Histórico de avaliações patrimoniais de uma AreaRural.

    Cada registro representa uma avaliação em uma data específica.
    O valor mais recente (data_avaliacao desc) é considerado o atual.

    Usos futuros:
    - Relatório de patrimônio consolidado por fazenda/tenant
    - Base de cálculo para ITR (valor terra nua)
    - Garantias para financiamentos (PRONAF, etc.)
    - Depreciação de benfeitorias (módulo financeiro)
    - Balanço patrimonial rural
    """
    __tablename__ = "cadastros_areas_valores_patrimoniais"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    data_avaliacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        comment="Data de referência desta avaliação"
    )
    metodo: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MetodoAvaliacao.DECLARADO,
        comment="Método de avaliação utilizado"
    )

    # Componentes do valor (todos opcionais — preenche o que for aplicável ao tipo de área)
    valor_terra_nua: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Valor da terra sem benfeitorias (base ITR/INCRA)"
    )
    valor_benfeitorias: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Valor de construções, silos, cercas, infraestrutura"
    )
    valor_lavoura_perene: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Valor de culturas perenes (laranjal, canavial, etc.)"
    )
    valor_total: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Valor total consolidado (pode ser soma ou valor independente)"
    )

    moeda: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")
    responsavel: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="Avaliador ou responsável pelo laudo")
    numero_laudo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    area: Mapped["AreaRural"] = relationship(back_populates="valores_patrimoniais", lazy="noload")
