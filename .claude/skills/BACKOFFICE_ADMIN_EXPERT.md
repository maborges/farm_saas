# Backoffice/Admin Expert - AgroSaaS

You are a specialist in the **Backoffice (SaaS Administration)** layer of AgroSaaS, responsible for platform administration, tenant management, billing operations, and support operations.

## Overview

The Backoffice is the administrative layer that sits above all tenant operations. It's where SaaS administrators manage the entire platform, tenants, subscriptions, and provide support.

**Access Level:** Backoffice users are NOT tenants. They are AgroSaaS employees/administrators with special privileges to manage the platform.

## Backoffice Roles

Defined in `BackofficePermissions` ([core/constants.py](../../services/api/core/constants.py))

### 1. super_admin
**Full System Access (Wildcard)**

- Everything a regular admin can do
- Plus: Destructive operations, system configuration, database access
- Typically: CTO, Lead Developer

**Unique Permissions:**
- Database migrations
- System-wide configuration changes
- Access to all tenants without logging
- Delete tenants (with safeguards)

### 2. admin
**Platform Management**

**Permissions:**
- `backoffice:dashboard:view` - Analytics dashboard
- `backoffice:tenants:*` - Full tenant CRUD
- `backoffice:plans:*` - Manage subscription plans
- `backoffice:users:*` - Manage backoffice users (not tenant users)
- `backoffice:billing:view` - View billing data
- `backoffice:reports:*` - Generate platform reports
- `backoffice:settings:*` - Platform settings

**Typical Role:** Platform Manager, Operations Manager

### 3. suporte (Support)
**Customer Support Operations**

**Permissions:**
- `backoffice:support:*` - Manage support tickets
- `backoffice:tenants:view` - View tenant data (read-only)
- `backoffice:impersonate` - Access tenant accounts for support
- `backoffice:knowledge_base:*` - Manage KB articles

**Typical Role:** Customer Success, Technical Support

**Key Activities:**
- Respond to support tickets
- Create knowledge base articles
- Impersonate tenants for troubleshooting
- Cannot modify billing or plans

### 4. financeiro (Billing/Finance)
**Billing and Revenue Operations**

**Permissions:**
- `backoffice:billing:*` - Full billing operations
- `backoffice:subscriptions:*` - Manage subscriptions
- `backoffice:payments:*` - Process payments
- `backoffice:invoices:*` - Generate invoices
- `backoffice:reports:financial` - Financial reports

**Typical Role:** Finance Manager, Billing Specialist

**Key Activities:**
- Process payments
- Issue invoices
- Manage subscription changes
- Handle refunds/chargebacks
- Financial reporting (MRR, ARR, churn)

### 5. comercial (Sales/Commercial)
**Sales and Marketing Operations**

**Permissions:**
- `backoffice:plans:view` - View plans (read-only)
- `backoffice:cupons:*` - Manage discount coupons
- `backoffice:leads:*` - Manage leads/prospects
- `backoffice:tenants:create` - Create new tenants (onboarding)
- `backoffice:reports:sales` - Sales reports

**Typical Role:** Sales Manager, Account Manager

**Key Activities:**
- Create promotional coupons
- Onboard new customers (assisted onboarding)
- Manage trials
- Sales analytics

## Core Backoffice Features

### 1. Tenant Management

**Location:** [core/routers/backoffice.py](../../services/api/core/routers/backoffice.py)

**Key Operations:**

**A. List Tenants:**
```python
GET /api/v1/backoffice/tenants
Query params: status, plan_id, created_after, search

# Returns list of tenants with key metrics
[
  {
    "id": "uuid",
    "nome": "Fazenda Santa Cruz",
    "status": "ATIVA",
    "plano_atual": "PRO",
    "data_criacao": "2024-01-15",
    "usuarios_ativos": 8,
    "fazendas_total": 3,
    "ultimo_acesso": "2024-12-15",
    "mrr": 299.00
  }
]
```

**B. View Tenant Details:**
```python
GET /api/v1/backoffice/tenants/{tenant_id}

# Returns complete tenant profile
{
  "tenant": {...},
  "subscriptions": [...],
  "users": [...],
  "farms": [...],
  "usage_stats": {
    "total_safras": 15,
    "total_operacoes": 234,
    "total_despesas": 1500,
    "storage_used_mb": 450
  },
  "billing_history": [...]
}
```

