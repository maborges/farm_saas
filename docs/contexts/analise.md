## NOSSA APLICAÇÃO ATUAL
Leia o arquivo CLAUDE.md para entender nossa aplicação atual.


# MISSÃO: Análise Competitiva e Arquitetura de Documentação Modular
## Sistema de Gestão Agropecuária — Preparação para Desenvolvimento Paralelo

---

## CONTEXTO

Temos uma aplicação de gestão de fazendas agropecuárias em desenvolvimento.
Precisamos de uma análise competitiva profunda e geração de documentação estruturada
por módulo/submódulo para que múltiplos agentes possam trabalhar em paralelo.

---

## TAREFA 1 — ANÁLISE COMPETITIVA

Compare nossa aplicação com as **5 maiores plataformas de gestão agropecuária 
do Brasil** (ex: Aegro, Agrotools, GDR Agro, Agronow, Siagri/Totvs Agro).

Para cada concorrente, documente:
- Módulos e funcionalidades oferecidas
- Pontos fortes e diferenciais
- Limitações e gaps identificados
- Modelo de precificação (quando público)
- Perfil de cliente-alvo

Em seguida, gere uma **tabela comparativa de pontuação** (0–10) por categoria:
finanças, produção, estoque, rastreabilidade, compliance, UX/mobile, integrações,
suporte, preço, e funcionalidades exclusivas.

Por fim, liste **todas as melhorias e gaps** que nossa aplicação deve endereçar
para se tornar a mais completa do mercado brasileiro, priorizadas por:
1. Impacto na dor do assinante
2. Viabilidade técnica
3. Diferencial competitivo

---

## TAREFA 2 — MÓDULO CORE (BASE OBRIGATÓRIA)

Antes de mapear os demais módulos, defina o **Módulo Core** — o núcleo da plataforma
que deve estar 100% implementado para que qualquer outro módulo funcione.

O Core não é vendido separadamente: ele é a fundação técnica e operacional
incluída em todos os pacotes de assinatura.

### Submódulos obrigatórios do Core:

**Identidade e Acesso**
- Cadastro de usuários e perfis de acesso (RBAC)
- Autenticação (email/senha, SSO, 2FA)
- Gestão de sessões e dispositivos autorizados
- Log de auditoria de ações por usuário

**Cadastro da Propriedade**
- Cadastro da fazenda/propriedade (nome, CNPJ/CPF, inscrição estadual, CAR)
- Estrutura de áreas: fazenda → talhão → gleba (hierarquia configurável)
- Geolocalização e perímetro de áreas (integração com shapefile/KML)
- Cadastro de infraestrutura (silos, galpões, currais, equipamentos fixos)

**Multipropriedade e Multitenant**
- Suporte a um assinante com múltiplas propriedades
- Isolamento de dados por propriedade
- Painel unificado com visão consolidada entre propriedades
- Permissões específicas por propriedade para o mesmo usuário

**Configurações Globais**
- Ano agrícola / safra (definição e troca de contexto)
- Unidades de medida (configurável por propriedade: hectare, alqueire, etc.)
- Moeda e fuso horário
- Categorias e tabelas auxiliares customizáveis (tipos de cultura, raças, etc.)

**Notificações e Alertas**
- Motor de notificações (push, email, SMS configurável)
- Alertas por regra de negócio (vencimentos, estoques críticos, tarefas em atraso)
- Central de notificações in-app com histórico

**Integrações Essenciais**
- API pública REST com autenticação OAuth2 (base para todos os módulos se conectarem)
- Webhook engine (disparo de eventos para sistemas externos)
- Importação/exportação base em CSV e XLSX

**Planos e Assinatura**
- Controle de plano ativo do assinante
- Feature flags por plano (habilita/desabilita módulos e submódulos)
- Controle de limites (nº de propriedades, usuários, hectares, etc.)
- Histórico de assinaturas e upgrades

Para cada submódulo do Core, gere o arquivo de contexto completo
conforme o template da Tarefa 3, sinalizando `core: true` no frontmatter.

---

