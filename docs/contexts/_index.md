---
titulo: Índice Mestre de Documentação — AgroSaaS
versao: 1.1
data_criacao: 2026-04-01
data_atualizacao: 2026-04-01
tipo: index
---

# AgroSaaS — Documentação de Contextos

## 📚 Visão Geral

Este diretório contém toda a documentação contextual do AgroSaaS, organizada para permitir **trabalho paralelo de múltiplos agentes** em módulos independentes.

---

## 🗺️ Mapa de Navegação Rápida

### Documentos de Estratégia (Nova Estrutura)

| Documento | Propósito | Quando Ler |
|-----------|-----------|------------|
| [`../strategy/module-architecture.md`](../strategy/module-architecture.md) | Missão, tarefas, estrutura de documentação | **Primeiro documento a ler** |
| [`../strategy/bundle-packages.md`](../strategy/bundle-packages.md) | 6 pacotes de assinatura, preços, limites | Antes de desenvolver features |
| [`../strategy/parallel-agent-workflow.md`](../strategy/parallel-agent-workflow.md) | Guia de trabalho paralelo para agentes | Ao iniciar como agente |

### Documentos de Contexto (Técnico)

| Documento | Propósito | Quando Ler |
|-----------|-----------|------------|
| [`_competitive-analysis.md`](_competitive-analysis.md) | Análise de 5 concorrentes, gaps, oportunidades | Durante planejamento de módulo |
| [`_module-dependency-graph.md`](_module-dependency-graph.md) | Dependências entre módulos, ordem de implantação | Antes de iniciar um módulo |
| [`_index.md`](_index.md) (este arquivo) | Navegação de toda a documentação | Sempre |

---

## 📁 Estrutura de Pastas

```
docs/
├── strategy/                          ← NOVA: Documentação Estratégica
│   ├── module-architecture.md         ← Missão, tarefas, estrutura (ex: analise.md)
│   ├── bundle-packages.md             ← Pacotes de assinatura, preços, limites
│   └── parallel-agent-workflow.md     ← Guia de trabalho paralelo para agentes
│
├── contexts/                          ← Documentação de Contexto por Módulo
│   ├── _index.md                      ← Você está aqui
│   ├── _competitive-analysis.md       ← Análise de mercado
│   ├── _module-dependency-graph.md    ← Dependências entre módulos
│   │
│   ├── core/                          ← Módulo Core (obrigatório)
│   │   ├── _overview.md
│   │   ├── _implantation-workflow.md
│   │   ├── identidade-acesso.md
│   │   ├── cadastro-propriedade.md
│   │   ├── multipropriedade.md
│   │   ├── configuracoes-globais.md
│   │   ├── notificacoes-alertas.md
│   │   ├── integracoes-essenciais.md
│   │   └── planos-assinatura.md
│   │
│   ├── agricola/                      ← Módulo Agrícola
│   │   ├── _overview.md
│   │   ├── _implantation-workflow.md
│   │   ├── essencial/
│   │   │   ├── safras.md
│   │   │   ├── operacoes-campo.md
│   │   │   └── caderno-campo.md
│   │   ├── profissional/
│   │   │   ├── planejamento-safra.md
│   │   │   ├── monitoramento-ndvi.md
│   │   │   └── custos-producao.md
│   │   └── enterprise/
│   │       ├── rastreabilidade-campo.md
│   │       ├── prescricoes-vrt.md
│   │       └── beneficiamento.md
│   │
│   ├── pecuaria/                      ← Módulo Pecuário
│   │   ├── _overview.md
│   │   ├── _implantation-workflow.md
│   │   ├── essencial/
│   │   ├── profissional/
│   │   └── enterprise/
│   │
│   ├── financeiro/                    ← Módulo Financeiro
│   │   ├── _overview.md
│   │   ├── _implantation-workflow.md
│   │   ├── essencial/
│   │   ├── profissional/
│   │   └── enterprise/
│   │
│   ├── estoque/                           ← Módulo Estoque
│   │   ├── _overview.md
│   │   ├── essencial/ (cadastro-produtos, movimentacoes, saldo-consulta)
│   │   ├── profissional/ (fifo-custo, lotes-validade, estoque-minimo)
│   │   └── enterprise/ (compras-integradas, integracao-fiscal, inventario-automatizado)
│   │
│   ├── frota/                             ← Módulo Frota
│   │   ├── _overview.md
│   │   ├── essencial/ (cadastro-equipamentos, checklist-diario, abastecimento)
│   │   ├── profissional/ (manutencao-preventiva, custo-hora-maquina, documentacao)
│   │   └── enterprise/ (telemetria, oficina-interna, indicadores-frota)
│   │
│   ├── pessoas/                           ← Módulo Pessoas / RH Rural
│   │   ├── _overview.md
│   │   ├── essencial/ (cadastro-colaboradores, controle-presenca, epi-seguranca)
│   │   ├── profissional/ (escalas-tarefas, folha-simplificada, treinamentos)
│   │   └── enterprise/ (esocial-rural, terceirizados, indicadores-rh)
│   │
│   ├── imoveis/                           ← Módulo Imóveis Rurais
│   │   ├── _overview.md
│   │   ├── essencial/ (cadastro-imovel, documentos-legais)
│   │   └── profissional/ (arrendamentos)
│   │
│   ├── rastreabilidade/               ← Módulo de Rastreabilidade
│   ├── compliance/                    ← Módulo de Compliance Ambiental
│   ├── comercializacao/               ← Módulo de Comercialização
│   └── contabilidade/                 ← Módulo Contábil
│
└── architecture/                      ← Documentação Técnica
    └── AgroSaaS-Manual.md             ← Regras de desenvolvimento (Seção 11: Módulos)
```

