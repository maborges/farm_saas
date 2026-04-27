# Análise Arquitetural — Concorrência em `participation_percent` (Consórcios)

**Data:** 2026-04-24
**Base:** [schema-diff-production-unit.md](./schema-diff-production-unit.md) — ponto de atenção #3
**Escopo:** Garantir que `SUM(participation_percent)` por `(tenant_id, safra_id, area_id)` nunca exceda 100 sob concorrência, sem depender apenas de service + job noturno.

**Stack:** FastAPI (async) + SQLAlchemy 2.0 async + asyncpg + PostgreSQL 14+.

---

## 1. O problema

### 1.1 Natureza da invariante

- Regra: `SUM(participation_percent) WHERE tenant_id=? AND safra_id=? AND area_id=? ≤ 100.00`
- É uma **invariante multi-linha**. PG não suporta `CHECK` multi-linha declarativo.
- Casos típicos:
  - **Consórcio** (ex: café + banana na mesma área) — 2+ PUs no mesmo talhão.
  - **Rotação parcial** dentro da safra — PUs com períodos diferentes, mas mesma janela lógica.

### 1.2 Janela de corrida (exemplo)

```
T1: BEGIN; SELECT SUM = 70; validar insert 30 → passa; INSERT 30;
T2: BEGIN;                  SELECT SUM = 70; validar insert 40 → passa; INSERT 40;
T1: COMMIT;  (total = 100)
T2: COMMIT;  (total = 140)  ❌ invariante quebrada
```

Isolamento default PG (`READ COMMITTED`) **não** detecta — os `SELECT SUM` enxergam apenas commits anteriores.

`SERIALIZABLE` detectaria via anomalia de serialização (`serialization_failure`), mas custo alto em throughput global e requer retry loop em todas as transações — **descartado** como solução única.

---

## 2. Opções técnicas

### 2.1 Opção A — `SELECT ... FOR UPDATE` (lock pessimista de linha)

**Mecânica:**
```
BEGIN;
SELECT id FROM production_units
  WHERE tenant_id=? AND safra_id=? AND area_id=?
  FOR UPDATE;          -- bloqueia as linhas existentes
-- valida SUM + novo percent ≤ 100
INSERT INTO production_units (..., participation_percent=?);
COMMIT;
```

**Problema clássico:** `FOR UPDATE` bloqueia apenas **linhas existentes**. Não impede T2 de inserir uma **nova** linha em paralelo (phantom insert). Duas sessões inserindo o primeiro PU num talhão vazio **ambas** passam pelo `SELECT` retornando 0 linhas.

**Mitigação: lock na linha-pai** (`areas_rurais` ou `safras`):
```
SELECT id FROM cadastros_areas_rurais WHERE id=? FOR UPDATE;
-- agora a área está travada; qualquer outra transação que tentar
-- o mesmo lock espera
SELECT SUM(participation_percent) FROM production_units WHERE ...;
INSERT ...;
COMMIT;
```

| Aspecto | Avaliação |
|---|---|
| Integridade | ✅ Forte, se o lock for na linha-pai correta |
| Concorrência | ⚠️ Serializa **toda** escrita para a mesma `(safra, area)` — aceitável (raro) |
| Implementação | ⚠️ Média — requer disciplina (todo código de write precisa chamar) |
| Risco operacional | ⚠️ Lock em `areas_rurais` afeta operações não-relacionadas ao consórcio |
| Multiusuário | ✅ Garantido; transações enfileiram |
| Performance | ✅ Irrelevante (operação rara, não hot path) |
| FastAPI + SQLAlchemy | ✅ Nativo: `select(AreaRural).where(...).with_for_update()` |

**Variante melhor:** lock na linha `safras` (contexto mais natural para mutações de PU). Ainda cruza com outras escritas de safra — pode gerar contenção em operações de listagem/atualização. **Não ideal.**

**Variante ótima:** lock em linha sintética (ver advisory locks abaixo).

---

