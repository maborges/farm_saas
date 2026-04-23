# 📐 DESIGN — Módulo de Templates Agrícolas

> **Status:** Design validado — pronto para implementação  
> **Data:** 2026-04-23  
> **Método:** Brainstorming estruturado com confirmação incremental

---

## 🎯 Understanding Summary

| Item | Definição |
|---|---|
| **O que é** | Módulo completo de Templates Agrícolas: Template de Fase (governança) + Template de Operações (plano operacional) |
| **Por que existe** | Evitar que o usuário monte manualmente checklists, tarefas e operações toda vez que iniciar uma safra ou entrar em uma nova fase |
| **Para quem** | Gestor (escolhe/aplica), Agrônomo (ajusta instância), Operador (executa), Admin SaaS (mantém globais no Backoffice) |
| **Não-goals** | Marketplace de templates, versionamento, templates por região/solo/irrigação |

---

## ✅ Decisões Confirmadas

| Ponto | Decisão |
|---|---|
| Escopo | Template de Fase + Template de Operações (completo) |
| Migração | `checklist_templates` → `phase_templates` (migração total) |
| Admin | Backoffice (globais) + módulo Agrícola (tenant + clone de globais) |
| Aplicação | Seleção explícita sempre, filtrado por fase + cultura, "nenhum" válido |
| O que gera | Apenas `SafraTarefa` com `origem=TEMPLATE` (não cria operações) |
| Ponto de entrada | Wizard de criação + botão "Aplicar Template" por fase ativa |
| Gate Rules | Regras base hardcoded sempre ativas + template adiciona extras opcionais |

---

## 🗃️ Schema do Banco (PostgreSQL + Alembic)

### Novas tabelas

```
phase_templates                         → container de governança
phase_template_checklist_items          → substitui checklist_templates
phase_template_tasks                    → tarefas padrão por template
phase_gate_rules                        → regras extras de gate (1:1 com template)
operation_templates                     → container operacional
operation_template_items                → operações padrão
operation_dependencies                  → pré-requisitos entre itens
```

### Migration (10 passos sequenciais)

```
1–7.   CREATE TABLE (todas as novas tabelas)
8.     INSERT dados de checklist_templates → phase_template_checklist_items
9.     ALTER safra_checklist_itens (novo FK, remove legado)
10.    DROP TABLE checklist_templates
```

---

## 🔌 API (FastAPI)

```
/templates/phase/            → CRUD + duplicate
/templates/phase/{id}/checklist/  → CRUD de itens
/templates/phase/{id}/tasks/      → CRUD de tarefas
/templates/phase/{id}/gate/       → GET/PUT gate rule

/templates/operations/       → CRUD
/templates/operations/{id}/items/ → CRUD de itens

/templates/apply/phase       → POST: instancia PhaseTemplate na safra
/templates/apply/operations  → POST: instancia OperationTemplate na safra
```

### Regra de Ouro da instanciação

- Template nunca é alterado ao aplicar
- PhaseTemplate gera: `SafraChecklistItem` + `SafraTarefa (origem=TEMPLATE)`
- OperationTemplate gera: `SafraTarefa (origem=TEMPLATE)` por item com `can_generate_task=true`

---

## 🖥️ Frontend (Next.js + shadcn/ui)

### Rotas

```
/agricola/templates/           → listagem (Tabs: Fase | Operações)
/agricola/templates/novo       → wizard criação
/agricola/templates/[id]       → editor (Tabs: Checklist | Tarefas | Gate Rules)
```

### Componentes-chave

- `<DataTable>` com busca + PDF + Excel (padrão do projeto)
- `<Sheet side="right">` para aplicar template na safra (não Dialog)
- `<Tabs>` shadcn no editor — Checklist / Tarefas / Gate Rules
- Botões: `variant="outline" size="sm"` / ações ghost `size="icon"` sem header de coluna
- `rounded-sm` em todos os cards e inputs

---

## 🧪 Testes

### Backend (pytest — TDD)

```
test_phase_template_crud.py       → CRUD + duplicate + filtros
test_apply_phase_template.py      → instanciação + idempotência + isolamento tenant
test_operation_template_crud.py   → CRUD + dependências
test_apply_operation_template.py  → geração de tarefas + custo estimado
test_gate_integration.py          → gate base sempre válido + extras do template
```

### E2E (Playwright)

```
phase-template.spec.ts   → CRUD via UI, duplicar global, desativar
apply-template.spec.ts   → aplicar na safra, verificar instâncias criadas
```

---

## 📋 Decision Log

| # | Decisão | Motivo |
|---|---|---|
| D1 | Módulo próprio `agricola/templates/` | Responsabilidade única; testável isolado |
| D2 | Migração total de `checklist_templates` | Sem dívida técnica; projeto em construção |
| D3 | Seleção explícita sempre | Controle total do usuário; sem surpresas de governança |
| D4 | Gera apenas `SafraTarefa` | Regra de Ouro: template não executa |
| D5 | `Sheet` para aplicar template | Preview longo; não bloqueia o contexto |
| D6 | Gate hardcoded + template adiciona extras | Integridade garantida mesmo sem template |
| D7 | Migration Alembic 10 passos sequenciais | Banco único de truth; sem ambiguidade |

---

## ✔️ Critérios de Aceite

- [ ] Criar template de fase (checklist + tarefas + gate rules)
- [ ] Criar template de operações (itens + dependências + custos)
- [ ] Aplicar template à safra (wizard + botão por fase ativa)
- [ ] Instanciar checklist/tarefas com `origem=TEMPLATE`
- [ ] Gate rules adicionais integradas ao gate existente
- [ ] Editar instância sem alterar o template original
- [ ] Clonar template global como template do tenant
- [ ] Backoffice gerencia templates globais (`is_system_default=true`)

---

> 🔥 **Template não executa. Template gera estrutura executável.**
