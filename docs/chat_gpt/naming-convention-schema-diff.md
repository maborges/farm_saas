# Proposta de Nomenclatura — Schema Diff (Steps 14 → 20)

**Data:** 2026-04-24
**Escopo:** Padronizar nomes de tabelas e campos em pt-BR antes da geração dos DDLs Alembic, preservando consistência com o schema atual.

---

## 1. Padrão predominante no projeto (levantado)

### 1.1 Convenções observadas

| Aspecto | Padrão em uso | Evidência |
|---|---|---|
| Case | `snake_case` | Todas as tabelas |
| Tabelas | Plural | `safras`, `cultivos`, `cadastros_areas_rurais` |
| Prefixo de domínio | Sim, quando módulo tem múltiplas tabelas | `cadastros_*` (37), `compras_*` (8), `fin_*` (7), `crm_*`, `frota_*`, `rh_*`, `ambiental_*`, `pec_*`, `estoque_*`, `agricola_*`, `safra_*` |
| Entidades raiz do domínio | Sem prefixo | `safras`, `cultivos`, `tenants`, `operacoes_agricolas` |
| FKs | `<entidade_singular>_id` | `safra_id`, `cultivo_id`, `area_id`, `produto_id`, `operacao_id` |
| Timestamps técnicos | Inglês | `created_at`, `updated_at`, `created_by` (convenção ORM) |
| Campos de domínio | pt-BR | `area_ha`, `cultura`, `ano_safra`, `custo_total`, `consorciado`, `ativo` |
| Campos de auditoria de negócio | pt-BR | `aprovado_em`, `aprovado_por`, `cancelado_em`, `assinado_por` |
| Booleanos | pt-BR sem prefixo `is_` | `ativo`, `ativa`, `consorciado`, `concluido`, `assinado` |

### 1.2 Regra consolidada

- **snake_case** sempre.
- **Tabelas em plural**.
- **FKs em singular**: `<entidade_singular>_id`.
- **Prefixo de domínio** quando o módulo tem várias tabelas relacionadas. Entidades centrais não recebem prefixo.
- **Timestamps técnicos em inglês** (`created_at`, `updated_at`) — consistência com SQLAlchemy/convenções ORM.
- **Campos de negócio em pt-BR** (datas, flags, totais).
- **Booleanos sem `is_`** — apenas o adjetivo (`ativo`, `consorciado`).

---

## 2. ⚠️ Conflito semântico crítico detectado

### 2.1 Problema

No projeto, **`unidades_produtivas` já existe** e significa **FAZENDA** (propriedade rural).

- Migration histórica: `rename_fazendas_to_unidades_produtivas.py`
- FK `unidade_produtiva_id` aparece **29 vezes** no codebase.
- Contexto: "unidade produtiva = propriedade/fazenda onde o produtor atua".

Usar `unidades_produtivas` para o novo conceito `ProductionUnit` (Safra × Cultivo × Área) **colide semanticamente**. Não é viável.

### 2.2 Opções de tradução para `ProductionUnit`

| Candidato | Prós | Contras | Veredito |
|---|---|---|---|
| `unidades_produtivas` | Tradução literal | **COLIDE** com Fazenda | ❌ inviável |
| `unidades_producao` | Próximo literal, não colide | Confunde com fábrica/indústria | ⚠️ ambíguo |
| `unidades_safra` | Contextualiza ao ciclo | Não captura "centro de custo" | ⚠️ parcial |
| `centros_producao` | Reforça papel de centro de custo | Termo contábil, não agronômico | ⚠️ |
| `centros_custo_safra` | Explícito | Muito longo, mistura contábil + agrícola | ❌ |
| **`production_units`** (manter inglês) | Evita colisão; alinha com doc mestre; termo técnico | Foge do padrão pt-BR do projeto | ✅ viável |
| **`safra_cultivo_areas`** | Descritivo, sem colisão, segue padrão pt-BR | Nome longo; não captura semântica de "unidade" | ⚠️ verboso |

### 2.3 Recomendação para PU

**Opção escolhida: `production_units` (manter em inglês)** — com justificativa documentada.

