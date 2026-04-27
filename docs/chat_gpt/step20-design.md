# Step 20 — Safra Cenários: Design Técnico e Funcional

**Data:** 2026-04-24  
**Status:** ✅ Decisões aprovadas — pronto para implementar

---

## 1. Objetivo Funcional

Permitir que o produtor crie múltiplos **cenários econômicos hipotéticos** para uma safra, simulando diferentes combinações de produtividade, preço de venda e custo. O sistema calcula automaticamente receita bruta, custo total, margem de contribuição e resultado líquido — tanto no nível da safra inteira quanto por `ProductionUnit` (cultivo × talhão).

Casos de uso principais:
- "E se a soja cair para R$ 120/sc?" (cenário pessimista de preço)
- "E se eu atingir 65 sc/ha em vez de 55 sc/ha?" (cenário otimista de produtividade)
- "E se eu reduzir 15% no custo de fertilizantes?" (cenário de eficiência de custo via `fator_custo_pct`)
- Comparar cenário orçado (A1) vs. realizado (romaneios + cost_allocations) vs. projeções futuras

---

## 2. Regras de Negócio

1. Um cenário pertence a uma **safra** e a um **tenant** (isolamento multi-tenant obrigatório).
2. Cada cenário pode ter **N linhas de `safra_cenarios_unidades`**, uma por `ProductionUnit` ativa na safra.
3. Existe sempre **um cenário marcado como `base`** por safra — **criado automaticamente no primeiro GET de `/cenarios`**. Também pode ser recriado via `POST /base/recalcular`.
4. O cenário `base` não pode ser excluído. Outros cenários podem ser excluídos livremente.
5. Campos calculados (`receita_bruta`, `margem_contribuicao`, `resultado_liquido`) são **somente leitura** — calculados no service, nunca gravados pelo usuário.
6. **`resultado_liquido` = `margem_contribuicao`** neste step. Depreciação, IR e ajustes fiscais reservados para Step 20b.
7. Campos de entrada por unidade: `produtividade_simulada`, `preco_simulado`, `custo_total_simulado_ha`. `NULL` = herda do cabeçalho do cenário.
8. **`fator_custo_pct`** aplica-se globalmente às unidades que **não** tenham `custo_total_simulado_ha` explícito. Custo próprio da unidade prevalece.
9. Um cenário pode ser **duplicado** (clone com novo nome).
10. Cenário não pode ser criado para safra com status `CANCELADA`.
11. `percentual_participacao` vem da `ProductionUnit` — não é editável no cenário.
12. Máximo de **20 cenários ativos** por safra (gate anti-spam).

### Prioridade do custo base (cenário BASE automático)
```
1º  cost_allocations realizados  →  SUM(amount) por production_unit_id / area_ha
2º  a1_planejamento orçado       →  SUM(custo_total) por production_unit_id / area_ha
3º  NULL                         →  usuário preenche manualmente
```
A `fonte_custo` é registrada no campo `custo_base_fonte` da linha para rastreabilidade.

### Unidade de medida e conversão por cultura
- Produtividade e preço são armazenados com referência a uma `unidade_medida_id` FK → `unidades_medida` (Step 14).
- O `unidade_medida_id` fica na **linha** (`safra_cenarios_unidades`) — pode variar por cultivo.
- Padrão por cultura: soja/milho/feijão → `SC60` (sc/60kg); café → `SC60`; algodão → `AR` (arroba). Resolvido via `cultivo.unidade_medida_padrao_id` se disponível.
- Conversões entre unidades usam `unidades_medida_conversoes`. O service normaliza para a unidade efetiva antes de calcular `producao_total`.
- `produtividade_simulada` e `preco_simulado` são **sempre na unidade referenciada** por `unidade_medida_id` da linha.

---

## 3. Modelagem das Tabelas

### 3.1 `safra_cenarios`