---

## 🏗️ Módulos Disponíveis

### Core (Fundação Obrigatória)

**Status:** ✅ Documentação base criada  
**Complexidade:** M  
**Tempo de Implantação:** 4 semanas

| Submódulo | Nível | Complexidade | Status |
|-----------|-------|--------------|--------|
| [`identidade-acesso`](core/identidade-acesso.md) | Core | L | 📄 Criado |
| [`cadastro-propriedade`](core/cadastro-propriedade.md) | Core | M | 📄 Criado |
| [`multipropriedade`](core/multipropriedade.md) | Core | M | 📄 Criado |
| [`configuracoes-globais`](core/configuracoes-globais.md) | Core | S | 📄 Criado |
| [`notificacoes-alertas`](core/notificacoes-alertas.md) | Core | M | 📄 Criado |
| [`integracoes-essenciais`](core/integracoes-essenciais.md) | Core | L | 📄 Criado |
| [`planos-assinatura`](core/planos-assinatura.md) | Core | M | 📄 Criado |

**Workflow:** [`core/_implantation-workflow.md`](core/_implantation-workflow.md)

---

### Agrícola

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** L  
**Tempo de Implantação:** 8 semanas (Essencial → Enterprise)

| Nível | Submódulos | Complexidade | Status |
|-------|-----------|--------------|--------|
| Essencial | [`safras`](agricola/essencial/safras.md), [`operacoes-campo`](agricola/essencial/operacoes-campo.md), [`caderno-campo`](agricola/essencial/caderno-campo.md) | M | 📝 Pendente |
| Profissional | [`planejamento-safra`](agricola/profissional/planejamento-safra.md), [`monitoramento-ndvi`](agricola/profissional/monitoramento-ndvi.md), [`custos-producao`](agricola/profissional/custos-producao.md) | L | 📝 Pendente |
| Enterprise | [`rastreabilidade-campo`](agricola/enterprise/rastreabilidade-campo.md), [`prescricoes-vrt`](agricola/enterprise/prescricoes-vrt.md), [`beneficiamento`](agricola/enterprise/beneficiamento.md) | XL | 📝 Pendente |

**Workflow:** [`agricola/_implantation-workflow.md`](agricola/_implantation-workflow.md)  
**Overview:** [`agricola/_overview.md`](agricola/_overview.md)

---

### Pecuária

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** M  
**Tempo de Implantação:** 6 semanas (Essencial → Enterprise)

| Nível | Submódulos | Complexidade | Status |
|-------|-----------|--------------|--------|
| Essencial | [`rastreio-basico`](pecuaria/essencial/rastreio-basico.md), [`controle-sanitario`](pecuaria/essencial/controle-sanitario.md), [`piquetes-pastos`](pecuaria/essencial/piquetes-pastos.md) | M | 📝 Pendente |
| Profissional | [`genetica-reprodutiva`](pecuaria/profissional/genetica-reprodutiva.md), [`nutricao-feedlot`](pecuaria/profissional/nutricao-feedlot.md), [`pecuaria-leiteira`](pecuaria/profissional/pecuaria-leiteira.md) | L | 📝 Pendente |
| Enterprise | [`rastreabilidade-sisbov`](pecuaria/enterprise/rastreabilidade-sisbov.md), [`gta-digital`](pecuaria/enterprise/gta-digital.md), [`genealogia-deps`](pecuaria/enterprise/genealogia-deps.md) | XL | 📝 Pendente |

