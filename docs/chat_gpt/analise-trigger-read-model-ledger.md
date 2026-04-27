# Análise Arquitetural — Trigger BEFORE/AFTER, Read Model e Ledger Imutável

**Data:** 2026-04-24
**Base:** [analise-concorrencia-participation-percent.md](./analise-concorrencia-participation-percent.md)
**Escopo:** 3 aprofundamentos antes das migrations.

---

# PARTE 1 — Trigger `BEFORE` vs `AFTER` na validação de soma

## 1.1 Mecânica de cada abordagem

### BEFORE INSERT/UPDATE
- Dispara **antes** da linha entrar na tabela.
- Pode ver `NEW` (linha candidata) mas **não** pode consultar a tabela incluindo `NEW`.
- Para validar soma: precisa calcular `SUM(existentes) + NEW.participation_percent`.

```
-- conceitual, sem código
CREATE TRIGGER BEFORE INSERT OR UPDATE
  novo_total := (SELECT SUM(p) FROM production_units WHERE ... AND id <> NEW.id) + NEW.p;
  IF novo_total > 100 THEN RAISE EXCEPTION;
```

### AFTER INSERT/UPDATE
- Dispara **após** a linha entrar (ainda dentro da transação, antes do COMMIT).
- A query `SELECT SUM(...)` **já enxerga** NEW.
- Mais simples de escrever.

```
-- conceitual
CREATE TRIGGER AFTER INSERT OR UPDATE
  total := (SELECT SUM(p) FROM production_units WHERE ...);
  IF total > 100 THEN RAISE EXCEPTION;
```

## 1.2 Comparativo

| Aspecto | BEFORE | AFTER |
|---|---|---|
| **Comportamento transacional** | Bloqueia inserção antes do `heap insert` | Insere, depois valida; erro aborta transação |
| **Rollback** | Sem rollback de linha (nem chegou a entrar) | Rollback da linha inserida + toda a transação |
| **Custo em caso de falha** | Baixo (nunca gravou) | Médio (gravou e reverteu — gera WAL, invalida cache de página) |
| **Visibilidade de `NEW` na query** | ❌ precisa `WHERE id <> NEW.id` + somar NEW manualmente | ✅ query natural inclui NEW |
| **Batch INSERT (multi-linha)** | Dispara **para cada linha** — validação incremental; pode rejeitar primeira linha válida isolada mas que somada quebra | Dispara **para cada linha**, mas pode usar `CONSTRAINT TRIGGER DEFERRABLE` |
| **Risco de inconsistência** | Nenhum — rejeição antes do dado persistir | Nenhum — rejeição aborta transação (mesmo resultado efetivo) |
| **Concorrência** | Idêntica (locks independem de BEFORE/AFTER; depende do advisory lock da Parte 1) | Idêntica |
| **Interação com advisory lock** | Lock adquirido antes → `SELECT SUM` dentro do trigger vê estado estável | Idem |
| **Deferrable (checagem em COMMIT)** | ❌ não suportado para BEFORE | ✅ `CONSTRAINT TRIGGER ... DEFERRABLE INITIALLY DEFERRED` |

## 1.3 Caso decisivo — múltiplas PUs criadas na mesma transação

Cenário: usuário cria consórcio com 3 PUs (60% + 30% + 10%) em uma única chamada de API/transação.

**BEFORE (não deferrable):**
- INSERT 60% → trigger: sum=0 + 60 = 60 ≤ 100 ✅
- INSERT 30% → trigger: sum=60 + 30 = 90 ≤ 100 ✅
- INSERT 10% → trigger: sum=90 + 10 = 100 ≤ 100 ✅
- OK.

**BEFORE com ordem invertida (ex: 60 + 50 + -10 via update):**
- INSERT 60% → 60 ✅
- INSERT 50% → 110 ❌ aborta
- Mesmo que UPDATE posterior corrigisse, trigger BEFORE já rejeitou.

**AFTER DEFERRABLE (validação no COMMIT):**
- INSERT 60%, 50%, UPDATE 50→40 → no COMMIT, SUM=100 ✅
- Permite **refatorações intermediárias** dentro da transação.

## 1.4 Recomendação

**Usar `CONSTRAINT TRIGGER AFTER INSERT OR UPDATE ... DEFERRABLE INITIALLY DEFERRED`.**

