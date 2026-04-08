# Auditoria UX/UI — AgroSaaS vs AEGRO
> Data: 2026-04-02 | Auditor: Claude Code (análise estática de código + benchmarking competitivo)

---

## TL;DR — Diagnóstico Executivo

O sistema tem **arquitetura técnica sólida** e **componentes de boa qualidade** (shadcn/ui, EmptyState, sidebar configurável). Porém, do ponto de vista do **produtor rural** que vai usar isso pela primeira vez, há três problemas críticos que explicam por que o AEGRO ganha em "curva de aprendizado baixa":

| # | Problema | Impacto | Esforço |
|---|---------|---------|---------|
| P1 | **30 páginas mostram "Em Desenvolvimento"** — usuário bate em dead ends | Crítico | Médio |
| P2 | **Navegação excessivamente complexa** — sidebar com 5 níveis de hierarquia | Alto | Médio |
| P3 | **Sem onboarding guiado** — usuário novo não sabe por onde começar | Alto | Alto |

---

## 1. Análise Competitiva de UX

### Por que o AEGRO tem curva de aprendizado baixa

Com base na análise competitiva (`_competitive-analysis.md`) e no que foi levantado no código:

| Critério | AEGRO | AgroSaaS (atual) | Gap |
|----------|-------|-----------------|-----|
| Tela inicial (0 dados) | Dashboard com checklist de setup | Dashboard sem guia | ❌ Grande |
| Navegação | Flat, orientada a tarefas | Hierárquica por módulo técnico | ❌ Médio |
| Páginas ativas vs placeholder | ~90% funcionais | ~65% funcionais (30 dead ends) | ❌ Grande |
| Mobile | App offline-first maduro | Sidebar desktop-first | ⚠️ Médio |
| Primeiro uso | Wizard de onboarding | Fluxo de billing → dashboard vazio | ❌ Grande |
| Terminologia | Linguagem do produtor | Mix técnico/agronômico | ⚠️ Pequeno |
| Feedback de ação | Toasts contextuais | Não avaliado no código | ? |

---

## 2. Problemas Encontrados (por criticidade)

### 🔴 CRÍTICO — P1: 30 páginas com "Em Desenvolvimento"

**Páginas que retornam `<EmDesenvolvimento />` ao usuário:**

**Agrícola:**
- `/dashboard/agricola/safras` ← safras é o coração do módulo!
- `/dashboard/agricola/custos`
- `/dashboard/agricola/fenologia`
- `/dashboard/agricola/beneficiamento`

**Financeiro:**
- `/dashboard/financeiro/fluxo-caixa` ← funcionalidade central
- `/dashboard/financeiro/contas-pagar`
- `/dashboard/financeiro/contas-bancarias`
- `/dashboard/financeiro/lcdpr`
- `/dashboard/financeiro/nf-e`
- `/dashboard/financeiro/esocial`
- `/dashboard/financeiro/romaneios`

**Operacional:**
- `/dashboard/operacional/estoque`
- `/dashboard/operacional/frota`
- `/dashboard/operacional/manutencoes`
- `/dashboard/operacional/movimentacoes`
- `/dashboard/operacional/pedidos-compra`
- `/dashboard/operacional/fornecedores`

**RH:**
- `/dashboard/rh/colaboradores`
- `/dashboard/rh/departamentos`
- `/dashboard/rh/folha-pagamento`
- `/dashboard/rh/ponto`
- `/dashboard/rh/esocial`

**Ambiental:**
- `/dashboard/ambiental` (página raiz!)
- `/dashboard/ambiental/car/areas`
- `/dashboard/ambiental/car/importar`
- `/dashboard/ambiental/car/lista`
- `/dashboard/ambiental/monitoramento/mapa`
- `/dashboard/ambiental/monitoramento/historico`
- `/dashboard/ambiental/monitoramento/alertas`
- `/dashboard/ambiental/outorgas`

**Impacto:** Um usuário que contrata o sistema, vê itens no menu, clica — e encontra "Em Desenvolvimento" — gera churn imediato. **O menu não deveria mostrar o que não está pronto.**

