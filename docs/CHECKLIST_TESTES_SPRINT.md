# 📋 Checklist de Testes por Sprint - AgroSaaS

**Sprint:** ______
**Data:** ___/___/___
**Responsável QA:** _____________________

---

## 🎯 Objetivo

Este checklist garante que todos os testes necessários sejam executados antes de cada release da sprint.

---

## 📊 Resumo da Sprint

| Item | Status |
|------|--------|
| **Total de Testes** | 0 |
| **Testes Passando** | 0 |
| **Testes Falhando** | 0 |
| **Coverage Backend** | 0% |
| **Coverage Frontend** | 0% |
| **Bugs Críticos** | 0 |
| **Bugs Altos** | 0 |

---

## 1️⃣ Testes de Unidade (Backend)

**Responsável:** Dev Backend
**Duração Estimada:** 30 min

### Execução

- [ ] Rodar todos os testes unitários
  ```bash
  ./scripts/run-tests.sh --unit
  ```

- [ ] Verificar coverage mínimo (70%)
  ```bash
  ./scripts/run-tests.sh --coverage
  ```

### Resultados

| Módulo | Testes | Passando | Coverage | Status |
|--------|--------|----------|----------|--------|
| Core | 0 | 0 | 0% | ⏳ |
| Agrícola | 0 | 0 | 0% | ⏳ |
| Financeiro | 0 | 0 | 0% | ⏳ |
| Operacional | 0 | 0 | 0% | ⏳ |
| Pecuária | 0 | 0 | 0% | ⏳ |
| RH | 0 | 0 | 0% | ⏳ |

### ✅ Critérios de Aceite

- [ ] Coverage ≥ 70%
- [ ] 0 testes falhando
- [ ] Novos testes criados para novas features

---

## 2️⃣ Testes de Integração (Backend)

**Responsável:** Dev Backend
**Duração Estimada:** 1 hora

### Execução

- [ ] Rodar testes de integração
  ```bash
  ./scripts/run-tests.sh --integration
  ```

### Fluxos Críticos

| Fluxo | Status | Observações |
|-------|--------|-------------|
| Safra → Operação → Despesa | ⏳ | |
| Safra → Romaneio → Receita | ⏳ | |
| OS → Saída de Estoque → Despesa | ⏳ | |
| Pedido → Recebimento → Entrada | ⏳ | |
| Isolamento de Tenant | ⏳ | |

### ✅ Critérios de Aceite

- [ ] Todos os fluxos críticos passando
- [ ] Webhooks funcionando corretamente
- [ ] Isolamento de tenant validado

---

## 3️⃣ Testes E2E (Frontend)

**Responsável:** Dev Frontend
**Duração Estimada:** 2 horas

### Execução

- [ ] Rodar testes E2E no Chromium
  ```bash
  ./scripts/run-e2e-tests.sh -p chromium
  ```

- [ ] Rodar testes E2E mobile (opcional)
  ```bash
  ./scripts/run-e2e-tests.sh -p "Mobile Chrome"
  ```

### Fluxos E2E

| Fluxo | Status | Observações |
|-------|--------|-------------|
| Login/Logout | ⏳ | |
| Criar Safra | ⏳ | |
| Criar Operação | ⏳ | |
| Criar Romaneio | ⏳ | |
| Dashboard Financeiro | ⏳ | |
| Gestão de Estoque | ⏳ | |

### ✅ Critérios de Aceite

- [ ] Todos os fluxos E2E críticos passando
- [ ] Sem erros de JavaScript no console
- [ ] Responsive design funcionando

---

## 4️⃣ Testes de Performance

**Responsável:** DevOps/Tech Lead
**Duração Estimada:** 1 hora

### Execução

- [ ] Testar endpoints críticos
  ```bash
  # Exemplo com k6 (se configurado)
  k6 run tests/performance/api-load-test.js
  ```

### SLA de Performance

| Endpoint | SLA (ms) | Medido (ms) | Status |
|----------|----------|-------------|--------|
| POST /auth/login | < 200 | - | ⏳ |
| GET /agricola/safras | < 300 | - | ⏳ |
| GET /financeiro/receitas | < 300 | - | ⏳ |
| GET /operacional/estoque/saldos | < 300 | - | ⏳ |
| GET /agricola/dashboard | < 500 | - | ⏳ |

### ✅ Critérios de Aceite

