# Step 15 — Desenho Conceitual (6 decisões pré-DDL)

**Data:** 2026-04-24
**Escopo:** Análise arquitetural e recomendações para decisões-chave antes do DDL do Step 15. **Sem schema ainda.**
**Contexto:** Step 14 aprovado deploy-ready em staging. Prosseguir apenas com desenho revisado, considerando dependência de `unidades_medida.id`.

---

## 1. Cardinalidade e unicidade formal de `production_units`

### 1.1 Opções

| Chave natural | Implicação |
|---|---|
| (A) `(tenant_id, safra_id, cultivo_id, area_id)` | 1 PU por cruzamento; rotação intra-safra impossível; consórcio OK |
| (B) `(tenant_id, safra_id, cultivo_id, area_id, data_inicio)` | Permite rotação intra-safra (mesmo cultivo, mesma área, janelas diferentes) |
| (C) `(tenant_id, id)` sem unique de negócio — apenas PK | Flexibilidade total, risco de duplicação descontrolada |

### 1.2 Análise

- **Consórcio** (ex: café + banana na mesma área): 2 PUs com mesmo `(safra, area)` e `cultivo` diferente. **Opção A cobre.**
- **Rotação intra-safra** (ex: soja + milho safrinha no mesmo ano): no projeto atual, isso é modelado como **2 cultivos dentro da mesma safra** (não 2 ciclos do mesmo cultivo). **Opção A cobre.**
- **Cancelamento e recriação**: se cancelar PU e criar novo, o (safra, cultivo, area) colide. Precisa incluir `status` na unique? Não — `status=CANCELADA` não deveria bloquear recriação. Solução: **partial unique** `WHERE status <> 'CANCELADA'`.

### 1.3 Recomendação

**Opção A com partial unique:**

```
UNIQUE (tenant_id, safra_id, cultivo_id, area_id) WHERE status <> 'CANCELADA'
```

- PU canônico: 1 por cruzamento ativo.
- Cancelamento preserva histórico sem bloquear recriação.
- `data_inicio`/`data_fim` permanecem como campos informativos (não na chave).

---

## 2. Área efetiva: armazenada ou derivada

### 2.1 Opções

| Modelo | `area_ha` em PU |
|---|---|
| (A) Armazenada (snapshot no momento da criação) | Coluna NOT NULL |
| (B) Derivada em query (`AreaRural.area_ha × participation_percent/100`) | Coluna ausente; view/função |
| (C) Armazenada + CHECK de coerência com AreaRural | Requer trigger multi-tabela |

### 2.2 Análise — o que quebra com cada escolha

**Cenário crítico:** `AreaRural.area_ha` é corrigido após plantio (remedição GPS, regularização CAR).

- (A) PU preserva área do momento da safra. Custos/produtividade históricos intactos. ✅ Auditoria.
- (B) PU recalcula automaticamente. Relatórios retroativos mudam. ❌ Contabilidade/fechamento fiscal.
- (C) CHECK requer trigger (não CHECK declarativo). Complexidade alta; pouco ganho.

**Necessidades reais:**
- Custo por hectare: `SUM(custo) / area_ha` — precisa área fixa no momento do custo.
- Produtividade: `SUM(producao) / area_ha` — mesma lógica.
- Rateio proporcional: usa `area_ha` do PU diretamente.

### 2.3 Recomendação

**Opção A — `area_ha` armazenada como snapshot.**

- Semântica: "área efetiva daquela PU naquela safra". Invariante após encerramento.
- Validação de coerência em **service layer** (não DB): ao criar PU, service valida `area_ha <= AreaRural.area_ha × (participation_percent/100)` com tolerância ±0,01.
- Se AreaRural mudar depois: PU não altera — representa o que foi plantado.
- Para reconciliação opcional futura: view `v_production_units_divergencia` que mostra PUs cujo `area_ha` diverge do atual de AreaRural. Read model, não gate.

---

## 3. PU nasce apenas por backfill ou pode ser criada manualmente

### 3.1 Opções

| Fonte de criação | Implicação |
|---|---|
| (A) Apenas via `CultivoArea` (trigger ou service sync) | PU é projeção de CultivoArea; simplicidade |
| (B) Apenas via API própria de PU | PU é first-class; CultivoArea torna-se redundante |
| (C) Ambos: backfill + criação manual via API | PU é first-class; CultivoArea é input UI opcional |

### 3.2 Análise