**Workflow:** [`pecuaria/_implantation-workflow.md`](pecuaria/_implantation-workflow.md)  
**Overview:** [`pecuaria/_overview.md`](pecuaria/_overview.md)

---

### Financeiro

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** L  
**Tempo de Implantação:** 8 semanas (Essencial → Enterprise)

| Nível | Submódulos | Complexidade | Status |
|-------|-----------|--------------|--------|
| Essencial | [`lancamentos-basicos`](financeiro/essencial/lancamentos-basicos.md), [`fluxo-caixa`](financeiro/essencial/fluxo-caixa.md), [`categorias-contas`](financeiro/essencial/categorias-contas.md) | S | 📝 Pendente |
| Profissional | [`contas-pagar-receber`](financeiro/profissional/contas-pagar-receber.md), [`centro-custo`](financeiro/profissional/centro-custo.md), [`conciliacao-bancaria`](financeiro/profissional/conciliacao-bancaria.md) | M | 📝 Pendente |
| Enterprise | [`conciliacao-automatica`](financeiro/enterprise/conciliacao-automatica.md), [`credito-rural`](financeiro/enterprise/credito-rural.md), [`custo-producao-safra`](financeiro/enterprise/custo-producao-safra.md) | XL | 📝 Pendente |

**Workflow:** [`financeiro/_implantation-workflow.md`](financeiro/_implantation-workflow.md)  
**Overview:** [`financeiro/_overview.md`](financeiro/_overview.md)

---

### Estoque

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** M  
**Tempo de Implantação:** 5 semanas (Essencial → Enterprise)

| Nível | Submódulos | Complexidade | Status |
|-------|-----------|--------------|--------|
| Essencial | [`cadastro-produtos`](estoque/essencial/cadastro-produtos.md), [`movimentacoes`](estoque/essencial/movimentacoes.md), [`saldo-consulta`](estoque/essencial/saldo-consulta.md) | S | 📝 Pendente |
| Profissional | [`fifo-custo`](estoque/profissional/fifo-custo.md), [`lotes-validade`](estoque/profissional/lotes-validade.md), [`estoque-minimo`](estoque/profissional/estoque-minimo.md) | M | 📝 Pendente |
| Enterprise | [`compras-integradas`](estoque/enterprise/compras-integradas.md), [`integracao-fiscal`](estoque/enterprise/integracao-fiscal.md), [`inventario-automatizado`](estoque/enterprise/inventario-automatizado.md) | L | 📝 Pendente |

---

### Frota

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** M  
**Tempo de Implantação:** 5 semanas (Essencial → Enterprise)

| Nível | Submódulos | Complexidade | Status |
|-------|-----------|--------------|--------|
| Essencial | [`cadastro-equipamentos`](frota/essencial/cadastro-equipamentos.md), [`checklist-diario`](frota/essencial/checklist-diario.md), [`abastecimento`](frota/essencial/abastecimento.md) | S | 📝 Pendente |
| Profissional | [`manutencao-preventiva`](frota/profissional/manutencao-preventiva.md), [`custo-hora-maquina`](frota/profissional/custo-hora-maquina.md), [`documentacao`](frota/profissional/documentacao.md) | M | 📝 Pendente |
| Enterprise | [`telemetria`](frota/enterprise/telemetria.md), [`oficina-interna`](frota/enterprise/oficina-interna.md), [`indicadores-frota`](frota/enterprise/indicadores-frota.md) | L | 📝 Pendente |

---

### Pessoas / RH Rural

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** M  
**Tempo de Implantação:** 5 semanas (Essencial → Enterprise)

| Nível | Submódulos | Complexidade | Status |
|-------|-----------|--------------|--------|
| Essencial | [`cadastro-colaboradores`](pessoas/essencial/cadastro-colaboradores.md), [`controle-presenca`](pessoas/essencial/controle-presenca.md), [`epi-seguranca`](pessoas/essencial/epi-seguranca.md) | S | 📝 Pendente |
| Profissional | [`escalas-tarefas`](pessoas/profissional/escalas-tarefas.md), [`folha-simplificada`](pessoas/profissional/folha-simplificada.md), [`treinamentos`](pessoas/profissional/treinamentos.md) | M | 📝 Pendente |
| Enterprise | [`esocial-rural`](pessoas/enterprise/esocial-rural.md), [`terceirizados`](pessoas/enterprise/terceirizados.md), [`indicadores-rh`](pessoas/enterprise/indicadores-rh.md) | XL | 📝 Pendente |