**C. Tenant Status Management:**
```python
PATCH /api/v1/backoffice/tenants/{tenant_id}/status

{
  "status": "SUSPENSA",  # ATIVA, SUSPENSA, CANCELADA
  "motivo": "Inadimplência - Fatura vencida há 30 dias"
}

# Effects:
# - ATIVA: Full access
# - SUSPENSA: Read-only access, no new data creation
# - CANCELADA: No access, data retained for 30 days then deleted
```

**D. Tenant Deletion (super_admin only):**
```python
DELETE /api/v1/backoffice/tenants/{tenant_id}

# Safeguards:
# 1. Require confirmation token
# 2. Soft delete (mark as deleted, retain data)
# 3. Hard delete only after 90 days
# 4. Export all tenant data before deletion (LGPD compliance)
# 5. Audit log entry with admin who deleted
```

### 2. Subscription Management

**Location:** [core/routers/billing.py](../../services/api/core/routers/billing.py)

**A. Plans (Subscription Templates):**
```python
# List all plans
GET /api/v1/backoffice/plans

# Create new plan
POST /api/v1/backoffice/plans
{
  "nome": "ENTERPRISE",
  "preco_mensal": 999.00,
  "limite_usuarios": 50,
  "limite_fazendas": 10,
  "modulos_inclusos": ["CORE", "A1", "A2", "A3", "A4", "A5", "P1", "F1", "F2", "O1", "O2"],
  "recursos_adicionais": {
    "api_access": true,
    "whitelabel": true,
    "sla_suporte": "4h"
  }
}

# Update plan (only for new subscriptions, existing unchanged)
PATCH /api/v1/backoffice/plans/{plan_id}
```

**B. Subscription CRUD:**
```python
# Create subscription (manual)
POST /api/v1/backoffice/subscriptions
{
  "tenant_id": "uuid",
  "plano_id": "uuid",
  "tipo_assinatura": "PRINCIPAL",  # or GRUPO
  "grupo_fazendas_id": null,  # if GRUPO type
  "data_inicio": "2025-01-01",
  "data_fim": "2025-12-31",  # or null for recurring
  "desconto_percentual": 10,  # promotional discount
  "observacoes": "Desconto promocional - primeiro ano"
}

# Change subscription (upgrade/downgrade)
PATCH /api/v1/backoffice/subscriptions/{subscription_id}/change_plan
{
  "novo_plano_id": "uuid",
  "aplicar_em": "PROXIMO_CICLO",  # or IMEDIATO
  "motivo": "Upgrade solicitado pelo cliente"
}

# Cancel subscription
DELETE /api/v1/backoffice/subscriptions/{subscription_id}
{
  "cancelar_em": "FIM_CICLO",  # or IMEDIATO
  "motivo": "Cliente solicitou cancelamento",
  "reembolso": false
}
```

**C. Billing Cycles:**
```python
# Process billing cycle (usually automated daily cron)
POST /api/v1/backoffice/billing/process_cycle
{
  "data_processamento": "2025-01-01"
}

# Actions:
# 1. Find all subscriptions with billing_date = today
# 2. Calculate prorated charges (if mid-cycle changes)
# 3. Generate invoice
# 4. Charge payment method on file
# 5. Send invoice email
# 6. Update subscription.proxima_cobranca
# 7. If payment fails → retry logic → suspend after 3 attempts
```

### 3. Payment Processing

**A. Payment Methods:**
- Credit Card (Stripe, PagSeguro)
- Boleto Bancário (Brazil)
- PIX (Brazil instant payment)
- Bank Transfer
- Manual (offline payment)

**B. Payment Flow:**
```python
# Record payment (manual or automatic)
POST /api/v1/backoffice/payments
{
  "tenant_id": "uuid",
  "subscription_id": "uuid",
  "valor": 299.00,
  "metodo": "CREDIT_CARD",
  "referencia": "charge_abc123 (Stripe)",
  "status": "APROVADO",  # PENDENTE, APROVADO, RECUSADO, ESTORNADO
  "data_pagamento": "2025-01-15"
}

# On payment success:
# 1. Update subscription.status = ATIVA
# 2. Generate receipt
# 3. Send confirmation email
# 4. Unlock tenant access (if was suspended)

# On payment failure:
# 1. Retry (day 3, day 7, day 14)
# 2. Send dunning emails (payment reminder)
# 3. After 30 days → suspend tenant
# 4. After 60 days → cancel subscription
```

