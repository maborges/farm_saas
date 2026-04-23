import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text, JSON, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TipoArea(str, enum.Enum):
    # Nível raiz (parent=None, filhos de UnidadeProdutiva)
    AREA_RURAL        = "AREA_RURAL"        # Contêiner de toda a área produtiva/ambiental
    INFRAESTRUTURA    = "INFRAESTRUTURA"    # Agrupamento de benfeitorias físicas

    # Filhos de AREA_RURAL
    GLEBA             = "GLEBA"             # Parcela legal com matrícula própria

    # Filhos de GLEBA
    TALHAO            = "TALHAO"            # Unidade de plantio (polígono)
    AREA_AMBIENTAL    = "AREA_AMBIENTAL"    # Agrupamento de áreas de preservação

    # Filhos de TALHAO
    AREA_OPERACIONAL  = "AREA_OPERACIONAL"  # Subdivisão operacional de talhão

    # Filhos de AREA_OPERACIONAL
    PIQUETE           = "PIQUETE"           # Subdivisão de pastagem para rotação
    ZONA_MANEJO       = "ZONA_MANEJO"       # Zona de manejo (agricultura de precisão)
    SUBTALHAO         = "SUBTALHAO"         # Subdivisão administrativa de talhão

    # Filhos de AREA_AMBIENTAL
    APP               = "APP"               # Área de Preservação Permanente
    RESERVA_LEGAL     = "RESERVA_LEGAL"     # Reserva Legal (Código Florestal)

    # Filhos de INFRAESTRUTURA
    SEDE              = "SEDE"              # Sede administrativa / moradia
    ARMAZEM           = "ARMAZEM"           # Armazém / silo / galpão
    CURRAL            = "CURRAL"            # Curral / mangueira / brete
    OUTROS            = "OUTROS"            # Outras benfeitorias


# ---------------------------------------------------------------------------
# Hierarquia permitida: pai → conjunto de tipos filhos válidos
# None = raiz (vinculado diretamente à UnidadeProdutiva)
# ---------------------------------------------------------------------------

# Camada TERRITORIAL (terra física): GLEBA → TALHAO → AREA_OPERACIONAL → folhas
# Camada AMBIENTAL (preservação): GLEBA → AREA_AMBIENTAL → APP / RESERVA_LEGAL
# Camada OPERACIONAL (infraestrutura): INFRAESTRUTURA → SEDE / ARMAZEM / CURRAL / OUTROS
FILHOS_PERMITIDOS: dict[str | None, set[str]] = {
    # Raiz — diretamente vinculados à UnidadeProdutiva
    None: {TipoArea.AREA_RURAL, TipoArea.INFRAESTRUTURA},

    # Contêiner de áreas
    TipoArea.AREA_RURAL:       {TipoArea.GLEBA},

    # Camada territorial
    TipoArea.GLEBA:            {TipoArea.TALHAO, TipoArea.AREA_AMBIENTAL},
    TipoArea.TALHAO:           {TipoArea.AREA_OPERACIONAL},
    TipoArea.AREA_OPERACIONAL: {TipoArea.PIQUETE, TipoArea.ZONA_MANEJO, TipoArea.SUBTALHAO},

    # Camada ambiental
    TipoArea.AREA_AMBIENTAL:   {TipoArea.APP, TipoArea.RESERVA_LEGAL},

    # Camada de infraestrutura
    TipoArea.INFRAESTRUTURA:   {TipoArea.SEDE, TipoArea.ARMAZEM, TipoArea.CURRAL, TipoArea.OUTROS},

    # Folhas — não aceitam filhos
    TipoArea.PIQUETE:          set(),
    TipoArea.ZONA_MANEJO:      set(),
    TipoArea.SUBTALHAO:        set(),
    TipoArea.APP:              set(),
    TipoArea.RESERVA_LEGAL:    set(),
    TipoArea.SEDE:             set(),
    TipoArea.ARMAZEM:          set(),
    TipoArea.CURRAL:           set(),
    TipoArea.OUTROS:           set(),
}

# Tipos que contribuem para cada agregação de área
TIPOS_AREA_PRODUTIVA  = {TipoArea.TALHAO, TipoArea.AREA_OPERACIONAL, TipoArea.PIQUETE, TipoArea.ZONA_MANEJO, TipoArea.SUBTALHAO}
TIPOS_AREA_AMBIENTAL  = {TipoArea.APP, TipoArea.RESERVA_LEGAL}
TIPOS_INFRAESTRUTURA  = {TipoArea.INFRAESTRUTURA, TipoArea.SEDE, TipoArea.ARMAZEM, TipoArea.CURRAL, TipoArea.OUTROS}


class TipoSolo(Base):
    __tablename__ = "cadastros_tipos_solo"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(50), nullable=False, unique=True) # Arenoso, Médio, Argiloso
    
    retencao_agua: Mapped[str] = mapped_column(String(10), nullable=False) # BAIXA, MEDIA, ALTA
    lixiviacao: Mapped[str] = mapped_column(String(10), nullable=False)    # BAIXA, MEDIA, ALTA
    ctc_resumo: Mapped[str] = mapped_column(String(10), nullable=False)    # BAIXA, MEDIA, ALTA
    
    descricao: Mapped[str | None] = mapped_column(String(200))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


