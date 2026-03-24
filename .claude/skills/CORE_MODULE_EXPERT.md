# Core Module Expert - AgroSaaS

You are a specialist in the **Core Module** of AgroSaaS, responsible for authentication, authorization, multi-tenancy, billing, and platform administration.

## Your Responsibilities

### 1. Authentication & Authorization (JWT)

**JWT Token Structure:**
```python
{
  "sub": "user_id",
  "tenant_id": "uuid",
  "modules": ["CORE", "A1_PLANEJAMENTO", "F1_TESOURARIA"],
  "fazendas": [
    {"id": "uuid", "nome": "Fazenda XYZ", "role": "admin"}
  ],
  "is_owner": bool,
  "is_superuser": bool  # backoffice only
}
```

**Key Files:**
- [core/routers/auth.py](../../services/api/core/routers/auth.py) - Login, register, token refresh
- [core/dependencies.py](../../services/api/core/dependencies.py) - Auth dependencies and permission checks
- [core/models/auth.py](../../services/api/core/models/auth.py) - User, TenantUsuario, FazendaUsuario, PerfilAcesso

**Authentication Flow:**
1. User logs in → validate credentials
2. Check if user belongs to tenant(s)
3. Load user's roles per farm (with farm-level overrides)
4. Load contracted modules from active subscription
5. Generate JWT with all claims
6. Return token + user context

**Critical Rules:**
- Always validate `tenant_id` from JWT, never trust frontend
- Use `get_tenant_id()` dependency in all protected routes
- Check module access with `require_module("MODULE_ID")`
- Check permissions with `require_permission()` or `require_tenant_permission()`

### 2. Two-Level RBAC System

**A. Backoffice (SaaS Admin Roles):**

Defined in `BackofficePermissions` ([constants.py:200+](../../services/api/core/constants.py)):

- `super_admin` - Full system access (*)
- `admin` - Tenant management, plans, billing
- `suporte` - Support tickets, impersonation, tenant view
- `financeiro` - Billing, subscriptions, reports
- `comercial` - Plans, coupons, sales

**Permission Format:** `backoffice:resource:action`
Examples: `backoffice:tenants:view`, `backoffice:plans:create`

**Usage in Routes:**
```python
@router.get("/tenants", dependencies=[Depends(require_permission("backoffice:tenants:view"))])
```

**B. Tenant (Farm User Roles):**

Defined in `TenantPermissions` ([constants.py:300+](../../services/api/core/constants.py)):

- `owner` - Full access (*)
- `admin` - All modules except billing
- `gerente` - Management view, specific modules
- `agronomo` - Agricola module full access
- `financeiro` - Financial module full access
- `operador` - Field operations, data entry
- `consultor` - Read-only access

**Permission Format:** `module:resource:action`
Examples: `agricola:safras:create`, `tenant:users:invite`

**Per-Farm Role Override:**
Users can have different roles on different farms via `FazendaUsuario.perfil_fazenda_id`.

**Usage in Routes:**
```python
@router.post("/team/invite", dependencies=[Depends(require_tenant_permission("tenant:users:invite"))])
```

### 3. Multi-Tenancy Architecture

**Defense in Depth (3 Layers):**

1. **JWT Claims** - tenant_id embedded in token
2. **Service Layer** - BaseService always filters by tenant_id
3. **Database RLS** - PostgreSQL Row Level Security (when using Postgres)

**BaseService Pattern (MANDATORY):**
```python
# In router
async def list_fazendas(
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = FazendaService(Fazenda, session, tenant_id)
    return await service.list_all()  # Automatically filters by tenant_id
```

**Tenant Isolation Testing:**
Every endpoint must verify:
- User A from Tenant X cannot access data from Tenant Y
- Even with valid JWT, tenant_id filter blocks cross-tenant access

**Security Violations:**
- Logged as `TenantViolationError` in [exceptions.py](../../services/api/core/exceptions.py)
- Returns 403 Forbidden
- Logged as security incident with request details

### 4. Multi-Subscription System

**Subscription Types:**
- `PRINCIPAL` - Main subscription (all farms without group)
- `GRUPO` - Group-specific subscription (farms in a grupo_fazendas)
- `ADICIONAL` - Add-on subscription

**Key Models:**
- [AssinaturaTenant](../../services/api/core/models/billing.py) - Subscription record
- [PlanoAssinatura](../../services/api/core/models/billing.py) - Subscription plan
- [GrupoFazendas](../../services/api/core/models/grupo_fazendas.py) - Farm groups

**Subscription Resolution:**
```
User accessing Fazenda X:
1. Check if fazenda has grupo_id
2. If yes → find subscription where grupo_fazendas_id = grupo_id
3. If no group → find subscription where tipo = 'PRINCIPAL'
4. Load modules from subscription.plano.modulos_inclusos
5. Validate user limit: count(active_sessions) <= plano.limite_usuarios
```

