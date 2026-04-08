# CLAUDE.md

## Context Efficiency (MANDATORY)
- Use `ctx_batch_execute` / `ctx_execute` for ALL commands producing >10 lines (tests, grep, analysis)
- NEVER use Bash for: tests, file search, log reading, output analysis
- Delegate fix loops to subagents via Agent tool
- Responses ≤150 words; artifacts to files, never inline

## Stack
- **Backend:** FastAPI + SQLAlchemy 2.0 async + Alembic + PostgreSQL + Python 3.12
- **Frontend:** Next.js 16 App Router + React 19 + shadcn/ui + Zustand + TanStack Query + Tailwind 4
- **Monorepo:** pnpm — `/apps/web`, `/services/api`, `/packages/zod-schemas`

## Architecture Rules

**Multi-tenancy (Defense in Depth):**
- JWT claims embed `tenant_id`
- `BaseService` auto-injects `tenant_id` on all queries — NEVER write raw queries in routers
- PostgreSQL RLS policies

**RBAC:**
- Backoffice: `require_permission("backoffice:resource:action")`
- Tenant: `require_tenant_permission("module:resource:action")`
- Module flags: `require_module("A1_PLANEJAMENTO")`
- `is_owner` bypasses all tenant permissions except billing
- Per-farm role overrides via `FazendaUsuario.perfil_fazenda_id`

**Service Pattern:** `FazendaService(BaseService[Fazenda])` — inherits `get/get_or_fail/list_all/create/update/hard_delete`

## Security (MANDATORY)
1. Always use `BaseService` — never raw SQLAlchemy in routers
2. Extract `tenant_id` via `get_tenant_id()` dependency only — never trust frontend
3. Every new endpoint needs tenant isolation test
4. Log `TenantViolationError` as security incident

## Code Style
- Python: async/await, type hints, Pydantic v2 `model_dump()`, SQLAlchemy 2.0 `mapped_column()`, Loguru
- TypeScript: functional components, strict mode, `interface` for shapes
- Naming: DB tables snake_case plural, Python PascalCase classes, routes kebab-case
- customized and standard components (WEB): apps/web/src/components
- customized and standard components (BACKOFFICE): apps/backoffice/src/components
- customized and standard components (MOBILE): apps/mobile/src/components

## Errors
`EntityNotFoundError`→404 | `TenantViolationError`→403 | `ModuleNotContractedError`→402 | `BusinessRuleError`→422

## Dev Commands
```bash
# Backend
cd services/api && ./start_server.sh          # port 8000
alembic revision --autogenerate -m "desc"     # new migration
alembic upgrade head

# Frontend
cd apps/web && pnpm dev                       # port 3000

# New module scaffold
python scripts/create_module.py <module_name>
```

## Known Issues
- **CORS:** reiniciar servidor após mudanças em `main.py`. Diagnóstico: `./check_cors.sh`
- **Alembic async:** `await connection.commit()` após `run_sync` (ROLLBACK silencioso sem isso)
- **Router registration:** novo router → importar e incluir em `main.py`
- **SQLite fallback:** RLS e schemas PostgreSQL não funcionam em SQLite

## Modules
`core/` auth/billing | `agricola/` safras/talhoes/operacoes | `pecuaria/` lotes/manejos | `financeiro/` despesas/receitas | `operacional/` frota/estoque | `imoveis/`

## Application Context

### Backend — 42 Routers (`/api/v1`)
- **SaaS/Admin:** auth, onboarding, backoffice (admins, tenants, audit, sessions, profiles, email_templates, crm, crm_ofertas, tabelas), knowledge_base, reports, configuration
- **Commerce:** billing, plan_changes, stripe_webhooks, cupons, webhooks_asaas
- **Operations:** team, grupos_fazendas, support, support_ws
- **Operational:** frota, estoque, oficina, compras, apontamento, abastecimento, checklist, doc_equipamento, operacional_relatorios
- **Registries:** core_cadastros, pessoas, tipos_relacionamento, equipamentos, areas_rurais, commodities
- **Agricola (22):** a1_planejamento, agronomo, alertas, amostragem_solo, analises_solo, beneficiamento, cadastros, checklist, climatico, custos, dashboard, fenologia, irrigacao, monitoramento, ndvi, ndvi_avancado, operacoes, prescricoes, previsoes, rastreabilidade, romaneios, safras

### Frontend — `/apps/web/src`
- **Layout components:** navbar, sidebar, app-sidebar, topbar, tenant-switcher, notification-bell, context-selector
- **Domain components:** `agricola/` (safra-timeline, ndvi, romaneios, rastreabilidade, orcamento, financeiro-kpis, beneficiamento-cafe, analise-solo, safras-kanban), `estoque/` (MovimentacaoTable, SaldoGrid, LotesCard), `contabilidade/` (LancamentoContabilForm, IntegracaoContabilList)

### Feature Status
- **Completo:** RBAC multi-subscription, Backoffice admin, billing Stripe/Asaas, 22 módulos agrícolas, FIFO estoque, integração colheita (P0.1-P0.3)
- **Em andamento:** Feature gates por módulo, UI backoffice para catálogo de módulos, telemetria de uso
- **Próximos:** Módulos A2-A5 seguindo padrão A1_PLANEJAMENTO, infraestrutura de gates no frontend

### Key Files
- `services/api/main.py` — registro de todos os routers (linhas 91-130)
- `services/api/core/dependencies.py` — feature gates e dependências RBAC
- `services/api/core/constants.py` — constantes de módulos/permissões
- `packages/zod-schemas/src/index.ts` — schemas compartilhados frontend/backend
- `docs/PROXIMOS_PASSOS.md` — roadmap de modularização

## Docs
- [IMPLEMENTACAO_RBAC_MULTI_SUB.md](IMPLEMENTACAO_RBAC_MULTI_SUB.md) — multi-subscription RBAC
- [FRONTEND_MAINTENANCE_GUIDE.md](FRONTEND_MAINTENANCE_GUIDE.md) — frontend guide
- [services/api/CORS_TROUBLESHOOTING.md](services/api/CORS_TROUBLESHOOTING.md) — CORS guide
- [docs/contexts/*](docs/contexts/*) — overview of all modules
- [docs/qwen/*](docs/qwen/*) — overview of all modules

