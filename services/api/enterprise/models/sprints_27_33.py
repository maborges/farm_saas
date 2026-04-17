"""Modelos consolidados para Sprints 27-33."""

from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date

from core.database import Base


# ============================================
# SPRINT 27 - MRV (Monitoramento, Reporte, Verificação)
# ============================================

class MRVProjeto(Base):
    """Projetos de carbono com MRV."""
    __tablename__ = "mrv_projetos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    carbono_projeto_id = Column(Integer, ForeignKey("carbono_projetos.id"))
    
    # Identificação
    nome = Column(String(200), nullable=False)
    metodologia = Column(String(100))  # Verra, Gold Standard
    padrao = Column(String(50))
    
    # Área
    area_ha = Column(Float)
    geometria = Column(JSON)
    
    # MRV
    monitoramento_ativo = Column(Boolean, default=True)
    ultimo_relatorio = Column(DateTime)
    proxima_verificacao = Column(Date)
    
    # Créditos
    creditos_gerados = Column(Float, default=0)
    creditos_verificados = Column(Float, default=0)
    creditos_vendidos = Column(Float, default=0)
    
    status = Column(String(50), default="ativo")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MRVRelatorio(Base):
    """Relatórios MRV."""
    __tablename__ = "mrv_relatorios"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    projeto_id = Column(Integer, ForeignKey("mrv_projetos.id"))
    
    # Período
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    
    # Dados
    remocoes_co2e = Column(Float, default=0)
    emissoes_evitadas = Column(Float, default=0)
    total_creditos = Column(Float, default=0)
    
    # Verificação
    verificado = Column(Boolean, default=False)
    verificador = Column(String(200))
    data_verificacao = Column(Date)
    
    # Arquivos
    arquivo_pdf = Column(String(500))
    
    status = Column(String(50), default="rascunho")
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# SPRINT 28 - ESG
# ============================================

class ESGIndicador(Base):
    """Indicadores ESG."""
    __tablename__ = "esg_indicadores"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    
    # Categoria
    categoria = Column(String(10), nullable=False)  # E, S, G
    subcategoria = Column(String(50))
    nome = Column(String(200), nullable=False)
    
    # Dados
    valor = Column(Float)
    unidade = Column(String(50))
    meta = Column(Float)
    
    # Período
    periodo_referencia = Column(String(20))  # "2026-Q1"
    
    # Padrões
    padrao_gri = Column(String(50))
    padrao_sasb = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ESGRelatorio(Base):
    """Relatórios ESG."""
    __tablename__ = "esg_relatorios"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    
    # Período
    ano_referencia = Column(Integer, nullable=False)
    
    # Scores
    score_ambiental = Column(Float)
    score_social = Column(Float)
    score_governanca = Column(Float)
    score_total = Column(Float)
    
    # Indicadores chave
    emissao_co2e = Column(Float)
    consumo_agua = Column(Float)
    residuos_reciclados = Column(Float)
    acidentes_trabalho = Column(Integer)
    diversidade_genero = Column(Float)
    rotatividade = Column(Float)
    
    # Status
    publicado = Column(Boolean, default=False)
    arquivo_pdf = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)


# ============================================
# SPRINT 28 - PISCICULTURA
# ============================================

class TanqueRede(Base):
    """Tanques-rede para piscicultura."""
    __tablename__ = "tanques_rede"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    unidade_produtiva_id = Column(Integer, ForeignKey("unidades_produtivas.id"))
    
    # Identificação
    nome = Column(String(100), nullable=False)
    codigo = Column(String(50))
    
    # Características
    volume_m3 = Column(Float)
    area_m2 = Column(Float)
    profundidade_m = Column(Float)
    formato = Column(String(50))  # circular, retangular
    
    # Espécie
    especie = Column(String(100))  # tilápia, tambaqui, etc.
    
    # Status
    status = Column(String(50), default="vazio")  # vazio, povoado, colheita
    data_povoamento = Column(Date)
    data_colheita_prevista = Column(Date)
    
    # Localização
    latitude = Column(Float)
    longitude = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Arracoamento(Base):
    """Registro de arraçoamento."""
    __tablename__ = "arracoamentos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    tanque_id = Column(Integer, ForeignKey("tanques_rede.id"), nullable=False)
    
    # Dados
    data = Column(Date, nullable=False)
    hora = Column(DateTime)
    
    quantidade_razao = Column(Float)  # kg
    tipo_racao = Column(String(100))
    
    # Responsável
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"))
    observacoes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Pesagem(Base):
    """Pesagem de peixes."""
    __tablename__ = "pesagens"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    tanque_id = Column(Integer, ForeignKey("tanques_rede.id"), nullable=False)
    
    # Dados
    data = Column(Date, nullable=False)
    
    # Amostragem
    total_peixes = Column(Integer)
    peso_total_kg = Column(Float)
    peso_medio_g = Column(Float)
    
    # Estimativa
    biomassa_estimada_kg = Column(Float)
    taxa_arracoamento = Column(Float)  # %
    
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"))
    observacoes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# SPRINT 29 - CONFINAMENTO