### 2.2 Opção B — Optimistic Locking com versionamento

**Mecânica:**
- Adicionar `version` em `production_units` (ou em `safras`/`cultivo_areas`).
- Cada update carrega `WHERE id=? AND version=?`; se 0 linhas afetadas → conflito → retry.

**Problema para este caso:** optimistic locking é projetado para **update de linha única**, não para **invariantes multi-linha**. Para garantir soma ≤ 100, seria necessário versionar um **agregado** (ex: uma linha `area_consortium_state(area_id, version)` que conta PUs):

```
T1 lê area_state (version=5) + SUM; calcula novo; INSERT PU; UPDATE area_state SET version=6 WHERE version=5;
T2 lê area_state (version=5) + SUM; calcula novo; INSERT PU; UPDATE area_state SET version=6 WHERE version=5; → 0 rows → retry
```

| Aspecto | Avaliação |
|---|---|
| Integridade | ✅ Correto **se** implementado com aggregate marker |
| Concorrência | ✅ Ótima — apenas transações conflitantes pagam o custo |
| Implementação | ❌ Alta — requer nova tabela agregada + disciplina em todo write path |
| Risco operacional | ⚠️ Retry logic não-trivial em async; falha silenciosa se esquecido |
| Multiusuário | ⚠️ Usuário pode ver "conflito, tente novamente" — UX ruim para ação rara |
| Performance | ✅ Excelente em carga baixa, degrada sob alta contenção |
| FastAPI + SQLAlchemy | ⚠️ SQLAlchemy tem `version_id_col` mas para linha única; agregado é manual |

**Veredito:** over-engineering. Mutação de PU em consórcio é operação **rara** (ocorre durante planejamento inicial da safra, com baixíssima concorrência real). Custo de implementação não compensa.

---

### 2.3 Opção C — PostgreSQL Advisory Locks

**Mecânica:**
PG fornece `pg_advisory_xact_lock(key)` — locks nomeados no nível de transação, não atrelados a linhas. Liberados automaticamente no COMMIT/ROLLBACK.

```
BEGIN;
SELECT pg_advisory_xact_lock(
  hashtextextended('pu_area:' || :tenant_id || ':' || :safra_id || ':' || :area_id, 0)
);
-- lock exclusivo para esta (tenant, safra, area); outras transações com mesma key esperam
SELECT SUM(participation_percent) FROM production_units WHERE ...;
-- valida
INSERT INTO production_units (...);
COMMIT;  -- lock liberado automaticamente
```

**Propriedades:**
- Lock é puramente lógico (não trava nenhuma tabela/linha).
- Chave é um `bigint` — derivada de hash de string composta.
- `xact_lock` evita vazamento (lock morre junto com a transação).
- Granularidade ideal: `(tenant, safra, area)` — dois consórcios em talhões diferentes não se bloqueiam.

| Aspecto | Avaliação |
|---|---|
| Integridade | ✅ Forte — serializa exatamente o escopo que precisa |
| Concorrência | ✅ Ótima — granularidade perfeita por (safra, area) |
| Implementação | ✅ Baixa — 1 linha antes da validação, em função helper |
| Risco operacional | ✅ Baixo — `xact_lock` limpa sozinho |
| Multiusuário | ✅ Transações enfileiram só dentro do mesmo escopo |
| Performance | ✅ Ótima — operação O(1) em memória PG |
| FastAPI + SQLAlchemy | ✅ `await session.execute(text("SELECT pg_advisory_xact_lock(...)"))` |

**Única ressalva:** colisão de hash em 64 bits é astronomicamente improvável (`2^64` espaço). Ainda assim, documentar a chave e usar `hashtextextended` (não o `hashtext` de 32 bits).

---

### 2.4 Comparativo síntese

