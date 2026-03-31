# Arquitetura Técnica - AgroSaaS 10/10

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** Em revisão

---

## 🏗️ Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         CAMADA DE API                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Mobile    │  │     Web     │  │   API       │              │
│  │   (RN)      │  │  (React)    │  │  Externa    │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └────────────────┴────────────────┘                      │
│                          │                                       │
│                  ┌───────▼────────┐                              │
│                  │  API Gateway   │                              │
│                  │  (Kong/AWS)    │                              │
│                  └───────┬────────┘                              │
└──────────────────────────┼──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    MICROSERVIÇOS (FastAPI)                       │
│  ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌────────┐      │
│  │  Core  │ │Agrícola│ │Financeiro│ │Pecuária│ │  RH    │      │
│  └────────┘ └────────┘ └──────────┘ └────────┘ └────────┘      │
│  ┌────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐      │
│  │Operac. │ │Ambiental │ │  IA    │ │  IoT   │ │Integration    │
│  └────────┘ └──────────┘ └────────┘ └────────┘ └────────┘      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    CAMADA DE DADOS                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  PostgreSQL │  │    Redis    │  │  Timescale  │              │
│  │  (Principal)│  │   (Cache)   │  │  (IoT/TS)   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  S3/MinIO   │  │ ElasticSearch│ │  MongoDB    │              │
│  │  (Files)    │  │  (Search)   │  │  (Docs)     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Stack Tecnológico

### Backend

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Framework | FastAPI (Python) | Performance, async, type hints |
| ORM | SQLAlchemy 2.0 | Type-safe, async support |
| Migrations | Alembic | Versionamento de banco |
| Validação | Pydantic v2 | Validação de dados |
| Auth | JWT + OAuth2 | Padrão industry |
| Task Queue | Celery + Redis | Background jobs |
| API Docs | OpenAPI/Swagger | Documentação automática |

### Frontend

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Framework | React 18 | Ecossistema, performance |
| Language | TypeScript | Type safety |
| State | Zustand | Simples, performático |
| UI | shadcn/ui + Tailwind | Customizável, moderno |
| Forms | React Hook Form + Zod | Validação |
| HTTP | TanStack Query | Cache, sync |
| Maps | Leaflet/Mapbox | GIS integration |

### Mobile

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Framework | React Native + Expo | Cross-platform |
| Offline DB | Dexie.js (IndexedDB) | Offline-first |
| Navigation | Expo Router | File-based routing |
| State | Zustand | Consistente com web |

### DevOps

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Cloud | AWS | Escala, confiabilidade |
| Container | Docker + ECS | Orquestração |
| CI/CD | GitHub Actions | Automação |
| Monitoring | Datadog + Sentry | Observabilidade |
| Logs | ELK Stack | Centralização |

---

## 🗄️ Modelo de Dados

### Core Models

```python
# services/api/core/models/tenants.py
class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    razao_social = Column(String(200), nullable=False)
    cnpj_cpf = Column(String(14), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    telefone = Column(String(20))
    plano_id = Column(UUID, ForeignKey('planos_assinatura.id'))
    status = Column(Enum(TenantStatus), default='ATIVO')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relações
    fazendas = relationship("Fazenda", back_populates="tenant")
    usuarios = relationship("UsuarioTenant", back_populates="tenant")
    assinaturas = relationship("AssinaturaTenant", back_populates="tenant")
```

```python
# services/api/core/models/usuarios.py
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(String(120), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    nome = Column(String(200), nullable=False)
    telefone = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relações
    tenants = relationship("UsuarioTenant", back_populates="usuario")
```

### Módulo Agrícola

```python
# services/api/agricola/models/safras.py
class Safra(Base):
    __tablename__ = "safras"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    tenant_id = Column(UUID, ForeignKey('tenants.id'), nullable=False)
    nome = Column(String(100), nullable=False)
    cultura = Column(String(50), nullable=False)  # soja, milho, etc.
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date)
    fase_atual = Column(Enum(FaseSafra), default='PLANEJADA')
    area_total_hectares = Column(Float)
    status = Column(Enum(StatusSafra), default='ATIVA')
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('tenant_id', 'nome', name='uq_tenant_safra'),
    )
```

```python
# services/api/agricola/models/operacoes.py
class OperacaoAgricola(Base):
    __tablename__ = "operacoes_agricolas"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    tenant_id = Column(UUID, ForeignKey('tenants.id'), nullable=False)
    safra_id = Column(UUID, ForeignKey('safras.id'))
    talhao_id = Column(UUID, ForeignKey('talhoes.id'), nullable=False)
    tipo_operacao = Column(Enum(TipoOperacao), nullable=False)
    data_execucao = Column(Date, nullable=False)
    descricao = Column(Text)
    custo_total = Column(Float, default=0)
    responsavel_id = Column(UUID, ForeignKey('usuarios.id'))
    
    # Condições climáticas
    temperatura = Column(Float)
    umidade = Column(Float)
    vento_velocidade = Column(Float)
    vento_direcao = Column(String(10))
```