# ============================================

class ConfinamentoLote(Base):
    """Lotes de confinamento."""
    __tablename__ = "confinamento_lotes"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    unidade_produtiva_id = Column(Integer, ForeignKey("unidades_produtivas.id"))
    
    # Identificação
    codigo = Column(String(50), nullable=False)
    safra = Column(String(20))
    
    # Animais
    total_animais = Column(Integer)
    peso_inicial_kg = Column(Float)
    peso_inicial_total_kg = Column(Float)
    
    # Datas
    data_entrada = Column(Date, nullable=False)
    data_saida_prevista = Column(Date)
    data_saida_real = Column(Date)
    
    # Performance
    peso_saida_kg = Column(Float)
    ganho_medio_diario = Column(Float)  # GMD em kg/dia
    conversao_alimentar = Column(Float)  # CA
    
    # Status
    status = Column(String(50), default="confinado")  # confinado, terminado
    observacoes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class RacaoTMR(Base):
    """Fórmulas de ração TMR (Total Mixed Ration)."""
    __tablename__ = "racoes_tmr"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    
    # Identificação
    nome = Column(String(100), nullable=False)
    codigo = Column(String(50))
    
    # Fórmula
    ingredientes = Column(JSON)  # {"milho": 60, "silagem": 35, "nucleo": 5}
    
    # Nutrientes
    proteina_bruta = Column(Float)  # %
    ndt = Column(Float)  # Nutrientes Digestíveis Totais %
    energia_liquida = Column(Float)  # Mcal/kg
    
    # Custo
    custo_por_tonelada = Column(Float)
    
    # Status
    ativa = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Cocho(Base):
    """Controle de cochos."""
    __tablename__ = "cochos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    lote_id = Column(Integer, ForeignKey("confinamento_lotes.id"), nullable=False)
    
    # Identificação
    codigo = Column(String(50), nullable=False)
    comprimento_m = Column(Float)
    
    # Controle
    racao_fornecida_kg = Column(Float)
    sobra_kg = Column(Float)
    consumo_kg = Column(Float)
    
    # Data
    data = Column(Date, nullable=False)
    turno = Column(String(20))  # manhã, tarde
    
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# SPRINT 30 - GENÉTICA
# ============================================

class Raca(Base):
    """Raças bovinas."""
    __tablename__ = "racas"

    id = Column(Integer, primary_key=True, index=True)
    
    nome = Column(String(100), nullable=False)
    especie = Column(String(50))  # bovino, ovino
    origem = Column(String(100))
    
    # Padrões
    peso_adulto_macho = Column(Float)
    peso_adulto_femea = Column(Float)
    cor_padrao = Column(String(50))
    
    # DEPs médios
    dep_ganho_peso = Column(Float)
    dep_area_olho_lombo = Column(Float)
    dep_gordura_subcutanea = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AnimalGenetica(Base):
    """Dados genéticos de animais."""
    __tablename__ = "animal_genetica"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    animal_id = Column(Integer, ForeignKey("lotes.id"))  # Referenciar modelo existente

    # Identificação
    brinco = Column(String(50))
    raca_id = Column(Integer, ForeignKey("racas.id"))

    # Pedigree
    pai_id = Column(Integer)
    mae_id = Column(Integer)

    # DEPs
    dep_ganho_peso = Column(Float)
    dep_area_olho_lombo = Column(Float)
    dep_gordura_subcutanea = Column(Float)
    dep_maciez = Column(Float)
    
    # Status
    matriz = Column(Boolean, default=False)
    reprodutor = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SugestaoAcasalamento(Base):
    """Sugestões de acasalamento."""
    __tablename__ = "sugestoes_acasalamento"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    
    matriz_id = Column(Integer, nullable=False)
    reprodutor_id = Column(Integer, nullable=False)
    
    # Expected Progeny Differences
    dep_esperado = Column(JSON)
    
    # Score
    score_complementaridade = Column(Float)
    
    # Status
    realizado = Column(Boolean, default=False)
    data_acasalamento = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# SPRINT 31 - HEDGING
