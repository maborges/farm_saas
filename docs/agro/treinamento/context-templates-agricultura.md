# 🌱 FEATURE — TEMPLATES DE FASE E TEMPLATES DE OPERAÇÕES

## 🎯 Objetivo

Permitir que o sistema carregue estruturas pré-configuradas para uma fase da safra, evitando que o usuário monte manualmente checklists, tarefas, operações e regras toda vez que iniciar uma safra ou entrar em uma fase.

A feature deve suportar:

- Templates de Fase
- Templates de Operações
- Templates por Cultura (opcional)
- Templates customizados por cliente

---

# 🧠 CONCEITO

Existem dois tipos de template:

## 1. Template de Fase

Configura a governança da fase.

Define:

- checklist padrão
- tarefas padrão
- dependências
- regras do gate
- critérios para avanço

Não executa operações.

Organiza a fase.

---

## 2. Template de Operações

Configura o pacote operacional da fase.

Define:

- operações padrão
- sequência sugerida
- custos estimados
- tarefas derivadas
- dependências operacionais

Executa o plano da fase.

---

# 🧱 ESCOPO

Aplica inicialmente às fases:

- Planejamento
- Preparo do Solo
- Plantio
- Desenvolvimento
- Colheita
- Pós-Colheita
- Encerramento

---

# 📦 ENTIDADES

## PhaseTemplate

Campos:

- id
- name
- phase
- culture_id (nullable)
- tenant_id (nullable)
- is_system_default (bool)
- active (bool)

Relacionamentos:

- hasMany checklist_items
- hasMany task_templates
- hasMany gate_rules

---

## PhaseTemplateChecklistItem

- id
- phase_template_id
- description
- required (bool)
- blocks_phase_advance (bool)
- generates_task_if_pending (bool)
- sort_order

---

## PhaseTemplateTask

- id
- phase_template_id
- name
- criticality (CRITICA/NORMAL/OPCIONAL)
- suggested_role
- auto_create (bool)
- sort_order

---

## PhaseGateRule

- id
- phase_template_id
- requires_checklist_completion (bool)
- requires_critical_tasks_completion (bool)

---

## OperationTemplate

- id
- name
- phase
- culture_id (nullable)
- tenant_id (nullable)
- active

Relacionamentos:

- hasMany operations
- hasMany dependencies

---

## OperationTemplateItem

- id
- operation_template_id
- name
- description
- prerequisite_rule
- can_generate_task
- estimated_cost_default
- critical_operation (bool)
- sort_order

---

## OperationDependency

- id
- operation_template_id
- operation_item_id
- depends_on_operation_item_id

---

# ⚙️ FLUXOS

## Fluxo 1 — Aplicar Template na criação da Safra

Usuário cria safra.

Sistema exibe:

Escolher template de Planejamento:

- Template padrão
- Template por cultura
- Template personalizado

Usuário seleciona.

Sistema instancia:

- checklist da fase
- tarefas da fase
- gate rules

---

## Fluxo 2 — Aplicar Template de Operações ao entrar na fase

Ao entrar em Preparo do Solo:

Sistema sugere:

Aplicar template operacional?

Usuário confirma.

Sistema cria:

- operações padrão
- tarefas derivadas
- custos estimados

---

# 🔄 INSTANCIAÇÃO

Template nunca é executado diretamente.

Template gera instâncias.

Exemplo:

PhaseTemplate
→ gera
PhaseChecklist

PhaseTasks

GateRules

---

OperationTemplate
→ gera

Operations

OperationTasks

CostEstimates

---

# 📋 REGRAS

## Regra 1

Template é editável antes da instância.

Instância não deve alterar template original.

---

## Regra 2

Usuário pode remover itens após aplicar template.

---

## Regra 3

Usuário pode adicionar itens além do template.

---

## Regra 4

Se existir template por cultura, ele tem prioridade sobre template padrão.

Ordem:

1 cultura template

2 tenant template

3 system default

---

# 🚦 GATE DA FASE

Regra padrão:

```text
Checklist obrigatório concluído
AND
tarefas críticas concluídas
```

Liberar próxima fase.

---

# 💰 CUSTOS

OperationTemplateItem pode carregar:

- estimated_cost_default
- estimated_resource_qty

Somente estimativa.

Custo real nasce na operação executada.

---

# 👤 PAPÉIS

Gestor:

- escolhe template

Agrônomo:

- ajusta template instanciado

Operador:

- executa tarefas/operações

Admin SaaS:

- mantém templates globais

---

# 🖥 TELAS NECESSÁRIAS

## 1. Manutenção de Templates de Fase

Listar:

- nome
- fase
- cultura
- padrão?

Ações:

- criar
- editar
- duplicar
- desativar

---

## 2. Editor do Template da Fase

Abas:

Checklist

Tarefas

Gate Rules

---

## 3. Manutenção de Templates de Operações

Lista de operações padrão.

---

## 4. Aplicar Template na Safra

Modal:

Selecionar template

Preview:

- itens do checklist
- tarefas
- operações

Confirmar

---

# 📌 EXEMPLO

Template Planejamento Café

Checklist:

- cultivo definido
- análise de solo revisada
- orçamento definido

Tarefas:

- revisar correções
- planejar insumos

Gate:

checklist obrigatório

+

tarefas críticas

---

# 🚀 EVOLUÇÃO FUTURA

Suportar:

- templates versionados
- marketplace de templates
- templates por região
- templates por tipo de solo
- templates por irrigação

---

# ⚠️ NÃO FAZER

Não permitir:

- template alterar instância executada

Não misturar:

- template com operação real

---

# 🎯 ACEITE DA FEATURE

Feature pronta quando usuário puder:

✔ criar template de fase

✔ criar template de operações

✔ aplicar template à safra

✔ instanciar checklist/tarefas/operações

✔ usar regras de gate

✔ editar instância sem alterar template

---

# 🔥 REGRA DE OURO

Template não executa.

Template gera estrutura executável.