**Solução:** Ocultar no sidebar itens sem implementação real (via feature flag `COMING_SOON`), ou substituir por "preview" com formulário de interesse.

---

### 🔴 CRÍTICO — P2: Duas implementações de sidebar em paralelo

**Problema detectado no código:**
- `apps/web/src/components/layout/sidebar.tsx` — sidebar escura (`bg-slate-900`), antiga, com lógica própria de collapse
- `apps/web/src/components/layout/app-sidebar.tsx` — nova, baseada em shadcn `<Sidebar>`, com `sidebar-config.ts`

São dois componentes ativos com comportamento diferente. Isso gera:
- Inconsistência visual para o usuário (dependendo de qual rota usa qual)
- Duplicação de lógica de permissão e navegação
- Manutenção dobrada

**Solução:** Migrar 100% para `app-sidebar.tsx` + `sidebar-config.ts` e remover `sidebar.tsx`.

---

### 🔴 CRÍTICO — P3: Sem onboarding guiado pós-ativação

**O que existe:** `/onboarding/ativar`, `/onboarding/sucesso`, `/onboarding/cancelado` — são páginas do fluxo de **billing** (Stripe/Asaas), não de **configuração inicial do sistema**.

**O que falta:** Após o pagamento, o usuário cai num dashboard potencialmente vazio sem saber o que fazer. O AEGRO tem um checklist de setup que guia o usuário pelos primeiros passos.

**Por que isso importa:** Um produtor rural de 50+ anos que nunca usou um sistema de gestão precisa de uma mão para começar. Sem isso, o churn na primeira semana é alto.

---

### 🟡 ALTO — P4: Navegação orientada ao sistema, não ao usuário

**Estrutura atual do sidebar:**
```
Cadastros Principais
  ├── Pessoas & Parceiros
  ├── Propriedades & Áreas
  ├── Equipamentos & Frota
  ├── Commodities
  └── Catálogo de Produtos
Tabelas Auxiliares
  ├── Marcas
  ├── Modelos
  └── Categorias de Produto
Agricultura (collapsible)
  ├── Dashboard
  ├── Planejamento (...)
  ├── Operações (...)
  ├── Monitoramento (...)
  └── Resultados (...)
Pecuária (collapsible)
  └── (seções)
Financeiro (collapsible)
  └── (seções)
Operacional (collapsible)
  └── (seções)
RH (collapsible)
  └── (seções)
Ambiental (collapsible)
  └── (seções)
Backoffice (apenas admin)
  └── 6 seções
Gestão de Acessos
  ├── Minhas Fazendas
  ├── Equipe
  ├── Perfis e Permissões
  └── Grupos de Fazendas
Configurações
  ├── Minha Conta
  ├── Base de Conhecimento
  ├── Configuração de E-mail
  └── Ajuda e Suporte
```

**Problemas:**
- "Tabelas Auxiliares" (Marcas, Modelos, Categorias) não é uma tarefa do produtor — é configuração interna. Não deveria estar no menu principal.
- O usuário precisa expandir módulo → seção → clicar item: **3 cliques para qualquer tarefa**
- Nomes como "Fenologia", "NDVI", "Apontamento" são técnicos. AEGRO usa linguagem mais próxima do produtor.

---

### 🟡 ALTO — P5: Ausência de contexto da fazenda ativa

**O que existe:** `context-selector.tsx` e `tenant-switcher.tsx` — bom que existam.

**Problema:** Em um sistema multi-fazenda, o usuário precisa saber **em qual fazenda está trabalhando** em todas as telas. Se isso não estiver sempre visível no topo (topbar ou sidebar header), o usuário pode lançar dados na fazenda errada — uma dor muito real.

**Solução:** O nome da fazenda ativa deve aparecer de forma destacada no topo da sidebar ou topbar, com indicador visual claro (cor, ícone).

---

### 🟡 ALTO — P6: Ausência de "ação rápida" global