**C. Refunds:**
```python
POST /api/v1/backoffice/payments/{payment_id}/refund
{
  "motivo": "Cobrança indevida",
  "valor_reembolso": 299.00,  # full or partial
  "estornar_assinatura": true  # cancel subscription?
}
```

### 4. Coupons & Promotions

**Location:** [core/routers/cupons.py](../../services/api/core/routers/cupons.py)

**A. Create Coupon:**
```python
POST /api/v1/backoffice/cupons
{
  "codigo": "PROMO2025",
  "tipo": "PERCENTUAL",  # or VALOR_FIXO
  "desconto": 20,  # 20% off
  "data_inicio": "2025-01-01",
  "data_fim": "2025-03-31",
  "limite_uso": 100,  # max 100 redemptions
  "planos_aplicaveis": ["BASIC", "PRO"],  # or null for all
  "primeiro_mes_apenas": false,  # or true for first month only
  "ativo": true
}
```

**B. Coupon Redemption:**
```python
# User applies coupon during signup/renewal
POST /api/v1/onboarding/apply-coupon
{
  "codigo": "PROMO2025"
}

# Validation:
# 1. Coupon exists and active
# 2. Not expired (data_inicio <= today <= data_fim)
# 3. Redemption limit not reached
# 4. Applicable to selected plan
# 5. Not already used by this tenant (if one-time-per-customer)

# On success:
# - subscription.desconto_percentual = coupon.desconto
# - cupom_uso.usos_total += 1
```

### 5. Support Operations

**Location:** [core/routers/support.py](../../services/api/core/routers/support.py)

**A. Ticket Management:**
```python
# List all support tickets
GET /api/v1/backoffice/support/tickets
Query params: status, prioridade, categoria, atendente_id

# Assign ticket to support agent
PATCH /api/v1/backoffice/support/tickets/{ticket_id}/assign
{
  "atendente_id": "uuid",
  "prioridade": "ALTA"  # escalate
}

# Respond to ticket
POST /api/v1/backoffice/support/tickets/{ticket_id}/messages
{
  "mensagem": "Olá, identifiquei o problema...",
  "tipo": "RESPOSTA_INTERNA"  # or RESPOSTA_CLIENTE
}

# Close ticket
PATCH /api/v1/backoffice/support/tickets/{ticket_id}/status
{
  "status": "RESOLVIDO",
  "solucao": "Problema resolvido através de...",
  "tempo_resolucao_minutos": 45
}
```

**B. Ticket Categories:**
- TECNICO - Technical issue
- BILLING - Billing/payment issue
- BUG - Bug report
- FEATURE_REQUEST - Feature request
- DUVIDA - General question
- ONBOARDING - Help with setup

**C. SLA Tracking:**
```python
# SLA rules by plan
sla_rules = {
    "BASIC": {"first_response": 24, "resolution": 48},  # hours
    "PRO": {"first_response": 12, "resolution": 24},
    "ENTERPRISE": {"first_response": 4, "resolution": 8}
}

# Auto-escalate if SLA breach imminent
if ticket.tempo_desde_abertura_h > sla.first_response * 0.8:
    notify_supervisor(ticket)
    ticket.prioridade = "ALTA"
```

### 6. Knowledge Base Management

**Location:** [core/routers/knowledge_base.py](../../services/api/core/routers/knowledge_base.py)

**A. Articles:**
```python
POST /api/v1/backoffice/knowledge-base/articles
{
  "titulo": "Como criar uma safra?",
  "conteudo": "Markdown content...",
  "categoria": "AGRICOLA",
  "modulo": "A1_PLANEJAMENTO",
  "tags": ["safra", "planejamento", "tutorial"],
  "visibilidade": "PUBLICO",  # PUBLICO, SOMENTE_ASSINANTES
  "autor_id": "uuid",
  "publicado": true
}

# Track article views, helpfulness votes
POST /api/v1/knowledge-base/articles/{article_id}/feedback
{
  "util": true,  # was this helpful?
  "comentario": "Muito claro, obrigado!"
}
```