### Justificativa
1. **Semântica transacional correta:** a invariante é "no fim da transação, a soma é válida" — não "cada linha intermediária é válida".
2. **Permite edição em lote:** criar 3 PUs de consórcio em uma transação, ou reajustar percentuais, sem que a ordem importe.
3. **Custo extra em caso de falha é irrelevante** — consórcios são operação rara; otimizar o happy path.
4. **Query natural** — `SELECT SUM(...) WHERE ...` sem gymnastics de `id <> NEW.id`.
5. **Combina bem com advisory lock** — lock garante serialização, DEFERRABLE garante validação final.

### Quando NÃO usar DEFERRED
- Se a aplicação cria PUs uma a uma (separadas por `flush()`) e quiser feedback imediato em cada insert — nesse caso, trigger `IMMEDIATE` (default AFTER, não deferred). Mas a UX é pior para edição.
- **Escolha aqui:** `DEFERRABLE INITIALLY DEFERRED` — validação no COMMIT.

### Fallback imediato
Se for preciso um erro imediato (ex: form de UI em tempo real), a validação em **service layer** (com advisory lock) já dá. Trigger é defense-in-depth, não precisa ser imediato.

---

# PARTE 2 — `area_consortium_status` é read model?

## 2.1 Definição — fonte de verdade vs read model

| Característica | Fonte de verdade | Read model (projeção) |
|---|---|---|
| Pode ser reconstruído a partir de outra tabela? | ❌ Não | ✅ Sim |
| Mutações diretas (UI/API) permitidas? | ✅ Sim | ❌ Não (só via recomputar) |
| Usado em JOINs/consultas analíticas? | ✅ | ✅ |
| Perda = perda de dado | ✅ | ❌ (basta recomputar) |

## 2.2 Aplicando a `area_consortium_status`

- Reconstruível a partir de `SELECT SUM(participation_percent) FROM production_units GROUP BY (tenant_id, safra_id, area_id)` → **SIM**
- Mutação direta faz sentido? → **NÃO** (usuário não edita status; ele emerge da soma)
- Perda é catastrófica? → **NÃO** — job pode reconstruir

**Conclusão: É read model. Fonte de verdade é `production_units.participation_percent`.**

## 2.3 Implicações arquiteturais

### 2.3.1 Propriedades obrigatórias
1. **Determinística:** dada a mesma `production_units`, o status é único.
2. **Idempotente:** recomputar 100x resulta no mesmo estado.
3. **Auto-curável:** job de reconciliação pode reconstruir a tabela inteira a qualquer momento.
4. **Não é referenciada por FK de outras tabelas:** ninguém depende de `area_consortium_status.id` — só lê `status`.
5. **Sem UNIQUE de negócio além de `(tenant_id, safra_id, area_id)`:** é a chave natural do agregado.

### 2.3.2 Como manter atualizada
Duas formas válidas (escolher uma):

**(a) Trigger em `production_units`** — refresh síncrono na transação:
- ✅ Sempre consistente com fonte
- ⚠️ Overhead em cada mutação de PU
- Escolha natural para dado com baixa escrita (consórcios são raros)

**(b) Refresh assíncrono (job / event handler):**
- ✅ Zero overhead no write path
- ⚠️ Janela de staleness — status pode estar desatualizado por segundos/minutos
- Exige endpoint "reprocessar" para correções

**Recomendação:** **(a) trigger** — consórcios são operação rara, consistência imediata vale o custo. Job noturno existe apenas como safety net (detecta drift em caso de bug no trigger).

### 2.3.3 Checklist — está refletido no Step 15?

Revisando `schema-diff-production-unit.md` + análise da Parte 1:

| Item | Presente? | Ação |
|---|---|---|
| `area_consortium_status` marcado como read model/projeção | ⚠️ Implícito | **Explicitar** na descrição da tabela |
| Campo `last_computed_at` ou similar | ❌ | Adicionar para debug/observabilidade |
| Documentar que não recebe mutação direta | ❌ | Adicionar nota "Read model — não mutar diretamente" |
| Job de reconstrução total documentado | ⚠️ | Documentar como operação de recovery |
| Ausência de FKs apontando **para** esta tabela | ✅ | Manter (nada referencia status) |
| Trigger em `production_units` como fonte de atualização | ✅ | Confirmado |