**Justificativa:**
1. Evita colisão com `unidades_produtivas` (Fazenda).
2. Termo técnico alinhado com o documento mestre e literatura de agronegócio digital.
3. FK `production_unit_id` é distinta de `unidade_produtiva_id` (já em uso) — zero ambiguidade em queries/joins.
4. Projeto já tem precedente de manter termos técnicos em inglês (`created_at`, `tenant_id`).

**Alternativa aceitável** se a diretriz pt-BR for inegociável: **`safra_cultivo_areas`** com FK `safra_cultivo_area_id`. Mais verboso mas sem colisão.

**Decisão fica com o usuário** — impacta os steps 15, 16, 17, 18, 19, 20.

---

## 3. Mapeamento de tabelas — proposta

### 3.1 Opção A (recomendada) — manter PU em inglês, demais em pt-BR

| Proposta inicial | Nome final | Justificativa |
|---|---|---|
| `uom_units` | `unidades_medida` | "UOM" é sigla inglesa; `unidades_medida` é claro e segue padrão pt-BR |
| `uom_conversions` | `unidades_medida_conversoes` | Prefixo do domínio UOM; plural composto |
| `production_units` | **`production_units`** (mantido) | Evita colisão — ver seção 2 |
| `area_consortium_status` | `status_consorcio_area` | Read model; prefixo `status_` comum |
| `operation_executions` | `operacoes_execucoes` | Prefixo `operacoes_` alinha com `operacoes_agricolas` |
| `inventory_movements` | `estoque_movimentos` | Prefixo `estoque_` já em uso (7 tabelas) |
| `inventory_movement_notes` (opcional) | `estoque_movimentos_notas` | Segue o pai |
| `cost_allocations` | `custos_rateios` | `custos_` como prefixo de domínio; evita colidir com `fin_rateios` (financeiro) |
| `scenarios` | `safra_cenarios` | Prefixo `safra_` contextualiza (cenário é sempre de safra) |
| `scenario_production_units` | `safra_cenarios_unidades` | Composição natural |

### 3.2 Opção B (alternativa) — `production_units` em pt-BR verboso

Aplicaria apenas se a decisão for banir inglês para entidades de negócio. Troca:
- `production_units` → `safra_cultivo_areas`
- FK `production_unit_id` → `safra_cultivo_area_id`
- `scenario_production_units` → `safra_cenarios_scas` (ou nome longo)

**Impacto:** nome de FK sobe para 21 caracteres; queries mais verbosas; alinhamento com doc mestre se perde.

### 3.3 Relação com prefixos já em uso no projeto

| Prefixo | Tabelas existentes | Tabelas novas propostas |
|---|---|---|
| `unidades_medida_` | — (novo domínio) | `unidades_medida`, `unidades_medida_conversoes` |
| `estoque_` | 7 existentes | `estoque_movimentos`, `estoque_movimentos_notas` |
| `operacoes_` | `operacoes_agricolas` | `operacoes_execucoes` |
| `custos_` | — (novo domínio) | `custos_rateios` |
| `safra_` | `safra_fase_historico`, `safra_talhoes`, `safra_tarefas` | `safra_cenarios`, `safra_cenarios_unidades` |
| `status_` | (implícito) | `status_consorcio_area` |
| (sem prefixo) | `safras`, `cultivos`, `cultivo_areas` | `production_units` (exceção justificada) |

---

## 4. Mapeamento de campos — proposta

### 4.1 Campos da Opção A

