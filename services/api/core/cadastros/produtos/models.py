import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, Integer, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TipoProduto(str, enum.Enum):
    # Insumos agrícolas
    SEMENTE         = "SEMENTE"
    DEFENSIVO       = "DEFENSIVO"       # herbicida, fungicida, inseticida
    FERTILIZANTE    = "FERTILIZANTE"    # NPK, calcário, micronutrientes
    INOCULANTE      = "INOCULANTE"
    ADJUVANTE       = "ADJUVANTE"

    # Insumos pecuários
    RACAO           = "RACAO"
    MEDICAMENTO     = "MEDICAMENTO"     # veterinário
    VACINA          = "VACINA"
    MINERAL         = "MINERAL"         # sal mineral, suplemento

    # Almoxarifado / manutenção
    PECA            = "PECA"            # peças de máquinas
    LUBRIFICANTE    = "LUBRIFICANTE"
    COMBUSTIVEL     = "COMBUSTIVEL"
    MATERIAL_GERAL  = "MATERIAL_GERAL"  # materiais de uso geral

    # Segurança
    EPI             = "EPI"             # Equipamento de Proteção Individual

    # Serviços contratados
    SERVICO         = "SERVICO"

    OUTRO           = "OUTRO"


class UnidadeMedida(str, enum.Enum):
    UN      = "UN"      # unidade
    KG      = "KG"
    G       = "G"       # grama
    T       = "T"       # tonelada
    L       = "L"       # litro
    ML      = "ML"
    M3      = "M3"
    SACA    = "SACA"    # saca 60kg
    SC40    = "SC40"    # saca 40kg
    FARDO   = "FARDO"
    CX      = "CX"      # caixa
    M       = "M"       # metro linear
    M2      = "M2"
    H       = "H"       # hora (serviços)


# ---------------------------------------------------------------------------
# Marca — catálogo de marcas/fabricantes pré-cadastradas
# ---------------------------------------------------------------------------

class Marca(Base):
    """
    Catálogo de marcas e fabricantes.
    tenant_id=NULL → padrão do sistema (sistema=True, não editável pelo tenant).
    Cada tenant pode criar suas próprias marcas adicionais.
    """
    __tablename__ = "cadastros_marcas"
    __table_args__ = (
        UniqueConstraint("tenant_id", "nome", name="uq_marca_tenant_nome"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True,
        comment="NULL = padrão do sistema"
    )
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, comment="True = não editável pelo tenant")

    nome: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(150), nullable=True)
    cnpj: Mapped[str | None] = mapped_column(String(18), nullable=True)
    pais_origem: Mapped[str | None] = mapped_column(String(60), nullable=True, default="Brasil")
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    modelos: Mapped[list["ModeloProduto"]] = relationship(back_populates="marca", lazy="noload", cascade="all, delete-orphan")
    produtos: Mapped[list["Produto"]] = relationship(back_populates="marca_rel", lazy="noload")


# ---------------------------------------------------------------------------
# ModeloProduto — modelos por marca
# ---------------------------------------------------------------------------

class ModeloProduto(Base):
    """
    Catálogo de modelos de produto vinculados a uma Marca.
    Permite padronizar "Roundup", "NK 7059", "Shell Rimula R4" etc.
    """
    __tablename__ = "cadastros_modelos_produto"
    __table_args__ = (
        UniqueConstraint("tenant_id", "marca_id", "nome", name="uq_modelo_tenant_marca_nome"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True,
        comment="NULL = padrão do sistema"
    )
    marca_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_marcas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, comment="True = não editável pelo tenant")

    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    referencia: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Código/referência do fabricante")
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Tipo de produto compatível (opcional — permite filtrar modelos por tipo no frontend)
    tipo_produto: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="TipoProduto compatível, ou null p/ qualquer")

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    marca: Mapped["Marca"] = relationship(back_populates="modelos", lazy="noload")
    produtos: Mapped[list["Produto"]] = relationship(back_populates="modelo_rel", lazy="noload")


# ---------------------------------------------------------------------------
# CategoriaProduto — categorias hierárquicas de produto
# ---------------------------------------------------------------------------