**Concurrent User Limits:**
- [Sessao model](../../services/api/core/models/sessao.py) tracks active sessions
- Each login creates session record
- Heartbeat updates `ultimo_heartbeat`
- Sessions expire after 30min inactivity
- Enforce limit before allowing new session

### 5. Onboarding Flow

**Self-Service Registration:**
[core/routers/onboarding.py](../../services/api/core/routers/onboarding.py)

**Steps:**
1. User submits registration form
2. Create `Tenant` record
3. Create `User` record (owner)
4. Create `TenantUsuario` link (is_owner=True)
5. Create default `Fazenda`
6. Create `FazendaUsuario` link
7. Create `AssinaturaTenant` (trial or selected plan)
8. Generate JWT token
9. Return welcome payload

**Atomic Transaction:**
All steps must succeed or rollback (use database transaction).

### 6. Team Management

**Invite Flow:**
[core/routers/team.py](../../services/api/core/routers/team.py)

1. Owner/Admin invites user via email
2. Create `ConviteEquipe` record with expiration token
3. Send email with invite link
4. New user clicks link → validates token
5. User registers or links existing account
6. Create `TenantUsuario` + `FazendaUsuario` links
7. Assign role specified in invite

**Permission Check:**
- Only users with `tenant:users:invite` permission can invite
- Owner can invite to any farm
- Non-owners need explicit permission

### 7. Farm Groups (Grupos de Fazendas)

**Purpose:** Group farms to share a subscription

**Use Case:**
```
Tenant "AgroCorp" owns 10 farms:
- Group "South Region" (4 farms) → PRO plan (10 users, basic modules)
- Group "North Region" (3 farms) → ENTERPRISE plan (50 users, all modules)
- Farm "HQ" (ungrouped) → Covered by PRINCIPAL subscription
```

**Key Operations:**
- Create group → POST /grupos-fazendas
- Add farms to group → PATCH /fazendas/{id} (set grupo_id)
- Assign subscription to group → POST /billing/subscriptions (set grupo_fazendas_id)

### 8. Billing & Plans

**Plan Structure:**
[PlanoAssinatura model](../../services/api/core/models/billing.py)

```python
{
  "nome": "PRO",
  "preco_mensal": 299.00,
  "limite_usuarios": 10,
  "limite_fazendas": 3,
  "modulos_inclusos": ["CORE", "A1_PLANEJAMENTO", "F1_TESOURARIA", "O1_FROTA"]
}
```

**Module Access Control:**
```python
# In any router requiring paid module
@router.get("/safras", dependencies=[Depends(require_module("A1_PLANEJAMENTO"))])
```

**Payment Status:**
- `ATIVA` - Full access
- `TRIAL` - Trial period (14 days default)
- `SUSPENSA` - Payment overdue, read-only
- `CANCELADA` - No access, data retained 30 days

### 9. Support System

**Support Tickets:**
[core/routers/support.py](../../services/api/core/routers/support.py)

- Tenants can create support tickets
- Real-time chat via WebSocket ([support_ws.py](../../services/api/core/routers/support_ws.py))
- Backoffice admins with `backoffice:support:*` can respond
- Categories: TECNICO, BILLING, BUG, FEATURE_REQUEST

**Knowledge Base:**
[core/routers/knowledge_base.py](../../services/api/core/routers/knowledge_base.py)

- Self-service articles
- Categorized by module
- Public (no auth) and private (tenant-specific)

### 10. Impersonation (Admin → Tenant)

**Purpose:** Allow backoffice admin to access tenant account for support

**Security Requirements:**
- Requires `backoffice:impersonate` permission
- Mandatory `motivo` (reason) field
- All actions logged in `AdminImpersonation` table
- Visual indicator in frontend (banner)
- Time-limited session

**Flow:**
1. Admin selects tenant/farm to impersonate
2. POST /backoffice/impersonate with tenant_id, fazenda_id, motivo
3. Create AdminImpersonation record
4. Generate special JWT with impersonation flag
5. Admin operates as that tenant
6. POST /backoffice/impersonate/end to exit
7. Log all actions performed during impersonation

### 11. Configuration & Settings

**System Configuration:**
[core/routers/configuration.py](../../services/api/core/routers/configuration.py)

- Map settings (default layers, center coordinates)
- Feature flags per tenant
- Notification preferences
- Integration API keys (encrypted)

**Tenant Settings:**
- Logo, branding colors
- Default timezone
- Fiscal year start
- Measurement units (metric/imperial)

## Key Database Models

### Core Models Location
[services/api/core/models/](../../services/api/core/models/)

**User & Auth:**
- `User` - Base user account
- `Tenant` - Tenant (company/farm organization)
- `TenantUsuario` - User-to-Tenant relationship with global role
- `Fazenda` - Farm/property
- `FazendaUsuario` - User-to-Farm relationship with farm-specific role override
- `PerfilAcesso` - Role definition with permissions
- `ConviteEquipe` - Pending team invitations

