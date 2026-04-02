"""Modelos para integração com ERP Sankhya."""

from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date

from core.database import Base


class SankhyaConfig(Base):
    """Configuração de integração com Sankhya."""
    __tablename__ = "sankhya_config"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # Conexão
    ws_url = Column(String(500), nullable=False)  # https://<servidor>/bpm/ws
    username = Column(String(100), nullable=False)
    password = Column(String(200), nullable=False)  # Criptografado
    
    # Status
    ativo = Column(Boolean, default=True)
    ultimo_teste = Column(DateTime)
    teste_status = Column(String(50))  # sucesso, erro
    
    # Sincronização
    sync_interval = Column(Integer, default=900)  # segundos (15 min)
    ultimo_sync = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SankhyaSyncLog(Base):
    """Log de sincronizações com Sankhya."""
    __tablename__ = "sankhya_sync_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    config_id = Column(Integer, ForeignKey("sankhya_config.id"))
    
    # Tipo de sincronização
    tipo = Column(String(50), nullable=False)  # pessoas, produtos, nfe, financeiro
    operacao = Column(String(20), nullable=False)  # import, export, sync
    
    # Status
    status = Column(String(50), default="pendente")  # pendente, processando, sucesso, erro
    registros_processados = Column(Integer, default=0)
    registros_sucesso = Column(Integer, default=0)
    registros_erro = Column(Integer, default=0)
    erro_mensagem = Column(Text)
    
    # Performance
    tempo_execucao_ms = Column(Float)
    
    # Período
    periodo_inicio = Column(DateTime)
    periodo_fim = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


class SankhyaPessoa(Base):
    """Pessoas sincronizadas do Sankhya."""
    __tablename__ = "sankhya_pessoas"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # ID Sankhya
    sankhya_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # Dados básicos
    tipo = Column(String(20))  # FISICA, JURIDICA
    nome = Column(String(200), nullable=False)
    nome_fantasia = Column(String(200))
    
    # Documentos
    cpf = Column(String(14))
    cnpj = Column(String(18))
    ie = Column(String(20))
    im = Column(String(20))
    
    # Contato
    email = Column(String(200))
    telefone = Column(String(20))
    celular = Column(String(20))
    
    # Endereço
    endereco = Column(String(200))
    numero = Column(String(20))
    complemento = Column(String(50))
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(String(2))
    cep = Column(String(10))
    pais = Column(String(100), default="Brasil")
    
    # Sankhya
    codigo_sankhya = Column(String(50))
    categoria = Column(String(50))  # CLIENTE, FORNECEDOR, TRANSPORTADORA, etc.
    
    # Status
    ativo = Column(Boolean, default=True)
    sincronizado_em = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SankhyaProduto(Base):
    """Produtos sincronizados do Sankhya."""
    __tablename__ = "sankhya_produtos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # ID Sankhya
    sankhya_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # Dados básicos
    codigo = Column(String(50), nullable=False)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    
    # Classificação fiscal
    ncm = Column(String(8))
    cest = Column(String(7))
    cfop = Column(String(5))
    origem = Column(String(2), default="0")  # 0=Nacional, 1=Importado, etc.
    
    # Unidade
    unidade = Column(String(10), default="UN")
    
    # Preços
    preco_custo = Column(Float)
    preco_venda = Column(Float)
    
    # Controle
    controle_estoque = Column(Boolean, default=True)
    controle_serial = Column(Boolean, default=False)
    
    # Sankhya
    codigo_sankhya = Column(String(50))
    categoria = Column(String(50))
    
    # Status
    ativo = Column(Boolean, default=True)
    sincronizado_em = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SankhyaNFe(Base):
    """Notas Fiscais sincronizadas com Sankhya."""
    __tablename__ = "sankhya_nfe"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # ID Sankhya
    sankhya_id = Column(String(50), unique=True, index=True)
    
    # Tipo
    tipo_operacao = Column(String(20))  # ENTRADA, SAIDA
    
    # Dados da NF
    numero = Column(String(20), nullable=False)
    serie = Column(String(10))
    modelo = Column(String(10), default="55")
    
    # Chave de acesso
    chave_acesso = Column(String(44), unique=True, index=True)
    
    # Documentos
    cnpj_emitente = Column(String(18))
    cnpj_destinatario = Column(String(18))
    
    # Valores
    valor_total = Column(Float)
    valor_produtos = Column(Float)
    valor_frete = Column(Float)
    valor_seguro = Column(Float)
    valor_desconto = Column(Float)
    valor_ipi = Column(Float)
    valor_icms = Column(Float)
    valor_pis = Column(Float)
    valor_cofins = Column(Float)
    
    # Datas
    data_emissao = Column(Date)
    data_saida = Column(Date)
    data_entrada = Column(Date)
    
    # Status
    status_sankhya = Column(String(50))  # AGUARDANDO_ENVIO, ENVIADO, AUTORIZADO, etc.
    protocolo_sankhya = Column(String(50))
    
    # Sincronização
    exportado_sankhya = Column(Boolean, default=False)
    importado_sankhya = Column(Boolean, default=False)
    sincronizado_em = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SankhyaLancamentoFinanceiro(Base):
    """Lançamentos financeiros sincronizados com Sankhya."""
    __tablename__ = "sankhya_lancamentos_financeiros"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # ID Sankhya
    sankhya_id = Column(String(50), unique=True, index=True)
    
    # Tipo
    tipo = Column(String(20))  # CONTAS_PAGAR, CONTAS_RECEBER
    
    # Dados do lançamento
    numero_documento = Column(String(50))
    valor = Column(Float, nullable=False)
    valor_saldo = Column(Float)
    
    # Datas
    data_lancamento = Column(Date)
    data_vencimento = Column(Date)
    data_pagamento = Column(Date)
    
    # Histórico
    historico = Column(String(500))
    
    # Rateio
    rateio = Column(JSON)  # {centro_custo: valor, ...}
    
    # Status
    status = Column(String(50))  # ABERTO, BAIXADO, VENCIDO, etc.
    
    # Sincronização
    exportado_sankhya = Column(Boolean, default=False)
    importado_sankhya = Column(Boolean, default=False)
    sincronizado_em = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SankhyaTabela(Base):
    """Tabelas auxiliares do Sankhya (CFOP, NCM, etc.)."""
    __tablename__ = "sankhya_tabelas"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Tipo de tabela
    tipo = Column(String(20), nullable=False)  # CFOP, NCM, CST, CSOSN, etc.
    
    # Dados
    codigo = Column(String(20), nullable=False)
    descricao = Column(String(500), nullable=False)
    complemento = Column(String(200))
    
    # Metadados
    dados_adicionais = Column(JSON)
    
    # Status
    ativo = Column(Boolean, default=True)
    sincronizado_em = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
