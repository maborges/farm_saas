# Schema Diff Lógico — Steps 14 → 20 (Núcleo Operacional)

**Data:** 2026-04-24
**Base:** [gap-analysis-production-unit.md](./gap-analysis-production-unit.md)
**Nomenclatura:** [naming-convention-schema-diff.md](./naming-convention-schema-diff.md)
**Escopo:** Desenho lógico incremental. **Sem código Alembic.** Todas as FKs novas são **nullable**. Nenhuma mudança destrutiva.

**Convenções (aprovadas):**
- snake_case, tabelas em plural, FKs `<entidade_singular>_id`.
- Tabelas e campos de negócio em **pt-BR**; timestamps técnicos (`created_at`/`updated_at`) em inglês.
- **Exceção:** `production_units` (mantida em inglês) por colidir semanticamente com `unidades_produtivas` (= Fazenda). ProductionUnit é conceito de domínio — unidade econômica/operacional de apropriação. Justificativa documentada em `naming-convention-schema-diff.md`.
- Toda tabela nova tem: `id UUID PK`, `tenant_id UUID NOT NULL FK→tenants.id CASCADE`, `created_at`, `updated_at`.
- Índice `(tenant_id, ...)` em **toda** consulta — RLS defense-in-depth.
- `ondelete`: `CASCADE` para filhos diretos do tenant; `SET NULL` para FKs transversais opcionais.

**Mapeamento final de tabelas:**
- Step 14: `unidades_medida`, `unidades_medida_conversoes`
- Step 15: `production_units` (exceção), `status_consorcio_area`
- Step 17: `operacoes_execucoes`
- Step 18: `estoque_movimentos`
- Step 19: `custos_rateios`
- Step 20: `safra_cenarios`, `safra_cenarios_unidades`

---

## STEP 14 — Measurement Engine (`unidades_medida`)

**Motivação:** Pré-requisito para `estoque_movimentos` e `operacoes_execucoes`. Nunca salvar valor sem unidade.

### 14.1 Tabelas novas

#### `unidades_medida`
Unidades de medida canônicas do sistema.

| Coluna | Tipo | Nullable | Notas |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | **NULL** | NULL = unidade global (sistema); preenchido = customização do cliente |
| codigo | VARCHAR(16) | NOT NULL | Ex: `KG`, `SC60`, `L`, `HA`, `HR_MAQ` |
| nome | VARCHAR(80) | NOT NULL | Ex: "Saca 60kg" |
| dimensao | VARCHAR(24) | NOT NULL | `massa`, `volume`, `area`, `tempo`, `contagem`, `moeda`, `hora_maquina`, `hora_homem` |
| codigo_canonico | VARCHAR(16) | NOT NULL | Unidade canônica da dimensão (ex: `massa → KG`) |
| fator_canonico | NUMERIC(18,9) | NOT NULL | Multiplicador p/ canônica (ex: `SC60 → 60.000000000`) |
| sistema | BOOLEAN | NOT NULL default `false` | `true` em registros seed de sistema |
| ativo | BOOLEAN | NOT NULL default `true` | |
| casas_decimais | SMALLINT | NOT NULL default `2` | Precisão de **apresentação** (UI/máscaras). **Não substitui a precisão de cálculo (NUMERIC).** Cálculos internos usam o precision/scale das colunas NUMERIC. |
| eh_canonica | BOOLEAN | NOT NULL default `false` | Marca explícita da unidade canônica da dimensão. Só `true` quando `codigo=codigo_canonico` e `fator_canonico=1` (CHECK garante). |
| created_at, updated_at | TIMESTAMP | NOT NULL | |

**Unique (partial, PG nativo):**
- `uq_unidades_medida_codigo_global ON (codigo) WHERE tenant_id IS NULL` — código único globalmente
- `uq_unidades_medida_codigo_tenant ON (tenant_id, codigo) WHERE tenant_id IS NOT NULL` — código único por tenant
- `uq_unidades_medida_canonica_global ON (dimensao) WHERE eh_canonica = true AND tenant_id IS NULL` — 1 canônica global por dimensão
- `uq_unidades_medida_canonica_tenant ON (tenant_id, dimensao) WHERE eh_canonica = true AND tenant_id IS NOT NULL` — 1 canônica por tenant por dimensão

**Check:**
- `ck_unidades_medida_fator_canonico_positivo CHECK (fator_canonico > 0)`
- `ck_unidades_medida_dimensao CHECK (dimensao IN ('massa','volume','area','tempo','contagem','moeda','hora_maquina','hora_homem'))`
- `ck_unidades_medida_casas_decimais_range CHECK (casas_decimais BETWEEN 0 AND 9)`
- `ck_unidades_medida_canonica_coerencia CHECK ((eh_canonica = false) OR (codigo = codigo_canonico AND fator_canonico = 1))` — flag só é true quando dados são de fato canônicos

**Índices:**
- `ix_unidades_medida_dimensao ON (dimensao)`
- `ix_unidades_medida_tenant_ativo ON (tenant_id, ativo)`

> **Nota:** `casas_decimais` representa precisão de apresentação e **não substitui** a precisão de cálculo (NUMERIC). Operações aritméticas (soma, rateio, conversão) preservam toda a precisão de `NUMERIC(18,9)` do `fator_canonico` e dos valores monetários/quantidade; `casas_decimais` orienta apenas máscaras de entrada e formatação de saída na UI.

---

#### `unidades_medida_conversoes`
Conversões não-lineares ou por cultura (ex: m³ granel vs tonelada para grão com densidade variável).

| Coluna | Tipo | Nullable | Notas |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | **NULL** | NULL = conversão de sistema |
| unidade_origem_id | UUID | NOT NULL FK→`unidades_medida.id` RESTRICT | |
| unidade_destino_id | UUID | NOT NULL FK→`unidades_medida.id` RESTRICT | |
| cultura | VARCHAR(50) | NULL | Ex: "CAFE", "SOJA" |
| commodity_id | UUID | NULL FK→`cadastros_commodities.id` SET NULL | Mais granular que cultura |
| fator | NUMERIC(18,9) | NOT NULL | |
| percentual_tolerancia | NUMERIC(5,2) | NULL | |
| created_at | TIMESTAMP | NOT NULL | |

**Unique (expression index para tratar NULLs):**
- `UQ_unidades_medida_conversoes ON (COALESCE(tenant_id, uuid_nil()), unidade_origem_id, unidade_destino_id, COALESCE(cultura,''), COALESCE(commodity_id, uuid_nil()))`

**Check:**
- `CK_unidades_medida_conversoes_fator_positivo CHECK (fator > 0)`
- `CK_unidades_medida_conversoes_unidades_distintas CHECK (unidade_origem_id <> unidade_destino_id)`

**Índices:**
- `IX_unidades_medida_conversoes_origem_destino ON (tenant_id, unidade_origem_id, unidade_destino_id)`
- `IX_unidades_medida_conversoes_cultura ON (cultura)`

### 14.2 Seed (migration)

Registros `sistema=true`, `tenant_id=NULL`:

| codigo | dimensao | codigo_canonico | fator_canonico | casas_decimais | eh_canonica |
|---|---|---|---|---|---|
| KG | massa | KG | 1.000000000 | 2 | ✅ |
| G | massa | KG | 0.001000000 | 3 | |
| TON | massa | KG | 1000.000000000 | 4 | |
| SC60 | massa | KG | 60.000000000 | 2 | |
| SC50 | massa | KG | 50.000000000 | 2 | |
| L | volume | L | 1.000000000 | 2 | ✅ |
| ML | volume | L | 0.001000000 | 3 | |
| M3 | volume | L | 1000.000000000 | 4 | |
| HA | area | HA | 1.000000000 | 2 | ✅ |
| M2 | area | HA | 0.000100000 | 0 | |
| HR_MAQ | hora_maquina | HR_MAQ | 1.000000000 | 2 | ✅ |
| HR_HOMEM | hora_homem | HR_HOMEM | 1.000000000 | 2 | ✅ |
| UN | contagem | UN | 1.000000000 | 0 | ✅ |
| BRL | moeda | BRL | 1.000000000 | 2 | ✅ |

Tabela `unidades_medida_conversoes` é criada **vazia**. Conversões lineares entre unidades da mesma dimensão são derivadas do `fator_canonico`. Conversões especiais (densidade de grão, umidade, etc.) entram conforme demanda via tabela de conversões.

### 14.3 Compatibilidade

- **Zero impacto** em tabelas existentes neste step.
- Módulos legados continuam gravando `Numeric` livre.
- Adoção gradual: FKs `unidade_medida_id` introduzidas nos steps 17 e 18.

---

## STEP 15 — `production_units` (+ backfill)

**Motivação:** Centro de custo agrícola canônico. ProductionUnit é **entidade de primeira classe** — unidade econômica/operacional de apropriação (centro de custo, execução, produção e análise) no cruzamento Safra × Cultivo × AreaRural. Não é projeção derivada; nasce por backfill inicial e depois disso é criada/mantida via API própria.

**Decisões aprovadas (ver `step15-desenho-conceitual.md`):**
- Unicidade: partial unique `WHERE status <> 'CANCELADA'` — permite recriação após cancelamento.
- `area_ha`: **snapshot** da safra; preserva histórico mesmo se AreaRural mudar.
- Criação: backfill inicial + API manual + sync via service (sem trigger DB).
- `status_consorcio_area`: **read model + gate seletivo** (mutação em INCONSISTENTE; transição ENCERRADA).
- **PU é** o centro de custo agrícola canônico — sem tabela `centros_custo` externa.
- Rateio (default `AREA_HA`) é responsabilidade do Step 19, não da PU.

### 15.1 Tabela nova

#### `production_units` (mantida em inglês — exceção documentada)

| Coluna | Tipo | Nullable | Notas |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | NOT NULL FK→`tenants.id` CASCADE | |
| safra_id | UUID | NOT NULL FK→`safras.id` CASCADE | |
| cultivo_id | UUID | NOT NULL FK→`cultivos.id` CASCADE | |
| area_id | UUID | NOT NULL FK→`cadastros_areas_rurais.id` CASCADE | |
| cultivo_area_id | UUID | **NULL** FK→`cultivo_areas.id` SET NULL | Rastreia origem quando a PU nasce via backfill ou sync de CultivoArea; permite dessincronizar sem quebrar |
| percentual_participacao | NUMERIC(5,2) | NOT NULL default `100.00` | Consórcio: soma por (safra, area) deve ser ≤ 100 (enforcement em advisory lock + CONSTRAINT TRIGGER DEFERRED — ver 15.3) |
| area_ha | NUMERIC(12,4) | NOT NULL | **Snapshot da safra** — área efetiva no momento da criação. Não recalcula se `cadastros_areas_rurais.area_ha` mudar depois. Preserva histórico contábil/produtivo. |
| status | VARCHAR(20) | NOT NULL default `ATIVA` | `ATIVA`, `ENCERRADA`, `CANCELADA` |
| data_inicio | DATE | NULL | Informativo — não integra a chave unique |
| data_fim | DATE | NULL | Informativo |
| created_at, updated_at | TIMESTAMPTZ | NOT NULL | |

**Unique (partial, PG nativo):**
- `uq_production_units_ativa ON (tenant_id, safra_id, cultivo_id, area_id) WHERE status <> 'CANCELADA'` — 1 PU ativa/encerrada por cruzamento. PU cancelada preserva histórico e não bloqueia recriação.

**Check:**
- `ck_production_units_percentual_participacao CHECK (percentual_participacao > 0 AND percentual_participacao <= 100)`
- `ck_production_units_area_ha_positiva CHECK (area_ha > 0)`
- `ck_production_units_status CHECK (status IN ('ATIVA','ENCERRADA','CANCELADA'))`
- `ck_production_units_datas_ordenadas CHECK (data_fim IS NULL OR data_inicio IS NULL OR data_fim >= data_inicio)`

**Índices:**
- `ix_production_units_tenant_safra ON (tenant_id, safra_id)` — listagem por safra
- `ix_production_units_tenant_cultivo ON (tenant_id, cultivo_id)`
- `ix_production_units_tenant_area ON (tenant_id, area_id)` — "o que está plantado neste talhão?"
- `ix_production_units_tenant_status ON (tenant_id, status)`
- `ix_production_units_cultivo_area ON (cultivo_area_id) WHERE cultivo_area_id IS NOT NULL` — rastreio de origem

**Semântica de `area_ha` (snapshot):**
- Definido no momento da criação como `AreaRural.area_ha × (percentual_participacao / 100)` (ou valor customizado pelo operador).
- Validação em service: `area_ha ≤ AreaRural.area_ha × (percentual_participacao / 100) × 1.01` (tolerância 1% para arredondamento/erro GPS menor).
- Se `AreaRural.area_ha` for corrigido após criação: PU **não altera**. View opcional `v_production_units_divergencia_area` pode listar divergências > tolerância para reconciliação manual (fora do escopo do step15).

**Semântica de criação (first-class):**
- **Backfill (executado uma vez na migration):** converte cada linha de `cultivo_areas` em 1 PU. Bootstrap inicial.
- **Após o step15:** PUs são criadas via `ProductionUnitService.criar(...)` — camada canônica. Consórcio = N PUs para mesma `(safra, area)` com cultivos distintos.
- **Sync com CultivoArea:** quando CultivoArea é criada/atualizada/deletada via fluxo UI legacy, o service `ProductionUnitService.syncFromCultivoArea()` é chamado **explicitamente na mesma transação**. Nenhum trigger DB.
- **Gate de integridade:** `ProductionUnitService.criar/atualizar` consulta `status_consorcio_area` da `(safra, area)` alvo; se status = `INCONSISTENTE`, recusa mutação até reconciliação manual (ver 15.2).

### 15.2 Read model + gate seletivo — `status_consorcio_area`