```sql
safra_cenarios
├── id                          UUID PK
├── tenant_id                   UUID FK tenants.id CASCADE NOT NULL
├── safra_id                    UUID FK safras.id CASCADE NOT NULL
├── nome                        VARCHAR(100) NOT NULL
├── descricao                   TEXT NULL
├── tipo                        VARCHAR(20) NOT NULL DEFAULT 'CUSTOM'
│                               -- 'BASE' | 'OTIMISTA' | 'PESSIMISTA' | 'CUSTOM'
├── eh_base                     BOOLEAN NOT NULL DEFAULT FALSE
├── status                      VARCHAR(20) NOT NULL DEFAULT 'ATIVO'
│                               -- 'ATIVO' | 'ARQUIVADO'
│
│   -- Parâmetros default (herdados pelas unidades que não sobrescrevem)
├── produtividade_default       NUMERIC(10,3) NULL
├── preco_default               NUMERIC(14,4) NULL
├── custo_ha_default            NUMERIC(14,2) NULL
├── fator_custo_pct             NUMERIC(6,4) NULL   -- 0.85 = redução 15%
├── unidade_medida_id           UUID FK unidades_medida.id RESTRICT NULL
│                               -- unidade de referência dos defaults
│
│   -- Totalizadores calculados (snapshot do último recálculo)
├── area_total_ha               NUMERIC(12,4) NULL
├── receita_bruta_total         NUMERIC(18,2) NULL
├── custo_total                 NUMERIC(18,2) NULL
├── margem_contribuicao_total   NUMERIC(18,2) NULL
├── resultado_liquido_total     NUMERIC(18,2) NULL  -- = margem_contribuicao_total neste step
├── ponto_equilibrio_sc_ha      NUMERIC(10,3) NULL  -- custo_total / (receita_bruta_total / area_total_ha)
│
├── calculado_em                TIMESTAMPTZ NULL
├── created_by                  UUID NULL
├── created_at                  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
└── updated_at                  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
```

**Constraints:**
- `UNIQUE (tenant_id, safra_id, nome)`
- `CHECK (tipo IN ('BASE','OTIMISTA','PESSIMISTA','CUSTOM'))`
- `CHECK (status IN ('ATIVO','ARQUIVADO'))`
- Partial unique: `UNIQUE (tenant_id, safra_id) WHERE eh_base = TRUE`
- `CHECK (fator_custo_pct IS NULL OR (fator_custo_pct > 0 AND fator_custo_pct <= 2.0))`

---

### 3.2 `safra_cenarios_unidades`

```sql
safra_cenarios_unidades
├── id                          UUID PK
├── tenant_id                   UUID FK tenants.id CASCADE NOT NULL
├── cenario_id                  UUID FK safra_cenarios.id CASCADE NOT NULL
├── production_unit_id          UUID FK production_units.id CASCADE NOT NULL
│
│   -- Snapshot de contexto (desnormalizado — imune a mudanças de cadastro)
├── cultivo_nome                VARCHAR(100) NULL
├── area_nome                   VARCHAR(200) NULL
├── area_ha                     NUMERIC(12,4) NOT NULL   -- snapshot de production_units.area_ha
├── percentual_participacao     NUMERIC(5,2)  NOT NULL   -- snapshot de production_units.percentual_participacao
├── unidade_medida_id           UUID FK unidades_medida.id RESTRICT NULL
│                               -- unidade efetiva desta linha (herda cultivo ou cenário pai)
│
│   -- Parâmetros simulados (NULL = herda cabeçalho do cenário)
├── produtividade_simulada      NUMERIC(10,3) NULL   -- na unidade_medida_id / ha
├── preco_simulado              NUMERIC(14,4) NULL   -- R$ por unidade_medida_id
├── custo_total_simulado_ha     NUMERIC(14,2) NULL   -- R$/ha (sobrescreve fator_custo_pct)
│
│   -- Rastreabilidade da fonte do custo base
├── custo_base_fonte            VARCHAR(20) NULL
│                               -- 'REALIZADO' | 'ORCADO' | 'MANUAL' | NULL
│
│   -- Valores calculados (snapshot do último recálculo)
├── produtividade_efetiva       NUMERIC(10,3) NULL   -- resolvido: próprio ?? default pai
├── preco_efetivo               NUMERIC(14,4) NULL
├── custo_ha_efetivo            NUMERIC(14,2) NULL   -- após aplicar fator_custo_pct se aplicável
├── producao_total              NUMERIC(14,3) NULL   -- produtividade_efetiva × area_ha
├── receita_bruta               NUMERIC(18,2) NULL   -- producao_total × preco_efetivo
├── custo_total                 NUMERIC(18,2) NULL   -- custo_ha_efetivo × area_ha
├── margem_contribuicao         NUMERIC(18,2) NULL   -- receita_bruta - custo_total
├── margem_pct                  NUMERIC(8,4)  NULL   -- margem / receita_bruta × 100
├── resultado_liquido           NUMERIC(18,2) NULL   -- = margem_contribuicao neste step
├── ponto_equilibrio            NUMERIC(10,3) NULL   -- custo_ha_efetivo / preco_efetivo
│
├── created_at                  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
└── updated_at                  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
```

