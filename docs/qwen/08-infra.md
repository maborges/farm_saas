# AgroSaaS - Infraestrutura e Deploy

**Versão:** 1.0.0  
**Última Atualização:** 2026-03-31  
**Status:** Ativo  

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Desenvolvimento Local](#2-desenvolvimento-local)
3. [Produção](#3-produção)
4. [Banco de Dados](#4-banco-de-dados)
5. [CI/CD](#5-cicd)
6. [Monitoramento](#6-monitoramento)
7. [Segurança](#7-segurança)
8. [Backup e Recovery](#8-backup-e-recovery)
9. [Escalabilidade](#9-escalabilidade)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Visão Geral

### Arquitetura de Infraestrutura

```
┌─────────────────────────────────────────────────────────────────┐
│                         K3s Cluster                             │
│                      (On-Premise)                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Ingress   │  │  Frontend   │  │      Backend Pods       │  │
│  │  Controller │→ │  (Next.js)  │→ │     (FastAPI x3)        │  │
│  │  (Traefik)  │  │   x3 Pods   │  │    ReplicaSet: 3        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│         │                │                      │                │
│         │                │                      │                │
│  ┌──────┴────────────────┴──────────────────────┴────────┐      │
│  │                    Internal Network                    │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  PostgreSQL  │  │    Redis     │  │     Celery Workers   │   │
│  │  (Stateful)  │  │  (Stateful)  │  │        x2            │   │
│  │   16 + GIS   │  │   Cache+Pub  │  │   Background Tasks   │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes Principais

| Componente | Tecnologia | Função |
|------------|------------|--------|
| **Orquestrador** | K3s | Kubernetes leve on-premise |
| **Ingress** | Traefik | Load balancing e SSL |
| **Frontend** | Next.js 16 | SPA/SSR |
| **Backend** | FastAPI | API REST |
| **Database** | PostgreSQL 16 | Dados persistentes |
| **Cache** | Redis 7 | Cache e filas |
| **Workers** | Celery | Tarefas assíncronas |

---

## 2. Desenvolvimento Local

### Pré-requisitos

```bash
# Instalar
- Docker >= 24.0
- Docker Compose >= 2.20
- Node.js >= 20
- Python >= 3.12
- pnpm >= 8
```

### Setup Inicial

```bash
# 1. Clonar repositório
git clone https://github.com/agrosaas/farm.git
cd farm

# 2. Subir banco e redis
docker-compose up -d db redis

# 3. Backend - Instalar dependências
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 4. Backend - Configurar ambiente
cp .env.example .env.local
# Editar DATABASE_URL, JWT_SECRET, etc.

# 5. Backend - Rodar migrações
alembic upgrade head

# 6. Backend - Seed inicial
python scripts/seed.py

# 7. Backend - Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 8. Frontend - Instalar dependências
cd apps/web
pnpm install

# 9. Frontend - Configurar ambiente
cp .env.example .env.local
# Editar NEXT_PUBLIC_API_URL

# 10. Frontend - Iniciar dev server
pnpm dev
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: agrosaas-db
    environment:
      POSTGRES_USER: pguser
      POSTGRES_PASSWORD: pgpassword
      POSTGRES_DB: agrosaas
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pguser"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: agrosaas-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

### Scripts de Desenvolvimento

```bash
# Backend
cd services/api

# Rodar testes
pytest

# Rodar linter
ruff check .

# Rodar type checker
mypy .

# Criar migration
alembic revision --autogenerate -m "description"

# Aplicar migrações
alembic upgrade head

# Reverter migration
alembic downgrade -1

# Frontend
cd apps/web

# Rodar testes
pnpm test

# Rodar linter
pnpm lint

# Build de produção
pnpm build

# Type check
pnpm type-check
```

---

## 3. Produção

### Variáveis de Ambiente

```bash
# .env.production

# Database
DATABASE_URL=postgresql://user:pass@db-host:5432/agrosaas

# JWT
JWT_SECRET=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Email (SMTP)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
EMAIL_FROM=noreply@agrosaas.com.br

# Redis
REDIS_URL=redis://redis-host:6379/0

# Frontend
NEXT_PUBLIC_API_URL=https://api.agrosaas.com.br/api/v1
NEXT_PUBLIC_APP_URL=https://app.agrosaas.com.br

# Celery
CELERY_BROKER_URL=redis://redis-host:6379/1
CELERY_RESULT_BACKEND=redis://redis-host:6379/1
```

### Build e Deploy

```bash
# Backend - Build Docker
docker build -t agrosaas-api:latest -f services/api/Dockerfile .

# Frontend - Build
cd apps/web
pnpm build

# Deploy Kubernetes
kubectl apply -f infra/k8s/

# Verificar deploy
kubectl get pods -n agrosaas
kubectl get services -n agrosaas
kubectl get ingress -n agrosaas
```

### Kubernetes Manifests

```yaml
# infra/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agrosaas-api
  namespace: agrosaas
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agrosaas-api
  template:
    metadata:
      labels:
        app: agrosaas-api
    spec:
      containers:
      - name: api
        image: agrosaas-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: agrosaas-secrets
              key: database-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: agrosaas-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agrosaas-frontend
  namespace: agrosaas
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agrosaas-frontend
  template:
    metadata:
      labels:
        app: agrosaas-frontend
    spec:
      containers:
      - name: frontend
        image: agrosaas-frontend:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### Ingress e SSL

```yaml
# infra/k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agrosaas-ingress
  namespace: agrosaas
  annotations:
    kubernetes.io/ingress.class: traefik
    traefik.ingress.kubernetes.io/router.tls: "true"
spec:
  tls:
  - hosts:
    - api.agrosaas.com.br
    - app.agrosaas.com.br
    secretName: agrosaas-tls
  rules:
  - host: api.agrosaas.com.br
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: agrosaas-api
            port:
              number: 80
  - host: app.agrosaas.com.br
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: agrosaas-frontend
            port:
              number: 80
```

---

## 4. Banco de Dados

### PostgreSQL Setup

```sql
-- Criar extensão PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Criar schema para dados de fazendas
CREATE SCHEMA IF NOT EXISTS farms;

-- Configurar RLS (Row Level Security)
ALTER TABLE safras ENABLE ROW LEVEL SECURITY;

-- Política de isolamento por tenant
CREATE POLICY tenant_isolation ON safras
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Índices de performance
CREATE INDEX CONCURRENTLY idx_safras_tenant_ativo 
    ON safras(tenant_id, ativo);
CREATE INDEX CONCURRENTLY idx_operacoes_safra_data 
    ON operacoes_agricolas(safra_id, data_operacao);
```

### Connection Pooling

```python
# core/database.py
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,          # Conexões no pool
    max_overflow=40,       # Conexões extras temporárias
    pool_pre_ping=True,    # Verificar conexão antes de usar
    pool_recycle=3600,     # Reciclar conexões após 1h
)
```

### Backup Automático

```bash
#!/bin/bash
# scripts/backup-db.sh

BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/agrosaas_$DATE.sql.gz"

# Criar backup
pg_dump -h db-host -U pguser agrosaas | gzip > $BACKUP_FILE

# Manter últimos 7 dias
find $BACKUP_DIR -name "agrosaas_*.sql.gz" -mtime +7 -delete

# Upload para S3 (opcional)
aws s3 cp $BACKUP_FILE s3://agrosaas-backups/postgresql/
```

---

## 5. CI/CD

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports: [5432:5432]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        cd services/api
        pip install -e ".[dev]"
    
    - name: Run tests
      run: |
        cd services/api
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
    
    - name: Install pnpm
      uses: pnpm/action-setup@v2
      with:
        version: 8
    
    - name: Install dependencies
      run: |
        cd apps/web
        pnpm install
    
    - name: Run tests
      run: |
        cd apps/web
        pnpm test
    
    - name: Run linter
      run: |
        cd apps/web
        pnpm lint
    
    - name: Type check
      run: |
        cd apps/web
        pnpm type-check

  build-and-deploy:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build and push API
      uses: docker/build-push-action@v5
      with:
        context: .
        file: services/api/Dockerfile
        push: true
        tags: agrosaas/api:${{ github.sha }}
    
    - name: Build and push Frontend
      uses: docker/build-push-action@v5
      with:
        context: .
        file: apps/web/Dockerfile
        push: true
        tags: agrosaas/frontend:${{ github.sha }}
    
    - name: Deploy to K8s
      run: |
        # Configurar kubectl
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        
        # Atualizar imagens
        kubectl set image deployment/agrosaas-api \
          api=agrosaas/api:${{ github.sha }} -n agrosaas
        kubectl set image deployment/agrosaas-frontend \
          frontend=agrosaas/frontend:${{ github.sha }} -n agrosaas
        
        # Aguardar rollout
        kubectl rollout status deployment/agrosaas-api -n agrosaas
        kubectl rollout status deployment/agrosaas-frontend -n agrosaas
```

---

## 6. Monitoramento

### Health Checks

```python
# main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

@app.get("/health/redis")
async def health_redis():
    try:
        redis_client = get_redis()
        await redis_client.ping()
        return {"status": "healthy", "redis": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "redis": str(e)}
```

### Logging Estruturado

```python
# main.py
from loguru import logger
import sys

logger.configure(handlers=[{
    "sink": sys.stdout,
    "format": (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    "serialize": True,  # JSON para produção
}])

# Uso
logger.info("Usuário logado", user_id=str(user_id), tenant=str(tenant_id))
logger.warning("Tentativa de acesso inválido", tenant=str(tenant_id))
logger.error("Erro ao processar pagamento", error=str(e), invoice_id=str(invoice_id))
```

### Métricas (Prometheus)

```python
# metrics.py
from prometheus_client import Counter, Histogram, generate_latest

# Contadores
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Histograma de latência
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Endpoint de métricas
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Grafana Dashboards

**Painéis Principais:**
- Requests por segundo
- Latência p95, p99
- Error rate
- CPU/Memory usage
- Database connections
- Cache hit rate
- Celery task queue size

---

## 7. Segurança

### SSL/TLS

```bash
# Gerar certificado (Let's Encrypt)
certbot certonly --webroot -w /var/www/html \
  -d api.agrosaas.com.br \
  -d app.agrosaas.com.br

# Renovar automaticamente
0 3 * * * certbot renew --quiet
```

### Firewall

```bash
# UFW (Uncomplicated Firewall)
ufw default deny incoming
ufw default allow outgoing

# Permitir SSH
ufw allow 22/tcp

# Permitir HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Permitir K3s
ufw allow 6443/tcp

# Habilitar
ufw enable
```

### Secrets Management

```bash
# Kubernetes Secrets
kubectl create secret generic agrosaas-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=jwt-secret='...' \
  --from-literal=stripe-key='sk_live_...' \
  -n agrosaas

# Nunca commitar secrets no git!
# Usar .gitignore
echo ".env*" >> .gitignore
echo "*.secret" >> .gitignore
```

### Rate Limiting

```python
# slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...

@app.post("/auth/register")
@limiter.limit("3/hour")
async def register(request: Request, ...):
    ...
```

---

## 8. Backup e Recovery

### Estratégia de Backup

| Tipo | Frequência | Retenção | Local |
|------|------------|----------|-------|
| Database | Diário | 7 dias | Local + S3 |
| Database | Semanal | 4 semanas | S3 |
| Database | Mensal | 12 meses | S3 Glacier |
| Files (uploads) | Contínuo | 30 dias | S3 |

### Recovery Procedure

```bash
# 1. Identificar backup
aws s3 ls s3://agrosaas-backups/postgresql/ | tail -10

# 2. Download
aws s3 cp s3://agrosaas-backups/postgresql/agrosaas_20260331_030000.sql.gz .

# 3. Decomprimir
gunzip agrosaas_20260331_030000.sql.gz

# 4. Restaurar
psql -h db-host -U pguser agrosaas < agrosaas_20260331_030000.sql

# 5. Verificar
psql -h db-host -U pguser -d agrosaas -c "SELECT COUNT(*) FROM tenants;"
```

### Disaster Recovery

**RTO (Recovery Time Objective):** 4 horas  
**RPO (Recovery Point Objective):** 24 horas

**Procedimento:**
1. Acionar equipe de plantão
2. Identificar causa raiz
3. Restaurar último backup válido
4. Validar integridade dos dados
5. Reaplicar transações pendentes (se necessário)
6. Reativar serviços
7. Comunicar stakeholders

---

## 9. Escalabilidade

### Horizontal Scaling

```yaml
# HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agrosaas-api-hpa
  namespace: agrosaas
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agrosaas-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Database Scaling

**Read Replicas:**
```yaml
# Configurar réplicas de leitura
primary:
  host: db-primary.agrosaas.internal
  port: 5432

replicas:
  - host: db-replica-1.agrosaas.internal
    port: 5432
  - host: db-replica-2.agrosaas.internal
    port: 5432
```

**Connection Pooling:**
- PgBouncer para pooling de conexões
- Configurar `pool_size` e `max_overflow` adequados

### Cache Strategy

```python
# Redis Cache
from functools import wraps
import json

def cache_result(expire_seconds: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Tentar cache
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Executar e cachear
            result = await func(*args, **kwargs)
            await redis.setex(
                cache_key, 
                expire_seconds, 
                json.dumps(result)
            )
            return result
        return wrapper
    return decorator

@cache_result(expire_seconds=600)
async def get_safra_details(safra_id: UUID):
    ...
```

---

## 10. Troubleshooting

### Problemas Comuns

#### Backend não inicia

```bash
# Verificar logs
kubectl logs deployment/agrosaas-api -n agrosaas

# Verificar variáveis de ambiente
kubectl exec -it deployment/agrosaas-api -n agrosaas -- env

# Testar conexão com banco
kubectl exec -it deployment/agrosaas-api -n agrosaas -- \
  python -c "from core.database import engine; print(engine.url)"
```

#### Database lento

```sql
-- Queries lentas
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Índices faltantes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY abs(correlation) DESC;

-- Locks
SELECT * FROM pg_locks WHERE NOT granted;
```

#### Frontend com erro 500

```bash
# Verificar logs do Next.js
kubectl logs deployment/agrosaas-frontend -n agrosaas

# Verificar conexão com API
kubectl exec -it deployment/agrosaas-frontend -n agrosaas -- \
  curl -v https://api.agrosaas.com.br/health

# Verificar variáveis de ambiente
kubectl exec -it deployment/agrosaas-frontend -n agrosaas -- env
```

#### Celery tasks travadas

```bash
# Verificar filas
celery -A tasks.celery inspect active

# Verificar workers
celery -A tasks.celery inspect registered

# Purgar filas (cuidado!)
celery -A tasks.celery purge

# Restart workers
kubectl rollout restart deployment/agrosaas-celery -n agrosaas
```

### Comandos Úteis

```bash
# Kubernetes
kubectl get pods -n agrosaas
kubectl get services -n agrosaas
kubectl get ingress -n agrosaas
kubectl describe pod <pod-name> -n agrosaas
kubectl logs -f <pod-name> -n agrosaas
kubectl exec -it <pod-name> -n agrosaas -- bash

# Database
psql -h db-host -U pguser -d agrosaas
pg_dump -h db-host -U pguser agrosaas > backup.sql

# Redis
redis-cli -h redis-host
redis-cli INFO
redis-cli MONITOR

# Logs
journalctl -u k3s -f
docker logs <container-name> -f
```

---

## Referências Cruzadas

| Documento | Descrição |
|-----------|-----------|
| `docs/qwen/01-arquitetura.md` | Arquitetura geral |
| `docs/qwen/03-banco-dados.md` | Schema do banco |

---

## Changelog

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Documentação inicial completa |
