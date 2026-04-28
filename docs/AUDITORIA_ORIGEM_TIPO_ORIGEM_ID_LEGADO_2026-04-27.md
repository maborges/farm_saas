# Auditoria de `origem_tipo` / `origem_id` em Lançamentos Legados

Data/hora do snapshot: 2026-04-27

Base consultada:

- PostgreSQL configurado em `apps/web/services/api/.env.local`
- banco: `farms`

Escopo desta auditoria:

- `fin_despesas`
- `fin_receitas`

Critério usado nesta etapa:

- **com rastreabilidade operacional**: `origem_tipo` preenchido e `origem_id` preenchido;
- **sem rastreabilidade operacional**: `origem_tipo IS NULL`, ou `origem_id IS NULL`, ou `origem_tipo = 'MANUAL'`.

Observação:

- neste snapshot, os registros legados sem rastreabilidade operacional aparecem como `origem_tipo = 'MANUAL'` com `origem_id = NULL`;
- não foi executado backfill automático;
- não foi alterado schema.

## Resumo executivo

Totais encontrados:

| Tipo | Com origem operacional | Sem rastreabilidade operacional | Total |
| --- | ---: | ---: | ---: |
| Despesa | 6 | 18 | 24 |
| Receita | 4 | 16 | 20 |
| **Total geral** | **10** | **34** | **44** |

Distribuição real de preenchimento:

| `origem_tipo` | `origem_id` | Total |
| --- | --- | ---: |
| `MANUAL` | `NULL` | 34 |
| `OPERACAO_AGRICOLA` | preenchido | 4 |
| `ROMANEIO_COLHEITA` | preenchido | 4 |
| `RECEBIMENTO_COMPRA` | preenchido | 2 |

Leitura objetiva:

- os lançamentos já rastreáveis somam `10`;
- os lançamentos ainda sem rastreabilidade operacional somam `34`;
- neste snapshot, **não houve ocorrência de `origem_tipo` nulo com `origem_id` preenchido**, nem de `origem_tipo` operacional com `origem_id` nulo;
- o passivo legado está concentrado em lançamentos classificados como `MANUAL`.

## Breakdown por módulo, tipo e data

Heurística de módulo para registros sem rastreabilidade:

- `Compra — Pedido%` -> `COMPRAS`
- `Abastecimento%` / `Manutenção — OS%` -> `FROTA`
- `Pecuária —%` -> `PECUARIA`
- `%Romaneio%` -> `AGRICOLA`
- `%Comercialização%` -> `FINANCEIRO_COMERCIALIZACAO`
- demais descrições -> `FINANCEIRO_MANUAL`

Resultado do snapshot:

| Data | Módulo inferido | Tipo | Total sem rastreabilidade |
| --- | --- | --- | ---: |
| 2026-04-27 | `FINANCEIRO_MANUAL` | `DESPESA` | 18 |
| 2026-04-27 | `FINANCEIRO_MANUAL` | `RECEITA` | 16 |

Conclusão desta visão:

- o passivo atual está 100% concentrado em `FINANCEIRO_MANUAL`;
- não apareceu, neste snapshot, passivo legado sem origem em `COMPRAS`, `FROTA`, `PECUARIA` ou `AGRICOLA`.

## Principais descrições sem rastreabilidade

| Módulo inferido | Tipo | Total | Descrição |
| --- | --- | ---: | --- |
| `FINANCEIRO_MANUAL` | `DESPESA` | 8 | `Parcelamento de defensivo` |
| `FINANCEIRO_MANUAL` | `RECEITA` | 8 | `Venda de soja safra 2025` |
| `FINANCEIRO_MANUAL` | `DESPESA` | 2 | `Compra de herbicida` |
| `FINANCEIRO_MANUAL` | `DESPESA` | 2 | `Despesa para atualizar` |
| `FINANCEIRO_MANUAL` | `DESPESA` | 2 | `Despesa para baixar` |
| `FINANCEIRO_MANUAL` | `DESPESA` | 2 | `Despesa rateada 60/40` |
| `FINANCEIRO_MANUAL` | `DESPESA` | 2 | `Despesa urgente` |
| `FINANCEIRO_MANUAL` | `RECEITA` | 2 | `Receita para atualizar` |
| `FINANCEIRO_MANUAL` | `RECEITA` | 2 | `Receita para baixar` |
| `FINANCEIRO_MANUAL` | `RECEITA` | 2 | `Receita pendente filtro` |
| `FINANCEIRO_MANUAL` | `RECEITA` | 2 | `Receita vencendo logo` |

## Interpretação operacional

O cenário atual indica:

- os fluxos operacionais já auditados estão gravando origem quando aplicável;
- o estoque legado remanescente, neste snapshot, está em lançamentos manuais do Financeiro;
- antes de qualquer backfill, o próximo passo seguro é decidir se:
  - `MANUAL` com `origem_id = NULL` continuará sendo aceito como categoria legítima de lançamento manual;
  - ou se esses registros deverão ser separados entre `MANUAL legítimo` e `LEGADO sem rastreabilidade`.

## Fora de escopo desta etapa

- backfill automático;
- reclassificação de registros;
- mudança de schema;
- bloqueio de lançamentos manuais existentes.
