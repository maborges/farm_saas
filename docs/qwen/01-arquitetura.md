# AgroSaaS - Arquitetura do Sistema

**Versão:** 1.0.0  
**Última Atualização:** 2026-03-31  
**Status:** Ativo  
**Owners:** Tech Lead + Arquiteto  

---

## 📋 Índice

1. [Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
2. [Stack Tecnológico](#2-stack-tecnológico)
3. [Arquitetura de Monolito Modular](#3-arquitetura-de-monolito-modular)
4. [Multi-Tenancy](#4-multi-tenancy)
5. [RBAC - Controle de Acesso](#5-rbac---controle-de-acesso)
6. [Estrutura do Monorepo](#6-estrutura-do-monorepo)
7. [Padrões de Comunicação](#7-padrões-de-comunicação)
8. [Segurança](#8-segurança)
9. [Infraestrutura](#9-infraestrutura)
10. [Dependências entre Módulos](#10-dependências-entre-módulos)

---

## 1. Visão Geral da Arquitetura

AgroSaaS é uma plataforma SaaS B2B para gestão de fazendas, construída como um **Monolito Modular** com separação clara de domínios.

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│                    Next.js 16 + React 19                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Dashboard  │  │   Backoffice│  │   Onboarding/Auth       │ │
│  │  (Tenant)   │  │   (Admin)   │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS / JSON
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                 │
│                   FastAPI (Python 3.12)                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    CORE (Núcleo)                          │  │
│  │  Auth │ Tenant │ RBAC │ Billing │ CRM │ Support │ Config  │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │
│  │  AGRICOLA   │ │  PECUARIA   │ │ FINANCEIRO  │ │OPERACIONAL│  │
│  │   (A1-A5)   │ │   (P1-P4)   │ │  (F1-F4)    │ │ (O1-O3)   │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │
│  ┌─────────────┐ ┌─────────────┐                                │
│  │     RH      │ │  AMBIENTAL  │                                │
│  │  (RH1-RH2)  │ │ (AM1-AM2)   │                                │
│  └─────────────┘ └─────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Async SQLAlchemy
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BANCO DE DADOS                             │
│                   PostgreSQL 16 + PostGIS                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Core Tables│  │ Module Tables│  │  Audit/History Tables  │  │
│  │  (tenants,  │  │ (safras,     │  │  (admin_audit_log,     │  │
│  │   usuarios) │  │  animais)    │  │   eventos_animais)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Pub/Sub
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CACHE / FILA                            │
│                        Redis 7                                  │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │   Cache     │  │  Celery     │                               │
│  │   Session   │  │  Tasks      │                               │
│  └─────────────┘  └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Stack Tecnológico

### Backend
| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Python** | 3.12 | Linguagem principal |
| **FastAPI** | 0.115+ | Framework web async |
| **SQLAlchemy** | 2.0+ | ORM async |
| **Pydantic** | 2.7+ | Validação de schemas |
| **Alembic** | 1.13+ | Migrações de banco |
| **asyncpg** | 0.29+ | Driver PostgreSQL async |
| **Redis** | 5.0+ | Cache e filas |
| **Celery** | 5.4+ | Tarefas assíncronas |
| **python-jose** | 3.3+ | JWT tokens |
| **passlib** | 1.7+ | Hash de senhas |
| **GeoAlchemy2** | 0.14+ | Dados geoespaciais |
| **Loguru** | 0.7+ | Logging estruturado |

### Frontend
| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Next.js** | 16 | Framework React |
| **React** | 19 | UI library |
| **TypeScript** | 5 | Type safety |
| **TanStack Query** | 5 | Server state management |
| **Zustand** | 5 | Client state management |
| **shadcn/ui** | 4 | Component library |
| **Tailwind CSS** | 4 | Styling |
| **Zod** | 4 | Validação de schemas |
| **MapLibre GL** | 5 | Mapas e GIS |

### Infraestrutura
| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **PostgreSQL** | 16 | Banco de dados principal |
| **PostGIS** | 3.x | Dados geoespaciais |
| **Redis** | 7 | Cache e message broker |
| **Docker** | - | Containerização |
| **K3s/Kubernetes** | - | Orquestração (planejado) |

---

## 3. Arquitetura de Monolito Modular

### Princípios Fundamentais

1. **Separação por Domínios**: Cada módulo representa um domínio de negócio completo
2. **Acoplamento Fraco**: Módulos se comunicam via APIs bem definidas
3. **Alta Coesão**: Cada módulo tem responsabilidade única e bem definida
4. **Defense in Depth**: Múltiplas camadas de validação e segurança

### Camadas da Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Routers)                      │
│  - Validação de entrada (Pydantic)                          │
│  - Feature gates (require_module)                           │
│  - RBAC (require_role)                                      │
│  - Injeção de dependências                                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Service Layer (Services)                    │
│  - Lógica de negócio                                        │
│  - Validações de domínio                                    │
│  - Tenant isolation (BaseService)                           │
│  - Transações de banco                                      │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               Repository Layer (BaseService)                │
│  - Acesso a dados                                           │
│  - Filtro tenant automático                                 │
│  - CRUD genérico                                            │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database Layer (Models)                    │
│  - SQLAlchemy ORM                                           │
│  - Multi-tenancy (tenant_id em todas tabelas)               │
│  - Constraints e foreign keys                               │
└─────────────────────────────────────────────────────────────┘
```

### Estrutura de Cada Módulo

```
services/api/{dominio}/{modulo}/
├── __init__.py              # Exports principais
├── router.py                # FastAPI router (rotas HTTP)
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic schemas (input/output)
├── services.py              # Lógica de negócio
├── dependencies.py          # Dependencies específicas (opcional)
├── exceptions.py            # Exceções customizadas (opcional)
└── README.md                # Documentação do módulo
```

**📄 Ver:** `docs/qwen/02-modulos.md` para detalhes de cada módulo

---

## 4. Multi-Tenancy

### Estratégia de Isolamento

AgroSaaS utiliza **isolamento lógico por tenant** com `tenant_id` em todas as tabelas.

```
┌─────────────────────────────────────────────────────────────┐
│                        TENANT A                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Safra 1 │  │  Safra 2 │  │  Safra 3 │                  │
│  │ tenant_id│  │ tenant_id│  │ tenant_id│                  │
│  │ = UUID-A │  │ = UUID-A │  │ = UUID-A │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        TENANT B                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Safra 1 │  │  Safra 2 │  │  Safra 3 │                  │
│  │ tenant_id│  │ tenant_id│  │ tenant_id│                  │
│  │ = UUID-B │  │ = UUID-B │  │ = UUID-B │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Camadas de Segurança

| Camada | Implementação | Descrição |
|--------|---------------|-----------|
| **1. JWT Claims** | `tenant_id` no token | Extraído em `get_tenant_id()` |
| **2. Service Layer** | `BaseService` injeta `tenant_id` | Filtro automático em todas queries |
| **3. Database** | PostgreSQL RLS (quando disponível) | Row Level Security no banco |
| **4. Validação** | `TenantViolationError` | Exceção se tentar acessar outro tenant |

### Fluxo de Requisição

```
1. Cliente → Request com JWT token
                │
                ▼
2. FastAPI → Depends(get_tenant_id)
                │
                ▼
3. Extrai tenant_id do JWT claim
                │
                ▼
4. Instancia Service(session, tenant_id)
                │
                ▼
5. BaseService filtra TODAS queries com tenant_id
                │
                ▼
6. Retorna apenas dados do tenant correto
```

**📄 Ver:** `docs/qwen/03-banco-dados.md` para schema completo

---

## 5. RBAC - Controle de Acesso

### Dois Níveis de RBAC

#### Backoffice (Admin SaaS)

| Role | Permissões |
|------|------------|
| `super_admin` | Acesso total (*) |
| `admin` | Gestão de tenants, planos, suporte |
| `suporte` | Visualização + suporte |
| `financeiro` | Faturamento e billing |
| `comercial` | Planos, cupons, CRM |

#### Tenant (Assinante)

| Role | Permissões |
|------|------------|
| `owner` | Acesso total no tenant (*) |
| `admin` | Gestão completa (exceto billing) |
| `gerente` | Gerente de área |
| `agronomo` | Módulo agrícola completo |
| `operador` | Operações de campo |
| `consultor` | Apenas leitura |
| `financeiro` | Módulo financeiro completo |

### Feature Gates por Módulo

```python
# Exemplo de uso em router
@router.post(
    "/safras",
    dependencies=[Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO))]
)
async def criar_safra(...):
    ...
```

**📄 Ver:** `docs/qwen/06-permissoes.md` para catálogo completo

---

## 6. Estrutura do Monorepo

```
/opt/lampp/htdocs/farm/
├── apps/
│   ├── web/                          # Next.js 16 frontend
│   │   ├── src/
│   │   │   ├── app/                  # App Router
│   │   │   │   ├── (auth)/           # Login, register
│   │   │   │   ├── (dashboard)/      # Dashboard autenticado
│   │   │   │   │   ├── agricola/     # Módulo agrícola
│   │   │   │   │   ├── pecuaria/     # Módulo pecuária
│   │   │   │   │   ├── financeiro/   # Módulo financeiro
│   │   │   │   │   ├── operacional/  # Módulo operacional
│   │   │   │   │   └── backoffice/   # Admin SaaS
│   │   │   ├── components/           # React components
│   │   │   ├── hooks/                # Custom hooks
│   │   │   ├── lib/                  # Utilities
│   │   │   └── types/                # TypeScript types
│   │   └── package.json
│   └── mobile/                       # React Native (planejado)
│
├── services/
│   └── api/                          # FastAPI backend
│       ├── core/                     # Núcleo (auth, tenant, RBAC)
│       │   ├── models/               # Core models
│       │   ├── routers/              # Core routers
│       │   ├── base_service.py       # Repository pattern
│       │   ├── constants.py          # Constantes globais
│       │   └── dependencies.py       # DI functions
│       │
│       ├── agricola/                 # Módulo agrícola
│       │   ├── a1_planejamento/      # Safra, orçamento
│       │   ├── safras/               # Gestão de safras
│       │   ├── talhoes/              # Talhões/geolocalização
│       │   ├── operacoes/            # Caderno de campo
│       │   ├── romaneios/            # Colheita
│       │   ├── monitoramento/        # Pragas/doenças
│       │   └── ... (24 submódulos)
│       │
│       ├── financeiro/               # Módulo financeiro
│       ├── pecuaria/                 # Módulo pecuária
│       ├── operacional/              # Módulo operacional
│       ├── rh/                       # Módulo RH
│       └── notificacoes/             # Notificações
│
├── packages/                         # Shared packages
│   ├── types/                        # TypeScript types
│   ├── utils/                        # Utilities compartilhadas
│   └── zod-schemas/                  # Validação compartilhada
│
├── docs/
│   ├── architecture/                 # Docs de arquitetura
│   └── qwen/                         # Documentação modular (esta pasta)
│
├── infra/
│   ├── docker/                       # Docker configs
│   └── k8s/                          # Kubernetes manifests
│
├── docker-compose.yml                # PostgreSQL + Redis
└── package.json                      # pnpm workspace
```

---

## 7. Padrões de Comunicação

### Frontend ↔ Backend

```
┌──────────────┐                    ┌──────────────┐
│   Next.js    │                    │   FastAPI    │
│   (Client)   │                    │   (Server)   │
└──────┬───────┘                    └──────┬───────┘
       │                                    │
       │  GET /api/v1/agricola/safras       │
       │  Authorization: Bearer <JWT>       │
       │  X-Tenant-ID: <UUID>               │
       │                                    │
       │◄───────────────────────────────────│
       │  200 OK                            │
       │  Content-Type: application/json    │
       │  { "data": [...], "total": 100 }   │
       │                                    │
```

### Comunicação entre Módulos

**Regra:** Módulos NÃO se comunicam diretamente. Toda comunicação passa pelo CORE ou via eventos.

```
❌ PROIBIDO:
  AgricolaService → PecuariaService (import direto)

✅ PERMITIDO:
  1. Via API interna (HTTP)
  2. Via eventos (Redis pub/sub)
  3. Via shared models do CORE
```

### Eventos de Domínio

```python
# Exemplo: Evento de colheita registrada
class ColheitaRegistradaEvent:
    safra_id: UUID
    talhao_id: UUID
    peso_total_kg: float
    produtividade_sc_ha: float
    tenant_id: UUID

# Publicado em romaneios/service.py após criar romaneio
# Financeiro consome e cria receita automaticamente
```

---

## 8. Segurança

### Autenticação

- **JWT Tokens** com expiração de 24h
- **Refresh tokens** armazenados em `sessoes` table
- **Hash de senha** com bcrypt (passlib)
- **Rate limiting** em endpoints de auth

### Autorização

- **RBAC** em todos endpoints
- **Feature gates** por módulo contratado
- **Tenant isolation** em todas queries
- **Audit logging** de ações críticas

### Validações

- **Pydantic** para input validation
- **Type hints** obrigatórios em Python
- **Zod schemas** no frontend (compartilhados)

### Dados Sensíveis

- **Nunca logar** dados sensíveis (CPF, valores)
- **HTTPS** obrigatório em produção
- **CORS** configurado por ambiente

---

## 9. Infraestrutura

### Desenvolvimento Local

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    environment:
      POSTGRES_USER: pguser
      POSTGRES_PASSWORD: pgpassword
      POSTGRES_DB: agrosaas

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

### Produção (Planejado)

```
┌────────────────────────────────────────────────────────────┐
│                    K3s Cluster (On-Prem)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Ingress     │  │  Frontend    │  │  Backend Pods    │  │
│  │  Controller  │→ │  (Next.js)   │→ │  (FastAPI x3)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                              │               │
│  ┌──────────────┐  ┌──────────────┐         │               │
│  │  PostgreSQL  │  │    Redis     │←────────┘               │
│  │  (Stateful)  │  │  (Stateful)  │                         │
│  └──────────────┘  └──────────────┘                         │
└────────────────────────────────────────────────────────────┘
```

---

## 10. Dependências entre Módulos

### Matriz de Dependências

| Módulo | Dependências | Impacto se Modificado |
|--------|--------------|----------------------|
| **CORE** | Nenhuma | Impacta TODOS módulos |
| **A1_PLANEJAMENTO** | CORE | Financeiro (custos), A5_COLHEITA |
| **A2_CAMPO** | CORE, A1 | Operacional (estoque), Financeiro |
| **A5_COLHEITA** | CORE, A1 | Financeiro (receitas) |
| **F1_TESOURARIA** | CORE | Nenhum (folha) |
| **F2_CUSTOS_ABC** | CORE, F1 | Todos módulos operacionais |
| **O1_FROTA** | CORE | Financeiro (custos), A2_CAMPO |
| **O2_ESTOQUE** | CORE | Todos módulos (insumos) |
| **P1_REBANHO** | CORE | Financeiro (receitas/despesas) |

### Fluxo de Dados entre Módulos

```
┌─────────────────────────────────────────────────────────────────┐
│                        FINANCEIRO (F1)                          │
│  ← Receitas de: Romaneios (A5), Venda Animais (P1)              │
│  ← Despesas de: Operações (A2), Manutenção (O1), Compras (O3)   │
│  → Rateio para: Safras (A1), Talhões, Lotes (P1)                │
└─────────────────────────────────────────────────────────────────┘
          ▲                          ▲
          │                          │
          │                          │
┌─────────┴──────────┐    ┌──────────┴──────────────────────────┐
│   AGRICOLA (A1-A5) │    │        PECUARIA (P1-P4)             │
│  → Romaneios       │    │  → Eventos (nascimento, venda)      │
│  → Operações       │    │  → Pesagens                         │
│  → Insumos         │    │  → Produção Leite                   │
└─────────┬──────────┘    └──────────┬──────────────────────────┘
          │                          │
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OPERACIONAL (O1-O3)                         │
│  → Estoque: fornece insumos para A2, P1                         │
│  → Frota: usada em operações agrícolas                          │
│  → Compras: abastece estoque                                    │
└─────────────────────────────────────────────────────────────────┘
```

**📄 Ver:** `docs/qwen/02-modulos.md` para detalhes de integração

---

## Referências Cruzadas

| Documento | Descrição |
|-----------|-----------|
| `docs/qwen/02-modulos.md` | Detalhamento de todos módulos |
| `docs/qwen/03-banco-dados.md` | Schema completo do banco |
| `docs/qwen/04-frontend.md` | Arquitetura frontend |
| `docs/qwen/05-api.md` | API reference |
| `docs/qwen/06-permissoes.md` | Catálogo de permissões |
| `docs/qwen/07-ui-ux.md` | Guidelines de UI/UX |
| `docs/qwen/08-infra.md` | Infraestrutura e deploy |

---

## Changelog

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Documentação inicial completa |
