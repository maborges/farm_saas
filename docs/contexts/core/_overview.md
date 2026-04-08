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

Este módulo implementa o modelo de dados central da plataforma, incluindo multi-tenancy com isolamento rigoroso de dados, RBAC granular com perfis por fazenda, gestão de propriedades rurais com hierarquia de áreas, configurações globais customizáveis, sistema de notificações multi-canal, integrações essenciais e controle de planos/assinaturas com feature flags.

## Submódulos

| # | Submódulo | Complexidade | Descrição curta |
|---|-----------|--------------|-----------------|
| 1 | [Identidade e Acesso](identidade-acesso.md) | L | Autenticação JWT, RBAC com perfis por fazenda, 2FA TOTP, auditoria de sessões |
| 2 | [Cadastro da Propriedade](cadastro-propriedade.md) | M | Registro de fazendas com NIRF/CAR, hierarquia de talhões, georreferenciamento |
| 3 | [Multipropriedade](multipropriedade.md) | M | Gestão de portfólio de fazendas, isolamento por propriedade, dashboards consolidados |
| 4 | [Configurações Globais](configuracoes-globais.md) | S | Ano agrícola, unidades (ha/alqueire), moeda, fuso horário, categorias customizáveis |
| 5 | [Notificações e Alertas](notificacoes-alertas.md) | M | Push, e-mail, SMS, alertas de vencimento, estoque crítico, condições climáticas |
| 6 | [Integrações Essenciais](integracoes-essenciais.md) | L | API REST OAuth2, webhooks assinados, import/export CSV/XLSX |
| 7 | [Planos e Assinatura](planos-assinatura.md) | M | Tiers Essencial/Profissional/Enterprise, feature flags, billing Stripe/Asaas |

## Princípios Arquiteturais

1. **Multi-tenancy com Defense in Depth**: JWT carrega `tenant_id`; `BaseService` auto-injeta filtro de tenant em todas as queries; RLS no PostgreSQL como camada adicional de segurança.

2. **RBAC granular com contexto de fazenda**: Permissões por recurso e ação (`modulo:recurso:acao`), com override por fazenda via `FazendaUsuario.perfil_fazenda_id`. Flag `is_owner` concede bypass total (exceto billing).

3. **Isolamento de dados rigoroso**: Cada propriedade possui dados completamente isolados. Queries sempre incluem `tenant_id` + `fazenda_id`. Dashboards consolidados só no nível do assinante.

4. **Feature flags por plano**: Módulos e funcionalidades são habilitados/desabilitados conforme o plano contratado via `require_module()`.

5. **Audit trail completo**: Toda operação de escrita gera log de auditoria com `user_id`, `tenant_id`, `action`, `resource`, `timestamp`, `ip_address` e `payload_diff`.

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

- **Backend:** FastAPI + SQLAlchemy 2.0 async + Alembic + PostgreSQL 15+
- **Frontend:** Next.js 16 App Router + React 19 + shadcn/ui + Zustand + TanStack Query
- **Billing:** Stripe (cartão internacional) e Asaas (boleto/PIX — mercado brasileiro)
- **Notificações:** SMTP (SendGrid/SES), Firebase Cloud Messaging (push), Twilio (SMS)
- **Geolocalização:** Leaflet/MapLibre + tiles IBGE + shapefiles/KML/GeoJSON
- **Storage:** S3/MinIO para arquivos georreferenciados e documentos
- **Cache/Queue:** Redis para rate limiting e jobs assíncronos

## Convenções de Nomenclatura

- Tabelas no banco: `snake_case` no plural (ex: `fazendas`, `usuarios`, `perfis_acesso`)
- Classes Python: `PascalCase` (ex: `FazendaService`, `UsuarioSchema`)
- Rotas API: `kebab-case` (ex: `/api/v1/cadastro-propriedade`)
- Componentes React: `PascalCase` (ex: `FazendaForm`, `NotificationCenter`)
- Enums no banco: `snake_case` (ex: `ativo`, `inativo`, `pendente`)

## Fluxo de Onboarding de Novo Tenant

1. **Cadastro inicial:** Usuário cria conta com e-mail/senha → `Tenant` é criado com status `trial`.
2. **Configuração wizard:** Ano agrícola, unidade de área, moeda, fuso horário, categorias padrão.
3. **Primeira fazenda:** Cadastro de propriedade com dados legais (CNPJ/CPF, CAR, área total).
4. **Convite de equipe:** Owner convida primeiros usuários com perfis de acesso.
5. **Trial de 14 dias:** Acesso completo a todos os módulos nível Enterprise.
6. **Conversão:** Seleção de plano (Essencial/Profissional/Enterprise) e configuração de billing.

## Modelo de Dados Central

```
Tenant (1) ── (N) Usuario
Tenant (1) ── (N) Fazenda
Tenant (1) ── (1) ConfiguracaoTenant
Tenant (1) ── (1) Assinatura
Tenant (1) ── (N) PerfilAcesso
Fazenda (1) ── (N) Talhao
Fazenda (1) ── (N) FazendaUsuario
Usuario (1) ── (N) FazendaUsuario
PerfilAcesso (1) ── (N) Permissao
```