---

### Imóveis Rurais

**Status:** ✅ Overview criado, submódulos essenciais e profissional criados  
**Complexidade:** M  
**Tempo de Implantação:** 4 semanas (Essencial → Profissional)

| Nível | Submódulos | Complexidade | Status |
|-------|-----------|--------------|--------|
| Essencial | [`cadastro-imovel`](imoveis/essencial/cadastro-imovel.md), [`documentos-legais`](imoveis/essencial/documentos-legais.md) | M / S | 📄 Criado |
| Profissional | [`arrendamentos`](imoveis/profissional/arrendamentos.md) | M | 📄 Criado |
| Enterprise | `avaliacao-patrimonial`, `gestao-multi-imovel` | L / M | 📝 Pendente |

**Overview:** [`imoveis/_overview.md`](imoveis/_overview.md)

---

### Rastreabilidade

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** L

| Nível | Submódulos | Status |
|-------|-----------|--------|
| Essencial | Lotes de Produção, Origem-Destino, Histórico de Aplicações | 📝 Pendente |
| Profissional | Cadeia de Custódia, QR Code Consulta, Laudos e Análises | 📝 Pendente |
| Enterprise | Certificações, Blockchain, Auditoria de Exportação | 📝 Pendente |

---

### Compliance Ambiental

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** L

| Nível | Submódulos | Status |
|-------|-----------|--------|
| Essencial | CAR Gestão, APP/Reserva Legal, Documentos Ambientais | 📝 Pendente |
| Profissional | Monitoramento de Desmatamento, Gestão de Resíduos, Relatórios ESG | 📝 Pendente |
| Enterprise | Carbono (inventário GEE), Due Diligence (EUDR), Biodiversidade | 📝 Pendente |

---

### Comercialização

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** M

| Nível | Submódulos | Status |
|-------|-----------|--------|
| Essencial | Registro de Vendas, Clientes/Compradores, Romaneios | 📝 Pendente |
| Profissional | Contratos de Venda, Cotações de Mercado, NF-e Emissão | 📝 Pendente |
| Enterprise | CPR/Cédulas, Hedge/Derivativos, Exportação (SISCOMEX) | 📝 Pendente |

---

### Contabilidade

**Status:** ✅ Overview criado, submódulos pendentes  
**Complexidade:** L

| Nível | Submódulos | Status |
|-------|-----------|--------|
| Essencial | LCDPR, Plano de Contas Rural, Lançamentos Contábeis | 📝 Pendente |
| Profissional | Integração Contábil, DRE Rural, Balancete | 📝 Pendente |
| Enterprise | Multi-Empresa, IRPF Rural, SPED Fiscal | 📝 Pendente |

---

## 📊 Status da Documentação

| Módulo | Overview | Workflow | Essencial | Profissional | Enterprise | Completude |
|--------|----------|----------|-----------|--------------|------------|------------|
| **Core** | ✅ | ✅ | 7/7 📄 | N/A | N/A | 95% |
| **Agrícola** | ✅ | ✅ | 0/3 📝 | 0/3 📝 | 0/3 📝 | 15% |
| **Pecuária** | ✅ | 📝 | 0/3 📝 | 0/3 📝 | 0/3 📝 | 10% |
| **Financeiro** | ✅ | 📝 | 1/3 📄 | 0/3 📝 | 0/3 📝 | 15% |
| **Estoque** | ✅ | 📝 | 0/3 📝 | 0/3 📝 | 0/3 📝 | 10% |
| **Frota** | ✅ | 📝 | 0/3 📝 | 0/3 📝 | 0/3 📝 | 10% |
| **Pessoas** | 📝 | 📝 | 0/3 📝 | 0/3 📝 | 0/3 📝 | 0% |
| **Imóveis Rurais** | ✅ | 📝 | 2/2 📄 | 1/1 📄 | 0/2 📝 | 70% |
| **Rastreabilidade** | ✅ | 📝 | 0/3 📝 | 0/3 📝 | 0/3 📝 | 10% |
| **Compliance** | ✅ | 📝 | 0/3 📝 | 0/3 📝 | 0/3 📝 | 10% |
| **Comercialização** | ✅ | 📝 | 0/3 📝 | 0/3 📝 | 0/3 📝 | 10% |
| **Contabilidade** | ✅ | 📝 | 0/3 📝 | 0/3 📝 | 0/3 📝 | 10% |
| **TOTAL** | 11/12 ✅ | 2/12 ✅ | 10/39 📄 | 1/28 📄 | 0/29 📝 | **25%** |