class TipoIrrigacao(Base):
    __tablename__ = "cadastros_tipos_irrigacao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(50), nullable=False, unique=True) # Gotejamento, Pivô Central, etc.
    metodo: Mapped[str | None] = mapped_column(String(50))
    descricao: Mapped[str | None] = mapped_column(String(200))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


# ---------------------------------------------------------------------------
# AreaRural — entidade hierárquica central
# ---------------------------------------------------------------------------

class AreaRural(Base):
    """
    Modelo hierárquico unificado para toda subdivisão espacial de uma fazenda.

    Hierarquia (parent=None = raiz da UnidadeProdutiva):

        UNIDADE_PRODUTIVA
        ├── GLEBA (Matrícula 1234)
        │   ├── TALHAO (T-01)
        │   │   └── AREA_OPERACIONAL
        │   │       ├── PIQUETE
        │   │       ├── ZONA_MANEJO
        │   │       └── SUBTALHAO
        │   └── AREA_AMBIENTAL
        │       ├── APP
        │       └── RESERVA_LEGAL
        └── INFRAESTRUTURA
            ├── SEDE
            ├── ARMAZEM
            ├── CURRAL
            └── OUTROS

    Validação de hierarquia: ver FILHOS_PERMITIDOS em models.py.
    Geometria armazenada como GeoJSON dict; em produção usar PostGIS Geometry.
    """
    __tablename__ = "cadastros_areas_rurais"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unidade_produtiva_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("unidades_produtivas.id", ondelete="CASCADE"), nullable=False, index=True
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
    area_hectares: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4), nullable=True,
        comment="Calculado do polígono ou preenchido manualmente"
    )
    area_hectares_manual: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4), nullable=True,
        comment="Override manual quando não há geometria"
    )

    # Geometria (GeoJSON — substituir por Geometry(PostGIS) em produção)
    geometria: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment="GeoJSON Polygon/MultiPolygon. Nulo para tipos administrativos."
    )
    centroide_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    centroide_lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Contexto Agronômico
    tipo_solo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_tipos_solo.id", ondelete="SET NULL"), nullable=True
    )
    irrigado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tipo_irrigacao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_tipos_irrigacao.id", ondelete="SET NULL"), nullable=True
    )

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
    infraestruturas: Mapped[list["Infraestrutura"]] = relationship(
        back_populates="area_rural", lazy="noload", cascade="all, delete-orphan"
    )
    arquivos_geo: Mapped[list["ArquivoGeo"]] = relationship(
        back_populates="area_rural", lazy="noload", cascade="all, delete-orphan"
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

# ---------------------------------------------------------------------------
# Infraestrutura — benfeitorias físicas da propriedade
# ---------------------------------------------------------------------------

class TipoInfraestrutura(str, enum.Enum):
    SEDE      = "sede"
    SILO      = "silo"
    CURRAL    = "curral"
    GALPAO    = "galpao"
    OFICINA   = "oficina"
    OUTRO     = "outro"


class Infraestrutura(Base):
    """
    Benfeitoria física de uma propriedade rural.
    Vinculada a AreaRural tipo PROPRIEDADE (unidade_produtiva_id lógico).
    """
    __tablename__ = "cadastros_infraestruturas"
    __table_args__ = (
        Index("ix_infraestruturas_tenant_area", "tenant_id", "area_rural_id"),
        Index("ix_infraestruturas_tenant_tipo", "tenant_id", "tipo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    area_rural_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    capacidade: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    unidade_capacidade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(11, 8), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    area_rural: Mapped["AreaRural"] = relationship("AreaRural", back_populates="infraestruturas", lazy="noload")


# ---------------------------------------------------------------------------
# ArquivoGeo — auditoria de uploads de arquivos geoespaciais
# ---------------------------------------------------------------------------

class FormatoArquivoGeo(str, enum.Enum):
    SHP     = "shp"
    KML     = "kml"
    KMZ     = "kmz"
    GEOJSON = "geojson"


class StatusProcessamentoGeo(str, enum.Enum):
    PENDENTE    = "PENDENTE"
    PROCESSADO  = "PROCESSADO"
    ERRO        = "ERRO"


class ArquivoGeo(Base):
    """
    Registro de auditoria de uploads de arquivos geoespaciais.
    O arquivo binário fica no storage (local/S3/MinIO); aqui ficam os metadados.
    """
    __tablename__ = "cadastros_arquivos_geo"
    __table_args__ = (
        Index("ix_arquivos_geo_tenant_area", "tenant_id", "area_rural_id"),
        Index("ix_arquivos_geo_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    area_rural_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    formato: Mapped[str] = mapped_column(String(10), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(nullable=False)
    storage_backend: Mapped[str] = mapped_column(String(10), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=StatusProcessamentoGeo.PENDENTE)
    poligonos_extraidos: Mapped[int | None] = mapped_column(nullable=True)
    area_ha_extraida: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    erro_msg: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    area_rural: Mapped["AreaRural"] = relationship("AreaRural", back_populates="arquivos_geo", lazy="noload")


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
