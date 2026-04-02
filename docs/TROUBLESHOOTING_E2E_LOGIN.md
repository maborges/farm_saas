# 🎭 Troubleshooting E2E Tests - AgroSaaS

**Problema:** `TimeoutError: page.fill: Timeout 15000ms exceeded`

---

## ✅ Correções Aplicadas

### 1. Adicionado `data-testid` no LoginForm

**Arquivo:** `apps/web/src/components/auth/login-form.tsx`

```tsx
// ✅ Adicionado:
<Input
  id="email"
  data-testid="email-input"  // ← Novo
  // ...
/>

<Input
  id="password"
  data-testid="password-input"  // ← Novo
  // ...
/>

<form data-testid="login-form">  // ← Novo
  {/* ... */}
</form>

<Button data-testid="login-button">  // ← Novo
```

### 2. Atualizado Teste E2E

**Arquivo:** `apps/web/tests/e2e/auth.spec.ts`

```typescript
// ✅ Adicionado wait explícito
test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
});

// ✅ Timeout aumentado para navegação
await page.waitForURL(/\/dashboard/, { timeout: 30000 });

// ✅ Wait para erro aparecer
await page.waitForSelector('[data-testid="email-error"]', { timeout: 5000 });
```

---

## 🔧 Como Rodar os Testes Agora

```bash
# 1. Navegar até web app
cd apps/web

# 2. Instalar dependências (se necessário)
pnpm install

# 3. Rodar testes E2E
pnpm test

# OU usar script
./scripts/run-e2e-tests.sh -p chromium
```

---

## 🐛 Se Ainda Falhar

### Erro: `Timeout 30000ms exceeded waiting for URL`

**Causa:** Backend não está rodando ou login falhou

**Solução:**

```bash
# 1. Verificar backend
curl http://localhost:8000/health

# 2. Se backend não rodar:
cd services/api
source .venv/bin/activate
uvicorn main:app --reload

# 3. Verificar credenciais do teste
# O usuário 'test@agrosaas.com.br' existe no banco?
```

### Erro: `401 Unauthorized`

**Causa:** Credenciais inválidas ou usuário não existe

**Solução:**

```bash
# Criar usuário de teste via API ou register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@agrosaas.com.br",
    "senha": "password123",
    "nome": "Test User"
  }'
```

### Erro: `Element not found: [data-testid="..."]`

**Causa:** `data-testid` não foi adicionado no componente

**Solução:**

```bash
# 1. Inspecionar elemento no browser
# F12 → Elements → Procurar input

# 2. Se não tiver data-testid, adicionar no componente
# Ver: apps/web/src/components/auth/login-form.tsx

# 3. Rebuild se necessário
pnpm build
```

---

## 🎯 Debug Mode

Para investigar falhas visualmente:

```bash
# UI Mode (recomendado)
./scripts/run-e2e-tests.sh --ui

# Debug mode
./scripts/run-e2e-tests.sh -d

# Codegen (gravar ações)
./scripts/run-e2e-tests.sh --codegen
```

---

## 📋 Checklist de Verificação

Antes de rodar testes E2E:

- [ ] Backend rodando em `http://localhost:8000`
- [ ] Frontend rodando em `http://localhost:3000`
- [ ] Banco de dados PostgreSQL ativo
- [ ] Usuário de teste existe no banco
- [ ] `data-testid` adicionados nos componentes
- [ ] Playwright browsers instalados (`pnpm exec playwright install`)

---

## 🔗 Links Úteis

- [GUIA_CORRECAO_BUGS.md](./GUIA_CORRECAO_BUGS.md)
- [GUIA_TESTES.md](./GUIA_TESTES.md)
- [Playwright Docs](https://playwright.dev/docs/debug)

---

**Última Atualização:** 2026-03-31