**Atualização necessária no Step 15:**
- Renomear mentalmente a seção para "Read model derivado".
- Adicionar `last_computed_at TIMESTAMP NOT NULL DEFAULT now()`.
- Adicionar nota: *"Tabela é projeção de `production_units`. Não recebe writes diretos da aplicação. Pode ser truncada e reconstruída a qualquer momento via `SELECT ... GROUP BY`."*
- Documentar procedimento de rebuild (operação de runbook, não de schema).

## 2.4 Decisão final — Parte 2

✅ `area_consortium_status` **É read model** — fonte de verdade permanece `production_units.participation_percent`.

**Atualização a fazer no schema-diff:** explicitar natureza de projeção + adicionar `last_computed_at` + nota de não-mutação direta.

---

# PARTE 3 — Ledger imutável (`inventory_movements`)

## 3.1 O que é "append-only real"

Ledger append-only significa:
- **INSERT permitido** livremente.
- **UPDATE proibido** — exceção: campos metadata puros (ex: `observacoes` pode ser atualizável? decisão abaixo).
- **DELETE proibido** — exceção: nenhuma em operação normal.
- Correções ocorrem via **novo movimento** (compensatório), nunca edição.

### 3.1.1 Nível de rigor — espectro

| Nível | UPDATE | DELETE | Como se corrige |
|---|---|---|---|
| **Soft append-only** | Permitido em alguns campos (obs, tags) | Proibido | UPDATE em metadata; compensação em quantidade |
| **Hard append-only** | Proibido em todos os campos | Proibido | Sempre novo movimento |
| **WORM (write-once-read-many)** | Impossível | Impossível | Mesmo que hard, + à prova de superuser |

**Recomendação:** **Hard append-only** — simplifica invariante e auditoria. Observações pós-lançamento entram como movimento adicional tipo `NOTE` ou em tabela separada `inventory_movement_notes` se necessário. **WORM** (nível PG com replica/extension) é over-engineering para esta fase.

## 3.2 Mecânica de compensação — `adjustment_of` vs `reversed_by_id`

### 3.2.1 Semântica distinta

| Campo | Significado | Tipo de correção |
|---|---|---|
| **`reversed_by_id`** | "Este movimento foi cancelado por X" — auto-referência do movimento original para o reversor | Estorno total |
| **`adjustment_of`** | "Este movimento é um ajuste relativo a Y" — do ajuste apontando para o original | Ajuste parcial, correção de quantidade/custo |

**Exemplo de uso:**

```
-- Cenário: saída de 100 kg de semente para a PU X.
-- Dias depois, descobre-se que só foram 80 kg.

Opção A (reversão total + novo):
  mov_1: SAIDA 100 kg
  mov_2: DEVOLUCAO 100 kg (adjustment_of=mov_1)  ← estorna
  mov_3: SAIDA 80 kg

Opção B (ajuste parcial):
  mov_1: SAIDA 100 kg
  mov_2: DEVOLUCAO 20 kg (adjustment_of=mov_1)  ← corrige diferença
```

Cada um tem casos de uso. Um sistema maduro suporta ambos.

### 3.2.2 Necessidade de ambos?

**Sim**, mas com nomenclatura consolidada.

**Proposta de simplificação:** **um único campo `adjustment_of UUID FK→inventory_movements.id`** — representa "este movimento ajusta/compensa outro". O `movement_type` (`DEVOLUCAO`, `AJUSTE`) define a semântica.

| `movement_type` | `adjustment_of` | Semântica |
|---|---|---|
| ENTRADA | NULL | Compra, recebimento |
| SAIDA | NULL | Consumo |
| DEVOLUCAO | NOT NULL (aponta para SAIDA original) | Retorno de estoque |
| AJUSTE | NOT NULL (aponta para movimento corrigido) | Correção genérica |
| AJUSTE | NULL | Ajuste absoluto (ex: inventário físico) |
| OPENING_BALANCE | NULL | Saldo inicial |

### 3.2.3 `reversed_by_id` (no original) — remover?

O schema-diff atual tem `reversed_by_id` em `inventory_movements` (auto-referência do original para o reversor). É **redundante** com `adjustment_of` — pode ser derivado por query inversa.

**Decisão:** **remover `reversed_by_id`** e manter apenas `adjustment_of`. Buscar reversões é trivial:
```
SELECT * FROM inventory_movements WHERE adjustment_of = :mov_id;
```

