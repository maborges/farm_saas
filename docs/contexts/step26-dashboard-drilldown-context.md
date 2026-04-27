# Contexto — Step 26: Drill-down Executivo do Dashboard

**Data:** 2026-04-26  
**Status:** CONCLUÍDO  

---

## Resumo executivo

Step 26 evoluiu o Dashboard Executivo da Safra com drill-down por KPI, permitindo investigar a origem dos indicadores principalmente por Production Unit.

A implementação manteve o escopo aprovado:
- sem novas tabelas
- sem backend novo
- sem duplicar lógica econômica
- reutilizando `cenarios`, `comparativo` e `production_units`
- evolução apenas frontend/UX

---

## O que foi entregue

**Arquivo principal**

`apps/web/src/app/(dashboard)/agricola/safras/[id]/dashboard/page.tsx`

### Interações

Os 4 KPIs agora são clicáveis:
- Receita projetada
- Custo total
- Margem
- Ponto de equilíbrio

Cada clique altera um único estado de controle:
- `selectedMetric`

Esse estado controla qual painel inline de drill-down está aberto.

### Painel de drill-down

O painel exibe breakdown por Production Unit com:
- unidade / cultivo / área
- área em hectares
- valor da métrica selecionada
- participação visual no total, quando aplicável
- badge de risco:
  - `Crítico`
  - `Atenção`
  - `Saudável`

Ordenação por métrica:
- Receita: maior receita primeiro
- Custo: maior custo primeiro
- Margem: pior margem primeiro
- Ponto de equilíbrio: maior ponto de equilíbrio primeiro

### Performance

Comparativo:
- lazy load
- cache após primeira carga
- `staleTime: Infinity`
- `refetchOnMount: false`
- `refetchOnReconnect: false`
- `refetchOnWindowFocus: false`

Production Units:
- mantém lazy load do Step 25

Renderização:
- drill-down exibe top 10 Production Units inicialmente
- botão para expandir todas

---

## Dados reutilizados

### Cenários

`GET /safras/{id}/cenarios`

Usado para:
- identificar cenário base
- selecionar cenários do comparativo MVP
- manter KPIs agregados

### Comparativo

`GET /safras/{id}/cenarios/comparativo?ids=...`

Usado para:
- dados econômicos calculados por cenário
- unidades do cenário base
- receita/custo/margem/ponto de equilíbrio por Production Unit

### Production Units

`GET /safras/{id}/production-units`

Permanece disponível no dashboard como lazy load e navegação rápida.

---

## Fallbacks

Fallback implementado para:
- comparativo ainda não carregado
- erro de API no drill-down
- cenário base sem dados de unidades
- métrica sem dados por Production Unit

---

## Validações executadas

### Lint focado

```bash
npm run lint -- 'src/app/(dashboard)/agricola/safras/[id]/dashboard/page.tsx'
```

Resultado: ✅ passou.

### TypeScript focado

```bash
npm exec tsc -- --noEmit --pretty false 2>&1 | rg 'safras/\[id\]/dashboard/page\.tsx' || true
```

Resultado: ✅ sem erros no arquivo alterado.

### Validação visual com Playwright

Servidor local:
- Next dev em `http://localhost:3002`

Cenários validados:
- Clique nos KPIs de Receita, Margem e Ponto de equilíbrio: ✅
- Top 10 Production Units + expandir todas: ✅
- Fallback de cenário base sem unidades: ✅
- Navegação rápida para Production Units, Cenários e Comparativo: ✅
- Cache do comparativo: ✅ apenas 1 chamada após 3 cliques de KPI

Screenshots gerados:
- `/tmp/step26-drilldown-kpis.png`
- `/tmp/step26-drilldown-sem-unidades.png`

---

## Dívida técnica mantida

O TypeScript global do frontend continua com dívidas preexistentes fora do escopo.

Status:
- Não bloqueia Step 26.
- Checagem focada no arquivo alterado não reportou erros.

---

## Critério de aceite

Step 26 está concluído porque:
- o usuário consegue clicar nos KPIs do dashboard;
- cada KPI abre um drill-down por Production Unit;
- unidades de pior desempenho são destacadas;
- o comparativo é carregado uma vez e reutilizado;
- há fallback quando o cenário base não possui unidades;
- top 10 inicial evita renderização excessiva;
- não houve backend, tabela ou regra econômica nova.
