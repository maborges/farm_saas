"""
Modelos de Notas Fiscais (NFP-e e NF-e)

Módulo responsável pela gestão de notas fiscais do produtor rural.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

from services.api.core.database import Base


class TipoNotaFiscal(str, enum.Enum):
    """Tipo de nota fiscal"""
    NFP_E = "NFP-e"  # Nota Fiscal de Produtor Rural Eletrônica
    NF_E = "NF-e"    # Nota Fiscal Eletrônica
    NFC_E = "NFC-e"  # Nota Fiscal ao Consumidor Eletrônica


class StatusSEFAZ(str, enum.Enum):
    """Status da nota na SEFAZ"""
    EM_DIGITACAO = "em_digitacao"
    ASSINADA = "assinada"
    TRANSMITIDA = "transmitida"
    AUTORIZADA = "autorizada"
    CANCELADA = "cancelada"
    DENEGADA = "denegada"
    INUTILIZADA = "inutilizada"


class NotaFiscal(Base):
    """
    Modelo de Nota Fiscal (NFP-e e NF-e)
    
    Armazena todas as informações da nota fiscal eletrônica,
    desde os dados de emissão até o retorno da SEFAZ.
    """
    __tablename__ = "notas_fiscais"
    
    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Tipo e identificação da nota
    tipo = Column(SQLEnum(TipoNotaFiscal), nullable=False, default=TipoNotaFiscal.NFP_E)
    numero = Column(Integer, nullable=False)
    serie = Column(String(10), nullable=False, default="1")
    
    # Datas
    data_emissao = Column(DateTime, nullable=False, default=datetime.utcnow)
    data_saida_entrada = Column(DateTime, nullable=True)
    data_autorizacao = Column(DateTime, nullable=True)
    
    # Emitente (produtor rural)
    emitente_id = Column(UUID(as_uuid=True), ForeignKey("fazendas.id"), nullable=True)
    emitente_nome = Column(String(200), nullable=False)
    emitente_cnpj_cpf = Column(String(14), nullable=False)
    emitente_ie = Column(String(20), nullable=True)
    emitente_im = Column(String(20), nullable=True)  # Inscrição Municipal
    
    # Destinatário
    destinatario_tipo = Column(String(10), nullable=False)  # PF ou PJ
    destinatario_nome = Column(String(200), nullable=False)
    destinatario_documento = Column(String(14), nullable=False)
    destinatario_ie = Column(String(20), nullable=True)
    destinatario_email = Column(String(120), nullable=True)
    destinatario_telefone = Column(String(20), nullable=True)
    
    # Endereço do destinatário
    destinatario_logradouro = Column(String(200), nullable=True)
    destinatario_numero = Column(String(20), nullable=True)
    destinatario_complemento = Column(String(100), nullable=True)
    destinatario_bairro = Column(String(100), nullable=True)
    destinatario_municipio = Column(String(100), nullable=True)
    destinatario_uf = Column(String(2), nullable=True)
    destinatario_cep = Column(String(10), nullable=True)
    destinatario_pais = Column(String(50), nullable=True, default="Brasil")
    destinatario_cod_municipio = Column(String(7), nullable=True)  # Código IBGE
    
    # Valores da nota
    valor_total = Column(Float, nullable=False, default=0.0)
    valor_produtos = Column(Float, default=0.0)
    valor_frete = Column(Float, default=0.0)
    valor_seguro = Column(Float, default=0.0)
    valor_descontos = Column(Float, default=0.0)
    valor_outras_despesas = Column(Float, default=0.0)
    valor_tributos = Column(Float, default=0.0)
    valor_pis = Column(Float, default=0.0)
    valor_cofins = Column(Float, default=0.0)
    valor_icms = Column(Float, default=0.0)
    valor_ipi = Column(Float, default=0.0)
    
    # Base de cálculo
    base_calculo_icms = Column(Float, default=0.0)
    base_calculo_icms_st = Column(Float, default=0.0)
    valor_icms_st = Column(Float, default=0.0)
    
    # Informações de transporte
    modalidade_frete = Column(Integer, nullable=True)  # 0=Por conta do emitente, 1=Destinatário, etc.
    transportadora_nome = Column(String(200), nullable=True)
    transportadora_cnpj_cpf = Column(String(14), nullable=True)
    transportadora_ie = Column(String(20), nullable=True)
    transportadora_endereco = Column(String(200), nullable=True)
    transportadora_municipio = Column(String(100), nullable=True)
    transportadora_uf = Column(String(2), nullable=True)
    veiculo_placa = Column(String(10), nullable=True)
    veiculo_uf = Column(String(2), nullable=True)
    veiculo_rntc = Column(String(20), nullable=True)  # Registro Nacional de Transportador de Carga
    
    # Itens da nota (produtos/serviços)
    itens = Column(JSONB, nullable=False, default=list)
    # Estrutura do item:
    # [
    #   {
    #     "codigo": "001",
    #     "descricao": "Soja em grão",
    #     "ncm": "12019000",
    #     "cfop": "5101",
    #     "quantidade": 1000.00,
    #     "unidade": "SC",
    #     "valor_unitario": 150.00,
    #     "valor_total": 150000.00,
    #     "origem": "0",  # 0=Nacional, 1=Importada, etc.
    #     "csosn": "102",
    #     "aliq_icms": 0.0,
    #   }
    # ]
    
    # Informações adicionais
    info_adicionais_fisco = Column(Text, nullable=True)
    info_adicionais_contribuinte = Column(Text, nullable=True)
    
    # Dados da safra (para NFP-e rural)
    safra_id = Column(UUID(as_uuid=True), ForeignKey("safras.id"), nullable=True)
    codigo_agricultor = Column(String(20), nullable=True)  # Código do agricultor no sistema estadual
    
    # SEFAZ
    chave_acesso = Column(String(44), unique=True, nullable=True, index=True)
    status_sefaz = Column(SQLEnum(StatusSEFAZ), nullable=False, default=StatusSEFAZ.EM_DIGITACAO)
    numero_recibo = Column(String(15), nullable=True)
    numero_protocolo = Column(String(15), nullable=True)
    motivo_cancelamento = Column(Text, nullable=True)
    data_cancelamento = Column(DateTime, nullable=True)
    
    # Arquivos
    xml = Column(Text, nullable=True)  # XML completo da nota
    xml_danfe = Column(Text, nullable=True)  # PDF do DANFE em base64
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="notas_fiscais")
    emitente = relationship("Fazenda", back_populates="notas_fiscais")
    safra = relationship("Safra", back_populates="notas_fiscais")
    lancamentos_financeiros = relationship("FinLancamento", back_populates="nota_fiscal")
    
    # Índices compostos
    __table_args__ = (
        UniqueConstraint('tenant_id', 'tipo', 'serie', 'numero', name='uq_nota_unica'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<NotaFiscal {self.tipo} {self.numero}/{self.serie}>"
    
    @property
    def chave_acesso_formatada(self) -> str:
        """Retorna a chave de acesso formatada com pontos"""
        if not self.chave_acesso:
            return None
        # Formata: 0000.0000.0000.0000.0000.0000.0000.0000.0000.0000.0000
        chave = self.chave_acesso
        return f"{chave[:4]}.{chave[4:8]}.{chave[8:12]}.{chave[12:16]}.{chave[16:20]}.{chave[20:24]}.{chave[24:28]}.{chave[28:32]}.{chave[32:36]}.{chave[36:40]}.{chave[40:]}"
    
    @property
    def url_consulta(self) -> str:
        """Retorna URL de consulta da nota na SEFAZ"""
        if not self.chave_acesso:
            return None
        return f"https://www.nfe.fazenda.gov.br/portal/consulta.aspx?tipoConsulta=completa&tipoConteudo=XbSeqxE1plM=&chNFe={self.chave_acesso}"
    
    def to_dict(self) -> dict:
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "tipo": self.tipo.value,
            "numero": self.numero,
            "serie": self.serie,
            "data_emissao": self.data_emissao.isoformat() if self.data_emissao else None,
            "emitente_nome": self.emitente_nome,
            "destinatario_nome": self.destinatario_nome,
            "valor_total": self.valor_total,
            "status_sefaz": self.status_sefaz.value,
            "chave_acesso": self.chave_acesso,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