**Natureza dupla:**
1. **Read model** de `production_units` — não é fonte de verdade. Fonte = `production_units.percentual_participacao`.
2. **Gate seletivo** — usado por duas regras de service (não bloqueia operações rotineiras):
   - **Gate 1:** `ProductionUnitService.criar()` e `.atualizar()` recusam mutação em área com `status='INCONSISTENTE'`.
   - **Gate 2:** `SafraService.avancar_fase(ENCERRADA)` rejeita safra que tenha qualquer área com `status != 'VALIDO'` (tolerância ±0,01).
   - Operações, romaneios, análises de solo e demais fluxos rotineiros **não** consultam este status.

#### `status_consorcio_area`

| Coluna | Tipo | Nullable | Notas |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | NOT NULL FK→`tenants.id` CASCADE | |
| safra_id | UUID | NOT NULL FK→`safras.id` CASCADE | |
| area_id | UUID | NOT NULL FK→`cadastros_areas_rurais.id` CASCADE | |
| soma_participacao | NUMERIC(6,2) | NOT NULL default `0` | Soma das PUs com status ∈ (ATIVA, ENCERRADA) |
| qtd_unidades | INTEGER | NOT NULL default `0` | Quantidade de PUs não-canceladas |
| status | VARCHAR(20) | NOT NULL | `VAZIO | INCOMPLETO | VALIDO | INCONSISTENTE` |
| calculado_em | TIMESTAMPTZ | NOT NULL default `now()` | Observabilidade do refresh |

**Unique:** `uq_status_consorcio_area (tenant_id, safra_id, area_id)` — chave natural do agregado.
**Check:** `ck_status_consorcio_area_status CHECK (status IN ('VAZIO','INCOMPLETO','VALIDO','INCONSISTENTE'))`.
**Índices:** `ix_status_consorcio_area_tenant_status ON (tenant_id, status)` — dashboards de incompletos/inconsistentes.

**Regras de transição de status (calculadas no trigger):**
- `qtd_unidades = 0` → `VAZIO`
- `soma_participacao < 99,99` → `INCOMPLETO`
- `99,99 ≤ soma_participacao ≤ 100,01` → `VALIDO`
- `soma_participacao > 100,01` → `INCONSISTENTE`

**Regras operacionais:**
- **Não recebe writes diretos** da aplicação — apenas o trigger `tg_production_units_refresh_status` pode escrever.
- **Nenhuma FK externa aponta para esta tabela** — nada depende dela como chave; é projeção pura.
- **Rebuild total seguro a qualquer momento:** `TRUNCATE status_consorcio_area` + `INSERT ... SELECT SUM(percentual_participacao), COUNT(*), status_from_soma(...) FROM production_units WHERE status <> 'CANCELADA' GROUP BY (tenant_id, safra_id, area_id)` reconstrói o estado a partir da fonte.
- **Runbook de reconciliação:** procedimento manual de rebuild total documentado como operação de recovery (não de migration).

### 15.3 Validação transacional — Advisory Lock + Constraint Trigger DEFERRED

**Mecanismo de serialização (service layer):**
Toda mutação em `production_units` é envelopada por `pg_advisory_xact_lock(hashtextextended('pu_area:' || tenant_id || ':' || safra_id || ':' || area_id, 0))`. Granularidade perfeita por `(tenant_id, safra_id, area_id)` — não contende com outras escritas.

**Enforcement em banco (defense in depth):**
- **Constraint trigger** `tg_production_units_valida_soma` em `production_units`:
  - Tipo: `CREATE CONSTRAINT TRIGGER ... AFTER INSERT OR UPDATE ... DEFERRABLE INITIALLY DEFERRED`
  - Dispara no COMMIT (não linha-a-linha).
  - Função: `SELECT SUM(percentual_participacao)` por `(tenant_id, safra_id, area_id)` filtrando `status <> 'CANCELADA'`; `RAISE EXCEPTION` se > 100.
  - **Por que DEFERRED:** permite criar/editar múltiplas PUs na mesma transação (ex: consórcio 60+30+10) sem que a ordem intermediária quebre a invariante. Validação final é o que importa.
- **Trigger de refresh** `tg_production_units_refresh_status` em `production_units`:
  - Tipo: `AFTER INSERT OR UPDATE OR DELETE` (não deferrable).
  - Recomputa `status_consorcio_area` para `(tenant_id, safra_id, area_id)` afetado.
  - Atualiza `soma_participacao`, `qtd_unidades`, `status`, `calculado_em`.

**Regra de consistência (gate de fase) — separada:**
- No `SafraService.avancar_fase(ENCERRADA)`: toda área com PUs ativas deve ter `status_consorcio_area.status = 'VALIDO'` (equivalente a `soma_participacao BETWEEN 99.99 AND 100.01`).
- Tolerância de ±0,01 absorve arredondamento de percentuais calculados a partir de `area_ha`.
- Não bloqueia planejamento em andamento (soma < 100 é válida durante PLANEJADA → COLHEITA).

### 15.4 Backfill (idempotente, executado 1 vez no step15)

1. **`production_units`:** para cada linha de `cultivo_areas`:
   - Se `cultivo.consorciado = false`: inserir PU com `percentual_participacao = 100.00`, `area_ha = cultivo_areas.area_ha` (snapshot).
   - Se `cultivo.consorciado = true`: calcular proporção por `area_ha` em `(safra_id, area_id)` — `percentual = round(cultivo_areas.area_ha / SUM(area_ha) × 100, 2)`.
   - `cultivo_area_id` preenchido para rastrear origem.
   - `ON CONFLICT DO NOTHING` usa a partial unique `(tenant_id, safra_id, cultivo_id, area_id) WHERE status <> 'CANCELADA'`.
2. **`status_consorcio_area`:** popular após o passo 1, agregando `production_units`. Equivalente ao rebuild total descrito em 15.2.
3. **Triggers criadas antes do backfill** ficam `DISABLE`d durante `INSERT ... SELECT` em massa; reabilitadas após. Evita overhead de refresh por linha.
4. **Pós-backfill:** criação de novas PUs segue pelo `ProductionUnitService` — esta etapa de backfill **não** se repete.

### 15.5 Relação com `CultivoArea` após o step15

**PU é first-class — decisão aprovada (ponto 3 do desenho conceitual).**

- `cultivo_areas` permanece como **input-UI layer** no modal atual de criação de safra.
- Quando safra é criada/atualizada via fluxo UI legacy, `ProductionUnitService.syncFromCultivoArea(cultivo_area_id)` é invocado na **mesma transação** — sem trigger DB.
- PU também pode ser criada **diretamente via API** — sem CultivoArea correspondente (ex: parcelas experimentais, ajuste manual de consórcio). Nesse caso `cultivo_area_id = NULL`.
- Módulos novos (step16+) usam `ProductionUnitService.criar(...)` como caminho canônico, não CultivoArea.
- CultivoArea **não é fonte de verdade** de operações/custos/estoque — é camada de entrada. Fonte de verdade é PU.

### 15.6 Compatibilidade