- Doc mestre trata ProductionUnit como **conceito de domínio de primeira classe** (centro de custo, unidade de apropriação, execução). Não é "só uma projeção".
- `CultivoArea` hoje é a camada de entrada UI para o modal de criação de safra — continua útil, mas não é a única.
- Casos futuros que exigem PU manual:
  - Ajuste de `percentual_participacao` em consórcio (raramente igual a `area_ha` direto).
  - Divisão de área em sub-PUs por talhão virtual (meia-geada, parte irrigada vs sequeiro).
  - Plantios fora do fluxo `CultivoArea` (testes agronômicos, parcelas experimentais).

### 3.3 Recomendação

**Opção C — PU é first-class, aceita criação manual + backfill inicial + sync opcional.**

- **Backfill (step15):** converte `CultivoArea` existentes em PUs. Bootstrap único.
- **Depois do step15:**
  - Service `ProductionUnitService.criar(...)` é o caminho canônico.
  - Quando safra é criada com cultivos + áreas na UI legacy, service instancia PUs explicitamente (não trigger).
  - `CultivoArea` permanece como input-UI layer; step16+ fazem module migration gradual para PU-first.
- **Sem trigger de sync DB** (decisão já firmada anteriormente). Service garante coerência.

---

## 4. `status_consorcio_area` é apenas read model ou também gate operacional

### 4.1 Estados em jogo

`VAZIO | INCOMPLETO | VALIDO | INCONSISTENTE`

### 4.2 Opções de uso

| Política | Comportamento |
|---|---|
| (A) Pure read model | UI mostra status; operações normais procedem sempre |
| (B) Gate total — bloqueia tudo se não-VALIDO | Muito restritivo; bloqueia planejamento em andamento |
| (C) Gate seletivo | Bloqueia (a) avanço para `ENCERRADA`, (b) criação de PU em `INCONSISTENTE` |

### 4.3 Análise

- **INCOMPLETO (soma < 99,99)** é estado **normal durante planejamento** — usuário está montando consórcio gradualmente. Bloquear operações quebra UX.
- **INCONSISTENTE (soma > 100,01)** é **bug ou bypass** — não deveria existir se trigger DEFERRED funciona. Se acontece, deve alertar e **impedir nova mutação** até reconciliar.
- **Gate de fase (ENCERRADA)** — safra encerrada com consórcio incompleto gera custo/ha errado. Deve bloquear.

### 4.4 Recomendação

**Opção C — gate seletivo, duplo propósito:**

1. **Read model (maioria dos casos):** UI, dashboards, relatórios. Operações normais procedem com qualquer status.
2. **Gate 1 — criação/mutação de PU em área `INCONSISTENTE`:** service `ProductionUnitService.criar()` e `.atualizar()` consultam o status e recusam mutação em área INCONSISTENTE até que o operador reconcilie manualmente. Alerta para o admin.
3. **Gate 2 — transição de fase `POS_COLHEITA → ENCERRADA`:** `SafraService.avancar_fase(ENCERRADA)` rejeita se qualquer área com PUs ativas estiver `INCOMPLETO` ou `INCONSISTENTE`. Mensagem lista áreas e status.

Não bloqueia: criação de operações, romaneios, análises de solo, etc. Esses continuam por cultivo/area e não dependem de status do consórcio.

---

## 5. PU é o centro de custo ou referencia um centro de custo externo

### 5.1 Opções

| Modelo | Relação |
|---|---|
| (A) PU **é** o centro de custo agrícola | `custos_rateios.production_unit_id` FK direta |
| (B) PU referencia `centros_custo` externo (tabela nova) | `production_units.centro_custo_id` + `custos_rateios.centro_custo_id` |
| (C) Híbrido — PU **é** CC agrícola, mas pode ser agrupada em CC contábil maior | `production_units.centro_custo_contabil_id` FK opcional |

### 5.2 Análise

- **Doc mestre:** "unidade produtiva como centro de custo" — afirma PU **é** CC.
- **Projeto atual:** não existe tabela `centros_custo` ou equivalente. `fin_rateios` opera em categoria de despesa, não em CC estruturado.
- **Contábil clássico:** CC tem hierarquia (plano de contas analítico → sintético). Para agronegócio, a hierarquia natural é **AreaRural → Cultivo → PU** — já coberta pelo modelo.
- **Agrupamento operacional** (ex: "todas as PUs de café fino"): resolvível via query/view, não precisa tabela de CC.