- [ ] Todos os endpoints dentro do SLA
- [ ] Sem memory leaks
- [ ] Database queries otimizadas

---

## 5️⃣ Testes de Segurança

**Responsável:** Tech Lead
**Duração Estimada:** 1 hora

### Verificações

- [ ] Testar autenticação sem token
- [ ] Testar token expirado
- [ ] Testar permissões RBAC
- [ ] Testar isolamento de tenant
- [ ] Testar SQL injection (endpoints críticos)
- [ ] Testar XSS (frontend)
- [ ] Validar LGPD (exportação de dados)

### ✅ Critérios de Aceite

- [ ] 401 para requests sem autenticação
- [ ] 403 para requests sem permissão
- [ ] 403 para tenant violation
- [ ] Inputs validados e sanitizados

---

## 6️⃣ Testes Manuais (QA)

**Responsável:** QA Team
**Duração Estimada:** 4 horas

### Cenários Manuais

| Cenário | Status | Observações |
|---------|--------|-------------|
| Fluxo completo de safra | ⏳ | |
| Conciliação bancária | ⏳ | |
| Gestão de estoque FIFO | ⏳ | |
| Relatórios financeiros | ⏳ | |
| Mobile (responsive) | ⏳ | |
| Cross-browser | ⏳ | |

### Browsers Testados

- [ ] Chrome (última versão)
- [ ] Firefox (última versão)
- [ ] Safari (última versão)
- [ ] Edge (última versão)

### Dispositivos Testados

- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

---

## 7️⃣ Validação de Features da Sprint

**Responsável:** Product Owner + QA
**Duração Estimada:** 2 horas

### Features Implementadas

| Feature | Status | Observações |
|---------|--------|-------------|
| [Feature 1] | ⏳ | |
| [Feature 2] | ⏳ | |
| [Feature 3] | ⏳ | |

### Critérios de Pronto por Feature

Para cada feature:
- [ ] Testes unitários escritos
- [ ] Testes de integração escritos
- [ ] Testes E2E (se aplicável)
- [ ] Documentação atualizada
- [ ] Validação do PO

---

## 8️⃣ Bugs e Issues

**Responsável:** QA Team
**Duração Estimada:** 30 min

### Bugs Encontrados

| ID | Severidade | Descrição | Status |
|----|------------|-----------|--------|
| #001 | 🔴 Crítico | | Aberto |
| #002 | 🟡 Alto | | Aberto |
| #003 | 🟢 Médio | | Aberto |

### Definição de Severidade

| Severidade | Critério | SLA |
|------------|----------|-----|
| 🔴 Crítico | Sistema fora, perda de dados | 4 horas |
| 🟡 Alto | Feature principal quebrada | 24 horas |
| 🟢 Médio | Feature secundária quebrada | 1 semana |
| ⚪ Baixo | Bug cosmético | 2 semanas |

---

## 9️⃣ Métricas da Sprint

**Responsável:** Tech Lead
**Duração Estimada:** 15 min

### Métricas de Qualidade

| Métrica | Meta | Atual | Status |
|---------|------|-------|--------|
| Coverage Backend | ≥ 70% | 0% | ⏳ |
| Coverage Frontend | ≥ 60% | 0% | ⏳ |
| Bugs Críticos | 0 | 0 | ⏳ |
| Bugs Altos | ≤ 2 | 0 | ⏳ |
| Performance SLA | 100% | 0% | ⏳ |
| Testes E2E | 100% | 0% | ⏳ |

---

## 🔟 Sign-Off

### Aprovações

| Role | Nome | Data | Assinatura |
|------|------|------|------------|
| **QA Lead** | _____________________ | _________ | _____________________ |
| **Tech Lead** | _____________________ | _________ | _____________________ |
| **Product Owner** | _____________________ | _________ | _____________________ |
| **Scrum Master** | _____________________ | _________ | _____________________ |

### Decisão de Release

- [ ] ✅ **APROVADO** - Release pode prosseguir
- [ ] ⚠️ **APROVADO COM RISCOS** - Release com ressalvas
- [ ] ❌ **REPROVADO** - Release bloqueado

### Observações

```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 📝 Anexos

- [ ] Relatório de Coverage (htmlcov/index.html)
- [ ] Relatório de Testes E2E (playwright-report/index.html)
- [ ] Lista de Bugs Encontrados
- [ ] Logs de Performance

---

**Próxima Sprint:** ___/___/___
**Data de Release:** ___/___/___