| Campo proposto | Campo final | Observação |
|---|---|---|
| `participation_percent` | `percentual_participacao` | pt-BR, sem abreviação |
| `adjustment_of` | `ajuste_de` | pt-BR direto; FK auto-referente |
| `movement_type` | `tipo_movimento` | pt-BR |
| `last_computed_at` | `calculado_em` | Segue padrão `<verbo>_em` já usado (`aprovado_em`, `cancelado_em`) |
| `is_active` | `ativo` | Projeto não usa prefixo `is_` |
| `participation_percent` | `percentual_participacao` | (repetido para ênfase) |
| `area_ha_override` | `area_ha_override` | **Manter em inglês** — "override" não tem tradução limpa em pt-BR técnico |
| `sum_participation` | `soma_participacao` | pt-BR |
| `pu_count` | `qtd_unidades` | Expandir abreviação; "pu" só faz sentido com PU nome |
| `allocation_method` | `metodo_rateio` | |
| `allocation_basis` | `base_rateio` | |
| `allocation_date` | `data_rateio` | Padrão `data_*` já em uso |
| `execution_date` | `data_execucao` | Idem |
| `execution_time` | `hora_execucao` | |
| `qty_planned` | `qtd_prevista` | |
| `qty_executed` | `qtd_executada` | |
| `qty_returned` | `qtd_devolvida` | |
| `qty` | `qtd` | Abreviação aceitável (já em uso no projeto) |
| `actual_cost` | `custo_real` | Padrão `custo_*` já existe (`custo_total`, `custo_por_ha`) |
| `area_ha_executed` | `area_executada_ha` | Padrão `area_*_ha` |
| `operator_id` | `operador_id` | Já em uso (5 ocorrências) |
| `execution_date` | `data_execucao` | |
| `movement_date` | `data_movimento` | |
| `warehouse_id` | `armazem_id` | Já em uso (3 ocorrências); `deposito_id` (6) também existe — preferir `armazem_id` para consistência no novo domínio |
| `product_id` | `produto_id` | Já em uso (12 ocorrências) |
| `unit_cost` | `custo_unitario` | Já em uso |
| `total_cost` | `custo_total` | Já em uso |
| `batch_number` | `numero_lote` | Padrão `lote_id` (8), `codigo_lote` |
| `source` | `origem` | pt-BR direto |
| `source_id` | `origem_id` | Idem |
| `currency` | `moeda` | |
| `cost_category` | `categoria_custo` | |
| `name` | `nome` | Padrão pt-BR |
| `description` | `descricao` | |
| `type` | `tipo` | |
| `parent_scenario_id` | `cenario_pai_id` | `parent_id` já em uso (4), mas `_pai_` é mais explícito |
| `code` (UOM) | `codigo` | Já em uso |
| `dimension` (UOM) | `dimensao` | |
| `canonical_code` | `codigo_canonico` | |
| `factor_to_canonical` | `fator_canonico` | |
| `is_system` | `sistema` | Booleano sem `is_` |
| `active` | `ativo` | Já em uso (padrão) |
| `from_unit_id` | `unidade_origem_id` | |
| `to_unit_id` | `unidade_destino_id` | |
| `factor` | `fator` | |
| `tolerance_percent` | `percentual_tolerancia` | |
| `observacoes` | `observacoes` | Já em uso (padrão) |

### 4.2 Enum values (`movement_type`, `status`, etc.)

**Decisão:** manter enum values em **MAIÚSCULAS**, podendo ser:
- **Português quando já há padrão** no projeto: `ATIVA`, `CANCELADA`, `PLANEJADA`, `ENCERRADA`, `REALIZADA`, `CONCLUIDA`, `APROVADO`, etc.
- **Inglês quando é termo técnico** sem tradução consolidada: `OPENING_BALANCE` (padrão contábil), `BASELINE`, `CUSTOM`.

Ficando:

| Tabela | Coluna | Valores |
|---|---|---|
| `estoque_movimentos` | `tipo_movimento` | `SALDO_INICIAL`, `ENTRADA`, `SAIDA`, `DEVOLUCAO`, `AJUSTE`, `TRANSFERENCIA` |
| `estoque_movimentos` | `origem` | `OPERACAO_EXECUCAO`, `COMPRA`, `COLHEITA`, `AJUSTE`, `MANUAL` |
| `production_units` | `status` | `ATIVA`, `ENCERRADA`, `CANCELADA` |
| `status_consorcio_area` | `status` | `VAZIO`, `INCOMPLETO`, `VALIDO`, `INCONSISTENTE` |
| `operacoes_execucoes` | `status` | `REALIZADA`, `DEVOLVIDA`, `CANCELADA` |
| `custos_rateios` | `categoria_custo` | `INSUMO`, `MAO_OBRA`, `MAQUINARIO`, `SERVICO`, `DESPESA_FINANCEIRA`, `OUTROS` |
| `custos_rateios` | `metodo_rateio` | `DIRETO`, `PERCENTUAL`, `AREA_HA`, `PRODUTIVIDADE_SC` |
| `safra_cenarios` | `tipo` | `BASELINE`, `OTIMISTA`, `PESSIMISTA`, `CUSTOMIZADO` |

