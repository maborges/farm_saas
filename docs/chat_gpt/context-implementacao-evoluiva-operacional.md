# Documento Mestre para IA — Implementação Evolutiva do Núcleo Operacional da Safra

## Instrução obrigatória para IA

Você NÃO deve reconstruir o sistema do zero.

Você deve evoluir o sistema existente incrementalmente, preservando:

* arquitetura atual
* compatibilidade com código legado
* modular monolith existente
* schema existente (usar diff e não redesign completo)
* APIs existentes
* comportamento atual das funcionalidades já implementadas

Todo desenvolvimento deve seguir additive evolution.

Não fazer mudanças destrutivas.

---

# Stack obrigatória

Frontend:

* Next.js 16.1 App Router
* React 19
* TypeScript strict
* Tailwind v4
* shadcn/ui
* TanStack Query v5
* Zustand apenas para estado leve UI
* React Hook Form + Zod
* AG Grid
* Recharts

Backend:

* FastAPI Python 3.12+
* PostgreSQL + PostGIS
* SQLAlchemy 2
* Alembic
* Celery + Redis
* GeoAlchemy2

Arquitetura:

* Modular Monolith
* Bounded Contexts
* PNPM Monorepo

Não introduzir novas tecnologias.

---

# Objetivo desta implementação

Evoluir o núcleo operacional da safra para suportar:

* unidade produtiva como centro de custo
* tarefas e operações com execução parcial
* ledger para estoque e custos
* apropriação/rateio
* gates por fase
* versionamento de laudos
* measurement engine
* cenários de planejamento
* capability-driven workflow

---

# Regras estruturais oficiais

## Centro de custo oficial

ProductionUnit = Talhão + Cultivo

Se não houver production_unit no legado:

fallback obrigatório:
Talhão atual assume unidade produtiva.

---

## Hierarquia oficial

Safra
→ Fases
→ Checklist
→ Tarefas
→ Operações
→ Execuções
→ Movimentos

---

## Regra de custos

Custo nasce na operação.

Tarefa consolida.

Não lançar custo manual na conclusão da tarefa.

---

## Regra estoque

Baixa estoque ocorre em OperationExecution.

Nunca na conclusão da tarefa.

---

## Regra ledger

Movimentos críticos são append-only.

Correções são ajustes.

Não editar fatos.

Aplica em:

* inventory movements
* cost entries
* operation executions

---

# Bounded Contexts a evoluir

Implementar ou evoluir módulos:

* safras
* production_units
* tasks
* operations
* inventory
* costs
* soil
* templates
* scenarios

Não concentrar tudo num único módulo.

---

# ENTREGAR PRIMEIRO UM GAP ANALYSIS

Antes de escrever código, analisar código existente e produzir matriz:

Para cada domínio:

* o que existe
* o que falta
* o que é reaproveitável
* o que exige refactor
* riscos

Formato:

| domínio | existente | gap | impacto |

Obrigatório.

Não pular esta etapa.

---

# ENTREGAR DEPOIS UM SCHEMA DIFF

Não gerar schema novo.

Gerar diff incremental sobre schema existente.

Adicionar prioritariamente:

1 production_units
2 operation_executions
3 inventory_movements
4 cost_allocations
5 scenarios

Incluir:

* novas tabelas
* FKs
* índices
* constraints
* Alembic migrations

Sem migrations destrutivas.

---

# Modelagem mínima obrigatória

## ProductionUnit

Campos mínimos:

* id
* safra_id
* talhao_id
* cultivo_id
* participation_percent

---

## Task

Adicionar:

* task_type
* requires_operation
* estimated_cost
* actual_cost
* cost_variance

Tipos:

* VERIFICACAO
* DECISAO
* EXECUCAO

---

## Operation

Adicionar:

* scope_type
* planned_qty
* executed_qty
* tolerance_type
* tolerance_value
* status

Status:

* PENDENTE
* EM_EXECUCAO
* PARCIAL
* CONCLUIDA
* CANCELADA

---

## OperationExecution

Relacionamento:
Operation 1:N OperationExecutions

Campos:

* operation_id
* execution_date
* qty_executed
* actual_cost

---

## InventoryMovement

Append-only.

Tipos:

* CONSUMO
* DEVOLUCAO
* PERDA

---

## CostAllocation

Métodos:

* por hectare (default)
* percentual
* manual
* igualitário

---

## Scenario

Campos:

* expected_yield
* expected_price
* expected_cost
* expected_margin
* is_selected

---

# Measurement Engine obrigatório

Implementar módulo de medidas.

Suportar:

* UOM
* conversões
* conversões por cultura
* unidade canônica interna
* tolerâncias

Nunca salvar valor sem unidade.

---

# Serviços de domínio a especificar

Gerar contratos para:

PhaseGateService
CostAllocationService
TaskGenerationService
MeasurementEngine
ScenarioEngine

Não implementar regra em controllers.

---

# Eventos internos a modelar

Definir eventos:

TaskApproved
TaskReopened
OperationExecuted
InventoryConsumed
CostAllocated
PhaseAdvanced

Definir:

* emissor
* consumidor
* síncrono ou Celery

---

# Capability-driven workflow

Workflow deve respeitar módulos contratados.

Capabilities habilitam inteligência.

Não podem quebrar processo.

Suportar fallback manual.

---

# Permissões

Respeitar modelo atual de perfis.

Adicionar permissões por ação crítica:

* approve_task
* reopen_task
* adjust_cost
* approve_soil_report
* advance_phase

Não redesenhar RBAC.

Evoluir.

---

# Dados padrão x dados do cliente

Respeitar dois níveis:

Backoffice:

* padrões globais SaaS

Tenant:

* extensões do cliente

Regra:
Overrides por clonagem.

Nunca editar padrão do SaaS.

---

# Ordem de implementação obrigatória

Implementar nesta ordem:

Fase 1
GAP Analysis

Fase 2
Schema Diff

Fase 3
ProductionUnit

Fase 4
Task -> Operations

Fase 5
OperationExecution

Fase 6
Inventory Ledger

Fase 7
Cost Allocation

Fase 8
Phase Gates

Fase 9
Scenarios

Não inverter ordem.

---

# Não implementar agora

Não priorizar:

* dashboards avançados
* ML preditivo
* PyTorch models
* analytics avançado
* redesign UX final

Primeiro domínio transacional.

---

# Critérios de aceite

Implementação só é aceita se estes cenários funcionarem:

1 tarefa com múltiplas operações

2 operação parcial com devolução

3 rateio multi-talhão

4 consórcio via production unit

5 avanço de fase com gates

Se qualquer um falhar:
modelo incompleto.

---

# Entregáveis esperados da IA

Entregar em sequência:

1 GAP analysis do código atual

2 schema diff incremental

3 plano de migração Alembic

4 contratos dos services de domínio

5 implementação do primeiro bounded context (ProductionUnit)

Não tentar entregar tudo em um único passo.

Incremental.

---

# Regra final

Frontend orquestra.
Backend decide.
Banco garante consistência.

Domínio não vive na interface.

Evoluir por composição.
Não por reconstrução.