class CategoriaProduto(Base):
    """
    Árvore de categorias de produto por tenant.
    Permite organização customizada além do TipoProduto (ex: Defensivos > Herbicidas > Pós-emergentes).
    """
    __tablename__ = "cadastros_categorias_produto"
    __table_args__ = (
        UniqueConstraint("tenant_id", "nome", "parent_id", name="uq_categoria_tenant_nome_parent"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True,
        comment="NULL = padrão do sistema"
    )
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, comment="True = não editável pelo tenant")
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_categorias_produto.id", ondelete="SET NULL"), nullable=True, index=True
    )

    nome: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    cor: Mapped[str | None] = mapped_column(String(7), nullable=True, comment="Hex color para UI, ex: #4CAF50")
    icone: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Nome de ícone (lucide/heroicons)")
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Ordem de exibição dentro do pai")

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Self-referential
    filhos: Mapped[list["CategoriaProduto"]] = relationship(
        "CategoriaProduto",
        back_populates="pai",
        lazy="noload",
        foreign_keys="CategoriaProduto.parent_id",
    )
    pai: Mapped["CategoriaProduto | None"] = relationship(
        "CategoriaProduto",
        back_populates="filhos",
        lazy="noload",
        remote_side="CategoriaProduto.id",
        foreign_keys="CategoriaProduto.parent_id",
    )
    produtos: Mapped[list["Produto"]] = relationship(back_populates="categoria", lazy="noload")


# ---------------------------------------------------------------------------
# Produto — catálogo base de insumos e almoxarifado
# ---------------------------------------------------------------------------

class Produto(Base):
    """
    Catálogo unificado de produtos de ENTRADA (insumos, peças, EPIs, serviços).
    Estes são produtos que geram DESPESA ao serem consumidos.

    NÃO representa produtos colhidos / commodities (ver cadastros/commodities/).
    NÃO representa ativos biológicos / animais (ver pecuaria/animal/).

    Extensões por tipo:
      - ProdutoAgricola  → defensivos, sementes, fertilizantes
      - ProdutoEstoque   → controle físico (NCM, peso, validade)
      - ProdutoEPI       → CA, tipo de proteção, vida útil
      - ProdutoCultura   → culturas agrícolas (ciclo, espaçamento)
    """
    __tablename__ = "cadastros_produtos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identificação
    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    unidade_medida: Mapped[str] = mapped_column(String(10), default="UN", nullable=False)
    codigo_interno: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    sku: Mapped[str | None] = mapped_column(String(100), nullable=True)
    codigo_barras: Mapped[str | None] = mapped_column(String(60), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Marca e modelo — FKs para cadastros pré-registrados
    marca_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_marcas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    modelo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_modelos_produto.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Campos texto como fallback quando marca/modelo não estão cadastrados
    marca: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Fallback quando marca_id é null")
    fabricante: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Razão social do fabricante")
    referencia_fabricante: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Código/part number do fabricante")

    # Categoria
    categoria_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_categorias_produto.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Imagem
    imagem_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Embalagem vs. conteúdo real
    # Ex: "Óleo Motor 3L" → unidade_medida=UN, qtd_conteudo=3.0, unidade_conteudo=L
    # Permite calcular consumo real: 2 UN consumidas = 6 L consumidos
    qtd_conteudo: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Quantidade de conteúdo por embalagem (ex: 3 para 3L/embalagem)")
    unidade_conteudo: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="Unidade do conteúdo (ex: L, KG, ML) quando diferente de unidade_medida")

    # Estoque e custo
    estoque_minimo: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    preco_medio: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    preco_ultima_compra: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Extensibilidade por tenant
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    marca_rel: Mapped["Marca | None"] = relationship(back_populates="produtos", lazy="noload", foreign_keys=[marca_id])
    modelo_rel: Mapped["ModeloProduto | None"] = relationship(back_populates="produtos", lazy="noload", foreign_keys=[modelo_id])
    categoria: Mapped["CategoriaProduto | None"] = relationship(back_populates="produtos", lazy="noload", foreign_keys=[categoria_id])
    detalhe_agricola: Mapped["ProdutoAgricola | None"] = relationship(back_populates="produto", lazy="noload", uselist=False, cascade="all, delete-orphan")
    detalhe_estoque: Mapped["ProdutoEstoque | None"] = relationship(back_populates="produto", lazy="noload", uselist=False, cascade="all, delete-orphan")
    detalhe_epi: Mapped["ProdutoEPI | None"] = relationship(back_populates="produto", lazy="noload", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "codigo_interno", name="uq_produto_tenant_codigo_interno"),
    )


# ---------------------------------------------------------------------------
# ProdutoAgricola — extensão para defensivos, sementes, fertilizantes
# ---------------------------------------------------------------------------