# ============================================

class ContratoFuturo(Base):
    """Contratos futuros de commodities."""
    __tablename__ = "contratos_futuros"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    
    # Contrato
    commodity = Column(String(50), nullable=False)  # soja, milho
    mercado = Column(String(50))  # CBOT, B3
    codigo_contrato = Column(String(50))
    
    # Vencimento
    mes_vencimento = Column(String(7))  # "JAN/2027"
    
    # Posição
    tipo_posicao = Column(String(10))  # compra, venda
    quantidade = Column(Float)
    unidade = Column(String(20))
    preco_contratado = Column(Float)
    
    # Status
    status = Column(String(50), default="aberto")  # aberto, encerrado, liquidado
    data_liquidacao = Column(Date)
    preco_liquidacao = Column(Float)
    
    # Resultado
    resultado = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class HedgeRegistro(Base):
    """Registros de operações de hedge."""
    __tablename__ = "hedge_registros"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    contrato_id = Column(Integer, ForeignKey("contratos_futuros.id"))
    
    # Operação
    tipo = Column(String(50))  # hedge_protecao, hedge_especulacao
    quantidade = Column(Float)
    preco = Column(Float)
    
    # Mercado
    cotacao_mercado = Column(Float)
    base = Column(Float)  # Diferença entre físico e futuro
    
    # Resultado
    resultado_papel = Column(Float)
    resultado_fisico = Column(Float)
    resultado_liquido = Column(Float)
    
    data_operacao = Column(Date, nullable=False)
    observacoes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# SPRINT 32 - IOT SENSORES
# ============================================

class SensorIoT(Base):
    """Sensores IoT."""
    __tablename__ = "sensores_iot"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    unidade_produtiva_id = Column(Integer, ForeignKey("unidades_produtivas.id"))
    
    # Identificação
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # temperatura, umidade, balanca, silo
    
    # Conexão
    protocolo = Column(String(20))  # MQTT, HTTP, LoRaWAN
    endpoint = Column(String(200))
    topic_mqtt = Column(String(200))
    
    # Localização
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Status
    status = Column(String(50), default="ativo")
    ultima_leitura = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SensorLeitura(Base):
    """Leituras de sensores."""
    __tablename__ = "sensores_leituras"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    sensor_id = Column(Integer, ForeignKey("sensores_iot.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False)
    
    # Dados
    timestamp = Column(DateTime, nullable=False, index=True)
    valor = Column(Float, nullable=False)
    unidade = Column(String(20))
    
    # Qualidade
    qualidade = Column(String(20))  # good, questionable, bad
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# SPRINT 33 - ILPF
# ============================================

class ILPFModulo(Base):
    """Módulos de ILPF (Integração Lavoura-Pecuária-Floresta)."""
    __tablename__ = "ilpf_modulos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    unidade_produtiva_id = Column(Integer, ForeignKey("unidades_produtivas.id"))
    
    # Identificação
    nome = Column(String(100), nullable=False)
    codigo = Column(String(50))
    
    # Tipo
    tipo_ilpf = Column(String(20))  # ILP, IPF, ILPF, ILPF
    
    # Área
    area_ha = Column(Float, nullable=False)
    geometria = Column(JSON)
    
    # Componentes
    cultura = Column(String(100))  # soja, milho
    especie_florestal = Column(String(100))  # eucalipto, pinus
    spacing_arvores = Column(String(50))  # 15x2m, etc.
    
    # Ciclo
    data_inicio = Column(Date)
    ano_implantacao = Column(Integer)
    
    # Crédito de carbono
    carbono_sequestrado = Column(Float)  # tCO2e
    
    status = Column(String(50), default="ativo")
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# SPRINT 33 - APP COLABORADORES
# ============================================

class ColaboradorApontamento(Base):
    """Apontamentos de horas de colaboradores."""
    __tablename__ = "colaborador_apontamentos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False)
    colaborador_id = Column(Integer, ForeignKey("colaboradores_rh.id"))
    
    # Dados
    data = Column(Date, nullable=False)
    horas_trabalhadas = Column(Float)
    
    # Atividade
    atividade = Column(String(200))
    talhao_id = Column(Integer)
    maquina_id = Column(Integer)
    
    # Produção
    quantidade_produzida = Column(Float)
    unidade = Column(String(20))
    
    # Status
    aprovado = Column(Boolean, default=False)
    aprovado_por = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Adicionar imports no final para evitar erros de circular import
# Estes modelos referenciam tabelas existentes em outros módulos