**Problema:** Tarefas repetitivas do dia a dia (registrar operação de campo, lançar despesa, abastecer trator) exigem navegar pela hierarquia. O AEGRO e outros sistemas maduros têm um botão "+" global (Quick Add / FAB) para as 5 ações mais comuns.

**Solução:** Botão flutuante ou menu de ações rápidas no topbar para as ações mais frequentes por módulo ativo.

---

### 🟡 ALTO — P7: Dashboard vazio sem KPIs contextuais

**Problema:** O dashboard agrícola (`dashboard-kpis.tsx` existe) mas quando não há dados, a experiência de "primeiro uso" é desconhecida. Um dashboard vazio sem guia de próximos passos é frustrante.

**Solução:** Dashboard com estado de "primeiros passos" que mostra um checklist progressivo enquanto o usuário não tem safras/animais/lançamentos registrados.

---

### 🟢 MÉDIO — P8: Responsividade mobile não priorizada

**Evidência no código:**
- `sidebar.tsx` tem `w-64` fixo com botão de colapsar — padrão desktop
- A maioria dos componentes usa classes desktop-first

**Por que importa:** Operadores de campo usam tablets e celulares na lavoura. O AEGRO tem app mobile offline-first. Não precisamos do app agora, mas o web precisa ser responsivo.

---

### 🟢 MÉDIO — P9: Falta de breadcrumb nas páginas internas

**Problema:** Em rotas profundas como `/agricola/safras/[id]/operacoes`, o usuário não sabe onde está nem como voltar para um nível acima sem usar o botão "voltar" do browser.

**Solução:** Breadcrumb consistente no topo de todas as páginas de detalhe.

---

### 🟢 MÉDIO — P10: Terminologia mista

**Exemplos encontrados no sidebar-config:**
- "Índices de Vegetação (NDVI)" — bom, explica
- "Fenologia" — técnico, sem explicação
- "Apontamento" — ambíguo
- "Tabelas Auxiliares" — linguagem interna de sistema

**Solução:** Glossário de termos + tooltips contextuais nos itens de menu menos óbvios.

---

## 3. O Que Está Bom (preservar)

- ✅ `EmptyState` — bem implementado com ação clara obrigatória
- ✅ `sidebar-config.ts` — centralização da configuração do menu é a abordagem certa
- ✅ `ModuleGate` — controle de feature flags no frontend existe
- ✅ Shadcn/ui — sistema de design consistente e acessível por padrão
- ✅ `context-selector` e `tenant-switcher` — multi-fazenda contemplado
- ✅ `notification-bell` — alertas existem
- ✅ Estrutura de `app/(dashboard)` — App Router bem organizado
- ✅ Zod schemas compartilhados — formulários com validação consistente

---

## 4. Plano de Ação por Fases

### FASE 1 — "Não quebre o que funciona" (1-2 semanas)
**Objetivo:** Eliminar dead ends e inconsistências que prejudicam a primeira impressão

| Tarefa | Arquivo(s) | Esforço |
|--------|-----------|---------|
| F1.1 — Ocultar no sidebar os 30 itens sem implementação real | `sidebar-config.ts` | P |
| F1.2 — Migrar 100% para `app-sidebar.tsx`, remover `sidebar.tsx` | `layout/*.tsx` | M |
| F1.3 — Fazenda ativa sempre visível no topo da sidebar | `app-sidebar.tsx`, `topbar.tsx` | P |
| F1.4 — Breadcrumb universal nas páginas de detalhe | Novo `breadcrumb.tsx` | P |
| F1.5 — Mover "Tabelas Auxiliares" para Settings/Configurações | `sidebar-config.ts` | P |

> **P = Pequeno (< 4h) | M = Médio (4-8h) | G = Grande (> 1 dia)**

---

### FASE 2 — "Reduzir a curva de aprendizado" (3-4 semanas)
**Objetivo:** Chegar mais perto do AEGRO em intuitividade