### Módulo Financeiro

```python
# services/api/financeiro/models/notas_fiscais.py
class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    tenant_id = Column(UUID, ForeignKey('tenants.id'), nullable=False)
    tipo = Column(String(10), nullable=False)  # 'NFP-e', 'NF-e'
    numero = Column(Integer, nullable=False)
    serie = Column(String(10), nullable=False)
    data_emissao = Column(DateTime, nullable=False)
    data_saida_entrada = Column(DateTime)
    
    # Destinatário
    destinatario_tipo = Column(String(10))  # 'PF', 'PJ'
    destinatario_documento = Column(String(14))
    destinatario_nome = Column(String(200))
    
    # Valores
    valor_total = Column(Float, nullable=False)
    valor_produtos = Column(Float)
    valor_frete = Column(Float)
    valor_seguro = Column(Float)
    valor_descontos = Column(Float)
    
    # SEFAZ
    chave_acesso = Column(String(44), unique=True)
    status_sefaz = Column(String(20))  # 'autorizada', 'cancelada'
    data_autorizacao = Column(DateTime)
    numero_recibo = Column(String(15))
    
    # Arquivos
    xml = Column(Text)  # XML da nota
    xml_danfe = Column(Text)  # PDF em base64
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

```python
# services/api/financeiro/models/lcdpr.py
class LCDPR(Base):
    __tablename__ = "lcdpr"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    tenant_id = Column(UUID, ForeignKey('tenants.id'), nullable=False)
    produtor_cpf = Column(String(11), nullable=False)
    mes_referencia = Column(Integer, nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    
    # Saldos
    saldo_anterior = Column(Float, default=0)
    total_receitas = Column(Float, default=0)
    total_despesas = Column(Float, default=0)
    saldo_atual = Column(Float, default=0)
    
    # Detalhes
    receitas = Column(JSON)  # [{tipo, valor, data, fonte}]
    despesas = Column(JSON)  # [{tipo, valor, data, favorecido}]
    
    # RFB
    hash_receita_federal = Column(String(64))
    numero_recibo = Column(String(20))
    data_transmissao = Column(DateTime)
    xml_gerado = Column(Text)
```

### Módulo Ambiental

```python
# services/api/ambiental/models/car.py
class CAR(Base):
    __tablename__ = "ambiental_car"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    tenant_id = Column(UUID, ForeignKey('tenants.id'), nullable=False)
    fazenda_id = Column(UUID, ForeignKey('fazendas.id'), nullable=False)
    
    # Dados do CAR
    codigo_car = Column(String(50), unique=True, nullable=False)
    numero_recibo = Column(String(50))
    data_cadastro = Column(DateTime)
    data_atualizacao = Column(DateTime)
    
    # Áreas
    area_total_hectares = Column(Float, nullable=False)
    area_app_hectares = Column(Float, default=0)
    area_rl_hectares = Column(Float, default=0)
    area_uso_restrito_hectares = Column(Float, default=0)
    area_consolidada_hectares = Column(Float, default=0)
    area_remanescente_vegetacao = Column(Float, default=0)
    
    # Sobreposições
    sobreposicoes = Column(JSON)  # [{tipo: 'TI', area, nome}, ...]
    
    # Status
    status = Column(String(20), default='ATIVO')  # ATIVO, PENDENTE, CANCELADO
    pendencias = Column(JSON)  # [{codigo, descricao, gravidade}]
    
    # Arquivos
    recibo_pdf = Column(Text)
    memoria_descritiva = Column(Text)
```

---

## 🔐 Segurança

### Autenticação e Autorização

```python
# services/api/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    to_encode.update({"type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### RBAC (Role-Based Access Control)

```python
# services/api/core/models/permissoes.py
class Role(Base):
    __tablename__ = "perfis_acesso"
    
    id = Column(UUID, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(200))
    permissoes = Column(JSON)  # ['agricola:safra:create', ...]

class UsuarioTenant(Base):
    __tablename__ = "tenants_usuarios"
    
    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID, ForeignKey('tenants.id'))
    usuario_id = Column(UUID, ForeignKey('usuarios.id'))
    role_id = Column(UUID, ForeignKey('perfis_acesso.id'))
    fazendas_permitidas = Column(JSON)  # Lista de IDs de fazendas
```

---

## 🚀 Performance e Escala

### Cache Strategy

```python
# services/api/core/cache.py
import redis
from functools import wraps
import json

redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=0,
    decode_responses=True
)

def cache_key(prefix: str, **kwargs):
    """Generate cache key"""
    key_parts = [prefix] + [f"{k}={v}" for k, v in kwargs.items()]
    return ":".join(key_parts)

def cached(expire_seconds: int = 300):
    """Decorator para cache de funções"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = cache_key(func.__name__, **kwargs)
            cached_value = redis_client.get(key)
            
            if cached_value:
                return json.loads(cached_value)
            
            result = await func(*args, **kwargs)
            redis_client.setex(key, expire_seconds, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Database Optimization

```python
# services/api/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    config.DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    echo=False
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Indexes críticos
# CREATE INDEX idx_operacoes_safra ON operacoes_agricolas(safra_id);
# CREATE INDEX idx_financeiro_vencimento ON fin_receitas(data_vencimento);
# CREATE INDEX idx_car_tenant ON ambiental_car(tenant_id);
```

---

## 📡 Integrações Externas

### SEFAZ (NFe)

```python
# services/api/financeiro/services/sefaz.py
from pynfe.processamento.assinatura import AssinaturaA1
from pynfe.processamento.serializacao import SerializacaoXML
from pynfe.processamento.validacao import Validacoes
from pynfe.entidades import NotaFiscal, Emitente, Destinatario

class SefazService:
    def __init__(self, certificado_path: str, senha: str):
        self.certificado = AssinaturaA1(certificado_path, senha)
        self.serializador = SerializacaoXML()
        self.validador = Validacoes()
        
    async def emitir_nfp(self, nota: NotaFiscalSchema):
        # 1. Criar entidade NotaFiscal
        nf = self._mapear_nota(nota)
        
        # 2. Serializar para XML
        xml = self.serializador.exportar(nf)
        
        # 3. Validar XML
        erros = self.validador.validar(xml)
        if erros:
            raise ValueError(erros)
        
        # 4. Assinar
        xml_assinado = self.certificado.assinar(xml)
        
        # 5. Transmitir
        resposta = self._transmitir_sefaz(xml_assinado)
        
        # 6. Processar resposta
        if resposta.status == 100:  # Autorizada
            return {
                'chave_acesso': resposta.chave,
                'numero_recibo': resposta.recibo,
                'xml': xml_assinado
            }
```

### eSocial

```python
# services/api/rh/services/esocial.py
class ESocialService:
    BASE_URL = "https://servicos.esocial.gov.br"
    
    def __init__(self, certificado_path: str, senha: str):
        self.certificado = (certificado_path, senha)
        
    async def enviar_admissao(self, colaborador: ColaboradorSchema):
        # Gerar XML S-2200
        xml = self._gerar_s2200(colaborador)
        
        # Assinar
        xml_assinado = self._assinar(xml)
        
        # Enviar
        resposta = self._enviar_lote([xml_assinado])
        
        return {
            'recibo': resposta.recibo,
            'status': resposta.status
        }
```

### John Deere Ops Center

```python
# services/api/iot/services/john_deere.py
import httpx

class JohnDeereService:
    BASE_URL = "https://operationscenter.jd.com"
    TOKEN_URL = "https://operationscenter.jd.com/oauth/2.0/token"
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        
    async def get_access_token(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                }
            )
            data = response.json()
            self._access_token = data['access_token']
            return self._access_token
            
    async def get_machine_data(self, machine_id: str):
        await self.get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/api/organizations/-/machines/{machine_id}",
                headers={'Authorization': f'Bearer {self._access_token}'}
            )
            return response.json()
