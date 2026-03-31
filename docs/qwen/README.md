# AgroSaaS - Documentação Completa

**Bem-vindo à documentação oficial do AgroSaaS**

Esta pasta contém a documentação técnica completa do sistema AgroSaaS, organizada por tópicos para facilitar a consulta e o entendimento do contexto.

---

## 📚 Índice de Documentos

### Documentação Principal

| # | Arquivo | Título | Descrição |
|---|---------|--------|-----------|
| 01 | [`01-arquitetura.md`](./01-arquitetura.md) | **Arquitetura do Sistema** | Visão geral da arquitetura, stack tecnológico, monolito modular, multi-tenancy, RBAC |
| 02 | [`02-modulos.md`](./02-modulos.md) | **Módulos do Sistema** | Detalhamento completo de todos os módulos (Agrícola, Pecuária, Financeiro, Operacional, RH, Ambiental) |
| 03 | [`03-banco-dados.md`](./03-banco-dados.md) | **Banco de Dados** | Schema completo do banco, models, migrações, padrões de modelagem |
| 04 | [`04-frontend.md`](./04-frontend.md) | **Frontend (Next.js)** | Arquitetura frontend, componentes, hooks, gerenciamento de estado, feature flags |
| 05 | [`05-api.md`](./05-api.md) | **API Reference** | Documentação completa de todos os endpoints da API |
| 06 | [`06-permissoes.md`](./06-permissoes.md) | **Permissões e RBAC** | Catálogo de permissões, roles, feature gates, hierarquia |
| 07 | [`07-ui-ux.md`](./07-ui-ux.md) | **UI/UX Guidelines** | Sistema de design, componentes, cores, tipografia, acessibilidade |
| 08 | [`08-infra.md`](./08-infra.md) | **Infraestrutura** | Deploy, CI/CD, monitoramento, backup, escalabilidade, troubleshooting |
| 09 | [`09-dependencias.md`](./09-dependencias.md) | **Dependências e Impacto** | Matriz de dependências entre módulos, fluxo de dados, impacto de mudanças |

---

## 🎯 Como Usar Esta Documentação

### Para Novos Desenvolvedores

1. **Comece por:** `01-arquitetura.md` - Entenda a visão geral do sistema
2. **Em seguida:** `02-modulos.md` - Conheça os módulos e suas responsabilidades
3. **Dependendo da sua função:**
   - **Backend:** `03-banco-dados.md` → `05-api.md`
   - **Frontend:** `04-frontend.md` → `07-ui-ux.md`
   - **DevOps:** `08-infra.md`
   - **Todos:** `06-permissoes.md`

### Para Consultas Específicas

| Preciso saber sobre... | Vá para... |
|------------------------|------------|
| Estrutura de pastas | `01-arquitetura.md` → Seção 6 |
| Como criar um novo módulo | `02-modulos.md` → Seção 1 + `docs/architecture/MODULO_TEMPLATE.md` |
| Schema de uma tabela | `03-banco-dados.md` → Seção do módulo correspondente |
| Endpoint da API | `05-api.md` → Seção do módulo |
| Permissões necessárias | `06-permissoes.md` → Catálogo de Permissões |
| Componentes UI | `07-ui-ux.md` → Seção 4 |
| Deploy em produção | `08-infra.md` → Seção 3 |

---

## 🔗 Dependências entre Documentos

```
┌─────────────────────────────────────────────────────────────────┐
│                    01-arquitetura.md                            │
│                    (Documento Base)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐   ┌──────────────┐
│ 02-modulos   │    │ 03-banco-dados   │   │ 04-frontend  │
│              │    │                  │   │              │
│ Depende de:  │    │ Depende de:      │   │ Depende de:  │
│ - Arquitetura│    │ - Arquitetura    │   │ - Arquitetura│
│              │    │ - Módulos        │   │ - Módulos    │
└──────────────┘    └──────────────────┘   └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   05-api.md      │
                    │                  │
                    │ Depende de:      │
                    │ - Módulos        │
                    │ - Banco de Dados │
                    │ - Frontend       │
                    └──────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐   ┌──────────────┐
│ 06-permissoes│    │ 07-ui-ux         │   │ 08-infra     │
│              │    │                  │   │              │
│ Depende de:  │    │ Depende de:      │   │ Depende de:  │
│ - Arquitetura│    │ - Frontend       │   │ - Arquitetura│
│ - Módulos    │    │ - Módulos        │   │ - Banco Dados│
└──────────────┘    └──────────────────┘   └──────────────┘
```

---

## 📋 Matriz de Rastreabilidade

### Quando modificar um módulo...