- `cultivo_areas` permanece intacta — usada como camada de input UI e rastreada em `production_units.cultivo_area_id`.
- `production_units` é **centro de custo agrícola canônico** e **fonte de verdade** de participação/área efetiva da safra.
- `status_consorcio_area` é **read model + gate seletivo** — projeção agregada; rebuild seguro a qualquer momento.
- `SafraTalhao` (legado) intocado.
- **Rateio de custo não é propriedade da PU** — será tratado no Step 19 (`custos_rateios`) com default `AREA_HA` e override por operação.

---

## STEP 16 — FK opcional `production_unit_id` em tabelas de operação

**Motivação:** Permitir que operações/romaneios/tarefas referenciem PU sem remover FK para `cultivo_id`.

### 16.1 Colunas novas (todas nullable)

| Tabela | Coluna nova | FK | Nullable |
|---|---|---|---|
| `operacoes_agricolas` | `production_unit_id` | `production_units.id` SET NULL | SIM |
| `tarefas` | `production_unit_id` | `production_units.id` SET NULL | SIM |
| `romaneios` | `production_unit_id` | `production_units.id` SET NULL | SIM |
| `beneficiamento_lotes` (ou similar) | `production_unit_id` | `production_units.id` SET NULL | SIM |
| `a1_planejamento_*` (tabelas de orçamento) | `production_unit_id` | `production_units.id` SET NULL | SIM |
| `prescricoes_vra` (se aplicável) | `production_unit_id` | `production_units.id` SET NULL | SIM |
| `analises_solo` | `production_unit_id` | `production_units.id` SET NULL | SIM |

**Índices:** `IX (tenant_id, production_unit_id)` em cada tabela acima.

**Check:** Nenhum nesta etapa. Consistência `production_unit.cultivo_id == operacao.cultivo_id` é validada em **service layer**, não em CHECK (evita falhas em backfill parcial).

### 16.2 Backfill

- Preencher `production_unit_id` em registros históricos onde `cultivo_id IS NOT NULL AND safra_id IS NOT NULL`:
  - `UPDATE ... SET production_unit_id = (SELECT id FROM production_units WHERE tenant_id=..., safra_id=..., cultivo_id=..., area_id=...)`
  - Apenas para registros que tenham `area_id` resolvível (operações que têm `talhao_id` direto ou indireto)
- Registros ambíguos (sem `area_id`): deixam `production_unit_id = NULL` — resolução via serviço em leitura.

### 16.3 Compatibilidade

- Código legado que filtra por `cultivo_id` **não muda**.
- Novo código filtra por `production_unit_id` quando disponível, com fallback para `cultivo_id`.
- `ProductionUnitResolver` service retorna PU a partir de `(safra_id, cultivo_id, area_id)` quando FK não está preenchida.

---

## STEP 17 — `operation_executions` (execução parcial)

**Motivação:** Critério de aceite #2 — operação parcial com devolução. Hoje `operacoes_agricolas` é monolítica.

### 17.1 Tabela nova

#### `operation_executions`