**Legenda:**
- ✅ Completo
- 📝 Pendente
- 📄 Em andamento
- ❌ Não iniciado

---

## 🚀 Ordem de Execução Recomendada

### Fase 1: Fundação (Semana 1-2)

1. ✅ Ler [`_competitive-analysis.md`](_competitive-analysis.md)
2. ✅ Ler [`_bundle-packages.md`](_bundle-packages.md)
3. ✅ Ler [`_module-dependency-graph.md`](_module-dependency-graph.md)
4. 📝 Criar workflows de implantação por módulo
5. 📝 Completar submódulos do Core

### Fase 2: Módulos Essenciais (Semana 3-6)

1. 📝 Agrícola Essencial (3 submódulos)
2. 📝 Pecuária Essencial (3 submódulos)
3. 📝 Financeiro Essencial (3 submódulos)
4. 📝 Operacional Essencial (6 submódulos)

### Fase 3: Módulos Profissionais (Semana 7-12)

1. 📝 Agrícola Profissional (3 submódulos)
2. 📝 Pecuária Profissional (3 submódulos)
3. 📝 Financeiro Profissional (3 submódulos)
4. 📝 Operacional Profissional (6 submódulos)
5. 📝 Rastreabilidade Profissional (3 submódulos)
6. 📝 Compliance Profissional (3 submódulos)
7. 📝 Comercialização Profissional (3 submódulos)

### Fase 4: Módulos Enterprise (Semana 13-20)

1. 📝 Agrícola Enterprise (3 submódulos)
2. 📝 Pecuária Enterprise (3 submódulos)
3. 📝 Financeiro Enterprise (3 submódulos)
4. 📝 Operacional Enterprise (6 submódulos)
5. 📝 Rastreabilidade Enterprise (3 submódulos)
6. 📝 Compliance Enterprise (3 submódulos)
7. 📝 Comercialização Enterprise (3 submódulos)
8. 📝 Contabilidade Enterprise (3 submódulos)

---

## 📋 Template de Documento de Contexto

Todo submódulo deve seguir o template abaixo:

```markdown
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

## 🔗 Links Relacionados

### Documentação Estratégica (Nova)

- [`../strategy/module-architecture.md`](../strategy/module-architecture.md) — Missão, tarefas e estrutura de documentação
- [`../strategy/bundle-packages.md`](../strategy/bundle-packages.md) — Pacotes de assinatura, preços, limites
- [`../strategy/parallel-agent-workflow.md`](../strategy/parallel-agent-workflow.md) — Guia de trabalho paralelo para agentes

### Documentação de Contexto

- [`_competitive-analysis.md`](_competitive-analysis.md) — Análise de concorrentes
- [`_module-dependency-graph.md`](_module-dependency-graph.md) — Dependências entre módulos
- [`_bundle-packages.md`](_bundle-packages.md) — Pacotes de assinatura (legado — ver também ../strategy/)

### Documentação Funcional

- [`../functional_requirements/funtionals.md`](../functional_requirements/funtionals.md) — Especificação funcional completa

### Documentação Técnica

- [`../../CLAUDE.md`](../../CLAUDE.md) — Contexto técnico da aplicação
- [`../../README.md`](../../README.md) — README do projeto
- [`../../docs/PROXIMOS_PASSOS.md`](../../docs/PROXIMOS_PASSOS.md) — Roadmap de desenvolvimento
- [`../architecture/AgroSaaS-Manual.md`](../architecture/AgroSaaS-Manual.md) — Regras de desenvolvimento (Seção 11: Módulos de Negócio)

### Repositórios

- Backend: `/services/api`
- Frontend Web: `/apps/web`
- Frontend Mobile: `/apps/mobile`
- Shared Schemas: `/packages/zod-schemas`

---

## 📞 Contato e Suporte

**Dúvidas sobre documentação:** Abrir issue no repositório  
**Sugestões de melhoria:** PR com revisão do Product Management  
**Erros ou inconsistências:** Issue com label `documentation`

---

**Última atualização:** 2026-04-01  
**Próxima revisão:** 2026-05-01 (mensal)  
**Responsável:** Documentation Team AgroSaaS
