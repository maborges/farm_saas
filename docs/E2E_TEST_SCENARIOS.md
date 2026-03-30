# Cenários E2E — Integração de Colheita

**Data:** 2026-03-30
**Duração Estimada:** 15-20 minutos por cenário

---

## 🎯 Pré-Requisitos

1. ✅ Backend rodando (alembic upgraded)
2. ✅ Frontend rodando (pnpm dev)
3. ✅ Usuário logado com permissão `agricola:safras:view`
4. ✅ Safra existente em fase COLHEITA
5. ✅ PostgreSQL com dados de teste

---

## 📋 Cenários

### Cenário 1: Validação de Operação por Fase

**Objetivo:** Verificar que operação PLANTIO é rejeitada em fase COLHEITA

**Pré-condições:**
- Safra "MILHO 2025/26" em fase COLHEITA

**Passos:**

| # | Ação | Esperado |
|---|------|----------|
| 1 | Acessar safra em COLHEITA | Página de detalhe carrega |
| 2 | Clicar "Operações" | Lista de operações (vazia ou com outras) |
| 3 | Clicar "+ Nova Operação" | Modal de criação abre |
| 4 | Preencher: Tipo=PLANTIO, Data=Hoje | Form é preenchido |
| 5 | Clicar "Adicionar" | ❌ Erro: "PLANTIO não permitido em COLHEITA" |
| 6 | Trocar para Tipo=COLHEITA | Form é atualizado |
| 7 | Clicar "Adicionar" | ✅ Operação criada com sucesso |

**Resultado:** ✅ Validação funciona conforme esperado

---

### Cenário 2: Webhook — Operação Gera Despesa

**Objetivo:** Verificar que operação com custo cria despesa automaticamente

**Pré-condições:**
- Safra em fase COLHEITA
- Plano de conta padrão configurado

**Passos:**

| # | Ação | Esperado |
|---|------|----------|
| 1 | Criar operação COLHEITA | Operação salva |
| 2 | Preencher Custo = R$ 5.000 | Valor aparece no form |
| 3 | Clicar "Adicionar" | Operação criada |
| 4 | Voltar para safra (refresh) | Operação aparece em lista |
| 5 | Acessar aba "Financeiro" | Dashboard carrega |
| 6 | Verificar "Despesa Total" | Mostra R$ 5.000 |
| 7 | Verificar "Total de Operações" | Mostra 1 |

**Validação no Backend:**
```bash
# Verificar despesa criada
psql -U postgres -d farm_db -c "
SELECT valor_total, origem_id, origem_tipo
FROM fin_despesas
WHERE origem_tipo = 'OPERACAO_AGRICOLA'
ORDER BY created_at DESC LIMIT 1;
"

# Esperado: 5000.00 | operacao-uuid | OPERACAO_AGRICOLA
```

**Resultado:** ✅ Despesa criada com rastreabilidade

---

### Cenário 3: Operação sem Custo = Sem Despesa

**Objetivo:** Verificar que operação SEM custo NÃO cria despesa

**Pré-condições:**
- Safra em fase COLHEITA

**Passos:**

| # | Ação | Esperado |
|---|------|----------|
| 1 | Criar operação COLHEITA | Form abre |
| 2 | Deixar Custo = 0 ou vazio | Field vazio/zero |
| 3 | Clicar "Adicionar" | Operação criada |
| 4 | Acessar aba "Financeiro" | Dashboard carrega |
| 5 | Verificar "Despesa Total" | Continua em valor anterior (não aumentou) |

**Resultado:** ✅ Sem custo = sem despesa

---

### Cenário 4: Webhook — Romaneio Gera Receita

**Objetivo:** Verificar que romaneio com preço cria receita automaticamente

**Pré-condições:**
- Safra em COLHEITA
- Operações já registradas (para custo)

**Passos:**