Se performance de listagem de reversões for crítica, adicionar `IX (adjustment_of)`. Não justifica coluna dupla.

## 3.3 Trigger para bloquear UPDATE/DELETE

### 3.3.1 Abordagens

**(a) Código apenas:**
- Service layer nunca chama UPDATE/DELETE em `inventory_movements`.
- Risco: migration manual, script ad-hoc, bug em código novo.

**(b) Código + trigger:**
- `CREATE TRIGGER BEFORE UPDATE OR DELETE ON inventory_movements ... RAISE EXCEPTION 'ledger is append-only'`
- Proteção contra todo path que não seja `role=superuser` ou `SET session_replication_role = replica`.

**(c) Código + trigger + permissions (revogar DML ao role da app):**
- `REVOKE UPDATE, DELETE ON inventory_movements FROM app_role;`
- Dupla proteção: mesmo um trigger `DISABLE` manual ainda é bloqueado por permission.
- Para correção legítima (runbook de incidente), usa role elevado com justificativa em audit.

### 3.3.2 Trade-offs

| Abordagem | Integridade | Complexidade | Risco operacional | Recovery em incidente |
|---|---|---|---|---|
| (a) Código | Baixa — depende de disciplina | Mínima | Alto (bug silencioso) | Fácil (direto SQL) |
| (b) Código + trigger | Alta — DB bloqueia até superuser | Baixa | Baixo | Médio (SET session_replication_role=replica) |
| (c) + permissions | Máxima | Média (gerir roles) | Mínimo | Difícil (role elevado documentado) |

### 3.3.3 Recomendação

**(b) Código + trigger** — para a fase inicial.

### Justificativa
1. **Proteção forte:** trigger bloqueia até migrations accidental ou scripts ad-hoc. Superuser ainda consegue em emergência.
2. **Custo operacional baixo:** sem gestão de roles separados; não quebra workflow de dev.
3. **Recuperação razoável:** em incidente, `BEGIN; SET LOCAL session_replication_role = replica; -- fix -- COMMIT;` com audit.
4. **Evolui para (c):** quando a app tiver separation of concerns real (roles dedicados), adicionar REVOKE. Não precisa agora.

**(c) é prematuro hoje** — exige role `app_ledger_writer` distinto de `app_default`, gestão de secrets, etc. Adicionar quando houver compliance/SOX driver. Documentar como roadmap.

### 3.3.4 Campos tecnicamente atualizáveis

Dúvida: e se precisarmos corrigir `observacoes` depois? Resposta: **proibir todo UPDATE mesmo assim**. Anotações posteriores vão para `inventory_movement_notes(movement_id, note, created_at, created_by)` — tabela separada, append-only também, mas SEM as mesmas invariantes de saldo. Decisão mantém ledger puro.

## 3.4 `OPENING_BALANCE` — tipo de movimento para saldo inicial

### 3.4.1 Proposta

Adicionar `OPENING_BALANCE` ao enum `movement_type`:

| Campo | Valor |
|---|---|
| `movement_type` | `OPENING_BALANCE` |
| `qty` | Saldo inicial (sinal +) |
| `movement_date` | Data de corte da implantação (ex: 2026-05-01) |
| `source` | `MANUAL` |
| `unit_cost` | Custo unitário médio na data de corte |
| `adjustment_of` | NULL |
| `observacoes` | Referência ao inventário físico ou snapshot anterior |

### 3.4.2 Vantagens sobre `AJUSTE` genérico

| Critério | `AJUSTE` genérico | `OPENING_BALANCE` dedicado |
|---|---|---|
| Separação semântica | ❌ mistura com correções operacionais | ✅ distinto |
| Relatórios/dashboards | ❌ precisa filtro por data/observação | ✅ filtro natural |
| Auditoria | ❌ "era ajuste ou saldo?" | ✅ intenção clara |
| Reconciliação com contábil | ❌ | ✅ — saldo de abertura é conceito contábil |
| Backfill em migration | ❌ | ✅ — migration insere OPENING_BALANCE por produto/almoxarifado |

### 3.4.3 Regras específicas

- **Unicidade:** no máximo 1 `OPENING_BALANCE` por `(tenant_id, product_id, warehouse_id)`.
  - Enforcer: partial unique index `WHERE movement_type='OPENING_BALANCE'`.