| Módulo | Verificar documentos | Impacto |
|--------|---------------------|---------|
| **CORE** | Todos | Alto - Afeta todo o sistema |
| **Agrícola** | 02, 03, 05, 06 | Médio - Integra com Financeiro, Operacional |
| **Pecuária** | 02, 03, 05, 06 | Médio - Integra com Financeiro |
| **Financeiro** | 02, 03, 05, 06 | Alto - Recebe dados de todos módulos |
| **Operacional** | 02, 03, 05, 06 | Médio - Fornece para outros módulos |
| **RH** | 02, 03, 05, 06 | Baixo - Integra apenas com Financeiro |

### Quando modificar...

| Alteração | Documentos a atualizar |
|-----------|----------------------|
| Adicionar endpoint | 05-api.md, 06-permissoes.md |
| Nova tabela no banco | 03-banco-dados.md, 02-modulos.md |
| Novo componente UI | 07-ui-ux.md, 04-frontend.md |
| Nova permissão | 06-permissoes.md, 05-api.md |
| Mudança de infra | 08-infra.md, 01-arquitetura.md |

---

## 🔍 Busca Rápida por Tópicos

### Arquitetura e Conceitos

- **Monolito Modular:** `01-arquitetura.md` → Seção 3
- **Multi-Tenancy:** `01-arquitetura.md` → Seção 4
- **RBAC:** `01-arquitetura.md` → Seção 5, `06-permissoes.md`
- **Feature Flags:** `01-arquitetura.md` → Seção 5, `04-frontend.md` → Seção 8

### Módulos de Negócio

- **Agrícola (A1-A5):** `02-modulos.md` → Seção 3
- **Pecuária (P1-P4):** `02-modulos.md` → Seção 4
- **Financeiro (F1-F4):** `02-modulos.md` → Seção 5
- **Operacional (O1-O3):** `02-modulos.md` → Seção 6
- **RH (RH1-RH2):** `02-modulos.md` → Seção 7

### Banco de Dados

- **Core Models:** `03-banco-dados.md` → Seção 2
- **Tabelas Agrícolas:** `03-banco-dados.md` → Seção 3
- **Tabelas Pecuária:** `03-banco-dados.md` → Seção 4
- **Tabelas Financeiro:** `03-banco-dados.md` → Seção 5
- **Migrações:** `03-banco-dados.md` → Seção 9

### API

- **Autenticação:** `05-api.md` → Seção 2
- **Core API:** `05-api.md` → Seção 3
- **API Agrícola:** `05-api.md` → Seção 4
- **API Pecuária:** `05-api.md` → Seção 5
- **API Financeiro:** `05-api.md` → Seção 6

### Frontend

- **Server Components:** `04-frontend.md` → Seção 2
- **Componentes:** `04-frontend.md` → Seção 4, `07-ui-ux.md` → Seção 4
- **Hooks:** `04-frontend.md` → Seção 6
- **Feature Flags:** `04-frontend.md` → Seção 8

### Infraestrutura

- **Deploy:** `08-infra.md` → Seção 3
- **CI/CD:** `08-infra.md` → Seção 5
- **Monitoramento:** `08-infra.md` → Seção 6
- **Backup:** `08-infra.md` → Seção 8

---

## 📖 Glossário

| Termo | Definição |
|-------|-----------|
| **Tenant** | Assinante do SaaS (fazenda/empresa) |
| **Safra** | Ciclo agrícola completo (plantio à colheita) |
| **Talhão** | Área/geleira de terra dentro da fazenda |
| **Romaneio** | Registro de colheita com pesos e qualidade |
| **Manejo** | Operação realizada em animais |
| **Rateio** | Distribuição de custos entre centros de custo |
| **Feature Gate** | Mecanismo de habilitar/desabilitar funcionalidades |
| **RSC** | React Server Component |
| **RBAC** | Role-Based Access Control |

---

## 🤝 Contribuindo

### Para adicionar nova documentação:

1. Criar arquivo em `docs/qwen/`
2. Seguir padrão de nomenclatura: `XX-nome-do-topico.md`
3. Adicionar referência neste README
4. Incluir seção de "Referências Cruzadas"

### Para atualizar documentação existente:

1. Verificar impacto em outros documentos (ver Matriz de Rastreabilidade)
2. Atualizar changelog no final do arquivo
3. Incrementar versão do documento

---

## 📝 Changelog da Documentação

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Criação inicial completa da documentação |

---

## 📞 Suporte

Para dúvidas sobre a documentação:
- **Slack:** `#docs`
- **Email:** tech@agrosaas.com.br

---

**Última atualização:** 2026-03-31