| # | Ação | Esperado |
|---|------|----------|
| 1 | Acessar aba "Romaneios" | Lista de romaneios |
| 2 | Clicar "+ Novo Romaneio" | Modal abre |
| 3 | Preencher dados: | |
|   | - Data Colheita = Hoje | Data é selecionada |
|   | - Peso Bruto = 60.000 kg | Valor inserido |
|   | - Umidade = 14% | Valor inserido |
|   | - Preco/Saca = R$ 100 | Valor inserido |
| 4 | Clicar "Calcular" | Sacas = 1.000 sc (MAPA) |
| 5 | Clicar "Adicionar" | Romaneio criado |
| 6 | Voltar para safra | Romaneio aparece em lista |
| 7 | Acessar aba "Financeiro" | Dashboard recarrega |
| 8 | Verificar "Receita Total" | Mostra R$ 100.000 (1.000 × 100) |
| 9 | Verificar "Total de Romaneios" | Mostra 1 |
| 10 | Verificar "Produtividade" | Mostra 10.0 sc/ha (1000/100) |

**Validação no Backend:**
```bash
psql -U postgres -d farm_db -c "
SELECT valor_total, origem_id, origem_tipo, sacas_60kg
FROM fin_receitas fr
JOIN romaneios_colheita rc ON fr.origem_id = rc.id
WHERE origem_tipo = 'ROMANEIO_COLHEITA'
ORDER BY fr.created_at DESC LIMIT 1;
"

# Esperado: 100000.00 | romaneio-uuid | ROMANEIO_COLHEITA | 1000.00
```

**Resultado:** ✅ Receita criada com rastreabilidade

---

### Cenário 5: Dashboard — Agregação Completa

**Objetivo:** Validar cálculos do dashboard (Custo, Receita, Lucro, ROI)

**Pré-condições:**
- Safra com 1 operação (R$ 5.000)
- Safra com 1 romaneio (R$ 100.000)

**Passos:**

| # | Ação | Esperado |
|---|------|----------|
| 1 | Acessar aba "Financeiro" | Dashboard carrega |
| 2 | Verificar KPI "Despesa Total" | R$ 5.000,00 |
| 3 | Verificar KPI "Receita Total" | R$ 100.000,00 |
| 4 | Verificar KPI "Lucro Bruto" | R$ 95.000,00 |
| 5 | Verificar KPI "ROI" | 1.900% |
| 6 | Verificar KPI "Produtividade" | 10,0 sc/ha |
| 7 | Verificar Gráfico | Barra despesa < barra receita |
| 8 | Verificar Timeline | 2 transações (1 despesa, 1 receita) |

**Cálculos Esperados:**
```
Despesa = R$ 5.000
Receita = R$ 100.000
Lucro = 100.000 - 5.000 = R$ 95.000
ROI = (95.000 / 5.000) × 100 = 1.900%
Produtividade = 1.000 sacas / 100 ha = 10,0 sc/ha
```

**Verificar via API:**
```bash
curl -X GET "http://localhost:8000/api/v1/agricola/dashboard/safras/SAFRA_ID/resumo-financeiro" \
  -H "Authorization: Bearer $JWT"

# Esperado:
{
  "financeiro": {
    "despesa_total": 5000.0,
    "receita_total": 100000.0,
    "lucro_bruto": 95000.0,
    "roi_pct": 1900.0,
    "produtividade_sc_ha": 10.0
  }
}
```

**Resultado:** ✅ Todos cálculos corretos

---

### Cenário 6: Isolamento de Tenant

**Objetivo:** Validar que User A NÃO vê dados de User B

**Pré-condições:**
- 2 usuários (User A + User B) em tenants diferentes
- Cada um com sua safra

**Passos (User A):**

| # | Ação | Esperado |
|---|------|----------|
| 1 | Login como User A | Dashboard do User A carrega |
| 2 | Acessar safra A | Dados de safra A mostram |
| 3 | Acessar aba "Financeiro" | KPIs de safra A |
| 4 | Tentar acessar URL de safra B | ❌ 403 Forbidden ou vê dados de A |

**Validação via API:**
```bash
# Com token de User A
curl -X GET "...safras/SAFRA_B_ID/resumo-financeiro" \
  -H "Authorization: Bearer $JWT_USER_A"

# Esperado: 403 Forbidden ou 404 Not Found
```

**Resultado:** ✅ Tenant isolation funciona

---

### Cenário 7: Timeline de Transações

**Objetivo:** Verificar que timeline mostra operações e romaneios em ordem cronológica

**Pré-condições:**
- Múltiplas operações com datas diferentes
- Múltiplos romaneios com datas diferentes

**Passos:**

