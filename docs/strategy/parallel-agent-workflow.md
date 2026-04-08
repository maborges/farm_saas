---
tipo: guia-trabalho-paralelo
data_atualizacao: 2026-04-01
versao: 1.0
---

# Guia de Trabalho Paralelo para Agentes

## 1. Mapa de Agentes

| Agente | Módulo | Responsabilidade |
|--------|--------|-----------------|
| **Agent-Core** | Core | Base obrigatória — todos aguardam |
| **Agent-Agricola** | Agrícola | Safras, operações, NDVI, planejamento |
| **Agent-Pecuaria** | Pecuária | Rebanho, reprodução, sanidade, SISBOV |
| **Agent-Financeiro** | Financeiro | Lançamentos, fluxo caixa, DRE, crédito rural |
| **Agent-Estoque** | Estoque | Produtos, movimentações, FIFO, compras |
| **Agent-Frota** | Frota e Máquinas | Equipamentos, manutenção, telemetria |
| **Agent-Comercializacao** | Comercialização | Vendas, contratos, NF-e, CPR |
| **Agent-Pessoas** | Pessoas e RH | Colaboradores, folha, eSocial |
| **Agent-Rastreabilidade** | Rastreabilidade | Lotes, cadeia custódia, certificações |
| **Agent-Compliance** | Compliance Ambiental | CAR, APP, carbono, ESG |
| **Agent-Contabilidade** | Contabilidade | LCDPR, DRE, SPED, IRPF |

---

## 2. Arquivos que Cada Agente Deve Ler

### Todos os agentes (obrigatório):
```
CLAUDE.md
docs/strategy/module-architecture.md
docs/contexts/_module-dependency-graph.md
docs/contexts/core/_overview.md
docs/strategy/bundle-packages.md
```

### Por agente (além dos obrigatórios):

| Agente | Arquivos específicos |
|--------|---------------------|
| Agent-Core | `core/*.md` (todos) |
| Agent-Agricola | `agricola/**/*.md`, `core/cadastro-propriedade.md`, `core/configuracoes-globais.md` |
| Agent-Pecuaria | `pecuaria/**/*.md`, `core/cadastro-propriedade.md` |
| Agent-Financeiro | `financeiro/**/*.md`, `core/planos-assinatura.md` |
| Agent-Estoque | `estoque/**/*.md`, `financeiro/profissional/contas-pagar-receber.md` |
| Agent-Frota | `frota/**/*.md`, `estoque/essencial/movimentacoes.md` |
| Agent-Comercializacao | `comercializacao/**/*.md`, `financeiro/essencial/*.md`, `estoque/profissional/lotes-validade.md` |
| Agent-Pessoas | `pessoas/**/*.md`, `financeiro/profissional/centro-custo.md` |
| Agent-Rastreabilidade | `rastreabilidade/**/*.md`, `agricola/enterprise/rastreabilidade-campo.md`, `estoque/profissional/lotes-validade.md` |
| Agent-Compliance | `compliance/**/*.md`, `core/cadastro-propriedade.md`, `rastreabilidade/enterprise/certificacoes.md` |
| Agent-Contabilidade | `contabilidade/**/*.md`, `financeiro/**/*.md` |

---

## 3. Ordem de Execução em 3 Fases

### Fase 1 — Core (bloqueante)

```
Agent-Core
├── identidade-acesso (auth, RBAC, JWT, audit)
├── cadastro-propriedade (fazenda, talhão, geo)
├── multipropriedade (multi-tenant, seletor contexto)
├── configuracoes-globais (safra, unidades, categorias)
├── notificacoes-alertas (motor de notificações)
├── integracoes-essenciais (API, webhooks, import/export)
└── planos-assinatura (billing, feature flags)
```

**Critério de conclusão:** Todos os 7 submódulos do Core com testes passando + endpoints documentados no Swagger.

**Todos os demais agentes aguardam a conclusão da Fase 1.**

### Fase 2 — Módulos Essenciais (paralelo)

```
         ┌─────────────┐
         │  Core ✅     │
         └──────┬──────┘
    ┌───────┬───┴───┬────────┬──────────┐
    ▼       ▼       ▼        ▼          ▼
Agrícola Pecuária Financ. Estoque   Pessoas
  Ess.    Ess.     Ess.    Ess.      Ess.
    │       │       │        │          │
    ▼       ▼       ▼        ▼          ▼
  Frota  Comerc. Contab. Rastrea.  Compliance
  Ess.    Ess.    Ess.    Ess.      Ess.
```

**Todos os módulos Essenciais podem rodar em paralelo** — eles dependem apenas do Core.

**Pontos de sincronização na Fase 2:**
- Estoque Essencial deve estar pronto antes de Frota Essencial (abastecimento consome estoque)
- Financeiro Essencial deve estar pronto antes de Contabilidade Essencial (LCDPR consome lançamentos)

### Fase 3 — Profissional e Enterprise (paralelo por módulo)

Cada agente avança verticalmente dentro do seu módulo:

```
Agent-X: Essencial ✅ → Profissional → Enterprise
```

**Pontos de sincronização na Fase 3:**
- `Financeiro.Profissional` (centro de custo) antes de `Agrícola.Profissional` (custos por talhão)
- `Estoque.Profissional` (FIFO) antes de `Agrícola.Enterprise` (rastreabilidade campo)
- `Estoque.Profissional` (lotes) antes de `Rastreabilidade.Profissional` (cadeia custódia)
- `Comercialização.Profissional` (NF-e) antes de `Estoque.Enterprise` (integração fiscal)
- `Financeiro.Profissional` antes de `Contabilidade.Profissional` (DRE depende de lançamentos)

---

## 4. Convenções de Código e Nomenclatura

