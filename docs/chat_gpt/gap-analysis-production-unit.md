# GAP Analysis — Introdução de `ProductionUnit` (Núcleo Operacional)

**Data:** 2026-04-24
**Escopo:** Avaliar impactos de introduzir o conceito `ProductionUnit` (PU) sem quebrar compatibilidade.
**Regra mestre:** Additive evolution — **nenhuma** mudança destrutiva.

---

## 1. Estado atual do schema (relevante)

| Conceito doc | Já existe no sistema? | Tabela atual | Observação |
|---|---|---|---|
| **Safra** (período agrícola) | ✅ SIM | `safras` | Máquina de estados (`SAFRA_FASES_ORDEM`) já implementada |
| **Cultivo** (unidade de negócio) | ✅ SIM | `cultivos` | Aninhado dentro de Safra; multi-cultivo concluído (step4–6) |
| **CultivoArea** (cultivo × talhão) | ✅ SIM | `cultivo_areas` | `area_id` → `cadastros_areas_rurais`, `area_ha` presente |
| **AreaRural** (ex-talhão) | ✅ SIM | `cadastros_areas_rurais` | Renomeado em step1 (talhoes → areas_rurais) |
| **SafraTalhao** (legado N:N) | ⚠️ legado | `safra_talhoes` | Mantido por compat; fonte de verdade migrou p/ `cultivo_areas` |
| **ProductionUnit** | ❌ NÃO | — | Conceito novo a ser introduzido |
| **Task** (com N operações) | ⚠️ parcial | `agricola/tarefas` + `checklist` | Existe `tarefas` com `cultivo_area_id`, mas sem modelagem Task→Operation 1:N |
| **Operation** | ✅ SIM (achatado) | `operacoes_agricolas` | Tem `custo_total`, `status`, `fase_safra`, mas sem `OperationExecution` separado — execução parcial **não** suportada |
| **OperationExecution** | ❌ NÃO | — | Gap crítico — impede execução parcial + devolução |
| **InventoryMovement** (ledger) | ❌ NÃO | — | Não há ledger imutável de estoque |
| **CostAllocation** (rateio multi) | ⚠️ parcial | `financeiro.rateio` | Existe `Rateio` financeiro, **não** há rateio por PU/talhão/cultivo |
| **Scenario** (planejamento) | ❌ NÃO | — | Nenhum suporte a cenários |
| **Measurement Engine** (UOM) | ❌ NÃO | — | Valores salvos sem unidade canônica |
| **Laudo versionado** | ❌ NÃO | `analises_solo` não versionado | `CultivoArea.analise_solo_id` é FK simples |

---

## 2. GAP por módulo (`/services/api/agricola/*`)

| Módulo | Impacto | Ação necessária |
|---|---|---|
| `safras` | **Alto** | Adicionar relacionamento `Safra 1:N ProductionUnit`; manter `SafraTalhao` como view/compat |
| `cultivos` | **Alto** | PU referencia `cultivo_id` + `area_id`; `CultivoArea` vira input do seed inicial de PUs |
| `operacoes` | **Alto** | `OperacaoAgricola.cultivo_id` ok; **adicionar** FK opcional `production_unit_id`; criar `operation_executions` em tabela nova |
| `tarefas` | **Médio** | Renomear conceitualmente para Task (manter tabela); vincular a PU; permitir 1 Task → N Operations |
| `checklist` | **Baixo** | Sem impacto direto — pode referenciar PU opcionalmente |
| `romaneios`, `beneficiamento` | **Médio** | Já têm `cultivo_id`; adicionar `production_unit_id` nullable para rastreio fino |
| `a1_planejamento` | **Alto** | Orçamento passa a pivotar em PU; manter agregação por safra para compat |
| `analises_solo`, `prescricoes`, `agronomo` | **Médio** | Versionamento de laudo + escopo PU; hoje atrelado a `CultivoArea` |
| `custos`, `financeiro_kpis` | **Alto** | Criar `cost_allocations` com FK p/ PU; manter `fin_rateios` como origem financeira |
| `dashboard`, `fenologia`, `monitoramento`, `irrigacao`, `climatico`, `ndvi` | **Baixo** | Leitura opcional por PU; agregação por cultivo/safra preservada |
| `estoque` (não mapeado) | **Alto** | Criar `inventory_movements` ledger — não existe hoje |

---

## 3. Impactos para introduzir `ProductionUnit` sem quebrar nada