class ProdutoAgricola(Base):
    """
    Dados técnicos e regulatórios para produtos de uso agrícola.
    Obrigatório para: DEFENSIVO, SEMENTE, FERTILIZANTE, INOCULANTE.
    """
    __tablename__ = "cadastros_produtos_agricola"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_produtos.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    # Defensivos — receituário agronômico
    registro_mapa: Mapped[str | None] = mapped_column(String(50), nullable=True)
    classe_agronomica: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="HERBICIDA | FUNGICIDA | INSETICIDA | ACARICIDA | NEMATICIDA")
    classe_toxicologica: Mapped[str | None] = mapped_column(String(5), nullable=True, comment="I | II | III | IV")
    principio_ativo: Mapped[str | None] = mapped_column(String(30), nullable=True)
    formulacao: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="CE | SC | WG | EC | SL")
    periodo_carencia_dias: Mapped[int | None] = mapped_column(Integer, nullable=True)
    intervalo_reentrada_horas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    epi_obrigatorio: Mapped[list | None] = mapped_column(JSON, nullable=True, comment="Lista de EPIs obrigatórios")

    # Sementes
    cultivar: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cultura_alvo: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="SOJA | MILHO | TRIGO | ALGODAO...")
    tsi: Mapped[bool] = mapped_column(Boolean, default=False, comment="Tratamento de sementes industrial")
    pureza_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    germinacao_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Fertilizantes
    composicao_npk: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="ex: 10-10-10, 00-18-00")
    densidade_g_ml: Mapped[float | None] = mapped_column(Float, nullable=True)

    produto: Mapped["Produto"] = relationship(back_populates="detalhe_agricola", lazy="noload")


# ---------------------------------------------------------------------------
# ProdutoEstoque — extensão para controle físico no almoxarifado
# ---------------------------------------------------------------------------

class ProdutoEstoque(Base):
    """
    Atributos físicos para produtos que passam por controle de estoque.
    Aplicável a todos os tipos com movimentação no almoxarifado.
    """
    __tablename__ = "cadastros_produtos_estoque"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_produtos.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    localizacao_default: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Prateleira / setor no almoxarifado")
    peso_unitario_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_unitario_l: Mapped[float | None] = mapped_column(Float, nullable=True)
    perecivel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    prazo_validade_dias: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ncm: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="Nomenclatura Comum do Mercosul")
    requer_receituario: Mapped[bool] = mapped_column(Boolean, default=False, comment="Exige receituário para saída (defensivos)")
    lote_controlado: Mapped[bool] = mapped_column(Boolean, default=False, comment="Controle por lote/série no estoque")

    produto: Mapped["Produto"] = relationship(back_populates="detalhe_estoque", lazy="noload")


# ---------------------------------------------------------------------------
# ProdutoEPI — extensão para Equipamentos de Proteção Individual
# ---------------------------------------------------------------------------

class ProdutoEPI(Base):
    """
    Dados regulatórios de EPIs (NR-6 / Portaria MTE).
    Controla CA (Certificado de Aprovação) e vida útil.
    """
    __tablename__ = "cadastros_produtos_epi"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_produtos.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    ca_numero: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="Certificado de Aprovação MTE")
    ca_validade: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tipo_protecao: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="CABECA | OLHOS | RESPIRATORIO | MAOS | PES | CORPO | AUDITIVO | QUEDAS")
    vida_util_meses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tamanho: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="PP | P | M | G | GG | UNICO")

    produto: Mapped["Produto"] = relationship(back_populates="detalhe_epi", lazy="noload")


# ---------------------------------------------------------------------------
# ProdutoCultura — culturas agrícolas (migrado de agricola/cadastros/Cultura)
# ---------------------------------------------------------------------------

class ProdutoCultura(Base):
    """
    Catálogo de culturas agrícolas do tenant.
    Migrado de agricola/cadastros/models.py (tabela 'culturas').
    Referenciado por: Safra, InsumoOperacao, ProdutoAgricola.cultura_alvo.
    """
    __tablename__ = "cadastros_culturas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True,
        comment="NULL = padrão do sistema"
    )
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, comment="True = não editável pelo tenant")

    nome: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    nome_cientifico: Mapped[str | None] = mapped_column(String(150), nullable=True)
    grupo: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="GRAOS | FIBRAS | FRUTAS | HORTALICAS | PASTAGEM | OUTRO")

    # Parâmetros agronômicos
    ciclo_dias_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ciclo_dias_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    espacamento_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    populacao_plantas_ha: Mapped[int | None] = mapped_column(Integer, nullable=True)
    produtividade_media_sc_ha: Mapped[float | None] = mapped_column(Float, nullable=True)

    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
