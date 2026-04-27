# Contexto — Step 25: Dashboard Executivo da Safra

**Data:** 2026-04-26  
**Status:** CONCLUÍDO  

---

## Resumo executivo

Step 25 entregou o MVP frontend/UX do Dashboard Executivo da Safra, consolidando KPIs, comparativo de cenários e visão por Production Unit sem criar backend novo, tabelas ou regras econômicas duplicadas.

O dashboard reutiliza os endpoints existentes de cenários, comparativo e Production Units. A lógica econômica permanece nos services já existentes dos Steps 20/21.

---

## Escopo entregue

### Frontend

**`apps/web/src/app/(dashboard)/agricola/safras/[id]/dashboard/page.tsx`**
- Nova rota `/agricola/safras/{id}/dashboard`
- KPIs principais:
  - receita projetada
  - custo total
  - margem
  - ponto de equilíbrio
- Alertas visuais:
  - sem cenário base
  - margem negativa
  - margem operacional baixa
  - sem Production Units ativas
  - erro de API
- Comparativo executivo limitado a 3 cenários
- Production Units com carregamento sob demanda e limite inicial de 10 unidades ativas
- Ações rápidas para:
  - Cenários
  - Production Units
  - Comparativo completo

**`apps/web/src/app/(dashboard)/agricola/safras/[id]/page.tsx`**
- Card de navegação adicionado:
  - `Dashboard Executivo`
  - href `/agricola/safras/{id}/dashboard`
- Tipagens locais ajustadas para remover `any` no arquivo tocado.

---

## Checklist obrigatório

| Item | Status | Observação |
|---|---:|---|
| Não criar novas tabelas | ✅ | Nenhuma migration/model novo |
| Não criar backend novo | ✅ | Apenas frontend |
| Não duplicar lógica Step 20/21 | ✅ | KPIs consomem campos já calculados |
| Reutilizar cenários | ✅ | `GET /safras/{id}/cenarios` |
| Reutilizar comparativo | ✅ | `GET /safras/{id}/cenarios/comparativo` lazy |
| Reutilizar Production Units | ✅ | `GET /safras/{id}/production-units` lazy |
| Limitar comparativo MVP | ✅ | Máximo de 3 cenários |
| Performance em PUs | ✅ | Lazy load + limite inicial de 10 ativas |

---

## Estratégia de carregamento

1. Carregamento inicial:
- Apenas lista de cenários.

2. Lazy load:
- Comparativo só carrega ao clicar em `Carregar`.
- Production Units só carregam ao clicar em `Carregar`.

3. Limites MVP:
- Comparativo: `MAX_COMPARATIVO = 3`
- Production Units: `INITIAL_PU_LIMIT = 10`

---

## Validações executadas

### Lint focado

```bash
npm run lint -- 'src/app/(dashboard)/agricola/safras/[id]/dashboard/page.tsx' 'src/app/(dashboard)/agricola/safras/[id]/page.tsx'
```

Resultado: ✅ passou.

### TypeScript focado

```bash
npm exec tsc -- --noEmit --pretty false 2>&1 | rg 'safras/\[id\]/(dashboard/page|page)\.tsx' || true
```

Resultado: ✅ sem erros nos arquivos alterados.

### Validação visual com Playwright

Servidor local:
- Next dev em `http://localhost:3001`

Cenários validados com mocks de API:
- Safra com cenário base: ✅
- Safra sem cenário base: ✅
- Safra sem Production Units ativas: ✅
- Navegação `Safra → Dashboard`: ✅
- Navegação `Dashboard → Cenários`: ✅
- Navegação `Dashboard → Comparativo`: ✅
- Navegação `Dashboard → Production Units`: ✅

Screenshots gerados:
- `/tmp/step25-dashboard-com-base.png`
- `/tmp/step25-dashboard-sem-base.png`
- `/tmp/step25-dashboard-sem-pus.png`
- `/tmp/step25-safra-dashboard-link.png`

---

## Dívida técnica registrada

O TypeScript global do frontend ainda falha por dívidas preexistentes fora do escopo do Step 25.

Status:
- Não bloqueia Step 25.
- Deve ser tratado como dívida técnica geral do frontend.
- A checagem focada nos arquivos alterados não reportou erros.

---

## Critério de aceite

Step 25 está concluído porque:
- O dashboard está acessível pela página da safra.
- KPIs usam dados existentes de cenários.
- Comparativo usa endpoint existente e lazy load.
- Production Units usam endpoint existente e lazy load.
- Fallbacks principais foram validados.
- Nenhum backend/tabela/regra econômica nova foi criado.
