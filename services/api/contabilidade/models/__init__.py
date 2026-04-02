"""Modelos para Contabilidade - Sprint 25."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date

from core.database import Base


class IntegracaoContabil(Base):
    """Configuração de integração com sistemas contábeis."""
    __tablename__ = "integracoes_contabeis"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Sistema contábil
    sistema = Column(String(50), nullable=False)  # dominio, fortes, contmatic, outros
    nome = Column(String(100), nullable=False)
    
    # Configurações
    configuracoes = Column(JSON, default={})
    credenciais = Column(JSON)  # Criptografado
    
    # Status
    ativo = Column(Boolean, default=True)
    ultima_exportacao = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExportacaoContabil(Base):
    """Histórico de exportações contábeis."""
    __tablename__ = "exportacoes_contabeis"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    integracao_id = Column(Integer, ForeignKey("integracoes_contabeis.id"))
    
    # Tipo de exportação
    tipo = Column(String(50), nullable=False)  # lancamentos, notas_fiscais, folha
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    
    # Arquivo
    arquivo_path = Column(String(500))
    arquivo_nome = Column(String(200))
    arquivo_formato = Column(String(20))  # txt, csv, xml, json
    arquivo_tamanho = Column(Integer)  # bytes
    
    # Status
    status = Column(String(50), default="pendente")  # pendente, processando, concluida, erro
    registros_exportados = Column(Integer)
    erro_mensagem = Column(Text)
    
    # Agendamento
    agendada = Column(Boolean, default=False)
    data_agendamento = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processada_em = Column(DateTime)
    
    # Relacionamentos
    integracao = relationship("IntegracaoContabil", backref="exportacoes")


class LancamentoContabil(Base):
    """Lançamentos contábeis para exportação."""
    __tablename__ = "lancamentos_contabeis"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Dados do lançamento
    data_lancamento = Column(Date, nullable=False)
    documento = Column(String(50))
    historico = Column(Text, nullable=False)
    
    # Valores
    valor_debito = Column(Float, default=0)
    valor_credito = Column(Float, default=0)
    
    # Contas contábeis
    conta_debito = Column(String(50))
    conta_credito = Column(String(50))
    
    # Centro de custo
    centro_custo = Column(String(50))
    
    # Origem
    origem = Column(String(50))  # fiscal, financeiro, rh, etc.
    origem_id = Column(Integer)  # ID do registro original
    
    # Status de exportação
    exportado = Column(Boolean, default=False)
    exportacao_id = Column(Integer, ForeignKey("exportacoes_contabeis.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    exportacao = relationship("ExportacaoContabil", backref="lancamentos")


class PlanoContas(Base):
    """Plano de contas contábeis."""
    __tablename__ = "plano_contas"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Dados da conta
    codigo = Column(String(50), nullable=False)
    nome = Column(String(200), nullable=False)
    tipo = Column(String(20))  # analitica, sintetica
    natureza = Column(String(20))  # devedora, credora
    
    # Hierarquia
    conta_pai_id = Column(Integer, ForeignKey("plano_contas.id"))
    nivel = Column(Integer, default=1)
    
    # Sistema contábil
    sistema_origem = Column(String(50))  # dominio, fortes, etc.
    codigo_sistema = Column(String(50))
    
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    conta_pai = relationship("PlanoContas", remote_side=[id], backref="contas_filhas")


class MapeamentoContabil(Base):
    """Mapeamento entre AgroSaaS e sistema contábil."""
    __tablename__ = "mapeamento_contabil"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    integracao_id = Column(Integer, ForeignKey("integracoes_contabeis.id"))
    
    # Mapeamento
    entidade_agrosaas = Column(String(50), nullable=False)  # receita, despesa, etc.
    campo_agrosaas = Column(String(100), nullable=False)
    valor_agrosaas = Column(String(100))  # Valor ou regra de mapeamento
    
    # Destino no sistema contábil
    conta_contabil = Column(String(50))
    centro_custo = Column(String(50))
    codigo_sistema = Column(String(50))
    
    # Tipo de operação
    tipo_operacao = Column(String(50))  # debito, credito, ambos
    
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    integracao = relationship("IntegracaoContabil", backref="mapeamentos")