### 3.1 Estratégia de compatibilidade (additive-only)
1. **Nova tabela** `production_units(id, tenant_id, safra_id, cultivo_id, area_id, participation_percent, area_ha, status, created_at, updated_at)` — **sem** remover `cultivo_areas` nem `safra_talhoes`.
2. **Backfill** idempotente: 1 PU por linha existente em `cultivo_areas` (`participation_percent = 100` quando não consórcio; rateio pelo `area_ha` quando consórcio).
3. Novas FKs em `operacoes_agricolas`, `romaneios`, `beneficiamento`, `tarefas`, `a1_planejamento.*` → **todas nullable** inicialmente. Leitura continua resolvendo via `cultivo_id` quando `production_unit_id` é NULL.
4. Views de compat (`v_safra_talhoes`, `v_cultivo_areas`) se for necessário desacoplar leituras legadas.
5. Camada de serviço: `ProductionUnitResolver` devolve PU a partir de (`safra_id`, `cultivo_id`, `area_id`) — mantém routers legados funcionando.

### 3.2 Riscos de compatibilidade
| Risco | Mitigação |
|---|---|
| Dupla fonte de verdade (`cultivo_areas` vs `production_units`) | PU = projeção derivada; triggers/service sync até deprecação futura |
| Rateio de `Rateio` financeiro × `CostAllocation` agrícola | Manter `fin_rateios` no financeiro; `cost_allocations` consome `fin_rateios` via FK opcional |
| Consórcio (`Cultivo.consorciado=True`) | PU já captura via `participation_percent` por talhão × cultivo |
| Gates de fase (`SAFRA_TRANSICOES`) | Gates permanecem em Safra; PU herda fase via `safra_id` |
| Execução parcial de operação | Requer **obrigatório** criar `operation_executions`; sem isso, critério de aceite #2 (devolução) falha |
| Measurement Engine ausente | Bloqueador para `InventoryMovement` e `OperationExecution` — criar módulo `core/measurements` antes do ledger |
| Ledger de estoque inexistente | Criar `inventory_movements` do zero; migration inicial é apenas DDL (não há dados a preservar) |

### 3.3 Ordem obrigatória (do doc + ajustada à realidade)
1. `measurements` (UOM) — **pré-requisito** para #3 e #4
2. `production_units` + backfill a partir de `cultivo_areas`
3. `operation_executions` (sem remover `custo_total` de `operacoes_agricolas`)
4. `inventory_movements` (ledger novo)
5. `cost_allocations` (consumindo PU + `fin_rateios`)
6. `scenarios` (planejamento)

### 3.4 Critérios de aceite × gap atual
| Cenário | Atende hoje? | Bloqueador |
|---|---|---|
| 1. Task com múltiplas operações | ❌ | `tarefas` 1:1 com operação |
| 2. Operação parcial com devolução | ❌ | Sem `operation_executions` nem `inventory_movements` |
| 3. Rateio multi-talhão | ⚠️ parcial | `fin_rateios` existe, mas não por PU/cultivo |
| 4. Consórcio via PU | ⚠️ modelo pronto | `Cultivo.consorciado` + `cultivo_areas` — falta apenas PU sintetizar |
| 5. Avanço de fase com gates | ✅ | `SAFRA_TRANSICOES` já funciona |

---

## 4. Migrations Alembic propostas (não destrutivas)

```
step14_measurements_uom.py              # UOM + conversões
step15_production_units.py              # tabela nova + backfill de cultivo_areas
step16_add_pu_fk_operations.py          # operacoes_agricolas.production_unit_id NULL
step17_operation_executions.py          # tabela nova; preserva custo_total agregado
step18_inventory_movements_ledger.py    # tabela nova (não existe estoque legacy)
step19_cost_allocations.py              # FK opcional para fin_rateios
step20_scenarios.py                     # cenários de planejamento
```

Nenhuma remove coluna/tabela. `SafraTalhao`, `cultivo_areas`, `fin_rateios` permanecem intactos.

---

## 5. Resumo executivo

- **Base já está madura:** `Safra → Cultivo → CultivoArea → AreaRural` cobre 80% da modelagem requerida para PU.
- **PU é projeção aditiva:** pode ser backfillado sem risco a partir de `cultivo_areas`.
- **Gaps bloqueantes reais:** `OperationExecution`, `InventoryMovement`, `Measurement Engine`, `Scenario`. Sem eles, 3 dos 5 critérios de aceite falham.
- **Sem mudanças destrutivas:** todas as FKs novas são nullable; tabelas legadas viram fontes secundárias/compat.
- **Maior esforço real** está em ledger de estoque + measurement + execução parcial — **não** em introduzir a tabela PU em si.
