# Brainstorm — Reorganização do Backoffice Admin

**Data:** 2026-03-22
**Status:** Concluído (Fases 1–6 todas implementadas)

## Problema

A área administrativa (backoffice) do AgroSaaS tinha:
- Menu plano com 11 itens sem agrupamento lógico
- Visibilidade restrita apenas a `is_superuser` (outros roles de backoffice não viam nada)
- Páginas faltando: cupons, audit logs, email templates, sessões ativas
- Funcionalidade nova necessária: módulo CRM
- Nomenclatura confusa nos itens do menu

## Decisão: Abordagem C (Híbrida)

Menu agrupado por domínio com filtragem por permissão individual.

## 6 Seções do Menu

| Seção | Itens | Roles |
|---|---|---|
| Visão Geral | Dashboard Executivo, BI | todos (BI: admin+, fin) |
| Comercial | Assinantes, Planos & Preços, Cupons, CRM | admin+, comercial |
| Financeiro | Faturamento, Mudanças de Plano | admin+, financeiro |
| Suporte | Chamados, Base de Conhecimento | admin+, suporte |
| Controle de Acesso | Usuários, Equipe Backoffice, Perfis | admin+, super_admin |
| Sistema | Configurações, Auditoria, Email Templates, Sessões | super_admin |

## Fases de Implementação

- [x] **Fase 1** — Reorganizar sidebar em 6 seções + filtro por permissão
- [x] **Fase 2** — Criar página `/backoffice/cupons` (backend pronto)
- [x] **Fase 3** — Criar router + página de Audit Logs
- [x] **Fase 4** — Criar router + página de Email Templates
- [x] **Fase 5** — Criar router + página de Sessões Ativas
- [x] **Fase 6** — Criar módulo CRM completo (models → router → frontend)

## Arquivos Criados/Modificados

### Frontend
- `apps/web/src/lib/permissions.ts` — Permissões expandidas para todos os roles
- `apps/web/src/components/layout/app-sidebar.tsx` — Componente BackofficeNav com 6 seções
- `apps/web/src/app/(dashboard)/backoffice/cupons/page.tsx` — Página de cupons (NOVO)
- `apps/web/src/app/(dashboard)/backoffice/audit/page.tsx` — Logs de auditoria (NOVO)
- `apps/web/src/app/(dashboard)/backoffice/email-templates/page.tsx` — Templates de email (NOVO)
- `apps/web/src/app/(dashboard)/backoffice/sessions/page.tsx` — Sessões ativas (NOVO)
- `apps/web/src/app/(dashboard)/backoffice/crm/page.tsx` — Página CRM Kanban + Lista (NOVO)

### Backend
- `services/api/core/models/crm.py` — Models PipelineEstagio, LeadCRM, AtividadeCRM (NOVO)
- `services/api/core/models/__init__.py` — Registro dos models CRM
- `services/api/core/routers/backoffice_audit.py` — Router auditoria (NOVO)
- `services/api/core/routers/backoffice_email_templates.py` — Router email templates (NOVO)
- `services/api/core/routers/backoffice_sessions.py` — Router sessões (NOVO)
- `services/api/core/routers/backoffice_crm.py` — Router CRM completo (NOVO)
- `services/api/main.py` — Registro dos 4 novos routers

## Observações Técnicas

- Backend de cupons não tem endpoint PUT (edição) — só POST, GET, DELETE
- `AdminAuditLog` model usa campo `entidade`, mas routers existentes escrevem `recurso` (mismatch)
- CRM: 3 tabelas (crm_pipeline_estagios, crm_leads, crm_atividades) — precisa rodar migration Alembic
- CRM frontend: Kanban board + lista com filtros, sheet de detalhes, atividades inline