## TAREFA 3 — MAPEAMENTO DE MÓDULOS E SUBMÓDULOS

Com base na análise competitiva e nas dores dos assinantes, defina a arquitetura
completa de módulos e submódulos da aplicação (excluindo o Core já definido).

### Regra de categorização por nível de maturidade

Cada módulo deve ter seus submódulos organizados em **3 níveis de maturidade**,
usando a nomenclatura consolidada do mercado SaaS agropecuário brasileiro:

| Nível | Nome | Descrição |
|-------|------|-----------|
| 1 | **Essencial** | Funcionalidades mínimas para operação básica do módulo. Atende pequenos produtores e iniciantes. |
| 2 | **Profissional** | Funcionalidades intermediárias com automações, relatórios avançados e integrações. Atende fazendas médias com gestão estruturada. |
| 3 | **Enterprise** | Funcionalidades complexas: BI, multi-propriedade avançado, integrações fiscais/bancárias, rastreabilidade completa. Atende grandes operações e cooperativas. |

### Exemplo de aplicação (Módulo Financeiro):
```
Módulo: Financeiro
├── Essencial
│   ├── Lançamentos manuais de receitas e despesas
│   ├── Fluxo de caixa simples
│   └── Categorização básica de contas
├── Profissional
│   ├── Contas a pagar e receber com vencimentos
│   ├── Centro de custo por talhão/atividade
│   ├── Conciliação bancária manual
│   └── Relatórios DRE e Balanço simplificado
└── Enterprise
    ├── Conciliação bancária automática (Open Finance)
    ├── Integração com ERP e contabilidade externa
    ├── Gestão de crédito rural e financiamentos
    ├── Custo de produção por safra com rateio automático
    └── Multi-empresa com consolidação contábil
```

Para cada módulo, documente também:
- Descrição geral do módulo
- Dependências do Core (quais submódulos do Core são pré-requisito)
- Dependências de outros módulos (com referência ao arquivo)
- Pode ser contratado de forma isolada? (sim/não + justificativa)
- Perfis de assinante que mais se beneficiam por nível

---

## TAREFA 4 — GERAÇÃO DE DOCUMENTOS DE CONTEXTO

Para **cada módulo e cada submódulo**, gere um arquivo de contexto separado.

### Estrutura de pastas obrigatória:
```
docs/
  contexts/
    _index.md
    _competitive-analysis.md
    _module-dependency-graph.md
    _bundle-packages.md
    _parallel-agent-workflow.md
    core/
      _overview.md
      identidade-acesso.md
      cadastro-propriedade.md
      multipropriedade.md
      configuracoes-globais.md
      notificacoes-alertas.md
      integracoes-essenciais.md
      planos-assinatura.md
    [slug-do-modulo]/
      _overview.md
      _implantation-workflow.md
      essencial/
        [slug-do-submodulo].md
      profissional/
        [slug-do-submodulo].md
      enterprise/
        [slug-do-submodulo].md
```

### Template de frontmatter YAML para cada arquivo:
```yaml
---
modulo: [nome do módulo pai]
submodulo: [nome do submódulo]
nivel: essencial | profissional | enterprise | core
core: true | false
dependencias_core: [lista de slugs de submódulos do core]
dependencias_modulos: [lista de caminhos relativos de outros submódulos]
standalone: true | false
complexidade: XS | S | M | L | XL
assinante_alvo: [pequeno produtor | fazenda média | grande operação | cooperativa]
---
```

### Corpo obrigatório de cada arquivo de submódulo:
```markdown
## Descrição Funcional
## Personas — Quem usa este submódulo
## Dores que resolve
## Regras de Negócio
## Entidades de Dados Principais
## Integrações Necessárias
## Fluxo de Uso Principal (step-by-step)
## Casos Extremos e Exceções
## Critérios de Aceite (Definition of Done)
## Sugestões de Melhoria Futura
```

---

## TAREFA 5 — PACOTES DE ASSINATURA

Com base nos níveis (Essencial / Profissional / Enterprise) e nos perfis
de assinante, sugira **pelo menos 6 pacotes** de assinatura:

| Pacote | Perfil | Módulos | Nível máximo |
|--------|--------|---------|--------------|
| **Produtor** | Pequeno produtor familiar | Selecionados | Essencial |
| **Gestão** | Fazenda média organizada | Selecionados | Profissional |
| **Pecuária** | Fazenda com foco em rebanho | Selecionados | Profissional |
| **Lavoura** | Fazenda com foco em grãos/cana | Selecionados | Profissional |
| **Rastreabilidade** | Exportadores e certificados | Selecionados | Enterprise |
| **Enterprise** | Grandes grupos e cooperativas | Todos | Enterprise |
| **Custom** | Regras para montagem sob demanda | Variável | Variável |

Para cada pacote documente:
- Módulos e níveis incluídos
- Módulos disponíveis como add-on
- Limites operacionais (propriedades, usuários, hectares)
- Perfil ideal do assinante
- Valor percebido e argumento de venda

Salve em: `docs/contexts/_bundle-packages.md`

---

## TAREFA 6 — WORKFLOW DE IMPLANTAÇÃO POR MÓDULO

Para cada módulo (incluindo Core), gere o arquivo `_implantation-workflow.md`:

- Pré-requisitos técnicos e de dados
- Ordem de implantação dos submódulos (do Essencial ao Enterprise)
- Checklist de configuração inicial
- Sequência de testes: unitário → integração → UAT
- Critérios de go-live por nível (Essencial, Profissional, Enterprise)
- Plano de rollback
- Estimativa de esforço por nível (em dias/sprint)

**Regra importante:** o workflow deve deixar explícito que os submódulos
Essenciais são sempre implantados antes dos Profissionais, e estes antes
dos Enterprise — nunca na ordem inversa.

---

## TAREFA 7 — GUIA DE TRABALHO PARALELO PARA AGENTES

Gere `docs/contexts/_parallel-agent-workflow.md` com:

- **Mapa de agentes sugeridos** — 1 agente por módulo principal
- **Agente Core** — responsável pela base, deve finalizar antes dos demais iniciarem
- **Quais arquivos cada agente deve ler antes de iniciar**
- **Pontos de sincronização obrigatórios** entre agentes (ex: quando Financeiro
  depende de algo do Estoque, ambos os agentes devem sincronizar)
- **Ordem de execução em 3 fases:**
  - Fase 1 — Core (todos os agentes aguardam)
  - Fase 2 — Módulos Essenciais em paralelo
  - Fase 3 — Profissional e Enterprise em paralelo por módulo
- **Convenções de código e nomenclatura** compartilhadas
- **Protocolo de conflito** quando dois agentes tocam na mesma entidade de dados
- **Checklist de entrega** por agente e por fase

---

## RESTRIÇÕES E CONVENÇÕES

- Todos os arquivos em **Markdown** com frontmatter YAML
- Slugs em **kebab-case** em português (`gestao-financeira`, `controle-estoque`)
- Níveis sempre nomeados como: `essencial`, `profissional`, `enterprise`
- Core sempre nomeado como: `core`
- Dependências referenciadas pelo **caminho relativo** do arquivo
- Complexidade usando: `XS | S | M | L | XL`
- Nenhum módulo documentado sem ao menos 1 submódulo por nível
- Idioma de toda a documentação: **Português Brasileiro**

---

## ORDEM DE EXECUÇÃO
```
Tarefa 1 ──► _competitive-analysis.md
    │
    ▼
Tarefa 2 ──► core/ (todos os arquivos)
    │
    ▼
Tarefa 3 ──► _module-dependency-graph.md + árvore de módulos
    │
    ├──────────────────────────┐
    ▼                          ▼
Tarefa 4                   Tarefa 5
_bundle-packages.md        workflows por módulo
    │                          │
    └──────────┬───────────────┘
               ▼
           Tarefa 6
    _parallel-agent-workflow.md
               │
               ▼
           _index.md
```

As Tarefas 4 e 5 podem ser executadas em paralelo após a Tarefa 3.
A Tarefa 6 só inicia após a conclusão de 4 e 5.