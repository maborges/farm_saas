"""
Modelos de Gestão Ambiental

Módulo responsável pela gestão do CAR (Cadastro Ambiental Rural)
e monitoramento ambiental.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, Date, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

from services.api.core.database import Base


class StatusCAR(str, enum.Enum):
    """Status do CAR"""
    ATIVO = "ativo"
    PENDENTE = "pendente"
    SUSPENSO = "suspenso"
    CANCELADO = "cancelado"


class TipoSobreposicao(str, enum.Enum):
    """Tipo de sobreposição"""
    TERRA_INDIGENA = "terra_indigena"
    UNIDADE_CONSERVACAO = "unidade_conservacao"
    QUILOMBO = "quilombo"
    APP = "app"
    RESERVA_LEGAL = "reserva_legal"


class CAR(Base):
    """
    Modelo de CAR (Cadastro Ambiental Rural)
    
    Armazena informações do Cadastro Ambiental Rural
    conforme Lei 12.651/2012 (Código Florestal).
    """
    __tablename__ = "ambiental_car"
    
    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    unidade_produtiva_id = Column(UUID(as_uuid=True), ForeignKey("unidades_produtivas.id"), nullable=False)
    
    # Dados do CAR
    codigo_car = Column(String(50), unique=True, nullable=False, index=True)
    numero_recibo = Column(String(50), nullable=True)
    hash_car = Column(String(64), nullable=True)
    
    # Datas
    data_cadastro = Column(DateTime, nullable=True)
    data_atualizacao = Column(DateTime, nullable=True)
    data_situacao = Column(DateTime, nullable=True)
    
    # Áreas (em hectares)
    area_total = Column(Float, nullable=False, default=0.0)
    area_app = Column(Float, default=0.0)  # Área de Preservação Permanente
    area_rl = Column(Float, default=0.0)  # Reserva Legal
    area_uso_restrito = Column(Float, default=0.0)
    area_consolidada = Column(Float, default=0.0)
    area_remanescente_vegetacao = Column(Float, default=0.0)
    area_pastagem = Column(Float, default=0.0)
    area_agricultura = Column(Float, default=0.0)
    area_silvicultura = Column(Float, default=0.0)
    area_outros = Column(Float, default=0.0)
    
    # Percentuais
    percentual_app = Column(Float, default=0.0)
    percentual_rl = Column(Float, default=0.0)
    percentual_vegetacao_nativa = Column(Float, default=0.0)
    
    # Sobreposições
    possui_sobreposicao = Column(Boolean, default=False)
    sobreposicoes = Column(JSONB, default=list)
    # Estrutura: [
    #   {
    #     "tipo": "terra_indigena",
    #     "nome": "TI X",
    #     "area_hectares": 100.5,
    #     "percentual": 5.2
    #   }
    # ]
    
    # Status
    status = Column(SQLEnum(StatusCAR), nullable=False, default=StatusCAR.ATIVO)
    situacao = Column(String(100), nullable=True)
    
    # Pendências
    possui_pendencias = Column(Boolean, default=False)
    pendencias = Column(JSONB, default=list)
    # Estrutura: [
    #   {
    #     "codigo": "P001",
    #     "descricao": "Área de APP inconsistente",
    #     "gravidade": "alta",
    #     "data": "2026-01-15"
    #   }
    # ]
    
    # Imóvel rural
    nome_imovel = Column(String(200), nullable=True)
    codigo_imovel = Column(String(50), nullable=True)
    municipio = Column(String(100), nullable=True)
    uf = Column(String(2), nullable=True)
    
    # Proprietário
    nome_proprietario = Column(String(200), nullable=True)
    cpf_cnpj_proprietario = Column(String(14), nullable=True)
    
    # Geometria (GeoJSON)
    geometria = Column(JSONB, nullable=True)
    # Estrutura: {
    #   "type": "Polygon",
    #   "coordinates": [[[lon, lat], ...]]
    # }
    
    # Arquivos
    recibo_pdf = Column(Text, nullable=True)  # Base64
    memoria_descritiva = Column(Text, nullable=True)  # Base64
    xml_car = Column(Text, nullable=True)  # XML completo
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    # Relacionamentos
    tenant = relationship("Tenant")
    fazenda = relationship("UnidadeProdutiva", back_populates="car")
    monitoramentos = relationship("MonitoramentoAPP", back_populates="car")
    alertas = relationship("AlertaDesmatamento", back_populates="car")
    
    def __repr__(self):
        return f"<CAR {self.codigo_car} - {self.nome_imovel}>"
    
    @property
    def url_consulta(self) -> str:
        """URL de consulta no SNA"""
        return f"https://www.car.gov.br/#/imoveis/consulta/{self.codigo_car}"
    
    def calcular_percentuais(self):
        """Calcula percentuais das áreas"""
        if self.area_total > 0:
            self.percentual_app = (self.area_app / self.area_total) * 100
            self.percentual_rl = (self.area_rl / self.area_total) * 100
            self.percentual_vegetacao_nativa = (self.area_remanescente_vegetacao / self.area_total) * 100
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "codigo_car": self.codigo_car,
            "nome_imovel": self.nome_imovel,
            "area_total": self.area_total,
            "area_app": self.area_app,
            "area_rl": self.area_rl,
            "status": self.status.value,
            "possui_sobreposicao": self.possui_sobreposicao,
            "possui_pendencias": self.possui_pendencias,
        }


class MonitoramentoAPP(Base):
    """
    Modelo de Monitoramento de APP (Área de Preservação Permanente)
    
    Armazena histórico de monitoramento de APPs via satélite.
    """
    __tablename__ = "ambiental_monitoramento_app"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    car_id = Column(UUID(as_uuid=True), ForeignKey("ambiental_car.id"), nullable=False)
    
    # Data do monitoramento
    data_monitoramento = Column(Date, nullable=False)
    data_processamento = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Áreas (em hectares)
    area_app_total = Column(Float, default=0.0)
    area_app_preservada = Column(Float, default=0.0)
    area_app_degradada = Column(Float, default=0.0)
    area_app_em_recuperacao = Column(Float, default=0.0)
    
    # Percentuais
    percentual_preservada = Column(Float, default=0.0)
    percentual_degradada = Column(Float, default=0.0)
    
    # Imagem de satélite
    imagem_satelite_url = Column(String(500), nullable=True)
    ndvi_medio = Column(Float, default=0.0)
    ndvi_minimo = Column(Float, default=0.0)
    ndvi_maximo = Column(Float, default=0.0)
    
    # Alertas
    possui_alerta = Column(Boolean, default=False)
    alertas_gerados = Column(Integer, default=0)
    
    # Geometria (GeoJSON)
    geometria = Column(JSONB, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relacionamentos
    tenant = relationship("Tenant")
    car = relationship("CAR", back_populates="monitoramentos")
    
    def __repr__(self):
        return f"<MonitoramentoAPP {self.data_monitoramento} - CAR {self.car_id}>"
    
    def calcular_percentuais(self):
        """Calcula percentuais de preservação"""
        if self.area_app_total > 0:
            self.percentual_preservada = (self.area_app_preservada / self.area_app_total) * 100
            self.percentual_degradada = (self.area_app_degradada / self.area_app_total) * 100


class AlertaDesmatamento(Base):
    """
    Modelo de Alerta de Desmatamento
    
    Alertas gerados automaticamente quando detectada
    supressão de vegetação nativa.
    """
    __tablename__ = "ambiental_alertas_desmatamento"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    car_id = Column(UUID(as_uuid=True), ForeignKey("ambiental_car.id"), nullable=False)
    
    # Data do alerta
    data_alerta = Column(DateTime, nullable=False, default=datetime.utcnow)
    data_evento = Column(Date, nullable=True)  # Data estimada do desmatamento
    
    # Localização
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Área desmatada (em hectares)
    area_desmatada = Column(Float, nullable=False, default=0.0)
    
    # Tipo de vegetação
    tipo_vegetacao = Column(String(100), nullable=True)
    # Floresta Ombrófila, Cerrado, Caatinga, etc.
    
    # Severidade
    severidade = Column(String(20), nullable=False, default="media")
    # baixa, media, alta, critica
    
    # Status
    status = Column(String(20), nullable=False, default="novo")
    # novo, em_analise, confirmado, falso_positivo, mitigado
    
    # Imagem
    imagem_url = Column(String(500), nullable=True)
    ndvi_anterior = Column(Float, default=0.0)
    ndvi_atual = Column(Float, default=0.0)
    
    # Notificações
    notificado = Column(Boolean, default=False)
    data_notificacao = Column(DateTime, nullable=True)
    email_notificado = Column(String(120), nullable=True)
    
    # Ações
    acoes_tomadas = Column(Text, nullable=True)
    data_acoes = Column(Date, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relacionamentos
    tenant = relationship("Tenant")
    car = relationship("CAR", back_populates="alertas")
    
    def __repr__(self):
        return f"<AlertaDesmatamento {self.data_alerta} - {self.area_desmatada}ha>"
    
    @property
    def severidade_cor(self) -> str:
        """Retorna cor do alerta"""
        cores = {
            "baixa": "green",
            "media": "yellow",
            "alta": "orange",
            "critica": "red",
        }
        return cores.get(self.severidade, "gray")


class OutorgaHidrica(Base):
    """
    Modelo de Outorga Hídrica
    
    Cadastro de outorgas para captação de água.
    """
    __tablename__ = "ambiental_outorgas_hidricas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    unidade_produtiva_id = Column(UUID(as_uuid=True), ForeignKey("unidades_produtivas.id"), nullable=False)
    
    # Dados da outorga
    numero_outorga = Column(String(50), nullable=True)
    orgao_emissor = Column(String(100), nullable=True)
    # ANA, DAEE, INEA, etc.
    
    # Datas
    data_emissao = Column(Date, nullable=True)
    data_vencimento = Column(Date, nullable=True)
    data_publicacao = Column(Date, nullable=True)
    
    # Tipo de captação
    tipo_captacao = Column(String(50), nullable=True)
    # superficial, subterranea
    
    # Uso da água
    uso_principal = Column(String(50), nullable=True)
    # irrigacao, animal, industrial, humano
    
    # Vazões (m³/h)
    vazao_maxima = Column(Float, default=0.0)
    vazao_media = Column(Float, default=0.0)
    vazao_outorgada = Column(Float, default=0.0)
    
    # Volume anual (m³)
    volume_anual = Column(Float, default=0.0)
    
    # Corpo hídrico
    nome_rio = Column(String(200), nullable=True)
    bacia_hidrografica = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default="ativa")
    # ativa, vencida, renovacao, suspensa
    
    # Coordenadas
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Arquivos
    pdf_outorga = Column(Text, nullable=True)  # Base64
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relacionamentos
    tenant = relationship("Tenant")
    fazenda = relationship("UnidadeProdutiva")
    
    def __repr__(self):
        return f"<OutorgaHidrica {self.numero_outorga}>"
    
    @property
    def dias_para_vencimento(self) -> int:
        """Calcula dias para vencimento"""
        if not self.data_vencimento:
            return 0
        delta = self.data_vencimento - datetime.now().date()
        return delta.days
    
    @property
    def precisa_renovar(self) -> bool:
        """Verifica se precisa renovar (180 dias antes)"""
        return self.dias_para_vencimento <= 180


class CCIR(Base):
    """
    Modelo de CCIR (Certificado de Cadastro de Imóvel Rural)
    
    Certificado emitido pelo INCRA.
    """
    __tablename__ = "ambiental_ccir"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    unidade_produtiva_id = Column(UUID(as_uuid=True), ForeignKey("unidades_produtivas.id"), nullable=False)
    
    # Dados do CCIR
    numero_ccir = Column(String(50), unique=True, nullable=False)
    codigo_imovel = Column(String(50), nullable=True)
    
    # Ano exercício
    ano_exercicio = Column(Integer, nullable=False)
    
    # Datas
    data_emissao = Column(Date, nullable=True)
    data_vencimento = Column(Date, nullable=True)
    
    # Área
    area_total = Column(Float, default=0.0)
    area_aproveitavel = Column(Float, default=0.0)
    
    # Status
    status = Column(String(20), nullable=False, default="ativo")
    # ativo, vencido
    
    # Arquivos
    pdf_ccir = Column(Text, nullable=True)  # Base64
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relacionamentos
    tenant = relationship("Tenant")
    fazenda = relationship("UnidadeProdutiva")
    
    def __repr__(self):
        return f"<CCIR {self.numero_ccir} - {self.ano_exercicio}>"
