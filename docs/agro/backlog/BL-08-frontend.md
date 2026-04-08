# BL-08 — Frontend (Settings & Estrutura Territorial)

**Módulo:** apps/web  
**Frente:** Frontend  
**Dependências:** BL-01, BL-02, BL-03, BL-04, BL-06  
**Estimativa:** 4 dias

---

## Contexto

Refatoração das páginas de Settings para o novo modelo.
Padrões existentes a respeitar: Sheet para formulários, PageHeader, EmptyState,
AreaTree (já existe), Badge de status, data-table para listas.

---

## User Stories

### US-08.1 — Página de Propriedades
**Como** gestor,  
**quero** gerenciar minhas propriedades em uma tela dedicada,  
**para** ter visão geral de toda a estrutura fundiária.

**Critérios de aceite:**
- [ ] Rota: `/dashboard/settings/propriedades`
- [ ] Cards por propriedade (não tabela): nome, tipo badge, área (ha), município/UF
- [ ] Badge status CAR: `Regular | Pendente | Não informado`
- [ ] Banner de uso do plano: "X de Y propriedades"
- [ ] Botão "Nova Propriedade" → Sheet de cadastro
- [ ] EmptyState com CTA quando sem propriedades
- [ ] Loading: skeleton dos cards

---

### US-08.2 — Formulário de Propriedade
**Como** gestor,  
**quero** cadastrar/editar uma propriedade em um formulário completo,  
**para** ter todos os dados regulatórios registrados.

**Critérios de aceite:**
- [ ] Sheet lateral (não modal) para não perder contexto
- [ ] Tabs no formulário: [Dados Gerais] [Localização] [Regulatório]
- [ ] CEP com lookup automático ao sair do campo
- [ ] CPF/CNPJ com lookup Receita Federal
- [ ] CAR com botão "Consultar SICAR" explícito
- [ ] Validação em tempo real (react-hook-form + zod)
- [ ] Toast de sucesso/erro

---

### US-08.3 — Estrutura Territorial (Gleba + Unidades)
**Como** gerente,  
**quero** visualizar e editar a estrutura interna de uma propriedade,  
**para** manter a hierarquia territorial atualizada.

**Critérios de aceite:**
- [ ] Rota: `/dashboard/settings/propriedades/[id]/estrutura`
- [ ] Layout 2 colunas: árvore (esquerda) + formulário contextual (direita como Sheet)
- [ ] Reutilizar componente `AreaTree` existente
- [ ] Adicionar filho ao selecionar nó: Sheet com form do tipo correto
- [ ] Formulário específico por tipo: Gleba / Talhão / Piquete / Área Funcional
- [ ] Drag-and-drop para reorganizar (fase 2)

---

### US-08.4 — Equipe & Acessos
**Como** gestor,  
**quero** gerenciar usuários e seus acessos por propriedade,  
**para** controlar quem vê o quê.

**Critérios de aceite:**
- [ ] Rota: `/dashboard/settings/team` (refatorar existente)
- [ ] Tabs: [Usuários] [Convites Pendentes]
- [ ] Lista de usuários com avatar, nome, perfil global
- [ ] Expandir usuário → mostra propriedades com acesso + vigência
- [ ] Botão "Gerenciar Acessos" → Sheet com checkboxes por propriedade
- [ ] Campos de vigência opcionais por propriedade
- [ ] Badge "Expira em X dias" para acessos temporários
- [ ] Convites: reenviar, cancelar

---

### US-08.5 — Componentes Compartilhados

- [ ] `PlanUsageBanner` — barra de progresso uso do plano
- [ ] `PropriedadeCard` — card reutilizável
- [ ] `PropriedadeSheet` — formulário em Sheet (create/edit)
- [ ] `EstruturaPage` — página de árvore territorial
- [ ] `AcessoDrawer` — Sheet de gerenciamento de acessos por usuário
- [ ] `VigenciaBadge` — badge de expiração de acesso
- [ ] Hooks: `usePropriedades()`, `usePropriedadeAcessos()`, `useConvites()`

---

## Tarefas Técnicas

### Frontend
- [ ] Refatorar `/dashboard/settings/fazendas` → `/settings/propriedades`
- [ ] Criar `/settings/propriedades/[id]/estrutura`
- [ ] Refatorar `/settings/team` para novo modelo de acessos
- [ ] Atualizar `fazendas-selector.tsx` → `propriedades-selector.tsx`
- [ ] Atualizar `area-tree.tsx` — verificar compatibilidade com novo schema
- [ ] Atualizar `fazendas-sync.tsx` em `/components/auth/`
- [ ] Atualizar sidebar-config para nova rota de propriedades
- [ ] Schemas Zod: `PropriedadeSchema`, `GlebaSchema`, `UnidadeOperacionalSchema`
