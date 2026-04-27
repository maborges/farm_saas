# Contexto — Step 20: Monetização de Cenários Econômicos

**Data:** 2026-04-27  
**Status:** CONCLUÍDO  

---

## Decisão de monetização aplicada

O módulo `A1_PLANEJAMENTO` permanece como acesso operacional agrícola. Ele permite leitura, consulta e manutenção operacional básica do cenário BASE.

O tier `PROFISSIONAL` passa a ser o limite comercial para inteligência executiva e simulação avançada:

- criação de cenários customizados;
- duplicação de cenários;
- comparativo multi-cenário;
- dashboard executivo que depende do comparativo;
- endpoints legados de dashboard financeiro/margem agrícola.

Não foram criadas novas tabelas, backends ou regras econômicas. A implementação reutiliza:

- backend: `require_tier(PlanTier.PROFISSIONAL)`;
- frontend: `useHasTier("PROFISSIONAL")`.

---

## Gates backend

### Permanecem disponíveis em A1

- `GET /safras/{safra_id}/cenarios`
- `GET /safras/{safra_id}/cenarios/{cenario_id}`
- `PATCH /safras/{safra_id}/cenarios/{cenario_id}`
- `DELETE /safras/{safra_id}/cenarios/{cenario_id}`
- `POST /safras/{safra_id}/cenarios/base/recalcular`
- endpoints de `production-units`

### Exigem PROFISSIONAL

- `POST /safras/{safra_id}/cenarios`
- `POST /safras/{safra_id}/cenarios/{cenario_id}/duplicar`
- `GET /safras/{safra_id}/cenarios/comparativo`
- `GET /agricola/dashboard/safras/{safra_id}/resumo-financeiro`
- `GET /agricola/dashboard/safras/{safra_id}/margem`

O backend continua sendo a fonte final de bloqueio. Requisições com tier insuficiente retornam `402` com headers `X-Tier-Required` e `X-Tier-Current`.

---

## Gates frontend

O frontend deixa de depender apenas do erro `402` para recursos premium:

- card `Dashboard Executivo` só aparece para `PROFISSIONAL`;
- página de Dashboard Executivo bloqueia antes de montar queries premium;
- página de Comparativo bloqueia antes de montar queries premium;
- botões `Novo Cenário`, `Duplicar` e `Comparar` exigem `PROFISSIONAL`;
- listagem e visualização de cenários continuam disponíveis para A1.

Os bloqueios visuais usam componentes padronizados de `apps/web/src/components/ui`, incluindo `Alert`, `Button` e `Card`.

---

## Testes executados

### Backend

```bash
services/api/.venv/bin/pytest \
  services/api/tests/unit/test_billing_gates.py \
  services/api/tests/test_step20_cenarios.py \
  services/api/tests/test_dashboard_financeiro_safra.py \
  -q
```

Resultado:

- `37 passed`
- `5 warnings`

Observações:

- warnings de `pytest.mark.asyncio` em testes síncronos já existentes;
- warning de `PydanticDeprecatedSince20` em schema de dashboard já existente.

### Frontend

```bash
npm run lint -- \
  src/app/\(dashboard\)/agricola/safras/\[id\]/page.tsx \
  src/app/\(dashboard\)/agricola/safras/\[id\]/dashboard/page.tsx \
  src/app/\(dashboard\)/agricola/safras/\[id\]/cenarios/page.tsx \
  src/app/\(dashboard\)/agricola/safras/\[id\]/cenarios/comparativo/page.tsx
```

Resultado:

- sem erros;
- warnings de imports/props não usados em páginas existentes.

### Sintaxe backend

```bash
services/api/.venv/bin/python -m py_compile \
  services/api/agricola/cenarios/router.py \
  services/api/agricola/dashboard/router.py \
  services/api/tests/conftest.py \
  services/api/tests/test_dashboard_financeiro_safra.py \
  services/api/tests/unit/test_billing_gates.py
```

Resultado:

- passou.

---

## Correções de teste realizadas

O erro `duplicate key value violates unique constraint "uq_assinatura_tenant_tipo"` em `test_dashboard_financeiro_safra.py` era causado pelo fixture criando uma nova assinatura `TENANT` para o mesmo tenant fixo a cada teste.

Correção aplicada:

- fixture passou a criar a assinatura principal de forma idempotente com `ON CONFLICT (tenant_id, tipo_assinatura) DO UPDATE`;
- teste de dashboard financeiro foi atualizado para o modelo atual de safra/cultivo:
  - `Safra`;
  - `Cultivo`;
  - `CultivoArea`;
  - `cadastros_areas_rurais` como origem de `talhao_id`;
- imports de models necessários foram registrados no metadata de testes.

Essa correção não altera regra de produto.

---

## Débitos técnicos fora do escopo

- `services/api/seed.py` possui `IndentationError` na linha 46 e bloqueia execução do seed.
- `ruff check` global continua acusando problemas legados fora deste step, especialmente em routers antigos.
- O frontend focado passa sem erro, mas há warnings de imports/props não usados já existentes nas páginas alteradas.

---

## Resumo de commit sugerido

```text
feat(agricola): enforce professional gates for economic scenarios
```

Resumo objetivo:

- aplica gate `PROFISSIONAL` em criação, duplicação e comparativo de cenários;
- mantém listagem, visualização e cenário BASE acessíveis para `A1_PLANEJAMENTO`;
- protege dashboard executivo/comparativo no frontend antes de disparar queries premium;
- adiciona cobertura de headers `X-Tier-Required`;
- corrige fixture de dashboard financeiro para assinatura idempotente e schema atual.