**B. Article Analytics:**
- Most viewed articles
- Least helpful articles (low vote score)
- Common search terms (identify content gaps)

### 7. Impersonation (Support Access)

**Location:** [core/routers/backoffice.py](../../services/api/core/routers/backoffice.py)

**Purpose:** Allow support agents to access tenant accounts for troubleshooting

**A. Start Impersonation:**
```python
POST /api/v1/backoffice/impersonate
{
  "tenant_id": "uuid",
  "fazenda_id": "uuid",  # optional, specific farm
  "motivo": "Cliente reportou erro ao criar safra, preciso replicar",
  "categoria": "SUPORTE"  # SUPORTE, AUDITORIA, DEMONSTRACAO
}

# Response:
{
  "impersonation_token": "special_jwt_with_impersonation_flag",
  "impersonation_id": "uuid",  # for audit trail
  "expira_em": "2025-01-15T18:00:00Z"  # 2 hours max
}

# This token allows support agent to use the system AS that tenant
# Frontend shows banner: "Você está em modo suporte (Tenant: XYZ)"
```

**B. End Impersonation:**
```python
POST /api/v1/backoffice/impersonate/end
{
  "impersonation_id": "uuid",
  "acoes_realizadas": [
    "Visualizei safras do talhão 01",
    "Reproduzi o erro: timeout ao salvar safra",
    "Identifiquei causa: geometria inválida no talhão"
  ]
}

# All actions logged in AdminImpersonation table
# Audit trail: who, when, what, why
```

**C. Security:**
- Requires `backoffice:impersonate` permission
- Mandatory `motivo` field
- Time-limited (2 hours max)
- All actions logged
- Cannot change billing/subscription during impersonation
- Visual indicator in frontend (banner/watermark)

### 8. Analytics & Reporting

**A. Platform Metrics Dashboard:**
```python
GET /api/v1/backoffice/dashboard/metrics

{
  "mrr": 125000,  # Monthly Recurring Revenue
  "arr": 1500000,  # Annual Recurring Revenue
  "active_tenants": 420,
  "trial_tenants": 35,
  "suspended_tenants": 12,
  "churn_rate_30d": 2.5,  # %

  "new_signups_30d": 42,
  "upgrades_30d": 18,
  "downgrades_30d": 5,
  "cancellations_30d": 11,

  "avg_revenue_per_tenant": 297.62,
  "lifetime_value": 3571,  # avg LTV

  "support_tickets_open": 23,
  "support_tickets_overdue_sla": 3,
  "avg_resolution_time_h": 18.5
}
```

**B. Revenue Reports:**
- MRR/ARR trends (monthly, quarterly)
- Revenue by plan
- Revenue by module (which modules generate most revenue)
- Cohort analysis (revenue retention by signup month)
- Churn analysis (why are customers leaving?)

**C. Usage Analytics:**
- Most used features
- Least used features (candidates for deprecation)
- Feature adoption by plan
- Storage usage per tenant
- API usage per tenant

**D. Support Reports:**
- Tickets by category
- SLA compliance (% resolved within SLA)
- Top ticket topics (identify pain points)
- Agent performance (tickets resolved, avg time, customer satisfaction)

### 9. Admin User Management

**Location:** [core/routers/backoffice_admins.py](../../services/api/core/routers/backoffice_admins.py)

**Purpose:** Manage backoffice administrators

**A. Create Admin:**
```python
POST /api/v1/backoffice/admins
{
  "email": "suporte@agrosaas.com",
  "nome": "João Silva",
  "role": "suporte",  # super_admin, admin, suporte, financeiro, comercial
  "ativo": true
}

# Auto-send invitation email with password setup link
```

**B. Role Changes:**
```python
PATCH /api/v1/backoffice/admins/{admin_id}/role
{
  "novo_role": "admin",
  "motivo": "Promoção para gerente de operações"
}
```

**C. Audit Log:**
All admin actions logged:
- Who (admin user)
- What (action performed)
- When (timestamp)
- Where (IP address)
- Why (reason, if provided)
- Result (success/failure)