**Constraints:**
- `UNIQUE (cenario_id, production_unit_id)`
- `CHECK (area_ha > 0)`
- `CHECK (percentual_participacao > 0 AND percentual_participacao <= 100)`
- `CHECK (produtividade_simulada IS NULL OR produtividade_simulada > 0)`
- `CHECK (preco_simulado IS NULL OR preco_simulado > 0)`
- `CHECK (custo_total_simulado_ha IS NULL OR custo_total_simulado_ha >= 0)`
- `CHECK (custo_base_fonte IS NULL OR custo_base_fonte IN ('REALIZADO','ORCADO','MANUAL'))`

---

## 4. Relacionamentos

```
Tenant (1)
  └── Safra (N)
        └── safra_cenarios (N, max 20 ativos)
              │   unidade_medida_id → unidades_medida
              └── safra_cenarios_unidades (N)
                    │   unidade_medida_id → unidades_medida
                    └── ProductionUnit (1)
                          ├── cultivo_id → cultivos
                          └── area_id → cadastros_areas_rurais
```

---

## 5. Campos editáveis — `safra_cenarios`

| Campo | Obrigatório | Editável |
|---|---|---|
| `nome` | ✅ | ✅ |
| `descricao` | ❌ | ✅ |
| `tipo` | ✅ (default CUSTOM) | ✅ |
| `produtividade_default` | ❌ | ✅ |
| `preco_default` | ❌ | ✅ |
| `custo_ha_default` | ❌ | ✅ |
| `fator_custo_pct` | ❌ | ✅ |
| `unidade_medida_id` | ❌ | ✅ |
| `eh_base` | — | ❌ sistema |
| `*_total` / calculados | — | ❌ sistema |

---

## 6. Campos editáveis — `safra_cenarios_unidades`

| Campo | Obrigatório | Editável |
|---|---|---|
| `produtividade_simulada` | ❌ (herda pai) | ✅ |
| `preco_simulado` | ❌ (herda pai) | ✅ |
| `custo_total_simulado_ha` | ❌ (herda pai) | ✅ |
| `unidade_medida_id` | ❌ (herda cultivo) | ✅ |
| calculados (`receita_bruta`, etc.) | — | ❌ sistema |
| `custo_base_fonte` | — | ❌ sistema |

---

## 7. Fluxo de Criação/Edição

### Criação do cenário BASE (automático no primeiro GET)
```
GET /safras/{safra_id}/cenarios
  → service verifica: existe cenário BASE para esta safra+tenant?
  → NÃO: _get_or_create_base() é chamado:
      1. Busca todas PUs ativas da safra
      2. Para cada PU:
         a. Tenta cost_allocations: SUM(amount) WHERE production_unit_id = pu.id
         b. Se vazio: tenta a1_planejamento: SUM(custo_total) WHERE production_unit_id = pu.id
         c. Se vazio: custo_ha = NULL, custo_base_fonte = 'MANUAL'
         d. Tenta romaneios: produtividade_sc_ha média, preco_saca médio
         e. Resolve unidade_medida_id via cultivo.unidade_medida_padrao_id ou default SC60
      3. Cria safra_cenario (eh_base=TRUE, tipo='BASE', nome='Base Realizado')
      4. Cria safra_cenarios_unidades com snapshots
      5. Recalcula e persiste
  → Retorna lista com BASE + demais cenários
```

### Criação manual
```
POST /safras/{safra_id}/cenarios
Body: { nome, tipo, descricao, produtividade_default, preco_default,
        custo_ha_default, fator_custo_pct, unidade_medida_id,
        unidades: [{ production_unit_id, produtividade_simulada, ... }] }
  → Valida safra não CANCELADA
  → Valida max 20 cenários ativos
  → Valida nome único na safra
  → Cria cenário + linhas
  → Recalcula → persiste snapshot
  → Retorna cenário completo
```

### Edição (PATCH)
```
PATCH /safras/{safra_id}/cenarios/{cenario_id}
  → Atualiza campos do cabeçalho e/ou linhas
  → Recalcula todas as linhas afetadas
  → Atualiza totalizadores do cabeçalho
  → Resposta inclui snapshot completo
```