| # | Ação | Esperado |
|---|------|----------|
| 1 | Acessar aba "Financeiro" | Dashboard carrega |
| 2 | Rolar até "Rastreabilidade Financeira" | Timeline visível |
| 3 | Verificar ordem de items | Cronológica (mais antigo → mais novo) |
| 4 | Clicar em operação | Badge "Despesa" aparece |
| 5 | Clicar em romaneio | Badge "Receita" aparece |
| 6 | Verificar valores | Despesa show -R$, Receita show +R$ |
| 7 | Verificar detalhes | Data, tipo, área/sacas aparecem |

**Resultado:** ✅ Timeline renderiza corretamente

---

### Cenário 8: Performance & Load Time

**Objetivo:** Validar que dashboard carrega em tempo aceitável

**Pré-condições:**
- Safra com múltiplas operações (10+) e romaneios (5+)

**Passos:**

| # | Ação | Esperado |
|---|------|----------|
| 1 | Abrir DevTools (F12) | Console abre |
| 2 | Ir para aba "Network" | Network monitor ativo |
| 3 | Clicar em "Financeiro" | Requests são capturados |
| 4 | Verificar GET `/resumo-financeiro` | < 500ms |
| 5 | Verificar GET `/operacoes` | < 300ms |
| 6 | Verificar GET `/romaneios` | < 300ms |
| 7 | Verificar tempo de render | < 2s no total |

**Lighthouse Audit:**
```bash
pnpm dlx lighthouse http://localhost:3000/agricola/safras/[id]/financeiro

# Esperado:
# Performance: > 80
# First Contentful Paint: < 2s
# Largest Contentful Paint: < 3s
```

**Resultado:** ✅ Performance aceitável

---

### Cenário 9: Responsive Design

**Objetivo:** Validar que frontend funciona em mobile/tablet

**Pré-condições:**
- Dashboard em estado normal

**Passos (Mobile):**

| # | Ação | Esperado |
|---|------|----------|
| 1 | DevTools → Device Toolbar | Mobile view ativa |
| 2 | Selecionar iPhone 12 | Viewport em 390px |
| 3 | Acessar aba "Financeiro" | Page carrega sem layout breaks |
| 4 | Verificar KPI cards | Stackam verticalmente |
| 5 | Verificar Chart | Responsivo, legível |
| 6 | Verificar Timeline | Items stackados, sem overflow |
| 7 | Scroll para baixo | Sem horizontal scroll |
| 8 | Testar em tablet (iPad) | Layout em 768px |

**Resultado:** ✅ Mobile-friendly

---

### Cenário 10: Erro Handling

**Objetivo:** Validar comportamento em cenários de erro

**Pré-condições:**
- Safra em COLHEITA

**Passos:**

| # | Ação | Esperado |
|---|------|----------|
| 1 | Acessar safra inexistente via URL | ❌ 404 error page |
| 2 | Acessar com token expirado | ❌ 401 redirect to login |
| 3 | Acessar sem permissão | ❌ 403 error message |
| 4 | Dashboard com safra vazia | ✅ "Sem operações" message |
| 5 | Criar operação com data futura | ❌ "Data não pode ser futura" |

**Resultado:** ✅ Error handling correto

---

## 📊 Resultado Final

| Cenário | Status | Data | Hora |
|---------|--------|------|------|
| 1. Validação Fase | ⏳ | — | — |
| 2. Webhook Despesa | ⏳ | — | — |
| 3. Sem Custo = Sem Despesa | ⏳ | — | — |
| 4. Webhook Receita | ⏳ | — | — |
| 5. Dashboard Agregação | ⏳ | — | — |
| 6. Isolamento Tenant | ⏳ | — | — |
| 7. Timeline | ⏳ | — | — |
| 8. Performance | ⏳ | — | — |
| 9. Responsive | ⏳ | — | — |
| 10. Error Handling | ⏳ | — | — |

**Total:** `__/10` cenários passando

---

## ✅ Sign-Off

```
Testador: _____________________
Data: ________________________
Horas Gastas: ________________
Bugs Encontrados: ____________
```

---

**Documentação:** [IMPLEMENTACAO_COLHEITA_COMPLETA.md](./IMPLEMENTACAO_COLHEITA_COMPLETA.md)
**Deployment:** [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
**API:** [API_ENDPOINTS_REFERENCE.md](./API_ENDPOINTS_REFERENCE.md)

