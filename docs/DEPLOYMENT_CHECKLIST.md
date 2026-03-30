# Deployment Checklist — Integração de Colheita

**Data:** 2026-03-30
**Versão:** 1.0
**Status:** Pronto para Staging/Produção

---

## 📋 Pré-Deployment (Local)

- [ ] Git status limpo (sem uncommitted changes)
- [ ] Todas as branches mergeadas em `main`
- [ ] Testes locais executados (ou ignorar se sem PostgreSQL local)
- [ ] Lint pass: `ruff check .` ✓
- [ ] Type check pass: `mypy .` ✓
- [ ] Frontend build: `pnpm build` ✓

---

## 🗄️ Database — Staging

### Step 1: Criar Backup (se DB existente)

```bash
# Snapshot da database atual
pg_dump farm_db > backup_2026-03-30_pre_colheita.sql

# Ou via container
docker exec farm-postgres pg_dump -U postgres farm_db > backup.sql
```

### Step 2: Aplicar Migrations

```bash
cd services/api
source .venv/bin/activate

# Verificar status atual
alembic current

# Aplicar nova migration (lookup table)
alembic upgrade head

# Verificar sucesso
alembic current  # deve mostrar: f0a1b2c3d4e5...
```

### Step 3: Seed Lookup Table

```bash
# Já feito na migration, mas verificar:
psql -U postgres -d farm_db -c "
SELECT COUNT(*) as tipos_operacao
FROM agricola_operacao_tipo_fase;
"

# Esperado: 8 linhas
```

---

## 🧪 Testing — Staging

### Step 1: Executar 27 Testes

```bash
cd services/api

# Todos os testes
pytest tests/test_operacoes_validacao_fase.py \
        tests/test_operacao_despesa_webhook.py \
        tests/test_romaneio_receita_webhook.py \
        tests/test_dashboard_financeiro_safra.py \
        -v --tb=short

# Output esperado:
# ======================== 27 passed in 15.23s ========================
```

Checklist de testes:
- [ ] test_operacoes_validacao_fase.py: 7/7 ✓
- [ ] test_operacao_despesa_webhook.py: 7/7 ✓
- [ ] test_romaneio_receita_webhook.py: 7/7 ✓
- [ ] test_dashboard_financeiro_safra.py: 6/6 ✓

### Step 2: Testar Endpoints Manualmente

#### Endpoint 1: Dashboard Financeiro

```bash
# GET /agricola/dashboard/safras/{safra_id}/resumo-financeiro
curl -X GET "http://localhost:8000/api/v1/agricola/dashboard/safras/ABC123/resumo-financeiro" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Esperado: 200 com SafraResumoFinanceiro
{
  "id": "uuid",
  "cultura": "MILHO",
  "financeiro": {
    "total_operacoes": 2,
    "custo_operacoes_total": 5000.00,
    "despesa_total": 5000.00,
    "receita_total": 100000.00,
    "roi_pct": 1900.0
  }
}
```

---

## 🌐 Frontend — Staging Build

### Step 1: Build Produção

```bash
cd apps/web

# Install dependencies
pnpm install

# Build
pnpm build

# Verificar outputs:
# ✓ 120 pages
# ✓ ~1.2 MB

# Testar localmente
pnpm start
# Acesso em http://localhost:3000
```

### Step 2: Testar Página Financeiro

1. Login em safra existente (COLHEITA phase)
2. Clicar em "Financeiro" button
3. Verificar:
   - [ ] KPI cards renderizam corretamente
   - [ ] Valores mostram com formato moeda
   - [ ] Chart desenha barras corretamente
   - [ ] Timeline carrega operações + romaneios
   - [ ] Isolamento: só vê dados da sua safra

### Step 3: Performance

```bash
# Lighthouse check
pnpm dlx lighthouse http://localhost:3000/agricola/safras/[id]/financeiro \
  --output json

# Esperado: Performance > 80
```

---

## 🚀 Deployment — Staging Server

### Step 1: Backend Deployment

```bash
# SSH para servidor staging
ssh user@staging.example.com

cd /opt/lampp/htdocs/farm/services/api

# Pull latest
git pull origin main

# Install requirements (if updated)
source .venv/bin/activate
pip install -r requirements.txt

# Migrations
alembic upgrade head

# Restart server
sudo systemctl restart farm-api
# ou
pm2 restart farm-api

# Verify
curl http://localhost:8000/api/v1/health
# Esperado: {"status": "ok"}
```

### Step 2: Frontend Deployment

```bash
cd /opt/lampp/htdocs/farm/apps/web

# Pull latest
git pull origin main

# Build
pnpm install
pnpm build

# Deploy to nginx/vercel
# Se usando Vercel: `vercel --prod`
# Se nginx: copy `out/` para nginx root

# Verify
curl https://staging.example.com
# Esperado: 200 OK com HTML
```