```

---

## 📊 Monitoramento e Observabilidade

### Logging

```python
# services/api/core/logging_config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logHandler = logging.StreamHandler()
    
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    
    return logger
```

### Metrics

```python
# services/api/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Requests
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

# Response time
REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'API request latency',
    ['endpoint']
)

# Database
DB_CONNECTIONS = Gauge(
    'db_connections_active',
    'Active database connections'
)
```

---

## 🔄 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=services/api
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t agrosaas/api:${{ github.sha }} .
      - name: Push to ECR
        run: aws ecr push ...

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        run: aws ecs update-service ...
```

---

## 📈 Escalabilidade

### Horizontal Scaling

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                         │
│                    (AWS ALB)                             │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐
│ API 1 │ │ API 2│ │ API 3│  (Auto-scaling group)
└───┬───┘ └──┬───┘ └──┬───┘
    │        │        │
    └────────┴────────┘
             │
    ┌────────▼────────┐
    │   PostgreSQL    │
    │   (RDS Multi-AZ)│
    └─────────────────┘
```

### Database Sharding (Futuro)

```python
# services/api/core/sharding.py
class ShardingRouter:
    """Roteamento por tenant_id"""
    
    def get_database_url(self, tenant_id: UUID) -> str:
        shard = self._get_shard(tenant_id)
        return config.DATABASE_URLS[shard]
    
    def _get_shard(self, tenant_id: UUID) -> int:
        # Hash-based sharding
        return hash(tenant_id) % len(config.DATABASE_URLS)
```

---

**Aprovado por:** _______________________
**Data:** ___/___/_____