### Recalcular BASE manualmente
```
POST /safras/{safra_id}/cenarios/base/recalcular
  → Força rebuild: re-busca cost_allocations + romaneios atuais
  → Atualiza valores do BASE sem alterar outros cenários
```

### Duplicação
```
POST /safras/{safra_id}/cenarios/{cenario_id}/duplicar
Body: { nome: "Cenário Pessimista 2" }
  → Copia cabeçalho (eh_base=FALSE, nome=novo)
  → Copia todas as linhas com novos IDs
  → Retorna novo cenário
```

---

## 8. Cálculos Econômicos

### Por `safra_cenarios_unidades`
```
-- Resolução de valores efetivos
produtividade_efetiva = unidade.produtividade_simulada
                        ?? cenario.produtividade_default

preco_efetivo         = unidade.preco_simulado
                        ?? cenario.preco_default

-- Custo: override próprio prevalece sobre fator global
custo_ha_efetivo      = unidade.custo_total_simulado_ha     [se informado]
                        ?? (cenario.custo_ha_default
                           × (cenario.fator_custo_pct ?? 1.0))

-- Produção (normalizada para unidade efetiva via UnidadeMedidaConversao se necessário)
producao_total        = produtividade_efetiva × area_ha

-- Resultados
receita_bruta         = producao_total × preco_efetivo
custo_total           = custo_ha_efetivo × area_ha
margem_contribuicao   = receita_bruta - custo_total
margem_pct            = (margem_contribuicao / receita_bruta) × 100  [se receita > 0, senão NULL]
resultado_liquido     = margem_contribuicao   -- Step 20: sem IR/depreciação
ponto_equilibrio      = custo_ha_efetivo / preco_efetivo    [se preco > 0, senão NULL]
```

### Totalizadores do cabeçalho
```
area_total_ha            = SUM(unidades.area_ha)
receita_bruta_total      = SUM(unidades.receita_bruta)
custo_total              = SUM(unidades.custo_total)
margem_contribuicao_total = SUM(unidades.margem_contribuicao)
resultado_liquido_total  = margem_contribuicao_total
ponto_equilibrio_sc_ha   = custo_total / (receita_bruta_total / area_total_ha)
                           [ponto de equilíbrio médio ponderado pela área]
```

---

## 9. Validações

| Regra | Camada | Resposta |
|---|---|---|
| `nome` único por safra/tenant | Service | 409 |
| Max 20 cenários ativos por safra | Service | 422 "Limite de 20 cenários atingido" |
| Safra com status `CANCELADA` | Service | 422 |
| `eh_base` não pode ser alterado | Service | 403 |
| Cenário BASE não pode ser excluído | Service | 422 |
| `produtividade`, `preco` > 0 quando informados | Schema | 422 |
| `custo_total_simulado_ha` ≥ 0 quando informado | Schema | 422 |
| `fator_custo_pct` entre 0.01 e 2.0 | Schema | 422 |
| `production_unit_id` pertence à safra do cenário | Service | 422 |
| `production_unit_id` pertence ao mesmo tenant | Service | 403 |
| PU duplicada no mesmo cenário | DB UNIQUE | 409 |
| `unidade_medida_id` deve existir | DB FK RESTRICT | 422 |

---

## 10. Multi-Tenant

1. Todo query filtra `tenant_id` — nenhuma busca global.
2. Ao criar `safra_cenarios_unidades`: validar `production_unit.tenant_id == cenario.tenant_id`.
3. Busca de cenários: filtro duplo `cenario.safra_id = X AND cenario.tenant_id = Y`.
4. Campos snapshot (`cultivo_nome`, `area_nome`, `area_ha`) preenchidos na criação — imunes a mudanças de cadastro.
5. Endpoint de duplicação: validar cenário fonte pertence ao tenant do JWT.
6. `BaseService` injeta `tenant_id` automaticamente; queries customizadas adicionam filtro explícito.

---

## 11. Estrutura Backend

```
services/api/agricola/cenarios/
├── __init__.py
├── models.py           # SafraCenario, SafraCenarioUnidade
├── schemas.py          # Create/Update/Response/DuplicarRequest/Comparativo
├── service.py          # CenariosService(BaseService)
│                         ├── list_cenarios()          → cria BASE se não existir
│                         ├── get_cenario()
│                         ├── create_cenario()
│                         ├── update_cenario()
│                         ├── delete_cenario()
│                         ├── duplicar()
│                         ├── get_comparativo()
│                         ├── recalcular_base()
│                         ├── _get_or_create_base()    → privado
│                         ├── _resolve_custo_base()    → cost_alloc → a1_plan → None
│                         ├── _resolve_uom()           → cultivo.uom ?? cenario.uom ?? SC60
│                         └── _recalculate_all()       → engine de cálculo
└── router.py
```