**Example Audit Entry:**
```json
{
  "admin_id": "uuid",
  "admin_email": "admin@agrosaas.com",
  "acao": "UPDATE_SUBSCRIPTION",
  "detalhes": {
    "tenant_id": "uuid",
    "subscription_id": "uuid",
    "plano_antigo": "BASIC",
    "plano_novo": "PRO",
    "motivo": "Upgrade solicitado pelo cliente"
  },
  "ip_address": "192.168.1.100",
  "timestamp": "2025-01-15T14:30:00Z",
  "resultado": "SUCESSO"
}
```

### 10. System Configuration

**Location:** [core/routers/configuration.py](../../services/api/core/routers/configuration.py)

**Purpose:** Platform-wide settings (super_admin only)

**A. Feature Flags:**
```python
# Enable/disable features globally
PUT /api/v1/backoffice/config/feature-flags
{
  "enable_new_dashboard": true,
  "enable_api_v2": false,
  "enable_experimental_ndvi": true,
  "maintenance_mode": false
}
```

**B. Integrations:**
```python
# Configure third-party integrations
PUT /api/v1/backoffice/config/integrations
{
  "stripe_api_key": "sk_live_...",
  "sendgrid_api_key": "SG...",
  "aws_s3_bucket": "agrosaas-prod-storage",
  "google_maps_api_key": "AIza..."
}
```

**C. Notification Templates:**
```python
# Email/SMS templates
PUT /api/v1/backoffice/config/templates/email
{
  "template_id": "welcome_email",
  "subject": "Bem-vindo ao AgroSaaS!",
  "body_html": "<html>...",
  "variables": ["tenant_name", "login_url"]
}
```

## Common Backoffice Workflows

### 1. Onboard New Customer (Assisted)
```
1. Commercial team creates lead
2. Demo/trial period
3. Customer decides to subscribe
4. Commercial creates tenant (via backoffice)
5. Commercial creates subscription + applies coupon
6. Send welcome email with login credentials
7. Schedule onboarding call (commercial → customer)
8. Monitor usage during first 30 days
9. Check-in for feedback (customer success)
```

### 2. Handle Payment Failure
```
1. Billing system attempts charge → FAILED
2. Auto-send dunning email #1: "Payment failed, please update card"
3. Wait 3 days → Retry charge → FAILED
4. Auto-send dunning email #2: "Urgent: Update payment method"
5. Wait 7 days → Retry charge → FAILED
6. Auto-send dunning email #3: "Final notice: Account will be suspended"
7. Wait 14 days → Still failed
8. Suspend tenant (status: SUSPENSA, read-only access)
9. Finance team manually contacts customer
10. Customer updates payment → Retry → SUCCESS
11. Reactivate tenant (status: ATIVA)
```

### 3. Escalate Support Ticket
```
1. Customer creates ticket: "Sistema está lento"
2. Auto-assigned to Tier 1 support
3. Tier 1 responds within SLA (4h for ENTERPRISE)
4. Tier 1 cannot resolve → escalate to Tier 2 (technical)
5. Tier 2 uses impersonation to debug
6. Identifies issue: slow query on large dataset
7. Tier 2 creates internal bug ticket for dev team
8. Tier 2 implements workaround for customer
9. Tier 2 responds to customer with solution
10. Customer confirms resolution
11. Close ticket, log resolution time
12. Dev team fixes underlying issue in next release
```

### 4. Process Monthly Billing Cycle
```
# Automated cron job (runs daily at 2am)

1. SELECT tenants with subscription.proxima_cobranca = TODAY
2. For each tenant:
   a. Calculate amount (plan price - discounts + add-ons)
   b. Generate invoice (PDF)
   c. Attempt payment (credit card on file)
   d. If success:
      - Send receipt email
      - Update subscription.proxima_cobranca = +1 month
      - Log payment
   e. If failure:
      - Start dunning process
      - Send payment failed email
      - Schedule retry (day +3, +7, +14)
3. Generate billing report (total collected, failed payments)
4. Alert finance team of any issues
```

## Key Metrics & KPIs (Backoffice)

