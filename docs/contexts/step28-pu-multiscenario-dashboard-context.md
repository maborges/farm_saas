# Contexto — Step 28: Comparação Multi-cenário por Production Unit

**Data:** 2026-04-26  
**Status:** CONCLUÍDO  

---

## Resumo executivo

Step 28 evoluiu o Dashboard Executivo da Safra com comparação multi-cenário por Production Unit, permitindo visualizar como cada unidade se comporta entre até 3 cenários carregados no comparativo.

A entrega manteve as restrições:
- sem novas tabelas
- sem backend novo
- sem duplicar lógica econômica
- reutilização do cache de comparativo já existente
- evolução apenas frontend/UX

---

## O que foi entregue

**Arquivo alterado**

`apps/web/src/app/(dashboard)/agricola/safras/[id]/dashboard/page.tsx`

### Nova seção

`Comparação por Production Unit`

Funciona com os dados já carregados de:

`GET /safras/{id}/cenarios/comparativo?ids=...`

Não dispara endpoint novo.

### Interações

- Antes do comparativo carregar:
  - mostra CTA `Carregar comparativo`
- Depois do comparativo carregar:
  - normaliza a união das Production Units presentes nos cenários selecionados
  - permite selecionar uma Production Unit
  - exibe métricas lado a lado por cenário

### Métricas comparadas

Por Production Unit:
- Receita
- Custo
- Margem
- Ponto de equilíbrio

### Destaques executivos

Cards compactos por unidade:
- Melhor margem
- Pior margem
- Maior custo
- Melhor ponto de equilíbrio

### Deltas contra BASE

Quando há cenário BASE:
- exibe diferença absoluta
- exibe diferença percentual quando possível
- protege contra divisão por zero e valores nulos

### Fallbacks

- Comparativo não carregado: CTA claro
- Comparativo sem unidades: alerta claro
- PU ausente em algum cenário: `PU ausente`
- Sem cenário BASE: mantém valores sem delta contra base
- Apenas um cenário: alerta de comparação limitada

---

## Regras de dados

### Normalização de Production Units

A lista de PUs usa a união de unidades presentes em todos os cenários selecionados:

```ts
normalizeScenarioProductionUnits(comparativoCols.slice(0, MAX_COMPARATIVO))
```

### Ordenação

Fallback de ordenação:
1. Margem no cenário BASE, quando disponível
2. Receita, quando margem não existe
3. Área, quando não há indicadores econômicos

### Limite visual

- Top 10 Production Units inicialmente
- Botão `Mostrar todas`

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
- Next dev em `http://localhost:3000`

Cenários validados:
- Comparação carregada por CTA: ✅
- União de PUs entre cenários: ✅
- PU ausente em cenário com fallback: ✅
- Cards melhor/pior cenário por unidade: ✅
- Estado vazio sem unidades no comparativo: ✅

Screenshots gerados:
- `/tmp/step28-pu-multicenario.png`
- `/tmp/step28-pu-multicenario-vazio.png`

---

## Dívida técnica mantida

O TypeScript global do frontend continua com dívidas preexistentes fora do escopo.

Status:
- Não bloqueia Step 28.
- Checagem focada no arquivo alterado não reportou erros.

---

## Critério de aceite

Step 28 está concluído porque:
- o usuário consegue comparar uma Production Unit entre até 3 cenários;
- a lista usa união das unidades dos cenários selecionados;
- variações contra BASE são exibidas com proteção contra nulos/divisão por zero;
- melhor/pior cenário por unidade é destacado;
- PUs ausentes em cenário são tratadas;
- nenhum backend, tabela ou regra econômica nova foi criado.