### Endpoints

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/safras/{safra_id}/cenarios` | Lista + cria BASE automaticamente |
| `POST` | `/safras/{safra_id}/cenarios` | Cria cenário manual |
| `GET` | `/safras/{safra_id}/cenarios/{cenario_id}` | Detalhe com unidades |
| `PATCH` | `/safras/{safra_id}/cenarios/{cenario_id}` | Atualiza + recalcula |
| `DELETE` | `/safras/{safra_id}/cenarios/{cenario_id}` | Remove (não-base) |
| `POST` | `/safras/{safra_id}/cenarios/{cenario_id}/duplicar` | Duplica |
| `GET` | `/safras/{safra_id}/cenarios/comparativo` | Tabela side-by-side de N cenários |
| `POST` | `/safras/{safra_id}/cenarios/base/recalcular` | Rebuild manual do BASE |

---

## 12. Estrutura Frontend

```
apps/web/src/app/(dashboard)/agricola/safras/[id]/cenarios/
├── page.tsx                       # RSC — lista + trigger criação BASE
├── [cenarioId]/page.tsx           # RSC — detalhe do cenário
└── components/
    ├── cenarios-list.tsx           # cards com KPIs + badge de tipo
    ├── cenario-form.tsx            # wizard 4 steps: nome→defaults→unidades→preview
    ├── cenario-unidades-table.tsx  # grid inline editável por PU
    ├── comparativo-table.tsx       # side-by-side N cenários
    └── cenario-kpi-cards.tsx       # Receita | Custo | Margem% | Ponto Equilíbrio
```

### UI por tela

**Listagem `/cenarios`:**
- Cards por cenário: badge tipo (BASE/OTIMISTA/PESSIMISTA/CUSTOM) + KPIs compactos
- Seleção múltipla → botão "Comparar"
- Botão "Novo Cenário" (outline sm)
- Badge especial no BASE: não exibe botão de exclusão

**Formulário de criação (wizard 4 steps):**
1. Nome, tipo, descrição
2. Parâmetros default: produtividade, preço, unidade de medida, `fator_custo_pct`
3. Tabela de PUs com inline override (produtividade, preço, custo/ha por linha)
4. Preview calculado antes de salvar (read-only)

**Detalhe `/cenarios/[id]`:**
- KPI cards: Receita Bruta | Custo Total | Margem Contribuição | Ponto de Equilíbrio
- Tabela: Cultivo | Talhão | Área (ha) | Produtiv. | Preço | Custo/ha | Receita | Margem% | Fonte Custo
- Botões: Editar | Duplicar | Recalcular (apenas BASE) | Arquivar
- Gráfico de barras: Receita vs Custo por PU

**Comparativo:**
- Colunas = cenários selecionados, linhas = PUs + linha de totais
- Destaque visual: maior margem (verde) / menor margem (vermelho/destrutivo)
- Exportação PDF/Excel via data-table padrão

---

## 13. Migration Step 20

Arquivo: `migrations/versions/step20_safra_cenarios.py`

Operações:
1. `CREATE TABLE safra_cenarios` com constraints e partial unique index
2. `CREATE TABLE safra_cenarios_unidades` com constraints
3. `CREATE INDEX ix_safra_cenarios_tenant_safra ON safra_cenarios (tenant_id, safra_id)`
4. `CREATE INDEX ix_safra_cenarios_unidades_cenario ON safra_cenarios_unidades (cenario_id)`
5. `CREATE INDEX ix_safra_cenarios_unidades_pu ON safra_cenarios_unidades (production_unit_id)`

Sem backfill automático — cenários BASE são criados on-demand pelo service.

---

**Decisões incorporadas neste design:**
- ✅ UnidadeMedida via Step 14, conversão por cultura, padrão SC60
- ✅ resultado_liquido = margem_contribuicao (Step 20b para IR/depreciação)
- ✅ BASE criado automaticamente no primeiro GET
- ✅ Endpoint manual `POST /base/recalcular`
- ✅ Prioridade custo: cost_allocations → a1_planejamento → NULL/manual
- ✅ fator_custo_pct global, sobrescrito por custo_total_simulado_ha da linha