### Step 3: Smoke Tests (Staging)

```bash
# Test API endpoints
curl https://staging.example.com/api/v1/agricola/dashboard/safras/[id]/resumo-financeiro

# Test Frontend
curl https://staging.example.com/agricola/safras/[id]/financeiro

# Test Webhook (create operation, verify despesa)
# Criar operação via UI ou API
# Verificar despesa criada em fin_despesas
```

---

## 🔍 Validation Checklist

### API Endpoints
- [ ] GET `/agricola/dashboard/safras/{id}/resumo-financeiro` — 200
- [ ] Permission checks working — `agricola:safras:view`
- [ ] Tenant isolation enforced
- [ ] Error handling (404, 403, 500)

### Webhooks
- [ ] Operação + custo → Despesa criada
- [ ] Operação sem custo → Despesa NÃO criada
- [ ] Romaneio + preço → Receita criada
- [ ] `origem_id` e `origem_tipo` populados

### Frontend
- [ ] KPI cards mostram valores corretos
- [ ] Chart renderiza com dados
- [ ] Timeline carrega transações
- [ ] Permission denied se sem `agricola:safras:view`
- [ ] Mobile responsivo

### Database
- [ ] Migration applied: `alembic current` = `f0a1b2c3d4e5...`
- [ ] Lookup table with 8 tipos
- [ ] Despesas com `origem_id` preenchido
- [ ] Receitas com `origem_id` preenchido

### Monitoring
- [ ] Logs de webhook aparecem
- [ ] Sem erros em console
- [ ] Sem breaking changes em dados existentes
- [ ] Performance: Dashboard < 500ms

---

## 📊 Rollback Plan

Se algo falhar em staging:

### Option A: Revert Database

```bash
# Se migration causou problema
alembic downgrade -1

# Restore backup
psql -U postgres -d farm_db < backup_2026-03-30_pre_colheita.sql
```

### Option B: Revert Code

```bash
git revert HEAD  # Cria commit de rollback
git push origin main

# Ou pull commit anterior
git reset --hard HEAD~1
```

---

## ✅ Go/No-Go Decision

### Go Criteria (TODOS devem ser TRUE)
- [ ] 27 testes passando
- [ ] API endpoints retornando 200
- [ ] Frontend carregando sem erros
- [ ] Dashboard mostrando dados corretos
- [ ] Webhooks funcionando
- [ ] Tenant isolation validado
- [ ] Performance aceitável
- [ ] Documentação atualizada

### Resultado: **GO / NO-GO**

```
Status: GO ✅ ou NO-GO ❌

Assinado por: _______________
Data: _____________________
```

---

## 🔐 Security Checklist

- [ ] Permissions checked on all endpoints
- [ ] Tenant isolation enforced in service layer
- [ ] No SQL injection risks (parameterized queries)
- [ ] No XSS in frontend (React auto-escapes)
- [ ] CORS headers correct
- [ ] JWT validation present
- [ ] Audit logs for financial operations
- [ ] No secrets in code/logs

---

## 📈 Post-Deployment (24h)

### Monitoring
- [ ] Error logs — zero deploy-related errors
- [ ] Performance — dashboard latency < 500ms
- [ ] Webhooks — no failed webhook deliveries
- [ ] Database — no locks or slowqueries

### Business Validation
- [ ] 2-3 operações criadas = despesas aparecem
- [ ] 2-3 romaneios criados = receitas aparecem
- [ ] Dashboard totais batem com operações
- [ ] ROI calculado corretamente

### User Feedback
- [ ] Agricultores podem acessar Financeiro tab
- [ ] KPIs são compreensíveis
- [ ] Timeline é útil
- [ ] Performance é rápida (< 2s load)

---

## 📞 Escalation Contacts

| Papel | Nome | Email | Telefone |
|-------|------|-------|----------|
| DevOps | — | — | — |
| DBA | — | — | — |
| Arquiteto | — | — | — |
| Product | — | — | — |

---

## 📝 Sign-Off

```
Deploy Aprovado Por:
______________________ (Lead Dev)

Data: _______________

Homologação Aprovada Por:
______________________ (QA)

Data: _______________

Produção Autorizada Por:
______________________ (Product)

Data: _______________
```

---

**Documentação:** [IMPLEMENTACAO_COLHEITA_COMPLETA.md](./IMPLEMENTACAO_COLHEITA_COMPLETA.md)
**Testes:** [E2E_TEST_SCENARIOS.md](./E2E_TEST_SCENARIOS.md)
**API:** [API_ENDPOINTS_REFERENCE.md](./API_ENDPOINTS_REFERENCE.md)