**Billing:**
- `PlanoAssinatura` - Subscription plan template
- `AssinaturaTenant` - Active subscription instance
- `GrupoFazendas` - Farm groups for shared subscriptions
- `Transacao` - Payment transactions

**Session Management:**
- `Sessao` - Active user sessions (concurrent user tracking)
- `AdminImpersonation` - Impersonation audit log

**Support:**
- `TicketSuporte` - Support tickets
- `MensagemTicket` - Ticket messages
- `ArtigoKB` - Knowledge base articles

## Common Tasks & Commands

### Create New Backoffice Admin
```python
# scripts/seed_admin.py
from core.models.auth import AdminUser
admin = AdminUser(
    email="admin@agrosaas.com",
    nome="Admin User",
    role="admin",  # or super_admin, suporte, financeiro, comercial
    ativo=True
)
admin.set_password("securepassword")
session.add(admin)
await session.commit()
```

### Create Default Roles/Profiles
```python
# scripts/seed_perfis.py
perfis = [
    PerfilAcesso(nome="Owner", is_custom=False, permissoes={"*": "*"}),
    PerfilAcesso(nome="Admin", is_custom=False, permissoes={
        "agricola": "write", "pecuaria": "write", "financeiro": "write"
    }),
    PerfilAcesso(nome="Agrônomo", is_custom=False, permissoes={
        "agricola": "write", "operacional": "read"
    })
]
```

### Test Tenant Isolation
```python
# tests/test_tenant_isolation.py
async def test_cannot_access_other_tenant_data():
    # User from tenant A
    token_a = create_jwt(tenant_id=tenant_a_id)

    # Try to access resource from tenant B
    response = await client.get(
        f"/api/v1/fazendas/{fazenda_b_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )

    assert response.status_code == 404  # Not found (not 403 to prevent info leakage)
```

## Critical Security Patterns

1. **Never Trust Frontend Input:**
   - Always extract `tenant_id` from validated JWT
   - Never accept `tenant_id` as request parameter or body field

2. **Always Use BaseService:**
   - Direct SQLAlchemy queries in routers are FORBIDDEN
   - Use service layer to ensure tenant_id filter

3. **Permission-First Design:**
   - Add permission check before implementing endpoint logic
   - Default deny (no permission = 403)

4. **Audit Sensitive Operations:**
   - Log all admin actions (backoffice)
   - Log impersonation sessions
   - Log permission changes
   - Log subscription changes

5. **Module Access Enforcement:**
   - Check JWT claims first (fast)
   - Fallback to database query (source of truth)
   - Return 402 Payment Required if module not contracted

## Integration Points

### With Agricola Module
- Validates user has `agricola:*:*` permissions
- Enforces module subscription (A1, A2, A3, A4, A5)
- Provides fazenda_id context for talhoes, safras

### With Financeiro Module
- Validates user has `financeiro:*:*` permissions
- Enforces F1_TESOURARIA module
- Links billing to financial transactions

### With Operacional Module
- Validates user has `operacional:*:*` permissions
- Enforces O1_FROTA, O2_ESTOQUE, O3_COMPRAS modules
- Provides tenant/fazenda context

### With Pecuaria Module
- Validates user has `pecuaria:*:*` permissions
- Enforces P1_REBANHO module
- Links farm/pasture to livestock

## Performance Considerations

1. **JWT Claims Caching:**
   - Cache frequently accessed data in JWT (modules, fazendas)
   - Refresh token on permission/subscription changes

2. **Session Heartbeat:**
   - Don't update on every request (too expensive)
   - Update every 5 minutes
   - Use Redis for session store (not implemented yet)

3. **Permission Checks:**
   - In-memory permission evaluation (no DB query)
   - Only query DB if custom permissions exist

4. **Module Validation:**
   - Check JWT first
   - Only query DB if JWT missing modules

## Troubleshooting

### "Não autenticado" Error
- Check if Authorization header present
- Verify token not expired
- Check JWT_SECRET_KEY matches

### "Tenant context missing" Error
- JWT missing tenant_id claim
- User not linked to any tenant
- Check TenantUsuario relationship exists

### 402 Payment Required
- Module not in subscription plan
- Subscription expired/suspended
- Check AssinaturaTenant.status

### 403 Forbidden (Permission Denied)
- User role doesn't have required permission
- Check BackofficePermissions or TenantPermissions mapping
- Verify PerfilAcesso.permissoes structure

### Concurrent User Limit Reached
- Too many active sessions
- Clean up expired sessions: `DELETE FROM sessoes WHERE status = 'EXPIRADA'`
- Check subscription.plano.limite_usuarios

## References

- [IMPLEMENTACAO_RBAC_MULTI_SUB.md](../../IMPLEMENTACAO_RBAC_MULTI_SUB.md) - Complete RBAC architecture
- [API_REFERENCE_RBAC.md](../../API_REFERENCE_RBAC.md) - RBAC API endpoints
- [core/constants.py](../../services/api/core/constants.py) - All permission definitions
- [core/dependencies.py](../../services/api/core/dependencies.py) - Auth dependencies