**Observação:** `OPENING_BALANCE` vira **`SALDO_INICIAL`** (tradução consolidada no contábil brasileiro); demais termos contábeis mantêm pt-BR. `BASELINE` pode virar `REFERENCIA` se preferir estrita pt-BR.

### 4.3 Lista de termos que permanecem em inglês

Justificativa caso a caso:

| Termo | Por quê |
|---|---|
| `created_at`, `updated_at`, `created_by` | Convenção ORM universal; já padrão do projeto |
| `tenant_id` | Convenção SaaS universal; já padrão do projeto |
| `production_units` (se opção A) | Evita colisão com `unidades_produtivas` (Fazenda) |
| `production_unit_id` | Coerência com a tabela |
| `BASELINE` (enum) | Termo técnico de planejamento/contábil |
| `TRANSFERENCIA` | pt-BR direto (não é inglês) |
| Nome da FK `cultivo_area_id` | Já existe; manter |

---

## 5. FKs — nomes finais

Seguindo regra `<entidade_singular>_id`:

| FK final | Aponta para |
|---|---|
| `unidade_medida_id` | `unidades_medida` |
| `unidade_origem_id` | `unidades_medida` (conversões) |
| `unidade_destino_id` | `unidades_medida` (conversões) |
| `production_unit_id` | `production_units` |
| `operacao_execucao_id` | `operacoes_execucoes` |
| `estoque_movimento_id` | `estoque_movimentos` |
| `custo_rateio_id` | `custos_rateios` |
| `safra_cenario_id` | `safra_cenarios` |
| `cenario_pai_id` | `safra_cenarios` (auto-ref) |
| `ajuste_de` | `estoque_movimentos` (auto-ref, nome especial) |
| `cultivo_area_id` (existente) | `cultivo_areas` |
| `fin_rateio_id` (existente) | `fin_rateios` |
| `commodity_id` (existente) | `cadastros_commodities` |

**Regra para FK auto-referente semântica (`ajuste_de`):** permitida exceção ao `<entidade>_id` porque o nome expressa a relação, não a entidade. Precedente: projeto já tem `parent_id` (4 ocorrências) — mesma natureza.

---

## 6. Impacto da refatoração

### 6.1 Compatibilidade com schema atual

- **Zero colisões** com tabelas existentes (nenhum dos nomes novos já existe).
- `production_units` confirmado único — não há tabela com esse nome hoje.
- FKs novas (`production_unit_id`, `operacao_execucao_id`, etc.) não colidem com existentes.
- Prefixos (`estoque_`, `operacoes_`, `safra_`, `custos_`, `unidades_medida_`) respeitam o agrupamento já usado.

### 6.2 Alembic

- Migrations precisam usar os nomes pt-BR nos `op.create_table(...)`, FKs, índices e triggers.
- Nenhum impacto em migrations existentes (todas adiditivas, sem rename).
- Naming de migrations: `step14_unidades_medida.py`, `step15_production_units.py`, `step16_add_pu_fk_tabelas_legadas.py`, `step17_operacoes_execucoes.py`, `step18_estoque_movimentos.py`, `step19_custos_rateios.py`, `step20_safra_cenarios.py`.

### 6.3 SQLAlchemy models

