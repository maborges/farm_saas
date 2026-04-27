# Contexto — Step 27: Alertas Executivos no Dashboard

**Data:** 2026-04-26  
**Status:** CONCLUÍDO  

---

## Resumo executivo

Step 27 evoluiu o Dashboard Executivo da Safra com uma seção consolidada de alertas proativos, priorizando riscos e inconsistências detectados a partir dos dados já carregados de cenários, comparativo e Production Units.

A entrega manteve as restrições:
- sem novas tabelas
- sem backend novo
- sem duplicar lógica econômica
- evolução apenas frontend/UX
- reutilização de `cenarios`, `comparativo` e `production_units`

---

## O que foi entregue

**Arquivo alterado**

`apps/web/src/app/(dashboard)/agricola/safras/[id]/dashboard/page.tsx`

### Seção `Alertas Executivos`

Criada seção consolidada com:
- contadores de críticos e atenção
- lista ordenada por severidade
- IDs únicos por alerta
- origem do alerta:
  - `Cenário`
  - `Comparativo`
  - `Production Unit`
- CTA de correção por alerta
- limite visual inicial de 5 alertas
- botão `Ver todos`
- estado positivo forte quando não há alertas

### Estado positivo

Quando nenhum risco é detectado:
- `Nenhum risco executivo detectado`
- `Monitoramento saudável`

### Deduplicação

Alertas similares são deduplicados:
- `BASE_MARGIN_NEGATIVE` suprime `BASE_COST_GT_REVENUE`
- `PU_MARGIN_NEGATIVE:{pu_id}` suprime `PU_COST_GT_REVENUE:{pu_id}`

### Limite por Production Unit

Cada Production Unit gera no máximo:
- `MAX_ALERTS_PER_PU = 2`

Isso evita ruído quando uma mesma unidade possui múltiplos problemas relacionados.

---

## Alertas implementados

### Cenário

- `NO_ACTIVE_SCENARIOS`
- `NO_BASE_SCENARIO`
- `BASE_NOT_CALCULATED`
- `BASE_MARGIN_NEGATIVE`
- `BASE_COST_GT_REVENUE`
- `BASE_MARGIN_LOW`
- `BASE_BREAK_EVEN_MISSING`

### Comparativo

- `ONLY_ONE_ACTIVE_SCENARIO`
- `PESSIMISTIC_MARGIN_NEGATIVE`
- `BASE_SCENARIO_WITHOUT_UNITS`

### Production Unit

- `NO_ACTIVE_PRODUCTION_UNITS`
- `ACTIVE_PU_MISSING_FROM_BASE`
- `PU_MARGIN_NEGATIVE:{production_unit_id}`
- `PU_COST_GT_REVENUE:{production_unit_id}`
- `PU_MARGIN_LOW:{production_unit_id}`
- `PU_INCOMPLETE_ECONOMICS:{production_unit_id}`

---

## Regras de carregamento

Os alertas não forçam chamadas extras.

Funcionamento:
- Sempre avalia cenários já carregados.
- Avalia comparativo apenas se o comparativo já foi carregado.
- Avalia Production Units apenas se PUs já foram carregadas.

Assim, o Dashboard continua leve no carregamento inicial.

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
- Next dev em `http://localhost:3003`

Cenários validados:
- Estado positivo saudável: ✅
- Alertas críticos: ✅
- Deduplicação margem negativa vs custo > receita: ✅
- CTA abrindo drill-down: ✅
- `Ver todos` nos alertas: ✅

Screenshots gerados:
- `/tmp/step27-alertas-positivo.png`
- `/tmp/step27-alertas-risco.png`

---

## Dívida técnica mantida

O TypeScript global do frontend continua com dívidas preexistentes fora do escopo.

Status:
- Não bloqueia Step 27.
- Checagem focada no arquivo alterado não reportou erros.

---

## Critério de aceite

Step 27 está concluído porque:
- o dashboard mostra alertas executivos consolidados automaticamente;
- alertas são priorizados por severidade;
- alertas semelhantes são deduplicados;
- há limite por Production Unit;
- cada alerta orienta uma ação concreta;
- estado positivo está claro;
- nenhuma tabela, backend ou regra econômica nova foi criada.