| Critério | A: `FOR UPDATE` | B: Optimistic | C: Advisory Lock |
|---|---|---|---|
| Integridade multi-linha | ⚠️ só se lock na linha-pai | ✅ com agregado | ✅ |
| Granularidade | ⚠️ grossa (linha inteira) | ✅ | ✅ ótima |
| Complexidade | Média | Alta | Baixa |
| Retry na aplicação | Não | Sim | Não |
| UX em conflito | Espera silenciosa | "Tente novamente" | Espera silenciosa |
| Performance sob contenção | OK | Degrada | OK |
| Risco de deadlock | ⚠️ médio | Baixo | ✅ Baixo (ordem de locks previsível) |

---

## 3. Recomendação final

### 3.1 Mecanismo preferencial: **Advisory Lock (Opção C)**

**Justificativa:**
1. Granularidade exata do escopo da invariante (`tenant_id, safra_id, area_id`).
2. Não contende com outras escritas (operações, romaneios, tarefas) na mesma safra ou área.
3. Implementação trivial — função helper `async with pu_lock(session, tenant_id, safra_id, area_id):`
4. Sem retry, sem nova tabela, sem SERIALIZABLE global.
5. Combina bem com trigger de validação (defense-in-depth).

### 3.2 Defesa em profundidade (camadas)

**Camada 1 — Aplicação (service):**
```
async with production_unit_lock(tenant_id, safra_id, area_id):
    sum_atual = await _sum_participation(safra_id, area_id)
    if sum_atual + novo_percent > 100:
        raise BusinessRuleError(...)
    await session.add(pu); await session.flush()
```

**Camada 2 — Banco (trigger `AFTER INSERT OR UPDATE`):**
```
-- Função verifica SUM e RAISE EXCEPTION se > 100
-- Garante que mesmo uma transação que pule o advisory lock
-- (bug, script manual, migration) seja rejeitada
```

**Camada 3 — Job de consistência (noturno):**
- Detecta incoerências legadas (ex: arredondamento, migrations antigas).
- Gera relatório de PUs em status `INCONSISTENTE`.

---

## 4. Duas regras separadas (transacional × consistência)

**Sim — recomendado.** As regras têm semânticas e tolerâncias diferentes.

### 4.1 Regra transacional — gravação
- **Invariante:** `SUM(participation_percent) ≤ 100.00` sempre, em toda escrita.
- **Enforcement:** advisory lock + trigger AFTER.
- **Tolerância:** **zero**. Nenhum insert/update pode ultrapassar 100.
- **Motivação:** evita corromper dados. Parcial (soma < 100) é válido durante planejamento.

### 4.2 Regra de consistência — encerramento de safra
- **Invariante:** no gate `POS_COLHEITA → ENCERRADA`, toda área com PUs ativas deve ter `SUM(participation_percent) BETWEEN 99.99 AND 100.01` (tolerância de arredondamento).
- **Enforcement:** check no `SafraService.avancar_fase()` quando `nova_fase=ENCERRADA`.
- **Tolerância:** ±0,01 para absorver arredondamento de percentuais calculados a partir de `area_ha`.
- **Motivação:** safras incompletas (soma < 100) não podem fechar, mas não devem bloquear planejamento em andamento.

### 4.3 Por que duas regras?

| Regra | Quando | Tolerância | Bloqueio |
|---|---|---|---|
| Transacional | Cada write | 0 | Abortar transação |
| Consistência | Mudança de fase terminal | ±0,01 | Impedir avanço de fase |

Misturar as duas leva a bloqueio de planejamento legítimo (usuário criando consórcio incremental) ou permite safras encerradas com soma 97%.

---

## 5. Modelagem de status do consórcio

**Proposta: adicionar campo calculado (não persistido) ou coluna `consortium_status` em `cadastros_areas_rurais` atualizada via trigger/job.**

### 5.1 Estados propostos

| Status | Regra | Quando atribuir |
|---|---|---|
| **INCOMPLETO** | `SUM < 99.99` | PUs existem mas não preenchem a área |
| **VALIDO** | `SUM BETWEEN 99.99 AND 100.01` | Consórcio ok para encerramento |
| **INCONSISTENTE** | `SUM > 100.01` | Só acessível via bug/bypass; alerta operacional |
| **VAZIO** | sem PUs ativas | Área disponível para planejamento |

