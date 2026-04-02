# 🧪 Guia de Testes - AgroSaaS

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** ✅ Ativo

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Testes de Backend](#2-testes-de-backend)
3. [Testes de Frontend](#3-testes-de-frontend)
4. [Executando Testes](#4-executando-testes)
5. [Escrevendo Novos Testes](#5-escrevendo-novos-testes)
6. [CI/CD](#6-cicd)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Visão Geral

### Stack de Testes

| Tipo | Ferramenta | Localização |
|------|------------|-------------|
| **Unitários Backend** | pytest | `services/api/tests/` |
| **Integração Backend** | pytest + httpx | `services/api/tests/` |
| **E2E Frontend** | Playwright | `apps/web/tests/e2e/` |
| **Performance** | k6/Locust | `tests/performance/` |
| **Segurança** | OWASP ZAP | Manual |

### Estrutura de Pastas

```
farm/
├── tests/                          # Testes globais
│   └── financeiro/
│       ├── test_nfe_xml.py
│       └── test_ofx_conciliacao.py
│
├── services/api/tests/             # Testes do backend
│   ├── conftest.py                 # Fixtures globais
│   ├── test_e2e_colheita_completa.py
│   ├── test_operacao_despesa_webhook.py
│   ├── test_romaneio_receita_webhook.py
│   └── templates/
│       └── test_template_agricola.py
│
├── apps/web/tests/e2e/             # Testes E2E frontend
│   ├── fixtures.ts
│   ├── auth.spec.ts
│   ├── agricola-safras.spec.ts
│   └── template.spec.ts
│
└── scripts/
    ├── run-tests.sh                # Script backend
    └── run-e2e-tests.sh            # Script frontend
```

---

## 2. Testes de Backend

### Dependências

```bash
cd services/api
source .venv/bin/activate
pip install pytest pytest-asyncio pytest-cov httpx
```

### Executando Testes

```bash
# Todos os testes
./scripts/run-tests.sh

# Com coverage
./scripts/run-tests.sh -c

# Apenas unitários
./scripts/run-tests.sh --unit

# Apenas integração
./scripts/run-tests.sh --integration

# Teste específico
./scripts/run-tests.sh -p tests/financeiro/test_nfe_xml.py

# Com marker específico
./scripts/run-tests.sh -m financeiro
```

### Fixtures Disponíveis

| Fixture | Descrição |
|---------|-----------|
| `session` | SQLAlchemy async session (Tenant A) |
| `session_b` | SQLAlchemy async session (Tenant B) |
| `tenant_id` | UUID do Tenant A |
| `outro_tenant_id` | UUID do Tenant B |
| `fazenda_id` | Fazenda criada no banco |
| `talhao_id` | UUID de talhão |

### Escrevendo Testes

```python
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from agricola.safras.models import Safra
from agricola.operacoes.service import OperacaoService

class TestMinhaFeature:
    @pytest.mark.asyncio
    async def test_minha_feature(
        self,
        session: AsyncSession,
        tenant_id: str,
        talhao_id: str
    ):
        # Arrange
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="SOJA",
            status="PLANTIO",
            area_plantada_ha=100.0
        )
        session.add(safra)
        await session.commit()

        # Act
        service = OperacaoService(session, tenant_id)
        resultado = await service.algum_metodo()

        # Assert
        assert resultado is not None
        assert resultado.valor == esperado
```

### Markers Disponíveis

```python
@pytest.mark.core         # Módulo Core
@pytest.mark.agricola     # Módulo Agrícola
@pytest.mark.financeiro   # Módulo Financeiro
@pytest.mark.operacional  # Módulo Operacional
@pytest.mark.pecuaria     # Módulo Pecuária
@pytest.mark.rh           # Módulo RH
@pytest.mark.integration  # Testes de integração
@pytest.mark.e2e          # Testes E2E
@pytest.mark.slow         # Testes lentos
```

---

## 3. Testes de Frontend

### Dependências

```bash
cd apps/web
pnpm install
pnpm add -D @playwright/test
pnpm exec playwright install
```

### Executando Testes

```bash
# Todos os testes
./scripts/run-e2e-tests.sh

# Apenas Chromium
./scripts/run-e2e-tests.sh -p chromium

# Modo debug
./scripts/run-e2e-tests.sh -d

# UI mode
./scripts/run-e2e-tests.sh --ui

# Ver relatório
./scripts/run-e2e-tests.sh --report

# Codegen (gravar testes)
./scripts/run-e2e-tests.sh --codegen
```

### Comandos npm

```bash
# Rodar testes
pnpm test

# UI mode
pnpm test:ui

# Debug
pnpm test:debug

# Apenas Chromium
pnpm test:chromium

# Mobile
pnpm test:mobile

# Ver relatório
pnpm test:report
```

### Escrevendo Testes E2E

```typescript
import { test, expect } from '@playwright/test';

test.describe('Minha Feature', () => {
  test.beforeEach(async ({ page }) => {
    // Login antes de cada teste
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@agrosaas.com.br');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    await page.waitForURL(/\/dashboard/);
  });

  test('deve fazer algo', async ({ page }) => {
    await page.goto('/modulo/pagina');
    
    // Aguardar loading
    await page.waitForSelector('[data-testid="loading"]', { state: 'detached' });
    
    // Preencher formulário
    await page.fill('[data-testid="input-nome"]', 'Valor');
    await page.selectOption('[data-testid="select"]', 'OPCAO');
    
    // Submeter
    await page.click('[data-testid="botao-salvar"]');
    
    // Aguardar sucesso
    await expect(page.locator('[data-testid="toast-success"]')).toBeVisible();
    
    // Validar redirect
    await expect(page).toHaveURL(/\/lista/);
  });
});
```

### Selectors Recomendados

```typescript
// Use data-testid para todos os elementos interativos
<button data-testid="botao-salvar">Salvar</button>
<input data-testid="email-input" />
<select data-testid="culture-filter" />

// Aguarde elementos específicos
await page.waitForSelector('[data-testid="tabela-carregada"]');

// Assertions
await expect(page.locator('[data-testid="titulo"]')).toContainText('Texto');
await expect(page).toHaveURL(/\/pagina/);
```

---

## 4. Executando Testes

### Fluxo Recomendado

```bash
# 1. Rodar testes unitários rápidos
./scripts/run-tests.sh --fast

# 2. Rodar testes de integração
./scripts/run-tests.sh --integration

# 3. Rodar testes E2E críticos
./scripts/run-e2e-tests.sh -p chromium

# 4. Gerar relatórios
./scripts/run-tests.sh -c --html
./scripts/run-e2e-tests.sh --report
```

### Checklist Rápido

```bash
# Backend
./scripts/run-tests.sh --unit -q     # Unitários rápidos
./scripts/run-tests.sh -m financeiro # Módulo específico

# Frontend
./scripts/run-e2e-tests.sh -p chromium --report # E2E + relatório
```

---

## 5. Escrevendo Novos Testes

### Backend

1. Copie o template:
   ```bash
   cp services/api/tests/templates/test_template_agricola.py \
      services/api/tests/test_minha_feature.py
   ```

2. Adapte para sua feature

3. Rode o teste:
   ```bash
   ./scripts/run-tests.sh -p services/api/tests/test_minha_feature.py
   ```

### Frontend

1. Copie o template:
   ```bash
   cp apps/web/tests/e2e/template.spec.ts \
      apps/web/tests/e2e/minha-feature.spec.ts
   ```

2. Adapte para sua feature

3. Rode o teste:
   ```bash
   ./scripts/run-e2e-tests.sh -p minha-feature
   ```

### Codegen (Frontend)

Grave testes automaticamente:

```bash
./scripts/run-e2e-tests.sh --codegen
```

1. Navegue pela aplicação
2. Playwright grava as ações
3. Copie o código gerado para seu teste

---

## 6. CI/CD

### GitHub Actions (Exemplo)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: ./scripts/run-tests.sh --coverage

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: pnpm install
      - run: pnpm exec playwright install --with-deps
      - run: ./scripts/run-e2e-tests.sh -p chromium
```

---

## 7. Troubleshooting

### Backend

**Erro: `ModuleNotFoundError`**
```bash
source services/api/.venv/bin/activate
pip install -r requirements.txt
```

**Erro: `pytest: command not found`**
```bash
pip install pytest pytest-asyncio
```

**Testes falhando por banco de dados**
```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Resetar banco de teste
docker-compose down -v
docker-compose up -d postgres
```

### Frontend

**Erro: `playwright: command not found`**
```bash
pnpm add -D @playwright/test
pnpm exec playwright install
```

**Testes falhando por timeout**
```typescript
// Aumentar timeout no teste
test('teste lento', async ({ page }) => {
  test.setTimeout(60000); // 60 segundos
  // ...
});
```

**Erro: `Cannot find module`**
```bash
cd apps/web
pnpm install
```

### Problemas Comuns

| Problema | Solução |
|----------|---------|
| Testes lentos | Use `--fast` para pular testes `@slow` |
| Falso positivo | Rode com `--debug` para investigar |
| Coverage baixo | Escreva testes para branches não cobertos |
| Timeout E2E | Aumente `timeout` no `playwright.config.ts` |

---

## 📊 Métricas

### Coverage Atual

| Módulo | Coverage | Meta | Status |
|--------|----------|------|--------|
| Core | 0% | 70% | ⏳ |
| Agrícola | 0% | 70% | ⏳ |
| Financeiro | 0% | 70% | ⏳ |
| Operacional | 0% | 70% | ⏳ |
| Pecuária | 0% | 70% | ⏳ |
| RH | 0% | 70% | ⏳ |

### Testes E2E

| Feature | Testes | Passando | Status |
|---------|--------|----------|--------|
| Auth | 6 | 0 | ⏳ |
| Safras | 12 | 0 | ⏳ |
| Operações | 0 | 0 | ⏳ |
| Romaneios | 0 | 0 | ⏳ |
| Financeiro | 0 | 0 | ⏳ |
| Estoque | 0 | 0 | ⏳ |

---

## 🔗 Links Úteis

- [pytest docs](https://docs.pytest.org/)
- [Playwright docs](https://playwright.dev/)
- [Test Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](./docs/qwen/05-api.md)
- [Plano de Testes QA](./docs/PLANO_TESTES_QA.md)

---

**Última Atualização:** 2026-03-31
**Próxima Revisão:** 2026-04-30
