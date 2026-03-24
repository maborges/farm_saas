# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgroSaaS is a modular monolithic SaaS platform for farm management (Gestão Rural), built with FastAPI backend and Next.js 16 frontend. The system implements strict multi-tenancy with RBAC at both tenant and backoffice levels.

**Key Characteristics:**
- Multi-tenant architecture with tenant isolation at service layer
- Modular monolith pattern (not microservices)
- Multi-subscription support: tenants can have multiple subscriptions per farm group
- Role-based access control (RBAC) at two levels: backoffice admins and tenant users
- Per-farm role overrides (users can have different roles on different farms)

## Repository Structure

This is a pnpm monorepo with the following structure:

```
/apps/web          - Next.js 16 frontend (React 19, TypeScript, shadcn/ui)
/services/api      - FastAPI backend (Python 3.12, SQLAlchemy 2.0, async/await)
/packages/zod-schemas - Shared validation schemas (currently not actively used)
```

## Backend Architecture (FastAPI)

### Technology Stack
- **FastAPI** with async/await patterns
- **SQLAlchemy 2.0** with async engine and mapped_column syntax
- **Alembic** for migrations
- **PostgreSQL** (production) with SQLite fallback (development)
- **Python 3.12** with type hints
- **Loguru** for structured logging
- **Jose** for JWT authentication

### Database & Multi-Tenancy

