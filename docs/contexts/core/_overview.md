---
modulo: Core
nivel: core
core: true
descricao: Módulo Core — fundação transversal da plataforma AgroSaaS
dependencias_core: []
dependencias_modulos: []
---

# Core — Visão Geral do Módulo

## Propósito

O módulo **Core** é a fundação obrigatória da plataforma AgroSaaS. Ele fornece toda a infraestrutura transversal que os módulos de negócio (Agrícola, Pecuária, Financeiro, Operacional, Imóveis) consomem para funcionar. Nenhum módulo pode operar sem o Core ativo.

## Submódulos

| # | Submódulo | Complexidade | Descrição curta |
|---|-----------|--------------|-----------------|
| 1 | [Identidade e Acesso](identidade-acesso.md) | L | Autenticação, autorização RBAC, auditoria |
| 2 | [Cadastro da Propriedade](cadastro-propriedade.md) | M | Registro de fazendas, hierarquia de áreas, geolocalização |
| 3 | [Multipropriedade](multipropriedade.md) | M | Gestão de múltiplas fazendas por assinante, isolamento de dados |
| 4 | [Configurações Globais](configuracoes-globais.md) | S | Ano agrícola, unidades de medida, moeda, fuso horário |
| 5 | [Notificações e Alertas](notificacoes-alertas.md) | M | Push, e-mail, SMS, central de notificações |
| 6 | [Integrações Essenciais](integracoes-essenciais.md) | L | API REST OAuth2, webhooks, import/export CSV/XLSX |
| 7 | [Planos e Assinatura](planos-assinatura.md) | M | Controle de plano ativo, feature flags, limites operacionais |

## Princípios Arquiteturais

1. **Multi-tenancy com Defense in Depth**: JWT carrega `tenant_id`; `BaseService` injeta filtro de tenant em todas as queries; RLS no PostgreSQL como camada adicional.
2. **RBAC granular**: Permissões por recurso e ação, com override por fazenda via `FazendaUsuario.perfil_fazenda_id`.
3. **Isolamento de dados**: Cada propriedade possui dados completamente isolados; dashboards consolidados só no nível do assinante.
4. **Feature flags por plano**: Módulos e funcionalidades são habilitados/desabilitados conforme o plano contratado.

## Relação com Outros Módulos

```
┌─────────────────────────────────────────────┐
│                   CORE                      │
│  Auth │ Propriedade │ Config │ Billing      │
│  RBAC │ Multi-prop  │ Notif  │ Integrações  │
└────────────────┬────────────────────────────┘
                 │ fornece identidade, tenant,
                 │ permissões, configurações
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐ ┌─────────┐ ┌───────────┐
│Agrícola│ │Pecuária │ │Financeiro │
└────────┘ └─────────┘ └───────────┘
    ▲            ▲            ▲
    └────────────┼────────────┘
                 │
         ┌───────┴───────┐
         │ Operacional   │
         │ Imóveis       │
         └───────────────┘
```

## Tecnologias Envolvidas

- **Backend:** FastAPI + SQLAlchemy 2.0 async + Alembic + PostgreSQL
- **Frontend:** Next.js 16 App Router + React 19 + shadcn/ui + Zustand
- **Billing:** Stripe e Asaas
- **Notificações:** SMTP (e-mail), Firebase Cloud Messaging (push), Twilio (SMS)
- **Geolocalização:** Leaflet/MapLibre + shapefiles/KML

## Convenções de Nomenclatura

- Tabelas no banco: `snake_case` no plural (ex: `fazendas`, `usuarios`, `perfis_acesso`)
- Classes Python: `PascalCase` (ex: `FazendaService`, `UsuarioSchema`)
- Rotas API: `kebab-case` (ex: `/api/v1/cadastro-propriedade`)
- Componentes React: `PascalCase` (ex: `FazendaForm`, `NotificationCenter`)