### Backend (Python/FastAPI)

```
services/api/
  {modulo}/
    models/         # SQLAlchemy models — PascalCase
    schemas/        # Pydantic schemas — PascalCase + sufixo (Create, Update, Response)
    services/       # Business logic — {Entidade}Service(BaseService[Entidade])
    routers/        # Endpoints — snake_case, prefixo /{modulo}/
    dependencies.py # Injeção de dependências
    __init__.py
```

**Regras:**
- Tabelas: `snake_case` plural (`movimentacoes_estoque`)
- Classes: `PascalCase` (`MovimentacaoEstoque`)
- Rotas: `kebab-case` (`/estoque/movimentacoes`)
- Serviços herdam de `BaseService[T]` — **nunca** queries raw em routers
- Tenant isolation via `get_tenant_id()` — **nunca** confiar em dados do frontend
- Feature gates via `require_module("MODULO")` e `require_tenant_permission()`

### Frontend (TypeScript/React)

```
apps/web/src/
  app/(dashboard)/{modulo}/
    page.tsx        # Página principal
    [id]/page.tsx   # Detalhe
    layout.tsx      # Layout do módulo
  components/{modulo}/
    {Componente}.tsx  # PascalCase
  hooks/{modulo}/
    use{Recurso}.ts   # camelCase com prefixo "use"
  lib/api/{modulo}.ts # API client
```

**Regras:**
- Componentes: `PascalCase` funcional
- Hooks: `use` + recurso (`useEstoqueSaldo`)
- API calls via TanStack Query
- State management via Zustand (stores por módulo)
- UI components via shadcn/ui

### Schemas Compartilhados

```
packages/zod-schemas/src/
  {modulo}/
    {entidade}.ts   # Zod schemas
  index.ts          # Re-exports
```

---

## 5. Protocolo de Conflito

Quando dois agentes tocam na mesma entidade ou tabela:

### Regra 1: Quem é dono da entidade?

| Entidade | Agente dono | Outros agentes |
|----------|-------------|---------------|
| `Fazenda` | Agent-Core | Read-only reference |
| `Produto` | Agent-Estoque | Agent-Agricola, Agent-Frota podem criar movimentações |
| `Lancamento` | Agent-Financeiro | Agent-Estoque, Agent-Comercializacao podem criar via integração |
| `Lote` | Agent-Estoque | Agent-Rastreabilidade pode ler e enriquecer metadata |
| `Colaborador` | Agent-Pessoas | Agent-Agricola, Agent-Frota podem referenciar |

### Regra 2: Protocolo de mudança compartilhada

1. Se precisar **alterar model** de outro agente → abrir issue com proposta (não alterar direto)
2. Se precisar **adicionar FK** para entidade de outro agente → usar `ForeignKey` com lazy loading
3. Se precisar **novo campo** em entidade de outro agente → propor via PR com justificativa
4. **Migrations:** Cada agente cria suas próprias. Conflitos resolvidos por order de merge.

### Regra 3: Comunicação entre módulos

- Via **Service calls** (importar Service do outro módulo, não chamar router)
- Via **Events/Signals** para ações assíncronas (ex: "estoque criou movimentação" → financeiro cria lançamento)
- **Nunca** duplicar lógica de negócio entre módulos

---

## 6. Checklist de Entrega por Agente

### Por submódulo (Essencial/Profissional/Enterprise):

- [ ] Models criados com migrations
- [ ] Schemas Pydantic (Create, Update, Response)
- [ ] Service herdando BaseService com regras de negócio
- [ ] Router com endpoints CRUD + específicos
- [ ] Router registrado em `main.py`
- [ ] Feature gate (`require_module`) configurado
- [ ] Permissões RBAC definidas
- [ ] Testes de isolamento multi-tenant
- [ ] Testes unitários do Service (regras de negócio)
- [ ] Testes de integração dos endpoints
- [ ] Zod schemas em `packages/zod-schemas`
- [ ] Páginas frontend (listagem + formulário + detalhe)
- [ ] API hooks via TanStack Query
- [ ] Documentação OpenAPI atualizada

### Por fase:

**Fase 1 (Core):**
- [ ] Todos os 7 submódulos do Core implementados
- [ ] Auth + RBAC testados end-to-end
- [ ] Multi-tenant isolation comprovado
- [ ] Feature flags funcionais
- [ ] Billing com Stripe/Asaas integrado

**Fase 2 (Essenciais):**
- [ ] CRUD básico de cada módulo funcional
- [ ] Integração entre módulos testada (ex: estoque → financeiro)
- [ ] Frontend navegável para todas as funcionalidades essenciais
- [ ] Seed data para demonstração

**Fase 3 (Profissional + Enterprise):**
- [ ] Funcionalidades avançadas implementadas
- [ ] Relatórios e dashboards disponíveis
- [ ] Integrações externas configuráveis
- [ ] Performance testada com volume realista
- [ ] Documentação de usuário por módulo

---

## 7. Referências Cruzadas

| Documento | Localização |
|-----------|-------------|
| Arquitetura Modular | [`../strategy/module-architecture.md`](module-architecture.md) |
| Pacotes de Assinatura | [`../strategy/bundle-packages.md`](bundle-packages.md) |
| Dependências entre Módulos | [`../contexts/_module-dependency-graph.md`](_module-dependency-graph.md) |
| Índice de Contextos | [`../contexts/_index.md`](_index.md) |
| Manual Técnico | [`../../docs/architecture/AgroSaaS-Manual.md`](../../docs/architecture/AgroSaaS-Manual.md) |

---

**Documento gerado em:** 2026-04-01
**Próxima revisão:** 2026-07-01 (trimestral)
**Responsável:** Engineering Team AgroSaaS