**Database URL Configuration:** Set via `DATABASE_URL` environment variable in `/services/api/.env.local`. Falls back to SQLite if PostgreSQL is unavailable (see [database.py:9-19](services/api/core/database.py#L9-L19)).

**Multi-Tenancy Strategy (Defense in Depth):**
1. **JWT Claims:** `tenant_id` embedded in token
2. **Service Layer Enforcement:** `BaseService` class always injects `tenant_id` filter on all queries
3. **Row Level Security (RLS):** PostgreSQL RLS policies (when using Postgres)

All database access MUST go through `BaseService` or services that extend it. Direct SQLAlchemy queries are forbidden in routers to prevent tenant isolation breaches.

### Module Organization

The API is organized into domain modules:

- **core/** - Authentication, authorization, billing, onboarding, support, configuration
- **agricola/** - Crop management (safras, talhoes, operacoes, romaneios, ndvi, climatico, etc.)
- **pecuaria/** - Livestock management (lotes, manejos, piquetes)
- **financeiro/** - Financial module (despesas, receitas, planos_conta, relatorios)
- **operacional/** - Operations (frota, estoque, oficina, compras)
- **imoveis/** - Property management

Each module typically contains: `models.py`, `schemas.py`, `service.py`, `router.py`

### Authentication & Authorization

**JWT Structure:**
```python
{
  "sub": "user_id",
  "tenant_id": "uuid",
  "modules": ["CORE", "A1_PLANEJAMENTO", "F1_FINANCEIRO"],
  "fazendas": [...],
  "is_owner": bool
}
```

**Two-Level RBAC:**

1. **Backoffice (SaaS Admins):**
   - Roles: `super_admin`, `admin`, `suporte`, `financeiro`, `comercial`
   - Permissions defined in `BackofficePermissions` ([constants.py](services/api/core/constants.py))
   - Use `require_permission("backoffice:resource:action")` dependency

2. **Tenant (Farm Users):**
   - Roles: `owner`, `admin`, `gerente`, `agronomo`, `operador`, `consultor`, `financeiro`
   - Permissions defined in `TenantPermissions` ([constants.py](services/api/core/constants.py))
   - Use `require_tenant_permission("module:resource:action")` dependency
   - Per-farm role overrides supported via `FazendaUsuario.perfil_fazenda_id`

**Permission Checking:**
```python
# In router
@router.get("/tenants", dependencies=[Depends(require_permission("backoffice:tenants:view"))])
@router.post("/team/invite", dependencies=[Depends(require_tenant_permission("tenant:users:invite"))])
```

### Service Pattern (BaseService)

All database operations must use `BaseService` ([base_service.py](services/api/core/base_service.py)):

```python
class FazendaService(BaseService[Fazenda]):
    # Inherits: get(), get_or_fail(), list_all(), create(), update(), hard_delete()
    # All methods auto-inject tenant_id filter
    pass

# Usage in router
service = FazendaService(Fazenda, session, tenant_id)
fazendas = await service.list_all()
```

**Critical:** Never write raw SQLAlchemy queries in routers. Always use service layer to ensure tenant isolation.

### Module Access Control

The system uses feature flags to control module access:

```python
# In router
@router.get("/safras", dependencies=[Depends(require_module("A1_PLANEJAMENTO"))])
```

Module availability is checked in JWT claims first (fast), then database (source of truth). See [dependencies.py:52-110](services/api/core/dependencies.py#L52-L110).

Available modules defined in `Modulos` class ([constants.py](services/api/core/constants.py)).

### Multi-Subscription Support

- A single tenant can have multiple subscriptions (see [IMPLEMENTACAO_RBAC_MULTI_SUB.md](IMPLEMENTACAO_RBAC_MULTI_SUB.md))
- Farm groups (`grupos_fazendas`) can have dedicated subscriptions
- Each subscription has its own user limits and module access
- Billing model tracks: `tipo_assinatura` (PRINCIPAL, GRUPO, ADICIONAL) and `grupo_fazendas_id`

## Frontend Architecture (Next.js)

### Technology Stack
- **Next.js 16** with App Router (not Pages Router)
- **React 19** with TypeScript
- **shadcn/ui** for UI components
- **Zustand** for state management
- **TanStack Query** for server state
- **Mapbox/MapLibre GL** for geospatial features
- **Tailwind CSS 4**

### Project Structure

```
/src/app          - App Router pages (Next.js 16 convention)
  /(auth)         - Authentication routes (login, register)
  /(dashboard)    - Main application routes
  /layout.tsx     - Root layout
  /globals.css    - Global styles

/src/components   - React components
  /auth           - Authentication components
  /layout         - Layout components (Sidebar, Header)
  /shared         - Shared/reusable components
  /ui             - shadcn/ui components

/src/lib          - Utilities and configurations
  /api.ts         - API client with axios
  /permissions.ts - Permission checking utilities
  /stores         - Zustand stores
  /constants      - Frontend constants

/src/hooks        - Custom React hooks
  /use-permission.ts
  /use-has-module.ts
  /use-team.ts
  /use-roles.ts
  /use-grupos.ts
```

### API Communication

API calls use axios client configured in [lib/api.ts](apps/web/src/lib/api.ts):

- Base URL: `http://localhost:8000/api/v1`
- Includes JWT token from localStorage
- CORS enabled for localhost:3000/3001

### State Management

- **Zustand** for global state (auth, tenant context)
- **TanStack Query** for server state caching and mutations
- Authentication state managed via hooks: `useAuth()`, `usePermission()`, `useHasModule()`

### Permission System (Frontend)

Frontend mirrors backend permissions. Use hooks to check access:

```typescript
const { hasPermission } = usePermission();
if (hasPermission('tenant:users:invite')) { /* show invite button */ }

const { hasModule } = useHasModule();
if (hasModule('A1_PLANEJAMENTO')) { /* show planning module */ }
```

## Common Development Tasks

### Running the Project

**Backend:**
```bash
cd services/api
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Runs on http://localhost:8000

# OU use o script de inicialização (recomendado):
./start_server.sh
```

**IMPORTANTE - CORS:** Sempre que modificar a configuração de CORS em `main.py`, **REINICIE O SERVIDOR**. As mudanças só são aplicadas após reiniciar.

**Frontend:**
```bash
cd apps/web
pnpm dev
# Runs on http://localhost:3000
```

**Database (Docker):**
```bash
docker-compose up -d  # Starts PostgreSQL and Redis
```

### Database Migrations

```bash
cd services/api
source .venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current
```

**Important:** Always use `mapped_column()` syntax (SQLAlchemy 2.0), not legacy `Column()`.

### Testing (Backend)

```bash
cd services/api
source .venv/bin/activate
pytest                    # Run all tests
pytest tests/unit         # Run unit tests only
pytest -v                 # Verbose output
```

Test configuration in [pyproject.toml](services/api/pyproject.toml). Async tests automatically handled via `pytest-asyncio`.

### Linting & Type Checking (Backend)

```bash
cd services/api
source .venv/bin/activate
ruff check .              # Lint code
ruff format .             # Format code
mypy .                    # Type checking
```

Configuration in [pyproject.toml](services/api/pyproject.toml).

### Adding a New Module

Use the scaffolding script:
```bash
cd services/api
python scripts/create_module.py <module_name>
```

This creates the standard module structure: models, schemas, service, router.

### Seeding Data

Available seed scripts in `services/api/scripts/`:
- `seed_plans.py` - Subscription plans
- `seed_admin.py` - Backoffice admin users
- `seed_kb.py` - Knowledge base articles
- `seed_map_configs.py` - Map configurations

## Critical Security Patterns

### Tenant Isolation (MANDATORY)

1. **Always use BaseService** - Never write raw queries in routers
2. **Validate tenant_id** - Always extract via `get_tenant_id()` dependency
3. **Test tenant isolation** - Every new endpoint should have tenant isolation test
4. **Audit sensitive operations** - Log tenant violations as security incidents

### Permission Checks

1. **Backend enforcement is source of truth** - Frontend permissions are UX only
2. **Use dependencies for permissions** - `require_permission()` or `require_tenant_permission()`
3. **Module access control** - Use `require_module()` for paid features
4. **Owner bypass** - `is_owner` users have all permissions (except billing changes)

### JWT Token Handling

- Tokens contain cached permissions/modules for performance
- Database is always source of truth for module access
- Token refresh on permission changes
- Never trust frontend-provided `tenant_id` - always extract from JWT

## Important Conventions

### Python Code Style
- Use async/await for all database operations
- Type hints required for function signatures
- Pydantic v2 syntax (`model_dump()` not `dict()`)
- SQLAlchemy 2.0 syntax (`mapped_column()`, `Mapped[]`)
- Loguru for logging (not print statements)

### TypeScript Code Style
- Functional components with hooks
- TypeScript strict mode enabled
- Use `interface` for object shapes
- Explicit return types for exported functions

### Naming Conventions
- Database tables: snake_case plural (`fazendas`, `tenant_usuarios`)
- Python classes: PascalCase (`FazendaService`, `AssinaturaTenant`)
- Python functions/variables: snake_case
- TypeScript/React: camelCase for variables, PascalCase for components
- Routes: kebab-case (`/grupos-fazendas`, `/planos-conta`)

### Error Handling

Backend uses custom exceptions:
- `EntityNotFoundError` → 404
- `TenantViolationError` → 403 (security incident logged)
- `ModuleNotContractedError` → 402
- `BusinessRuleError` → 422

Handlers defined in [main.py:129-145](services/api/main.py#L129-L145).

## Known Issues & Patterns

1. **SQLite Fallback:** Development uses SQLite if PostgreSQL unavailable. Some PostgreSQL features (RLS, schemas) won't work in SQLite.

2. **Router Registration:** Routers must be registered in [main.py](services/api/main.py). Don't forget to import and include new routers.

3. **CORS Configuration:**
   - Frontend dev server runs on :3000 or :3001. CORS configured in [main.py:50-66](services/api/main.py#L50-L66)
   - **CRITICAL:** Mudanças em CORS **REQUEREM REINICIAR O SERVIDOR** - use `cd services/api && ./start_server.sh`
   - Origens permitidas: localhost:3000, localhost:3001, 127.0.0.1:3000, 127.0.0.1:3001, 192.168.0.108:3000, 192.168.0.108:3001
   - Para diagnóstico: `cd services/api && ./check_cors.sh`
   - Documentação: [services/api/CORS_TROUBLESHOOTING.md](services/api/CORS_TROUBLESHOOTING.md)

4. **Async Session Management:** Use `async with async_session_maker() as session:` pattern. Don't forget to commit transactions.

5. **Geospatial Data:** Uses GeoAlchemy2 for PostGIS support. Geometry types require specific handling.

## Additional Documentation

For detailed information on specific implementations:
- [IMPLEMENTACAO_RBAC_MULTI_SUB.md](IMPLEMENTACAO_RBAC_MULTI_SUB.md) - RBAC and multi-subscription architecture
- [API_REFERENCE_RBAC.md](API_REFERENCE_RBAC.md) - RBAC API reference
- [FRONTEND_MAINTENANCE_GUIDE.md](FRONTEND_MAINTENANCE_GUIDE.md) - Frontend maintenance guide
- [AgroSaaS-Roles-e-Skills.md](AgroSaaS-Roles-e-Skills.md) - Roles and skills mapping
- [services/api/SETUP_POSTGRESQL.md](services/api/SETUP_POSTGRESQL.md) - PostgreSQL setup guide