### 5.2 Utilidade

- **UX:** dashboard mostra áreas `INCOMPLETO` que exigem atenção antes de avançar fase.
- **Gate de fase:** `avancar_fase(ENCERRADA)` valida que todas as áreas com safra ativa estão `VALIDO`.
- **Alerta:** status `INCONSISTENTE` dispara alerta (não deveria existir se trigger funciona; indica bug).
- **Relatório:** job noturno reconcilia e reporta `INCONSISTENTE`.

### 5.3 Onde calcular

**Opção escolhida:** coluna materializada em `cadastros_areas_rurais.consortium_status` atualizada por trigger em `production_units AFTER INSERT/UPDATE/DELETE` para a área afetada.

**Alternativa descartada:** view computada (`CREATE VIEW`) — custo de reagregar em toda consulta; não permite índice eficiente no status.

**Alternativa descartada:** só calcular em runtime — gera N+1 em listagens.

### 5.4 Escopo temporal

O status é por `(area_id, safra_id)` — uma área pode estar `VALIDO` em 2024/25 e `INCOMPLETO` em 2025/26. Portanto:

- **Não** em `cadastros_areas_rurais` diretamente.
- **Sim** em uma tabela/coluna derivada: `area_safra_status(tenant_id, area_id, safra_id, consortium_status, last_computed_at)` OU em `safra_talhoes` (ressuscitando uso legítimo do legado) OU em `production_units` agregado por trigger.

**Recomendação:** criar tabela derivada leve `area_consortium_status` no step15 (junto com PU), mantida por trigger. Separa agregado de fonte.

---

## 6. Decisão recomendada — síntese

1. **Advisory lock (Opção C)** como mecanismo de serialização em toda mutação de `production_units`, granulado por `(tenant_id, safra_id, area_id)`.
2. **Trigger AFTER INSERT/UPDATE** em `production_units` validando `SUM ≤ 100` por `(safra_id, area_id)` — defense in depth.
3. **Regra transacional** com tolerância zero (camadas 1+2).
4. **Regra de consistência** separada, aplicada no gate `avancar_fase(ENCERRADA)` com tolerância ±0,01.
5. **Status de consórcio** materializado em tabela derivada `area_consortium_status` com estados `VAZIO | INCOMPLETO | VALIDO | INCONSISTENTE`, atualizado por trigger.
6. **Job noturno** rodando apenas para detecção/relatório de `INCONSISTENTE` (não mais para validação — essa é transacional).

---

## 7. Impacto no schema-diff anterior

Alterações em `schema-diff-production-unit.md` para incorporar esta decisão:

- **Step 15** ganha:
  - Trigger `production_units_sum_check_fn()` + `tg_production_units_validate_sum`.
  - Tabela derivada `area_consortium_status` + trigger `tg_production_units_refresh_status`.
  - Coluna `status` em `production_units` já contempla (`ATIVA | ENCERRADA | CANCELADA`) — status de **consórcio** é da **área**, não da PU.

- **Step 15** **remove** da seção 15.2/15.3: "validar em service + job noturno de verificação". Substituído pela estratégia em camadas acima.

- **Service layer** (fora do schema) passa a usar helper `async with pu_lock(...)` antes de toda mutação.

---

## 8. Pontos ainda a definir (opcional)

- **Timeout do advisory lock:** PG não tem timeout nativo em `pg_advisory_xact_lock`. Se necessário, trocar por `pg_try_advisory_xact_lock` + retry com backoff. Não recomendado agora (contenção será mínima).
- **Deadlock entre PU + rateio financeiro:** improvável (rateio não locka PU); monitorar em staging.
- **Ordem dos locks quando múltiplas PUs são criadas na mesma transação:** adquirir advisory locks em ordem de `(safra_id, area_id)` ascendente para evitar deadlocks entre transações concorrentes.