### 5.3 Recomendação

**Opção A — PU é o centro de custo agrícola canônico.**

- `custos_rateios.production_unit_id` é FK direta (step19).
- Sem criar tabela `centros_custo` agora — YAGNI.
- **Extensão futura (opcional):** se houver demanda de agrupamento contábil mais amplo (ex: consolidar PUs de múltiplas safras sob um "projeto 2025"), adicionar `production_units.projeto_contabil_id` nullable em step futuro. Não bloqueante.

---

## 6. Regra default de rateio (percentual, hectare ou produção esperada)

### 6.1 Opções de default

| Método | Base | Natural para |
|---|---|---|
| (A) `PERCENTUAL` | `participation_percent` | Operações de overhead (laudo, monitoramento) |
| (B) `AREA_HA` | `area_ha` | Insumos que escalam com área (sementes, adubo, pulverização) |
| (C) `PRODUTIVIDADE_SC` | `produtividade_meta_sc_ha × area_ha` | Operações pós-colheita (beneficiamento, transporte, secagem) |
| (D) `DIRETO` | PU única | Quando operação é exclusiva de 1 PU |

### 6.2 Análise

- **80% das operações agrícolas escalam com área** (preparo, plantio, tratos culturais, irrigação, pulverização).
- **PERCENTUAL e AREA_HA são quase idênticos** na prática — porque `area_ha` do PU já reflete a participação. Diferença só aparece se `participation_percent` for definido manualmente fora da proporção `area_ha / AreaRural.area_ha`.
- **PRODUTIVIDADE_SC** faz sentido para custos que chegam só na colheita (saca/volume real). Minoritário.
- **DIRETO** é o caso fácil — operação numa única PU, sem necessidade de rateio.

### 6.3 Recomendação

**Default = `AREA_HA`.** Override por operação via campo `metodo_rateio` em `custos_rateios` (step 19).

**Razões:**
1. Reflete a realidade operacional predominante.
2. Consistente com `area_ha` armazenado (decisão ponto 2).
3. Alinha com `custo_por_ha` já existente em `operacoes_agricolas`.

**Hierarquia de resolução (service layer):**
1. Se operação aponta para 1 PU → `DIRETO`, `amount = custo_total`.
2. Se operação aponta para N PUs → aplica `metodo_rateio` (default AREA_HA).
3. Usuário pode sobrescrever `metodo_rateio` por operação (ex: colheita → PRODUTIVIDADE_SC).
4. Configuração de tenant futura (não step15): default por tipo de operação (preparo solo → AREA_HA, colheita → PRODUTIVIDADE_SC, overhead → PERCENTUAL).

**Implicação para step15:** PU não precisa de campo `metodo_rateio_default` — decisão fica no momento do rateio (step19). Step15 armazena só os dados estruturais (`percentual_participacao`, `area_ha`, `produtividade_meta_sc_ha` vem do cultivo).

---

## Síntese executiva

| # | Decisão | Recomendação |
|---|---|---|
| 1 | Unicidade de PU | `(tenant, safra, cultivo, area) WHERE status <> 'CANCELADA'` (partial unique) |
| 2 | `area_ha` | **Armazenada** como snapshot; validação de coerência em service |
| 3 | Criação de PU | **First-class** — backfill inicial + criação manual via API; sync por service, sem trigger DB |
| 4 | `status_consorcio_area` | **Read model + gate seletivo** (mutação em INCONSISTENTE; transição ENCERRADA) |
| 5 | PU como CC | PU **é** o centro de custo agrícola canônico; sem tabela externa |
| 6 | Default de rateio | **`AREA_HA`** como default; override por operação em `custos_rateios` (step19) |

## Impactos no desenho já existente do Step 15

- Ajustar unique de PU para partial (`WHERE status <> 'CANCELADA'`).
- Ajustar descrição de `area_ha` como snapshot semântico (já stored; adicionar nota).
- Ajustar texto de `status_consorcio_area` para "read model + gate seletivo" (duas funções explícitas).
- Nenhuma coluna nova exigida no PU em função destes pontos — o modelo atual suporta.

## Pendências antes do DDL

- Aprovação explícita das 6 recomendações.
- Propagar ajustes no `schema-diff-production-unit.md` §STEP 15 (seção 15.1 e 15.3).
- Só então gerar DDL do Step 15.

**Não avançar para DDL sem aprovação.**