- **Imutável:** cai na mesma regra de append-only — correção = novo movimento de `AJUSTE` referenciando o OPENING_BALANCE via `adjustment_of`.
- **Proibido após primeira operação:** idealmente, não permitir criar OPENING_BALANCE depois que já existe SAIDA/ENTRADA anterior. Enforce em service (regra de negócio, não estrutural).

### 3.4.4 Backfill no Step 18

**Decisão atualizada:** em vez de "sem backfill histórico / AJUSTE manual pós-deploy", usar:

- Step 18 cria a tabela vazia.
- **Runbook pós-deploy** (operação, não migration): para cada tenant com estoque legado, executar procedimento que:
  1. Lê estoque atual da fonte legada (módulo atual de estoque, se existir).
  2. Insere 1 `OPENING_BALANCE` por (produto, almoxarifado).
  3. Registra em tabela de auditoria o snapshot.
- Tenants sem estoque legado: começam com ledger vazio; primeiro movimento será `ENTRADA`.

**Alternativa (não recomendada):** migration de dados insere OPENING_BALANCE automaticamente — risco de inserir dado errado em produção sem revisão humana.

## 3.5 Recomendação final — Parte 3

### 3.5.1 Append-only
- **Hard append-only.**
- Sem UPDATE/DELETE permitidos em `inventory_movements`.
- Anotações posteriores em tabela separada `inventory_movement_notes` (se demandado).

### 3.5.2 Compensação
- **Um único campo `adjustment_of UUID FK self-ref`** — substitui `reversed_by_id`.
- Semântica definida pelo `movement_type` (`DEVOLUCAO`, `AJUSTE`).
- Índice `IX (adjustment_of) WHERE adjustment_of IS NOT NULL`.

### 3.5.3 Enforcement
- **Nível (b): Código + trigger** — `BEFORE UPDATE OR DELETE` com `RAISE EXCEPTION`.
- **Nível (c)** (permissions via REVOKE) fica no roadmap — aplicar quando houver role separation real.

### 3.5.4 `OPENING_BALANCE`
- **Adotar.**
- Partial unique index `(tenant_id, product_id, warehouse_id) WHERE movement_type='OPENING_BALANCE'`.
- Backfill via **runbook manual** pós-deploy, não via migration.
- Regra de negócio em service: bloquear criação de OPENING_BALANCE se já há outros movimentos anteriores.

### 3.5.5 Impacto no Step 18 do schema-diff

Mudanças:
- Adicionar `OPENING_BALANCE` ao enum/CHECK de `movement_type`.
- **Remover** coluna `reversed_by_id` — consolidar em `adjustment_of`.
- Adicionar trigger `tg_inventory_movements_append_only BEFORE UPDATE OR DELETE`.
- Adicionar partial unique index para OPENING_BALANCE único por produto/almoxarifado.
- Documentar runbook de saldo inicial como operação pós-deploy.
- Documentar recovery procedure (`SET session_replication_role = replica`) para incidentes.

---

# Síntese executiva

| Ponto | Decisão |
|---|---|
| **1. Trigger BEFORE vs AFTER** | `CONSTRAINT TRIGGER AFTER ... DEFERRABLE INITIALLY DEFERRED` — permite edição em lote |
| **2. `area_consortium_status`** | Confirmado como read model. Adicionar `last_computed_at` + nota de não-mutação |
| **3a. Append-only** | Hard (zero UPDATE/DELETE) |
| **3b. Compensação** | Único campo `adjustment_of` (remover `reversed_by_id`) |
| **3c. Enforcement** | Código + trigger (nível b); permissions no roadmap |
| **3d. OPENING_BALANCE** | Adotar; partial unique index; backfill via runbook |

## Pendências antes do DDL

- [ ] Atualizar `schema-diff-production-unit.md` Step 15 com read model explícito + `last_computed_at`
- [ ] Atualizar Step 15 com trigger `CONSTRAINT ... DEFERRABLE INITIALLY DEFERRED`
- [ ] Atualizar Step 18 removendo `reversed_by_id`, adicionando `OPENING_BALANCE`, trigger de imutabilidade, partial unique index
- [ ] Documentar runbook OPENING_BALANCE e recovery procedure do ledger