| Tarefa | Detalhe | Esforço |
|--------|---------|---------|
| F2.1 — Onboarding wizard (5 passos) | Cadastrar fazenda → talhão → safra → primeiro lançamento → convidar colega | G |
| F2.2 — Dashboard com "primeiros passos" | Checklist visível até 100% completo | M |
| F2.3 — Quick Add global (FAB/botão +) | 5 ações mais comuns por módulo ativo | M |
| F2.4 — Simplificar navegação do sidebar | Reduzir para 2 níveis máximo, agrupar por tarefa | M |
| F2.5 — Tooltips em termos técnicos | NDVI, Fenologia, Apontamento, etc. | P |
| F2.6 — Páginas "Coming Soon" com formulário de interesse | Substituir `<EmDesenvolvimento />` por preview + notificação | P |

---

### FASE 3 — "Experiência de uso diário" (5-8 semanas)
**Objetivo:** Aumentar retenção com fluxos fluidos no dia a dia

| Tarefa | Detalhe | Esforço |
|--------|---------|---------|
| F3.1 — Mobile-first para páginas de campo | Registro de operação, checklist de equipamento, abastecimento | G |
| F3.2 — Ações rápidas contextuais | Botão "Nova Operação" dentro da tela de safra (não só no menu) | M |
| F3.3 — Notificações in-app melhoradas | Painel de notificações com ações diretas (não só sino) | M |
| F3.4 — Histórico recente / "Continuar de onde parou" | Últimas 5 telas visitadas no dashboard | P |
| F3.5 — Atalhos de teclado | Para usuários power (backoffice, financeiro) | M |

---

### FASE 4 — "Diferenciação vs AEGRO" (2-3 meses)
**Objetivo:** Superar o AEGRO em pontos onde temos vantagem técnica

| Tarefa | Diferencial | Esforço |
|--------|------------|---------|
| F4.1 — Dashboard personalizado (widgets drag-and-drop) | AEGRO não tem | G |
| F4.2 — Modo offline básico (PWA) | Service worker para formulários críticos | G |
| F4.3 — Onboarding assistido por IA | Chat de setup guiado pelo nosso LLM | G |
| F4.4 — Plataforma de aprendizado integrada | AEGRO tem cursos, nós podemos ter tutoriais contextuais | G |

---

## 5. Priorização Resumida (Quick Wins)

Se tiver apenas 1 semana para melhorar a UX agora, faça nesta ordem:

```
1. sidebar-config.ts → ocultar itens sem implementação (2h, impacto visual imediato)
2. app-sidebar.tsx → fazenda ativa destacada no header (2h, confiança do usuário)
3. Remover sidebar.tsx → unificar implementação (4h, consistência)
4. Breadcrumb universal (4h, reduz desorientação)
5. Tabelas Auxiliares → mover para Settings (1h, limpeza do menu)
```

**Total: ~13h de trabalho, impacto enorme na primeira impressão.**

---

## 6. Métricas para Medir Melhoria

| Métrica | Como medir | Meta |
|---------|------------|------|
| Tempo até primeira ação útil (TTFA) | Analytics: tempo do login até 1ª operação registrada | < 5 min |
| Taxa de conclusão do onboarding | Eventos: % que completa os 5 passos | > 70% |
| Dead ends por sessão | Logs: cliques em páginas EmDesenvolvimento | 0 |
| Churn semana 1 | CRM: % que cancela nos primeiros 7 dias | < 15% |
| NPS | Pesquisa in-app após 30 dias | > 40 |

---

## 7. Referências para Implementação

- **Onboarding wizard:** ver `/apps/web/src/app/onboarding/` como ponto de partida
- **Feature flags:** `ModuleGate` já existe — criar `FeatureFlag` com estado `COMING_SOON`
- **Sidebar config:** `/apps/web/src/lib/sidebar-config.ts` — adicionar campo `status: 'active' | 'coming_soon' | 'hidden'`
- **AEGRO UX inspiração:** foco em "tarefa" não em "módulo" — perguntar "o que o usuário quer fazer" não "em qual módulo isso está"