| Coluna | Tipo | Nullable | Notas |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | NOT NULL CASCADE | |
| operation_id | UUID | NOT NULL FK→`operacoes_agricolas.id` CASCADE | |
| production_unit_id | UUID | **NULL** FK→`production_units.id` SET NULL | Execução pode ser rateada em multiple PUs (linha por PU) |
| execution_date | DATE | NOT NULL | |
| execution_time | TIME | NULL | |
| qty_planned | NUMERIC(18,6) | NULL | Para comparar planejado × real |
| qty_executed | NUMERIC(18,6) | NOT NULL | |
| qty_returned | NUMERIC(18,6) | NOT NULL default `0` | Devolução posterior (crítico p/ critério #2) |
| uom_id | UUID | NOT NULL FK→`uom_units.id` RESTRICT | Depende de step14 |
| actual_cost | NUMERIC(15,2) | NULL | Custo rateado desta execução |
| area_ha_executed | NUMERIC(12,4) | NULL | Área efetivamente trabalhada nesta execução |
| status | VARCHAR(20) | NOT NULL default `REALIZADA` | `REALIZADA`, `DEVOLVIDA`, `CANCELADA` |
| operator_id | UUID | NULL FK→`cadastros_pessoas.id` SET NULL | |
| observacoes | TEXT | NULL | |

**Unique:** Nenhum natural. Uma operação pode ter múltiplas execuções no mesmo dia em PUs diferentes.

**Check:**
- `CK qty_executed >= 0`
- `CK qty_returned >= 0`
- `CK qty_returned <= qty_executed`
- `CK status IN ('REALIZADA','DEVOLVIDA','CANCELADA')`

**Índices:**
- `IX (tenant_id, operation_id)` — listar execuções de uma operação
- `IX (tenant_id, production_unit_id, execution_date)` — "o que aconteceu nesta PU?"
- `IX (tenant_id, execution_date)`

### 17.2 Backfill

- Para cada `operacoes_agricolas` com `status='REALIZADA'`: criar 1 `operation_execution` com `qty_executed = <proxy>` (ex: area_ha ou custo_total com UOM `HA`), `execution_date = data` da operação.
- Operações com múltiplos talhões (via `safra_talhoes`): 1 execução por (operação, area) com `qty` proporcional ao `area_ha`.
- **Idempotência:** registrar `backfilled_from_operation_id` como coluna auxiliar? **Não** — usar migration com WHERE NOT EXISTS.

### 17.3 Compatibilidade

- `operacoes_agricolas.custo_total`, `status`, `fase_safra` **permanecem**. Viram **agregados derivados** de `operation_executions`.
- Durante transição: `custo_total` na tabela-mãe = SUM(`actual_cost`) das execuções. Service garante.
- Legado que lê `operacoes_agricolas` direto continua funcionando.

---

## STEP 18 — `inventory_movements` (ledger)

**Motivação:** Ledger imutável de estoque. Não há equivalente legado — é **tabela nova do zero**.

### 18.1 Tabela nova

#### `inventory_movements`

| Coluna | Tipo | Nullable | Notas |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | NOT NULL CASCADE | |
| movement_date | TIMESTAMP | NOT NULL default `now()` | |
| movement_type | VARCHAR(24) | NOT NULL | `OPENING_BALANCE`, `ENTRADA`, `SAIDA`, `DEVOLUCAO`, `AJUSTE`, `TRANSFERENCIA` |
| product_id | UUID | NOT NULL FK→`produtos.id` RESTRICT | |
| warehouse_id | UUID | NULL FK→`almoxarifados.id` SET NULL | |
| qty | NUMERIC(18,6) | NOT NULL | Sinal: positivo=entrada, negativo=saída |
| uom_id | UUID | NOT NULL FK→`uom_units.id` RESTRICT | |
| unit_cost | NUMERIC(15,6) | NULL | Custo unitário FIFO/médio |
| total_cost | NUMERIC(15,2) | NULL | qty * unit_cost |
| **source** | VARCHAR(32) | NOT NULL | `OPERATION_EXECUTION`, `PURCHASE`, `HARVEST`, `ADJUSTMENT`, `MANUAL` |
| source_id | UUID | NULL | ID polimórfico (FK lógica, não física) |
| operation_execution_id | UUID | NULL FK→`operation_executions.id` SET NULL | FK explícita quando origem é execução |
| production_unit_id | UUID | NULL FK→`production_units.id` SET NULL | Para movimentos ligados a PU |
| batch_number | VARCHAR(50) | NULL | Lote |
| adjustment_of | UUID | NULL FK→`inventory_movements.id` SET NULL | Auto-ref: este movimento ajusta/compensa outro (DEVOLUCAO, AJUSTE) |
| observacoes | TEXT | NULL | Somente escrita inicial; correções entram via `inventory_movement_notes` se necessário |

**Unique:**
- Partial unique index `UQ_inventory_movements_opening_balance ON (tenant_id, product_id, warehouse_id) WHERE movement_type='OPENING_BALANCE'` — no máximo 1 saldo de abertura por produto/almoxarifado por tenant.

**Check:**
- `CK qty <> 0`
- `CK movement_type IN ('OPENING_BALANCE','ENTRADA','SAIDA','DEVOLUCAO','AJUSTE','TRANSFERENCIA')`
- `CK source IN ('OPERATION_EXECUTION','PURCHASE','HARVEST','ADJUSTMENT','MANUAL')`
- `CK (source='OPERATION_EXECUTION' AND operation_execution_id IS NOT NULL) OR (source<>'OPERATION_EXECUTION')`
- `CK (movement_type IN ('DEVOLUCAO','AJUSTE') AND adjustment_of IS NOT NULL) OR (movement_type NOT IN ('DEVOLUCAO'))` — DEVOLUCAO sempre compensa; AJUSTE pode ser absoluto (NULL) ou relativo (FK)
- `CK (movement_type='OPENING_BALANCE' AND adjustment_of IS NULL)` — saldo inicial nunca é correção de outro

**Índices:**
- `IX (tenant_id, product_id, movement_date)` — saldo histórico
- `IX (tenant_id, warehouse_id, product_id)` — saldo por almoxarifado
- `IX (tenant_id, production_unit_id)` — consumo por PU
- `IX (tenant_id, source, source_id)` — rastreabilidade reversa
- `IX (operation_execution_id)` — conciliação com execuções
- `IX (adjustment_of) WHERE adjustment_of IS NOT NULL` — listar reversões/ajustes de um movimento original

### 18.2 Imutabilidade — Hard append-only

**Nível adotado:** código + trigger (nível b). Permissions via REVOKE fica no roadmap.

- **Trigger** `tg_inventory_movements_append_only`:
  - `CREATE TRIGGER BEFORE UPDATE OR DELETE ON inventory_movements FOR EACH ROW EXECUTE FUNCTION raise_ledger_immutable()`
  - Função levanta `RAISE EXCEPTION 'inventory_movements is append-only: use adjustment_of for corrections'`.
- **Regra de código:** service layer nunca chama UPDATE/DELETE. Correção = novo movimento com `movement_type IN ('DEVOLUCAO','AJUSTE')` e `adjustment_of` apontando para o original.
- **Recovery em incidente:** procedimento documentado via `SET LOCAL session_replication_role = replica` dentro de transação com justificativa em audit log. Runbook separado.

**Notas posteriores:** se surgir necessidade de anotar um movimento após criação, abrir tabela separada `inventory_movement_notes(movement_id, note, created_by, created_at)` — também append-only, sem efeito sobre saldo. Fora do escopo deste step; criar apenas se demanda aparecer.

### 18.3 Mecânica de compensação

| `movement_type` | `adjustment_of` | Semântica |
|---|---|---|
| `OPENING_BALANCE` | NULL | Saldo inicial de implantação |
| `ENTRADA` | NULL | Compra, recebimento, transferência entrada |
| `SAIDA` | NULL | Consumo, venda, transferência saída |
| `DEVOLUCAO` | NOT NULL → SAIDA original | Retorno total/parcial de estoque |
| `AJUSTE` | NULL ou FK | NULL = ajuste absoluto (inventário físico); FK = correção relativa a movimento específico |
| `TRANSFERENCIA` | NULL | Par de movimentos (saída origem + entrada destino) |

**Campo único `adjustment_of`** substitui conceitos redundantes (`reversed_by_id` removido). Reversões são consultadas via `SELECT * FROM inventory_movements WHERE adjustment_of = :id`.

### 18.4 Backfill — `OPENING_BALANCE` via runbook

- **Migration:** apenas DDL; tabela criada vazia.
- **Runbook pós-deploy** (operação manual, não automática):
  1. Para cada tenant com estoque legado, executar procedimento que lê saldo da fonte atual.
  2. Inserir 1 `OPENING_BALANCE` por `(product_id, warehouse_id)` com `unit_cost = custo médio na data de corte` e `observacoes = referência ao snapshot`.
  3. Registrar operação em audit log.
- **Regra de negócio (service):** bloquear criação de `OPENING_BALANCE` quando já existir qualquer movimento anterior para o mesmo `(product_id, warehouse_id)` — enforcement em service, não em DB (partial unique já impede duplicidade, mas não detecta "já houve movimento"; é regra temporal).
- Tenants sem estoque legado: começam com ledger vazio; primeiro movimento é `ENTRADA`.

### 18.5 Compatibilidade

- Zero impacto em tabelas legadas. Módulo `estoque` atual passa a **escrever** no ledger a partir de um flag de adoção por tenant.

---

## STEP 19 — `cost_allocations` (rateio por PU)

**Motivação:** Critério de aceite #3 — rateio multi-talhão. `fin_rateios` permanece como origem financeira.

### 19.1 Tabela nova

#### `cost_allocations`

| Coluna | Tipo | Nullable | Notas |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | NOT NULL CASCADE | |
| production_unit_id | UUID | NOT NULL FK→`production_units.id` CASCADE | |
| source | VARCHAR(32) | NOT NULL | `OPERATION_EXECUTION`, `INVENTORY_MOVEMENT`, `FIN_RATEIO`, `MANUAL` |
| source_id | UUID | NULL | FK lógica polimórfica |
| operation_execution_id | UUID | NULL FK→`operation_executions.id` SET NULL | |
| inventory_movement_id | UUID | NULL FK→`inventory_movements.id` SET NULL | |
| fin_rateio_id | UUID | NULL FK→`fin_rateios.id` SET NULL | Ponte p/ financeiro legado |
| cost_category | VARCHAR(32) | NOT NULL | `INSUMO`, `MAO_OBRA`, `MAQUINARIO`, `SERVICO`, `DESPESA_FINANCEIRA`, `OUTROS` |
| amount | NUMERIC(15,2) | NOT NULL | Valor alocado nesta PU |
| currency | VARCHAR(3) | NOT NULL default `BRL` | |
| allocation_date | DATE | NOT NULL | |
| allocation_method | VARCHAR(24) | NOT NULL default `DIRECT` | `DIRECT`, `PERCENTAGE`, `AREA_HA`, `YIELD_SC` |
| allocation_basis | NUMERIC(18,6) | NULL | Valor da base (ex: 12.5 HA) |

**Unique:** Nenhum (múltiplas alocações da mesma origem são válidas).

**Check:**
- `CK amount <> 0` — rateio zero não faz sentido
- `CK source IN (...)` (lista acima)
- `CK allocation_method IN ('DIRECT','PERCENTAGE','AREA_HA','YIELD_SC')`

**Índices:**
- `IX (tenant_id, production_unit_id, cost_category)` — custo por categoria por PU
- `IX (tenant_id, source, source_id)`
- `IX (tenant_id, allocation_date)`
- `IX (fin_rateio_id)` — reconciliação com financeiro

### 19.2 Backfill

1. **OperationExecution → CostAllocation:** para cada `operation_execution` com `actual_cost IS NOT NULL` e `production_unit_id IS NOT NULL`, criar 1 linha com `source='OPERATION_EXECUTION'`.
2. **Rateios financeiros existentes:** para cada linha de `fin_rateios` vinculável a uma safra/cultivo, criar `cost_allocations` com `source='FIN_RATEIO'`. Não-vinculáveis ficam fora (service cuida em tempo real daqui em diante).
3. Idempotência via `WHERE NOT EXISTS` baseado em `(source, source_id, production_unit_id)`.

### 19.3 Invariante

- Para uma origem `source_id`, **SUM(amount) por production_unit** não excede o valor total da origem.
- Validação em service layer (não em CHECK) — CHECK multi-linha não é viável em PG.

### 19.4 Compatibilidade

- `financeiro.fin_rateios` **permanece** como origem oficial de lançamentos financeiros.
- `cost_allocations` é a **visão agrícola** do custo por PU — **não substitui** o financeiro.
- Dashboards legados de `a1_planejamento` continuam consultando `fin_rateios` direto.

---

## STEP 20 — `scenarios` (cenários de planejamento)

**Motivação:** Simular variações de safra sem afetar dados reais.

### 20.1 Tabelas novas

#### `scenarios`

| Coluna | Tipo | Nullable | Notas |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | NOT NULL CASCADE | |
| safra_id | UUID | NOT NULL FK→`safras.id` CASCADE | Cenário sempre pertence a uma safra |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | NULL | |
| type | VARCHAR(24) | NOT NULL | `BASELINE`, `OTIMISTA`, `PESSIMISTA`, `CUSTOM` |
| is_active | BOOLEAN | NOT NULL default `false` | Apenas 1 `BASELINE` ativo por safra |
| created_by | UUID | NULL FK→`users.id` SET NULL | |
| parent_scenario_id | UUID | NULL FK→`scenarios.id` SET NULL | Para clonagem/versionamento |

**Unique:** `UQ (tenant_id, safra_id, name)` — nomes únicos por safra

**Check:** `CK type IN ('BASELINE','OTIMISTA','PESSIMISTA','CUSTOM')`

**Índice parcial (PostgreSQL):**
```
UQ scenarios_one_baseline_per_safra ON (tenant_id, safra_id)
   WHERE type='BASELINE' AND is_active=true
```

---

#### `scenario_production_units`
Override de parâmetros de PU dentro de um cenário.

| Coluna | Tipo | Nullable | Notas |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | NOT NULL CASCADE | |
| scenario_id | UUID | NOT NULL FK→`scenarios.id` CASCADE | |
| production_unit_id | UUID | NOT NULL FK→`production_units.id` CASCADE | |
| produtividade_meta_sc_ha | NUMERIC(8,2) | NULL | |
| preco_venda_previsto | NUMERIC(12,2) | NULL | |
| custo_previsto_ha | NUMERIC(12,2) | NULL | |
| area_ha_override | NUMERIC(12,4) | NULL | |

**Unique:** `UQ (scenario_id, production_unit_id)`

**Índices:** `IX (tenant_id, scenario_id)`

### 20.2 Backfill

- Para cada `safra` ativa: criar 1 cenário `BASELINE` com `is_active=true`, derivado dos valores atuais de `cultivos.produtividade_meta_sc_ha`, `cultivos.preco_venda_previsto`, etc.
- Idempotência: `WHERE NOT EXISTS (SELECT 1 FROM scenarios WHERE safra_id=? AND type='BASELINE')`.

### 20.3 Compatibilidade

- Campos atuais de `cultivos.produtividade_meta_sc_ha` etc. **permanecem**. Cenário BASELINE é **projeção**, não substitui.
- Módulo `a1_planejamento` pode escolher: ler do cultivo (legado) ou do scenario ativo (novo).

---

## Mapa consolidado de impactos

| Step | Tabelas novas | Colunas novas em legadas | FKs nullable | Backfill |
|---|---|---|---|---|
| 14 | `uom_units`, `uom_conversions` | — | — | Seed sistema |
| 15 | `production_units` | — | — | Derivado de `cultivo_areas` |
| 16 | — | `production_unit_id` em 7 tabelas | Sim | Resolve via (safra+cultivo+area) |
| 17 | `operation_executions` | — | — | 1 execução por `operacoes_agricolas` realizada |
| 18 | `inventory_movements` | — | — | Zero (saldo inicial manual) |
| 19 | `cost_allocations` | — | — | De `operation_executions` + `fin_rateios` |
| 20 | `scenarios`, `scenario_production_units` | — | — | 1 BASELINE por safra ativa |

**Total:** 9 tabelas novas, 7 FKs opcionais adicionadas em tabelas existentes, 0 colunas removidas, 0 tabelas removidas.

---

## Validação do desenho — pontos de atenção

**Stack de banco confirmada: PostgreSQL exclusivo.** Recursos nativos de PG (partial indexes, EXCLUDE constraints, triggers, expression indexes, deferred constraints) são usados sem ressalvas de portabilidade.

1. **Polimorfismo `source_id` em ledger/cost:** FK explícita (`operation_execution_id`, `inventory_movement_id`, `fin_rateio_id`) **além** de `source/source_id`, trocando polimorfismo puro por integridade referencial. FKs polimórficas puras são evitadas — PG não suporta nativamente.

2. **Ausência de triggers de sync `cultivo_areas ↔ production_units`:** coerência no service layer. Teste de integração **obrigatório** antes de mergear step15. Alternativa viável em PG: trigger `AFTER INSERT/UPDATE/DELETE ON cultivo_areas` chamando função `sync_production_unit()`. Decisão pendente de aprovação.

3. **`participation_percent` soma > 100 em consórcio:** resolvido em PG com **EXCLUDE constraint** + trigger ou via **deferred CHECK** com stored function. Opção recomendada:
   ```sql
   -- Função + trigger AFTER INSERT/UPDATE que consulta SUM por (tenant_id, safra_id, area_id)
   -- e levanta RAISE EXCEPTION se > 100
   ```
   Alternativa simples: validação em service layer + constraint `EXCLUDE USING gist` se período de ocupação entrar na chave.

4. **Ledger imutável (`inventory_movements`):** em PG, implementável via trigger `BEFORE UPDATE OR DELETE` com `RAISE EXCEPTION 'inventory_movements is append-only'`. **Recomendação:** incluir no step18 desde o início — custo zero e garante invariante a nível de banco.

5. **Unique global com `tenant_id NULL` (uom):** em PG, resolvido com **partial unique index**:
   ```sql
   CREATE UNIQUE INDEX uom_units_code_global ON uom_units (code) WHERE tenant_id IS NULL;
   CREATE UNIQUE INDEX uom_units_code_tenant ON uom_units (tenant_id, code) WHERE tenant_id IS NOT NULL;
   ```
   Sem necessidade de sentinel/COALESCE.

6. **`uom_id` NOT NULL em execução/movimento:** step14 precede — dependência garantida. `ON DELETE RESTRICT` protege contra apagar UOM em uso. UOM descontinuada usa `active=false` (não delete).

7. **Cenários — 1 BASELINE ativo por safra:** partial unique index nativo em PG:
   ```sql
   CREATE UNIQUE INDEX scenarios_one_baseline_per_safra
     ON scenarios (tenant_id, safra_id)
     WHERE type='BASELINE' AND is_active=true;
   ```
   Sem ressalvas.

### Decisões confirmadas após aprofundamentos

- **(2) Sync `cultivo_areas → production_units`:** sem trigger; service garante + teste de integração.
- **(3) Soma `participation_percent`:** advisory lock no service + `CONSTRAINT TRIGGER AFTER ... DEFERRABLE INITIALLY DEFERRED` em DB; `area_consortium_status` é read model com trigger de refresh; regra de consistência (tolerância ±0,01) aplicada no gate `avancar_fase(ENCERRADA)`.
- **(4) Imutabilidade do ledger:** incluída no step18 — trigger `BEFORE UPDATE OR DELETE` + campo único `adjustment_of` + `OPENING_BALANCE` com partial unique.

---

## Revisão de impactos finais (pré-DDL)

### A. Migration ordering — dependências entre steps

| Dependência | De | Para | Natureza |
|---|---|---|---|
| `uom_units.id` existir | step14 | step17 (`operation_executions.uom_id`) | Hard — FK NOT NULL |
| `uom_units.id` existir | step14 | step18 (`inventory_movements.uom_id`) | Hard — FK NOT NULL |
| `production_units.id` existir | step15 | step16 (FKs em tabelas legadas) | Hard — FK nullable, mas tabela precisa existir |
| `production_units.id` existir | step15 | step17 (`operation_executions.production_unit_id`) | Soft — FK nullable |
| `production_units.id` existir | step15 | step18 (`inventory_movements.production_unit_id`) | Soft — FK nullable |
| `operation_executions.id` existir | step17 | step18 (`inventory_movements.operation_execution_id`) | Soft — FK nullable |
| `operation_executions.id` existir | step17 | step19 (`cost_allocations.operation_execution_id`) | Soft — FK nullable |
| `inventory_movements.id` existir | step18 | step19 (`cost_allocations.inventory_movement_id`) | Soft — FK nullable |
| `fin_rateios.id` existir | (legado) | step19 (`cost_allocations.fin_rateio_id`) | Hard — FK existente no sistema |
| `safras.id`, `cultivos.id`, `cadastros_areas_rurais.id` | (legado) | step15 | Hard — FKs do core |
| `tenants.id` existir | (legado) | todos os steps | Hard — coluna `tenant_id` universal |

**Ordem obrigatória:** 14 → 15 → 16 → 17 → 18 → 19 → 20. **Nenhuma inversão válida.**

**Validação step15 ↔ step18:**
- Step 15 **não** depende de step 18.
- Step 18 depende de step 15 **e** step 17 (FKs nullable), portanto não pode rodar antes.
- Em ambiente novo (dev fresh), aplicar 14→20 sequencial; em ambientes com dados legados, mesma sequência — backfills idempotentes permitem replay.

**Downgrades:** intencionalmente não suportados (`downgrade()` vazio ou `RAISE` explícito). Reversão = restore de backup. Justificativa: triggers + read model + backfill de dados tornam downgrade automático perigoso.

### B. Test strategy — testes automatizados obrigatórios

#### B.1 Advisory lock (step15)

**Testes de integração com asyncpg (pytest-asyncio + duas sessões concorrentes):**

1. `test_advisory_lock_serializes_concurrent_pu_creation`
   - T1 e T2 tentam inserir PU simultâneo na mesma `(safra, area)`.
   - T2 deve bloquear até T1 commitar; se soma > 100, T2 falha.
2. `test_advisory_lock_does_not_block_different_areas`
   - T1 insere PU em area A; T2 insere em area B — ambos commitam em paralelo sem espera.
3. `test_advisory_lock_released_on_rollback`
   - T1 adquire lock e dá ROLLBACK; T2 deve prosseguir imediatamente.
4. `test_advisory_lock_key_collision_sanity`
   - Hash de chaves diferentes não colide em casos realistas (smoke test com 10k variações).

#### B.2 Constraint trigger DEFERRED (step15)

**Testes unitários de SQL (fixture de transação):**

5. `test_deferred_trigger_allows_intermediate_breach`
   - Na mesma transação: INSERT 60%, INSERT 50%, UPDATE 50→40; COMMIT → sucesso (soma final = 100).
6. `test_deferred_trigger_rejects_on_commit`
   - Transação com INSERT 60% + INSERT 50% sem correção; COMMIT → `RAISE EXCEPTION`, toda a transação aborta.
7. `test_deferred_trigger_fires_per_affected_area`
   - Transação afeta 2 áreas; erro numa não bloqueia validação da outra (erro é transacional — aborta tudo, mas teste valida que a verificação corre para todas).
8. `test_refresh_status_trigger_updates_read_model`
   - INSERT PU → `area_consortium_status` atualizado com `sum_participation`, `pu_count`, `status`, `last_computed_at`.
9. `test_read_model_rebuild_matches_trigger_state`
   - Estado após N mutações via trigger == estado após `TRUNCATE + INSERT ... SELECT GROUP BY`. Garante que rebuild é idempotente com o trigger.

#### B.3 Ledger imutável (step18)

10. `test_inventory_movements_reject_update`
    - INSERT movimento; UPDATE qualquer campo → `RAISE EXCEPTION`.
11. `test_inventory_movements_reject_delete`
    - INSERT movimento; DELETE → `RAISE EXCEPTION`.
12. `test_correction_via_adjustment_of_succeeds`
    - INSERT SAIDA; INSERT DEVOLUCAO com `adjustment_of=SAIDA.id` → aceito.
13. `test_devolucao_without_adjustment_of_rejected`
    - INSERT DEVOLUCAO com `adjustment_of=NULL` → CHECK viola.
14. `test_opening_balance_forbids_adjustment_of`
    - INSERT OPENING_BALANCE com `adjustment_of=X` → CHECK viola.
15. `test_recovery_session_replication_role_works`
    - Em contexto de runbook (role elevado ou `SET LOCAL session_replication_role = replica`), UPDATE é permitido. Guarda de regressão do escape hatch.

#### B.4 OPENING_BALANCE uniqueness (step18)

16. `test_opening_balance_unique_per_product_warehouse`
    - INSERT OPENING_BALANCE (tenant, prod_A, wh_1); segundo INSERT mesmo trio → partial unique viola.
17. `test_opening_balance_allowed_per_different_warehouse`
    - Mesmo produto, warehouses diferentes → ambos aceitos.
18. `test_opening_balance_service_blocks_if_movements_exist`
    - ENTRADA inserida; tentativa de service-layer de criar OPENING_BALANCE para mesmo `(product, warehouse)` → rejeitada pela regra de negócio (não DB).
19. `test_opening_balance_service_allowed_when_empty`
    - Sem movimentos prévios para `(product, warehouse)` → service permite OPENING_BALANCE.

#### B.5 Integração cross-step

20. `test_criterio_aceite_2_operacao_parcial_com_devolucao`
    - Critério de aceite #2 do doc mestre: operação parcial (operation_execution) com devolução (inventory_movement DEVOLUCAO). End-to-end.
21. `test_criterio_aceite_3_rateio_multi_talhao`
    - Operação em PU com cost_allocation para 2 PUs; soma não excede custo total. Critério #3.
22. `test_criterio_aceite_4_consorcio_via_pu`
    - Safra com 2 cultivos em mesma área (consórcio 60/40); sum_participation = 100; status = VALIDO. Critério #4.

#### B.6 Suíte mínima de regressão

- **20+ testes novos** antes de marcar step15–step20 como "done".
- `pytest tests/agricola/test_production_units_concurrency.py` deve rodar em CI com PG real (não SQLite).
- `pytest -k "ledger_immutable"` deve rodar em CI.

### C. Failure scenarios — como o modelo reage

| # | Cenário | Reação esperada | Observabilidade |
|---|---|---|---|
| 1 | **Deadlock em advisory lock** | Improvável — locks adquiridos em ordem de `(safra_id, area_id)` ASC na mesma transação. Se ocorrer: PG detecta e aborta 1 das transações com `deadlock_detected`; cliente recebe erro e pode retry. | `pg_stat_activity` + log nível ERROR |
| 2 | **Violação DEFERRED trigger no COMMIT** | Transação inteira aborta; todas as mutações (PUs, operações, etc. feitas na mesma transação) desfeitas. Cliente recebe exception no `session.commit()`. | Log com mensagem "SUM > 100 for (tenant, safra, area)" |
| 3 | **Tentativa de UPDATE em `inventory_movements`** | Trigger bloqueia com `RAISE EXCEPTION 'inventory_movements is append-only'`. Transação aborta. | Log ERROR + alerta (deve ser investigado — não deveria ocorrer via app) |
| 4 | **Tentativa de DELETE em `inventory_movements`** | Idem #3. | Idem |
| 5 | **Duplicidade de OPENING_BALANCE** | Partial unique index viola; `IntegrityError` com mensagem do constraint. Transação aborta. | Log no nível da aplicação |
| 6 | **OPENING_BALANCE depois de movimentos existentes** | Service layer bloqueia com `BusinessRuleError`. Não chega ao DB. | Log WARN + retorno 422 ao cliente |
| 7 | **Drift entre `production_units` e `area_consortium_status`** | Trigger de refresh falha silenciosa → read model desatualizado. Mitigação: job de reconciliação noturno faz rebuild via GROUP BY; compara com estado atual e reporta diferenças. | Dashboard de observabilidade + alerta se drift > 0 |
| 8 | **Sum > 100 por bypass (script manual ignorando lock)** | Trigger AFTER DEFERRED no COMMIT pega mesmo sem lock — segunda camada de defesa. Transação aborta. | Log ERROR + incidente |
| 9 | **Consórcio em POS_COLHEITA → ENCERRADA com soma < 99,99** | Service `SafraService.avancar_fase(ENCERRADA)` rejeita com `BusinessRuleError` listando áreas incompletas. | Erro 422 com detalhes |
| 10 | **Migração com trigger ativo em backfill massivo** | Performance degrada (refresh por linha). Mitigação: `ALTER TABLE ... DISABLE TRIGGER` antes do `INSERT ... SELECT`, reabilita depois, executa rebuild total de `area_consortium_status` uma vez. Documentado em 15.4. | Tempo de migration medido e logado |
| 11 | **DELETE CASCADE de `safras` → `production_units`** | Trigger AFTER DELETE em PUs dispara refresh de `area_consortium_status`. Cascade é transacional; status volta para `VAZIO`. | Sem incidente — comportamento esperado |
| 12 | **Rollback da transação de criação de safra com 3 PUs** | Advisory lock liberado (xact_lock), constraint trigger não dispara (não há COMMIT), read model não atualizado. Estado consistente. | Sem incidente |
| 13 | **`adjustment_of` apontando para movimento de tenant diferente** | Não é bloqueado estruturalmente (FK não valida tenant). Service layer valida `tenant_id` do original == do novo. | Log + rejeição 403 |
| 14 | **Concorrência entre DEVOLUCAO e outra SAIDA do mesmo produto** | Nenhum lock necessário — ledger é append-only, cada movimento independente. Saldo calculado por SUM no momento da consulta. | Sem incidente |

### D. Checklist final pré-DDL

- [x] `reversed_by_id` removido; `adjustment_of` consolidado
- [x] `OPENING_BALANCE` + partial unique definido
- [x] Trigger de imutabilidade documentado no step18
- [x] `area_consortium_status` marcado como read model com `last_computed_at`
- [x] `CONSTRAINT TRIGGER ... DEFERRABLE INITIALLY DEFERRED` documentado no step15
- [x] Advisory lock como camada de serialização documentada
- [x] Duas regras separadas (transacional vs gate de fase com tolerância ±0,01)
- [x] Runbook de OPENING_BALANCE documentado como operação manual
- [x] Test strategy (22 testes novos) enumerada
- [x] Failure scenarios (14 cenários) cobertos
- [x] Migration ordering validada (14→20 hard sequence, sem inversões)

**Próximo passo:** gerar DDLs Alembic `step14.py` → `step20.py`.

---

## Checklist de aprovação

- [ ] Todas as tabelas novas seguem convenção (`id UUID`, `tenant_id`, timestamps)
- [ ] Todas as FKs novas em tabelas existentes são nullable
- [ ] Nenhuma coluna/tabela é removida ou renomeada
- [ ] `cultivo_areas`, `safra_talhoes`, `fin_rateios`, `operacoes_agricolas` permanecem intactos
- [ ] Backfill idempotente em todos os steps com dados
- [ ] Índices cobrem padrões de consulta (por tenant, por PU, por safra)
- [ ] Check constraints não dependem de múltiplas linhas
- [ ] Impacto em compat explícito e mitigado em cada step

**Próximo passo sugerido:** gerar DDL Alembic (`step14.py` → `step20.py`) apenas após validação deste desenho.
