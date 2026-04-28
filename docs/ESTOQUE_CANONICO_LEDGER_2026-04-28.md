# Estoque Canônico — `estoque_movimentos` como única fonte oficial

Data de consolidação: `2026-04-28`

## Decisão arquitetural

A tabela `estoque_movimentos` é o **ledger canônico e único** de movimentações de estoque no AgroSaaS.

A tabela legada `estoque_movimentacoes` foi **removida fisicamente** no Step 79 (migration `step25_drop_estoque_movimentacoes`).

---

## Histórico da migração

| Step | Ação |
|------|------|
| 61 | Novos writes passaram a gravar somente em `estoque_movimentos` |
| 63 | Leituras funcionais adaptadas para o ledger canônico |
| 68 | Migration: `origem_tipo = LEGADO` liberado em `estoque_movimentos` |
| 69 | Script idempotente de backfill criado |
| 71 | Backfill real executado: 4 registros migrados como LEGADO, 0 erros |
| 72 | Caso remanescente `OPERACAO_AGRICOLA` revisado manualmente e descartado |
| 73 | Estratégia final de desativação definida |
| 74 | Model legado marcado read-only; guardrail estático ativado |
| 75 | Fallbacks removidos de `safras/service.py` e `relatorio_service.py` |
| 76 | Allowlist do guardrail reduzida ao mínimo |
| 77 | Auditoria final pré-remoção: 0 usos funcionais confirmados |
| 78 | Plano de remoção física documentado |
| 79 | Model removido, migration `DROP TABLE` executada, guardrail convertido para sentinela pós-drop |
| 80 | Validação final: 27 passed, 0 failed — todos os módulos dependem somente do ledger canônico |

---

## Estrutura do ledger canônico

**Tabela:** `estoque_movimentos`  
**Model:** `EstoqueMovimento` em `operacional/models/estoque.py`

Características:

- Append-only: correções são novos movimentos via `ajuste_de`
- `tenant_id` obrigatório: isolamento multi-tenant garantido
- `origem` e `origem_id`: rastreabilidade completa da origem do movimento
- `tipo_movimento`: tipagem explícita (`ENTRADA`, `SAIDA`, `TRANSFERENCIA`, `AJUSTE`, `LEGADO`)
- `production_unit_id`: vínculo com unidade produtiva
- `operacao_execucao_id`: vínculo com execução agrícola
- Custos em `Numeric(15,6)` e `Numeric(15,2)`: sem perda de precisão

---

## Módulos que gravam em `estoque_movimentos`

| Módulo | Evento que gera movimento |
|--------|--------------------------|
| Compras | Recebimento de pedido de compra |
| Estoque (API direta) | Entrada, saída, transferência, ajuste manual |
| Operações Agrícolas | Consumo de insumo em execução de operação |
| Beneficiamento | Entrada de produto beneficiado |
| Colheita / Romaneios | Entrada de produto colhido |

---

## Módulos que leem de `estoque_movimentos`

| Módulo | Finalidade |
|--------|-----------|
| Relatório de Estoque | Histórico e saldo por depósito/produto |
| Safras (KPIs) | Custo de insumos por safra |
| Dashboard Operacional | Consumo e entradas recentes |
| FIFO / Custo Médio | Base para cálculo de custo de saída |

---

## Sentinela ativo

O teste `test_estoque_movimentacoes_removida_do_codigo_ativo` em  
`tests/unit/operacional/test_estoque_movimentacoes_guardrails.py`  
impede que qualquer referência ao legado seja reintroduzida no código ativo.

---

## Arquivos de auditoria relacionados

- `docs/AUDITORIA_BACKFILL_ESTOQUE_MOVIMENTOS_REAL_STEP71_2026-04-28.md`
- `docs/AUDITORIA_MANUAL_OPERACAO_AGRICOLA_STEP72_2026-04-28.md`
- `docs/AUDITORIA_FINAL_PRE_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP77_2026-04-28.md`
- `docs/ESTRATEGIA_DESATIVACAO_ESTOQUE_LEGADO_STEP73.md`
- `docs/PLANO_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP78.md`
- `docs/CONTEXTO_CONTINUIDADE_ESTOQUE_LEGADO_2026-04-28.md`