- **Classes Python em PascalCase** podem permanecer próximas do doc mestre (inglês) ou pt-BR — não é constraint do DB.
- Projeto atual usa mix: `Safra`, `Cultivo`, `OperacaoAgricola`, `Rateio`, `Talhao` (legado) — pt-BR predomina.
- **Recomendação:** PascalCase em pt-BR para classes, correspondente ao nome da tabela:
  - `class UnidadeMedida` → `__tablename__ = "unidades_medida"`
  - `class ProductionUnit` → `__tablename__ = "production_units"` (exceção documentada)
  - `class StatusConsorcioArea` → `__tablename__ = "status_consorcio_area"`
  - `class OperacaoExecucao` → `__tablename__ = "operacoes_execucoes"`
  - `class EstoqueMovimento` → `__tablename__ = "estoque_movimentos"`
  - `class CustoRateio` → `__tablename__ = "custos_rateios"`
  - `class SafraCenario` → `__tablename__ = "safra_cenarios"`

### 6.4 APIs existentes

- **Zero impacto** — nenhuma API existente referencia as novas tabelas.
- Rotas novas seguem o padrão FastAPI atual (`/api/v1/<recurso>`):
  - `/api/v1/production-units` (kebab-case URL, inglês para consistência com o recurso)
  - `/api/v1/execucoes-operacao`
  - `/api/v1/movimentos-estoque`
  - `/api/v1/rateios-custo`
  - `/api/v1/cenarios`
- **Schemas Pydantic** em pt-BR seguindo campos da tabela.

### 6.5 Alinhamento com doc mestre

O doc mestre (`context-implementacao-evoluiva-operacional.md`) usa **apenas inglês** (`ProductionUnit`, `Task`, `Operation`, `OperationExecution`, `InventoryMovement`, `CostAllocation`, `Scenario`). A proposta aqui traduz para pt-BR no DB mantendo mapeamento 1:1 conceitual. Classes Python preservam legibilidade dos dois lados via docstring.

---

## 7. Recomendação final

### 7.1 Convenção oficial adotada

1. **snake_case** sempre.
2. **Tabelas em plural** com prefixo de domínio quando há agrupamento (≥2 tabelas).
3. **FKs em `<entidade_singular>_id`**, exceto relações semânticas (ex: `ajuste_de`, `cenario_pai_id`).
4. **Timestamps técnicos em inglês** (`created_at`, `updated_at`, `created_by`).
5. **Campos de negócio em pt-BR**.
6. **Booleanos sem prefixo `is_`** — só o adjetivo (`ativo`, `consorciado`).
7. **Enum values em MAIÚSCULAS pt-BR**, exceto termos técnicos sem tradução consolidada.
8. **Exceção `production_units`:** mantido em inglês para evitar colisão com `unidades_produtivas` (=Fazenda). Decisão documentada.

### 7.2 Mapeamento final consolidado

| Inicial (inglês) | Final (pt-BR) |
|---|---|
| `uom_units` | `unidades_medida` |
| `uom_conversions` | `unidades_medida_conversoes` |
| `production_units` | **`production_units`** (mantido; justificativa em 2.3) |
| `area_consortium_status` | `status_consorcio_area` |
| `operation_executions` | `operacoes_execucoes` |
| `inventory_movements` | `estoque_movimentos` |
| `cost_allocations` | `custos_rateios` |
| `scenarios` | `safra_cenarios` |
| `scenario_production_units` | `safra_cenarios_unidades` |

| Campo inicial | Campo final |
|---|---|
| `participation_percent` | `percentual_participacao` |
| `adjustment_of` | `ajuste_de` |
| `movement_type` | `tipo_movimento` |
| `last_computed_at` | `calculado_em` |
| `is_active` | `ativo` |
| `OPENING_BALANCE` (enum) | `SALDO_INICIAL` |
| `sum_participation` | `soma_participacao` |
| `allocation_method` | `metodo_rateio` |
| `cost_category` | `categoria_custo` |

### 7.3 Decisão pendente

**Uma única decisão** precisa ser confirmada antes de avançar para DDL:

**Mantemos `production_units` em inglês (Opção A, recomendada)** ou trocamos para **`safra_cultivo_areas` (Opção B)**?

Tudo o mais está consolidado. Aguardo a escolha para atualizar o `schema-diff-production-unit.md` com os nomes finais e gerar os DDLs Alembic.
