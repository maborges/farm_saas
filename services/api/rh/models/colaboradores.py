"""
Modelos de Colaboradores e Folha de Pagamento

Módulo responsável pela gestão de colaboradores e folha de pagamento rural.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

from services.api.core.database import Base


class TipoContrato(str, enum.Enum):
    """Tipo de contrato de trabalho"""
    CLT = "CLT"  # Celetista
    TEMPORARIO = "temporario"
    SAFRISTA = "safrista"
    ESTAGIARIO = "estagiario"
    AVULSO = "avulso"


class Cargo(str, enum.Enum):
    """Cargos comuns no agro"""
    TRATORISTA = "tratorista"
    MAQUINISTA = "maquinista"
    TRABALHADOR_RURAL = "trabalhador_rural"
    FEITOR = "feitor"
    AGRONOMO = "agronomo"
    VETERINARIO = "veterinario"
    ORDENHADOR = "ordenhador"
    OUTROS = "outros"


class Colaborador(Base):
    """
    Modelo de Colaborador (trabalhador rural)
    
    Armazena dados dos colaboradores para envio ao eSocial.
    """
    __tablename__ = "rh_colaboradores"
    
    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Dados pessoais
    nome = Column(String(200), nullable=False)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    nis = Column(String(11), nullable=True)  # Número de Identificação Social
    data_nascimento = Column(Date, nullable=True)
    sexo = Column(String(1), nullable=True)  # M ou F
    
    # Nacionalidade
    nacionalidade = Column(String(50), default="brasileira")
    naturalidade_municipio = Column(String(100), nullable=True)
    naturalidade_uf = Column(String(2), nullable=True)
    
    # Estado civil
    estado_civil = Column(String(20), nullable=True)
    
    # Escolaridade
    escolaridade = Column(String(50), nullable=True)
    
    # Endereço
    logradouro = Column(String(200), nullable=True)
    numero = Column(String(20), nullable=True)
    complemento = Column(String(100), nullable=True)
    bairro = Column(String(100), nullable=True)
    municipio = Column(String(100), nullable=True)
    uf = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    
    # Contato
    telefone = Column(String(20), nullable=True)
    email = Column(String(120), nullable=True)
    
    # Dados bancários (para pagamento)
    banco_codigo = Column(String(3), nullable=True)
    banco_agencia = Column(String(5), nullable=True)
    banco_conta = Column(String(20), nullable=True)
    banco_conta_dv = Column(String(2), nullable=True)
    banco_tipo = Column(String(20), nullable=True)  # conta_corrente, conta_poupanca
    
    # Dados do contrato
    tipo_contrato = Column(SQLEnum(TipoContrato), nullable=False, default=TipoContrato.CLT)
    cargo = Column(SQLEnum(Cargo), nullable=True)
    funcao = Column(String(100), nullable=True)
    cbo = Column(String(6), nullable=True)  # Código Brasileiro de Ocupação
    
    # Remuneração
    salario_base = Column(Float, nullable=False, default=0.0)
    piso_salarial = Column(Float, nullable=True)
    unidade_salario = Column(String(20), default="mensal")  # mensal, hora, tarefa
    
    # Jornada
    jornada_semanal = Column(Integer, default=44)  # horas semanais
    tipo_jornada = Column(String(20), default="normal")  # normal, parcial, noturna
    
    # Admissão
    data_admissao = Column(Date, nullable=False)
    data_inicio_atividades = Column(Date, nullable=True)
    
    # eSocial
    matricula_sistema = Column(String(30), nullable=True)
    codigo_categoria = Column(String(3), nullable=True)  # Categoria do eSocial
    
    # Status
    ativo = Column(Boolean, default=True)
    data_desligamento = Column(Date, nullable=True)
    motivo_desligamento = Column(String(100), nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="colaboradores")
    eventos = relationship("EventoAnimal", back_populates="colaborador")
    folha_pagamento = relationship("FolhaPagamento", back_populates="colaborador")
    
    def __repr__(self):
        return f"<Colaborador {self.nome} (CPF: {self.cpf})>"
    
    @property
    def nome_completo(self) -> str:
        """Retorna nome completo formatado"""
        return self.nome.strip()
    
    @property
    def cpf_formatado(self) -> str:
        """Formata CPF"""
        if not self.cpf or len(self.cpf) != 11:
            return self.cpf
        return f"{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}"
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "nome": self.nome,
            "cpf": self.cpf_formatado,
            "nis": self.nis,
            "cargo": self.cargo.value if self.cargo else None,
            "salario_base": self.salario_base,
            "data_admissao": self.data_admissao.isoformat() if self.data_admissao else None,
            "ativo": self.ativo,
        }


class FolhaPagamento(Base):
    """
    Modelo de Folha de Pagamento
    
    Armazena os valores de proventos e descontos por colaborador e competência.
    """
    __tablename__ = "rh_folha_pagamento"
    
    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    colaborador_id = Column(UUID(as_uuid=True), ForeignKey("rh_colaboradores.id"), nullable=False)
    
    # Competência
    mes_referencia = Column(Integer, nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    
    # Período de pagamento
    data_inicio_periodo = Column(Date, nullable=True)
    data_fim_periodo = Column(Date, nullable=True)
    data_pagamento = Column(Date, nullable=True)
    
    # Proventos
    salario_base = Column(Float, default=0.0)
    horas_extras = Column(Float, default=0.0)
    adicional_noturno = Column(Float, default=0.0)
    diarias = Column(Float, default=0.0)
    comissoes = Column(Float, default=0.0)
    producao = Column(Float, default=0.0)  # Pagamento por produção
    ferias = Column(Float, default=0.0)
    decimo_terceiro = Column(Float, default=0.0)
    outros_proventos = Column(Float, default=0.0)
    
    # Total de proventos
    total_proventos = Column(Float, default=0.0)
    
    # Descontos
    inss = Column(Float, default=0.0)
    irrf = Column(Float, default=0.0)
    funrural = Column(Float, default=0.0)
    vale_transporte = Column(Float, default=0.0)
    vale_alimentacao = Column(Float, default=0.0)
    emprestimos = Column(Float, default=0.0)
    atrasos = Column(Float, default=0.0)
    faltas = Column(Float, default=0.0)
    outros_descontos = Column(Float, default=0.0)
    
    # Total de descontos
    total_descontos = Column(Float, default=0.0)
    
    # Líquido
    salario_liquido = Column(Float, default=0.0)
    
    # eSocial
    enviado_esocial = Column(Boolean, default=False)
    data_envio_esocial = Column(DateTime, nullable=True)
    numero_recibo_esocial = Column(String(50), nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    # Relacionamentos
    tenant = relationship("Tenant")
    colaborador = relationship("Colaborador", back_populates="folha_pagamento")
    
    def __repr__(self):
        return f"<FolhaPagamento {self.colaborador.nome} - {self.mes_referencia}/{self.ano_referencia}>"
    
    def calcular_totais(self):
        """Calcula totais de proventos, descontos e líquido"""
        self.total_proventos = (
            self.salario_base +
            self.horas_extras +
            self.adicional_noturno +
            self.diarias +
            self.comissoes +
            self.producao +
            self.ferias +
            self.decimo_terceiro +
            self.outros_proventos
        )
        
        self.total_descontos = (
            self.inss +
            self.irrf +
            self.funrural +
            self.vale_transporte +
            self.vale_alimentacao +
            self.emprestimos +
            self.atrasos +
            self.faltas +
            self.outros_descontos
        )
        
        self.salario_liquido = self.total_proventos - self.total_descontos
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "colaborador_id": str(self.colaborador_id),
            "colaborador_nome": self.colaborador.nome if self.colaborador else None,
            "mes_referencia": self.mes_referencia,
            "ano_referencia": self.ano_referencia,
            "total_proventos": self.total_proventos,
            "total_descontos": self.total_descontos,
            "salario_liquido": self.salario_liquido,
            "enviado_esocial": self.enviado_esocial,
        }


class FunRural(Base):
    """
    Modelo de apuração do FUNRURAL
    
    Fundo de Assistência ao Trabalhador Rural (2.5% sobre receita bruta).
    """
    __tablename__ = "rh_funrural"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Competência
    mes_referencia = Column(Integer, nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    
    # Base de cálculo
    receita_bruta = Column(Float, nullable=False, default=0.0)
    aliquota = Column(Float, default=0.025)  # 2.5%
    
    # Valor devido
    valor_due = Column(Float, default=0.0)
    
    # Pagamento
    pago = Column(Boolean, default=False)
    data_pagamento = Column(Date, nullable=True)
    numero_darf = Column(String(50), nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def calcular(self):
        """Calcula valor devido"""
        self.valor_due = self.receita_bruta * self.aliquota
    
    def __repr__(self):
        return f"<FunRural {self.mes_referencia}/{self.ano_referencia} - R$ {self.valor_due}>"
