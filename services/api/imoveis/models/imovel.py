"""
Módulo Imóveis Rurais - Modelos SQLAlchemy

Implementa a gestão patrimonial e documental de propriedades rurais:
- ImovelRural: Representação legal da fazenda (NIRF, CAR, CCIR, matrícula)
- Cartorio: Cadastro de cartórios de registro de imóveis
- DocumentoLegal: Gestão documental com versionamento (CCIR, ITR, CAR, escritura)
- ContratoArrendamento: Contratos de arrendamento e parceria rural
- Benfeitoria: Instalações e melhorias no imóvel

Conformidade legal:
- Lei 9.393/1996 (ITR)
- Lei 12.651/2012 (Código Florestal - CAR)
- Lei 4.504/1964 (Estatuto da Terra - Arrendamentos)
- IN RFB 1.902/2019 (NIRF)
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Float, Integer, JSON,
    Text, Numeric, Date, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
import enum

from core.database import Base


# ==================== ENUMS ====================

class TipoImovel(str, enum.Enum):
    """Tipo de imóvel rural conforme INCRA."""
    RURAL = "rural"
    PARTICULAR = "particular"
    DEVOLUTA = "devoluta"
    POSSE = "posse"


class SituacaoImovel(str, enum.Enum):
    """Situação cadastral do imóvel."""
    REGULAR = "regular"
    PENDENTE = "pendente"
    IRREGULAR = "irregular"


class TipoDocumento(str, enum.Enum):
    """Tipos de documentos legais."""
    CCIR = "CCIR"
    ITR_DITR = "ITR_DITR"
    CAR = "CAR"
    ESCRITURA = "ESCRITURA"
    MATRICULA = "MATRICULA"
    GEOREFERENCIAMENTO = "GEOREFERENCIAMENTO"
    OUTRO = "OUTRO"


class StatusDocumento(str, enum.Enum):
    """Status do documento legal."""
    ATIVO = "ATIVO"
    SUBSTITUIDO = "SUBSTITUIDO"
    VENCIDO = "VENCIDO"
    CANCELADO = "CANCELADO"


class TipoContrato(str, enum.Enum):
    """Tipo de contrato de arrendamento."""
    ARRENDAMENTO = "ARRENDAMENTO"
    PARCERIA = "PARCERIA"


class TipoArrendatario(str, enum.Enum):
    """Tipo de arrendatário."""
    PESSOA_FISICA = "PESSOA_FISICA"
    PESSOA_JURIDICA = "PESSOA_JURIDICA"
    FAZENDA_TENANT = "FAZENDA_TENANT"


class ValorModalidade(str, enum.Enum):
    """Modalidade de valor do arrendamento."""
    FIXO_BRL = "FIXO_BRL"
    FIXO_SACAS = "FIXO_SACAS"
    PERCENTUAL = "PERCENTUAL"


class Periodicidade(str, enum.Enum):
    """Periodicidade de pagamento."""
    MENSAL = "MENSAL"
    SEMESTRAL = "SEMESTRAL"
    ANUAL = "ANUAL"
    SAFRA = "SAFRA"


class StatusContrato(str, enum.Enum):
    """Status do contrato de arrendamento."""
    ATIVO = "ATIVO"
    ENCERRADO = "ENCERRADO"
    RESCINDIDO = "RESCINDIDO"
    SUSPENSO = "SUSPENSO"


class StatusParcela(str, enum.Enum):
    """Status da parcela de arrendamento."""
    PREVISTA = "PREVISTA"
    PAGA = "PAGA"
    CANCELADA = "CANCELADA"
    VENCIDA = "VENCIDA"


# ==================== MODELOS PRINCIPAIS ====================

class Cartorio(Base):
    """
    Cartório de Registro de Imóveis.
    
    Permite vincular matrículas a cartórios específicos para organização
    e validação de documentos legais.
    """
    __tablename__ = "imoveis_cartorios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    comarca: Mapped[str] = mapped_column(String(100), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    codigo_censec: Mapped[str | None] = mapped_column(String(20))
    telefone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    endereco: Mapped[str | None] = mapped_column(String(500))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relacionamentos
    matriculas = relationship("MatriculaImovelRural", back_populates="cartorio", cascade="all, delete-orphan")


class ImovelRural(Base):
    """
    Imóvel Rural - Representação legal da propriedade.
    
    Vinculado a uma fazenda operacional, representa a dimensão jurídica
    do imóvel com dados para ITR, CAR, CCIR e matrícula cartorária.
    
    Conformidade: Lei 9.393/1996 (ITR), IN RFB 1.902/2019 (NIRF)
    """
    __tablename__ = "imoveis_rurais"
    
    __table_args__ = (
        UniqueConstraint('nirf', name='uq_imovel_nirf'),
        UniqueConstraint('tenant_id', 'cartorio_id', 'numero_matricula', name='uq_imovel_matricula'),
    )

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    fazenda_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Dados da matrícula
    cartorio_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_cartorios.id", ondelete="SET NULL")
    )
    numero_matricula: Mapped[str | None] = mapped_column(String(100))
    
    # Dados federais
    nirf: Mapped[str | None] = mapped_column(String(20), index=True)  # Receita Federal
    car_numero: Mapped[str | None] = mapped_column(String(50), index=True)  # CAR
    ccir_numero: Mapped[str | None] = mapped_column(String(50))  # INCRA
    
    # Áreas (em hectares, 4 casas decimais)
    area_total_ha: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal('0.0000'))
    area_aproveitavel_ha: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    area_app_ha: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    area_rl_ha: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    
    # Módulos fiscais (Receita Federal)
    modulos_fiscais: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    
    # Localização
    municipio: Mapped[str] = mapped_column(String(100), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    codigo_municipio_ibge: Mapped[str | None] = mapped_column(String(10))
    
    # Coordenadas da sede (SIRGAS 2000)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(11, 8))
    
    # Tipo e situação
    tipo: Mapped[TipoImovel] = mapped_column(
        SQLEnum(TipoImovel), default=TipoImovel.RURAL, nullable=False
    )
    situacao: Mapped[SituacaoImovel] = mapped_column(
        SQLEnum(SituacaoImovel), default=SituacaoImovel.PENDENTE, nullable=False
    )
    
    # Geometria (GeoJSON)
    geometria: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Observações e controle
    observacao: Mapped[str | None] = mapped_column(Text)
    motivo_alteracao_area: Mapped[str | None] = mapped_column(Text)
    
    # Auditoria
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    
    # Relacionamentos
    fazenda = relationship("Fazenda")
    cartorio = relationship("Cartorio")
    documentos = relationship("DocumentoLegal", back_populates="imovel", cascade="all, delete-orphan")
    contratos_arrendamento = relationship("ContratoArrendamento", back_populates="imovel", cascade="all, delete-orphan")
    benfeitorias = relationship("Benfeitoria", back_populates="imovel", cascade="all, delete-orphan")
    
    def calcular_situacao(self) -> SituacaoImovel:
        """
        Calcula situação cadastral baseada em documentos obrigatórios.
        
        REGULAR: Possui NIRF, CAR e CCIR válidos
        PENDENTE: Falta algum documento
        IRREGULAR: Documentos vencidos há mais de 90 dias
        """
        # Implementação no service
        return self.situacao


class MatriculaImovelRural(Base):
    """
    Matrícula de Imóvel no Cartório de Registro.
    
    Um imóvel pode ter múltiplas matrículas (ex: glebas distintas).
    Histórico de transmissões (compra, venda, partilha) é registrado aqui.
    """
    __tablename__ = "imoveis_matriculas"
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'cartorio_id', 'numero_matricula', name='uq_matricula_unica'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    imovel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_rurais.id", ondelete="CASCADE"), index=True
    )
    cartorio_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_cartorios.id", ondelete="SET NULL")
    )
    
    numero_matricula: Mapped[str] = mapped_column(String(50), nullable=False)
    cartorio_nome: Mapped[str | None] = mapped_column(String(200))  # Denormalizado para histórico
    area_matricula_ha: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal('0.0000'))
    
    # Histórico de transmissões
    data_transmissao: Mapped[Date | None] = mapped_column(Date)
    tipo_transmissao: Mapped[str | None] = mapped_column(String(50))  # COMPRA, VENDA, PARTILHA, DOACAO
    
    observacoes: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    cartorio = relationship("Cartorio", back_populates="matriculas")


class Benfeitoria(Base):
    """
    Benfeitorias e Instalações no Imóvel Rural.
    
    Inclui: sedes, casas de colonos, silos, currais, galpões, oficinas.
    Usado para avaliação patrimonial e controle de capacidade.
    """
    __tablename__ = "imoveis_benfeitorias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    imovel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_rurais.id", ondelete="CASCADE"), index=True
    )
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50))  # SEDE, SILO, CURRAL, CASA, GALPAO, OFICINA
    area_construida: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    capacidade: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    unidade_capacidade: Mapped[str | None] = mapped_column(String(20))  # TONELADAS, LITROS, CABECAS
    
    # Localização GPS
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(11, 8))
    
    valor_estimado: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    ano_construcao: Mapped[int | None] = mapped_column(Integer)
    
    observacoes: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relacionamentos
    imovel = relationship("ImovelRural", back_populates="benfeitorias")


# ==================== DOCUMENTOS LEGAIS ====================

class DocumentoLegal(Base):
    """
    Documento Legal de Imóvel Rural.
    
    Gestão documental com versionamento para:
    - CCIR (Certificado de Cadastro de Imóvel Rural) - vencimento anual
    - ITR/DITR (Imposto Territorial Rural) - vencimento anual
    - CAR (Cadastro Ambiental Rural) - sem vencimento
    - Escritura, Matrícula, Georreferenciamento
    
    Versionamento: novo upload substitui versão anterior (status SUBSTITUIDO).
    """
    __tablename__ = "imoveis_documentos"
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'imovel_id', 'tipo', 'versao', name='uq_documento_tipo_versao'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    imovel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_rurais.id", ondelete="CASCADE"), index=True
    )
    
    # Tipo e identificação
    tipo: Mapped[TipoDocumento] = mapped_column(
        SQLEnum(TipoDocumento), nullable=False, index=True
    )
    descricao: Mapped[str | None] = mapped_column(String(255))
    numero_documento: Mapped[str | None] = mapped_column(String(100))
    
    # Datas
    data_emissao: Mapped[Date | None] = mapped_column(Date)
    data_vencimento: Mapped[Date | None] = mapped_column(Date, index=True)
    
    # Status e versionamento
    status: Mapped[StatusDocumento] = mapped_column(
        SQLEnum(StatusDocumento), default=StatusDocumento.ATIVO, nullable=False
    )
    versao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    substituido_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_documentos.id", ondelete="SET NULL")
    )
    
    # Arquivo
    path_storage: Mapped[str] = mapped_column(String(512), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    hash_conteudo: Mapped[str | None] = mapped_column(String(64))  # SHA-256
    
    # Controle de acesso
    restrito: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Auditoria
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    
    # Relacionamentos
    imovel = relationship("ImovelRural", back_populates="documentos")
    versao_anterior = relationship("DocumentoLegal", remote_side=[id], foreign_keys=[substituido_por])


class HistoricoDocumento(Base):
    """
    Histórico de Ações em Documentos Legais.
    
    Auditoria completa de uploads, visualizações, downloads e substituições.
    """
    __tablename__ = "imoveis_documentos_historico"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    documento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_documentos.id", ondelete="CASCADE"), index=True
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    
    acao: Mapped[str] = mapped_column(String(50), nullable=False)  # UPLOAD, SUBSTITUICAO, VISUALIZACAO, DOWNLOAD
    dados_acao: Mapped[dict | None] = mapped_column(JSON)  # IP, user-agent, etc.
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


# ==================== ARRENDAMENTOS ====================

class ContratoArrendamento(Base):
    """
    Contrato de Arrendamento Rural ou Parceria Agrícola.
    
    Lei 4.504/1964 (Estatuto da Terra):
    - Arrendamento: pagamento fixo em dinheiro ou produto
    - Parceria: divisão dos frutos da produção
    
    Prazo mínimo: 3 anos (agrícola), 5 anos (misto)
    Valor máximo: 15% do valor cadastral anual
    """
    __tablename__ = "imoveis_arrendamentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    imovel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_rurais.id", ondelete="RESTRICT"), index=True
    )
    fazenda_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="RESTRICT"), index=True
    )
    
    # Tipo de contrato
    tipo: Mapped[TipoContrato] = mapped_column(
        SQLEnum(TipoContrato), nullable=False
    )
    
    # Arrendatário
    arrendatario_tipo: Mapped[TipoArrendatario] = mapped_column(
        SQLEnum(TipoArrendatario), nullable=False
    )
    arrendatario_pessoa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_pessoas.id", ondelete="SET NULL")
    )
    arrendatario_fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fazendas.id", ondelete="SET NULL")
    )
    
    # Área e valor
    area_arrendada_ha: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    valor_modalidade: Mapped[ValorModalidade] = mapped_column(
        SQLEnum(ValorModalidade), nullable=False
    )
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    commodity_referencia: Mapped[str | None] = mapped_column(String(50))  # SOJA, MILHO, etc.
    
    # Periodicidade e datas
    periodicidade: Mapped[Periodicidade] = mapped_column(
        SQLEnum(Periodicidade), nullable=False
    )
    data_inicio: Mapped[Date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[Date] = mapped_column(Date, nullable=False)
    dia_vencimento: Mapped[int | None] = mapped_column(Integer)  # 1-28
    
    # Reajuste
    indice_reajuste: Mapped[str | None] = mapped_column(String(20))  # IGP-M, IPCA, SELIC
    data_reajuste_anual: Mapped[Date | None] = mapped_column(Date)
    
    # Status
    status: Mapped[StatusContrato] = mapped_column(
        SQLEnum(StatusContrato), default=StatusContrato.ATIVO, nullable=False
    )
    motivo_rescisao: Mapped[str | None] = mapped_column(Text)
    
    # Documento e registro
    path_contrato_pdf: Mapped[str | None] = mapped_column(String(512))
    registro_cartorio: Mapped[str | None] = mapped_column(String(100))
    clausulas_observacoes: Mapped[str | None] = mapped_column(Text)
    
    # Auditoria
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    
    # Relacionamentos
    imovel = relationship("ImovelRural", back_populates="contratos_arrendamento")
    parcelas = relationship("ParcelaArrendamento", back_populates="contrato", cascade="all, delete-orphan")
    reajustes = relationship("HistoricoReajuste", back_populates="contrato", cascade="all, delete-orphan")


class ParcelaArrendamento(Base):
    """
    Parcela de Pagamento de Arrendamento.
    
    Gerada automaticamente ao criar contrato. Integrada com módulo Financeiro
    para lançamentos de contas a receber (proprietário) ou a pagar (arrendatário).
    """
    __tablename__ = "imoveis_arrendamento_parcelas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contrato_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_arrendamentos.id", ondelete="CASCADE"), index=True
    )
    
    numero_parcela: Mapped[int] = mapped_column(Integer, nullable=False)
    data_vencimento: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    
    # Valores
    valor_centavos: Mapped[int] = mapped_column(Integer, nullable=False)  # BRL em centavos
    valor_sacas: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # Se modalidade sacas
    
    # Status
    status: Mapped[StatusParcela] = mapped_column(
        SQLEnum(StatusParcela), default=StatusParcela.PREVISTA, nullable=False
    )
    
    # Integração com financeiro
    # FK para tabela de lançamentos financeiros — sem constraint até módulo financeiro unificado existir
    lancamento_financeiro_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Pagamento
    data_pagamento: Mapped[Date | None] = mapped_column(Date)
    indice_aplicado: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # Reajuste aplicado
    
    observacao: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relacionamentos
    contrato = relationship("ContratoArrendamento", back_populates="parcelas")


class HistoricoReajuste(Base):
    """
    Histórico de Reajustes de Contrato de Arrendamento.
    
    Registra todos os reajustes aplicados (IGP-M, IPCA, etc.)
    para auditoria e conformidade contratual.
    """
    __tablename__ = "imoveis_arrendamento_reajustes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contrato_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("imoveis_arrendamentos.id", ondelete="CASCADE"), index=True
    )
    
    data_reajuste: Mapped[Date] = mapped_column(Date, nullable=False)
    indice_nome: Mapped[str] = mapped_column(String(50), nullable=False)
    indice_valor: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    
    valor_anterior: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    valor_novo: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relacionamentos
    contrato = relationship("ContratoArrendamento", back_populates="reajustes")