### Revenue Metrics
- **MRR (Monthly Recurring Revenue):** Sum of all active subscriptions
- **ARR (Annual Recurring Revenue):** MRR * 12
- **ARPU (Average Revenue Per User):** Total revenue / Active tenants
- **LTV (Lifetime Value):** ARPU / Churn rate
- **CAC (Customer Acquisition Cost):** Marketing spend / New customers

### Growth Metrics
- **MRR Growth Rate:** (MRR_this_month - MRR_last_month) / MRR_last_month * 100
- **Net New MRR:** New MRR + Expansion MRR - Churned MRR - Contraction MRR
- **Quick Ratio:** (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)

### Retention Metrics
- **Churn Rate:** Customers lost / Total customers at start * 100
- **Revenue Retention:** (MRR_start + Expansion - Churn) / MRR_start * 100
- **Logo Retention:** 100 - Churn rate

### Support Metrics
- **First Response Time:** Time from ticket creation to first response
- **Resolution Time:** Time from creation to closure
- **SLA Compliance:** % tickets resolved within SLA
- **CSAT (Customer Satisfaction):** Avg rating on ticket resolution
- **Ticket Volume:** Tickets per tenant (lower = better product quality)

## Security Best Practices

### 1. Admin Account Security
- Require 2FA for all backoffice users
- Strong password policy (12+ chars, complexity)
- Session timeout (30 min inactivity)
- IP whitelisting (office/VPN only)
- Audit all admin actions

### 2. Tenant Data Access
- Least privilege principle (only access what's needed for role)
- Impersonation requires justification + approval (for sensitive ops)
- No direct database access (except super_admin via controlled console)
- Encrypt sensitive data (payment methods, personal info)

### 3. Billing Security
- PCI DSS compliance (if handling credit cards directly)
- Tokenize payment methods (never store raw card numbers)
- Secure API keys (Stripe, payment gateways)
- Fraud detection (unusual signup patterns, stolen cards)

## Testing Backoffice Features

```python
def test_admin_can_view_tenant_list():
    admin = create_admin(role="admin")
    token = create_jwt(admin, is_superuser=True)

    response = client.get(
        "/api/v1/backoffice/tenants",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()) > 0

def test_support_cannot_modify_billing():
    support = create_admin(role="suporte")
    token = create_jwt(support)

    response = client.patch(
        f"/api/v1/backoffice/subscriptions/{sub_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"plano_id": new_plan_id}
    )

    assert response.status_code == 403  # Forbidden

def test_impersonation_logs_actions():
    admin = create_admin(role="suporte")
    tenant = create_tenant()

    impersonation = start_impersonation(admin, tenant, "Debug issue")

    # Perform actions as tenant
    # ...

    end_impersonation(impersonation, actions=["Viewed safras", "Tested operation"])

    # Verify audit log
    log = get_impersonation_log(impersonation.id)
    assert log.admin_id == admin.id
    assert log.tenant_id == tenant.id
    assert "Viewed safras" in log.acoes_realizadas
```

## Troubleshooting

### Billing Issues
- **Charge failing:** Check payment method validity, expiry date
- **MRR discrepancy:** Verify all subscriptions counted, no duplicates
- **Refund request:** Check refund policy, approval required for > R$ 1000

### Support Bottlenecks
- **High ticket volume:** Check for widespread issue (bug, outage)
- **Low CSAT scores:** Review agent performance, training needs
- **SLA breaches:** Increase support staffing, improve self-service KB

### Performance Issues
- **Slow backoffice dashboard:** Optimize queries, add caching, paginate results
- **Impersonation lag:** Check tenant database size, optimize tenant queries

## References

- [core/routers/backoffice.py](../../services/api/core/routers/backoffice.py) - Tenant management
- [core/routers/billing.py](../../services/api/core/routers/billing.py) - Billing operations
- [core/routers/support.py](../../services/api/core/routers/support.py) - Support tickets
- [core/constants.py](../../services/api/core/constants.py) - BackofficePermissions
- [IMPLEMENTACAO_RBAC_MULTI_SUB.md](../../IMPLEMENTACAO_RBAC_MULTI_SUB.md) - RBAC details
- SaaS Metrics: Christoph Janz (SaaS Metrics 2.0), David Skok (SaaS Metrics)
