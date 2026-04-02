# Grafo de Dependências de Módulos — AgroSaaS

> Última atualização: 2026-04-01

Este documento mapeia todos os módulos não-Core da plataforma AgroSaaS, suas dependências internas e cruzadas, níveis de contratação e perfis-alvo.

---

## Grafo Visual de Dependências (ASCII)

```
                          ┌─────────────┐
                          │    CORE      │
                          │ (auth/tenant │
                          │  /billing)   │
                          └──────┬───────┘
                                 │
            ┌────────────────────┼────────────────────────┐
            │                    │                         │
     ┌──────▼──────┐     ┌──────▼──────┐          ┌──────▼──────┐
     │  Financeiro  │     │   Estoque   │          │  Pessoas/RH │
     └──────┬───────┘     └──────┬───────┘          └──────┬──────┘
            │                    │                         │
    ┌───────┼──────────┬─────────┼───────────┬─────────────┤
    │       │          │         │           │             │
┌───▼───┐ ┌▼────────┐ ┌▼────────┐ ┌▼────────┐ ┌▼──────────┐
│Agríco-│ │Pecuária │ │  Frota  │ │Comercia-│ │Contabili- │
│  la   │ │         │ │         │ │lização  │ │  dade     │
└───┬───┘ └────┬────┘ └─────────┘ └────┬────┘ └───────────┘
    │          │                        │
    ├──────────┼────────────────────────┤
    │          │                        │
┌───▼──────────▼───┐           ┌───────▼────────┐
│ Rastreabilidade  │           │  Compliance/   │
│                  │           │  Ambiental     │
└──────────────────┘           └────────────────┘

Legenda:
  ──▶  "depende de" (módulo filho depende do módulo pai)
  Core é dependência implícita de TODOS os módulos
```

### Dependências detalhadas (setas)

```
Agrícola        ──▶ Estoque, Financeiro
Pecuária        ──▶ Estoque, Financeiro
Frota           ──▶ Estoque, Financeiro
Comercialização ──▶ Financeiro, Estoque, (Agrícola | Pecuária)
Rastreabilidade ──▶ Agrícola | Pecuária, Estoque
Compliance      ──▶ Agrícola | Pecuária (opcional)
Contabilidade   ──▶ Financeiro
Pessoas/RH      ──▶ (nenhum além de Core)
Estoque         ──▶ (nenhum além de Core)
Financeiro      ──▶ (nenhum além de Core)
```

---

## 1. Agrícola (`agricola`)

**Descrição:** Gestão completa do ciclo agrícola — do planejamento de safras à colheita, incluindo monitoramento por NDVI, controle de operações mecanizadas e apuração de custos por talhão.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| Cadastro de safras e talhões | Planejamento de operações (calendarização) | Monitoramento NDVI via satélite |
| Registro de operações (plantio, colheita) | Custos por talhão e por safra | Integração com telemetria de máquinas |
| Apontamento manual de insumos | Recomendações de adubação/defensivos | Benchmarking entre talhões e safras |
| Histórico de safras | Mapas de produtividade | Modelagem preditiva de produtividade |

### Dependências

- **Core:** autenticação, tenant, fazendas
- **Cross-module:** Estoque (baixa de insumos), Financeiro (custos de operações)

### Contratação standalone?

**Não.** Requer ao menos Estoque (Essencial) para controle de insumos aplicados. A contratação do Agrícola provisiona automaticamente o Estoque Essencial.

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Pequeno produtor de grãos (< 500 ha) |
| Profissional | Médio produtor ou cooperativa (500–5.000 ha) |
| Enterprise | Grandes grupos agrícolas, tradings (> 5.000 ha) |

### Complexidade: **L**

---

## 2. Pecuária (`pecuaria`)

**Descrição:** Gestão de rebanho, manejos sanitários e reprodutivos, rastreabilidade animal (GTA/SISBOV), e controle de lotes de engorda ou cria.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| Cadastro de animais e lotes | Protocolos reprodutivos (IATF, monta) | Integração SISBOV/GTA automatizada |
| Movimentação entre piquetes | Controle sanitário com calendário vacinal | Indicadores zootécnicos avançados (DEP, GMD) |
| Pesagens e manejos básicos | Gestão de matrizes e touros | Dashboard de performance por lote |
| Registro de nascimentos/mortes | Custos por cabeça / arroba | Integração com balanças e brincos eletrônicos |

### Dependências

- **Core:** autenticação, tenant, fazendas
- **Cross-module:** Estoque (medicamentos, rações, sal mineral), Financeiro (custo por cabeça)

### Contratação standalone?

**Não.** Requer Estoque (Essencial) para controle de medicamentos e insumos. Provisiona Estoque Essencial automaticamente.

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Pecuarista de corte/leite (< 500 cabeças) |
| Profissional | Confinamento ou fazenda de cria/recria (500–5.000 cab.) |
| Enterprise | Grandes pecuárias, frigoríficos integrados (> 5.000 cab.) |

### Complexidade: **L**

---

## 3. Financeiro (`financeiro`)

**Descrição:** Controle financeiro da operação rural — contas a pagar/receber, fluxo de caixa, DRE gerencial e conciliação bancária.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| Cadastro de receitas e despesas | Fluxo de caixa projetado | Conciliação bancária automática (OFX) |
| Categorização por centro de custo | DRE gerencial por fazenda/safra | Multi-empresa e consolidação de grupos |
| Contas a pagar / a receber | Parcelamento e renegociação | Integração com ERP contábil externo |
| Extrato simplificado | Relatórios comparativos safra x safra | Orçamento anual com acompanhamento |

### Dependências

- **Core:** autenticação, tenant, fazendas

### Contratação standalone?

**Sim.** Módulo base que funciona de forma independente. Muitos produtores iniciam a adoção pelo financeiro.

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Qualquer produtor que precise sair da planilha |
| Profissional | Produtor com múltiplas fazendas ou safras simultâneas |
| Enterprise | Grupos com holding, múltiplos CNPJs |

### Complexidade: **M**

---

## 4. Estoque (`estoque`)

**Descrição:** Controle de insumos, produtos e materiais — movimentações de entrada/saída, custeio FIFO, alertas de estoque mínimo e rastreabilidade de lotes.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| Cadastro de produtos e categorias | Custeio FIFO por lote | Multi-almoxarifado com transferências |
| Entradas e saídas manuais | Estoque mínimo com alertas | Integração com NF-e (entrada automática) |
| Saldo por almoxarifado | Inventário e ajustes | Dashboard de consumo e previsão |
| Relatório de movimentações | Lotes de fornecedor e validade | Requisições com aprovação por alçada |

### Dependências

- **Core:** autenticação, tenant, fazendas

### Contratação standalone?

**Sim.** Funciona independentemente. É pré-requisito para Agrícola e Pecuária.

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Produtor que quer controle básico de insumos |
| Profissional | Fazenda com alto volume de insumos e múltiplos almoxarifados |
| Enterprise | Grupos com logística centralizada de insumos |

### Complexidade: **M**

---

## 5. Frota e Máquinas (`frota`)

**Descrição:** Gestão de equipamentos agrícolas, planos de manutenção preventiva/corretiva, controle de abastecimento e checklist operacional.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| Cadastro de veículos e equipamentos | Plano de manutenção preventiva | Telemetria e integração com rastreadores |
| Registro de abastecimentos | Ordens de serviço com peças | Análise de custo por hora/máquina (TCO) |
| Checklist pré-operação | Controle de pneus e horímetro | Integração com operações agrícolas (custo mecanizado) |
| Histórico de manutenções corretivas | Alertas de manutenção programada | Dashboard de disponibilidade mecânica |

### Dependências

- **Core:** autenticação, tenant, fazendas
- **Cross-module:** Estoque (peças, combustível, lubrificantes), Financeiro (custos de manutenção)

### Contratação standalone?

**Não.** Requer Estoque (Essencial) para controle de peças e combustível. Provisiona Estoque Essencial automaticamente.

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Produtor com frota pequena (< 10 máquinas) |
| Profissional | Fazenda mecanizada com oficina própria |
| Enterprise | Grupos com frota numerosa e prestação de serviços mecanizados |

### Complexidade: **S**

---

## 6. Comercialização (`comercializacao`)

**Descrição:** Gestão de vendas de produção, contratos a termo, CPR (Cédula de Produto Rural), emissão/recebimento de NF-e e controle de entregas.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| Cadastro de compradores e destinos | Contratos a termo e fixação de preço | Emissão de NF-e integrada (SEFAZ) |
| Registro de vendas e romaneios | CPR física e financeira | Integração com bolsas e cotações em tempo real |
| Histórico de entregas | Controle de tickets de balança | Gestão de hedge e posição de mercado |
| Relatório de comercialização | Simulação de preço médio de venda | Portal do comprador com documentos |

### Dependências

- **Core:** autenticação, tenant, fazendas
- **Cross-module:** Financeiro (receitas de vendas), Estoque (baixa de produto vendido), Agrícola ou Pecuária (origem da produção)

### Contratação standalone?

**Não.** Requer Financeiro (para lançamento de receitas) e ao menos um módulo produtivo (Agrícola ou Pecuária) para origem dos produtos.

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Produtor que vende direto para cooperativa |
| Profissional | Produtor com contratos a termo e CPR |
| Enterprise | Tradings, grandes produtores com operações em bolsa |

### Complexidade: **L**

---

## 7. Pessoas e RH (`pessoas`)

**Descrição:** Cadastro de colaboradores, controle de funções e escalas, folha de pagamento simplificada e gestão de EPIs.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| Cadastro de colaboradores e funções | Folha de pagamento simplificada | Integração com eSocial rural |
| Controle de EPIs entregues | Gestão de férias e afastamentos | Treinamentos e certificações obrigatórias |
| Escala de trabalho básica | Horas extras e banco de horas | Avaliação de desempenho |
| Documentos do colaborador | Custo de mão de obra por atividade | Portal do colaborador (holerite, docs) |

### Dependências

- **Core:** autenticação, tenant, fazendas

### Contratação standalone?

**Sim.** Funciona de forma independente. Enriquece outros módulos ao permitir vincular colaboradores a operações.

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Fazenda com poucos funcionários (< 10) |
| Profissional | Fazenda com equipe média e necessidade de folha (10–100) |
| Enterprise | Grandes empregadores rurais, usinas, frigoríficos (> 100) |

### Complexidade: **M**

---

## 8. Rastreabilidade (`rastreabilidade`)

**Descrição:** Rastreamento de lotes de produção desde a origem (talhão/animal) até o destino final, com cadeia de custódia, QR code e suporte a certificações.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| Rastreio de lotes por origem | Cadeia de custódia completa (field-to-fork) | Integração com certificadoras (Rainforest, GlobalG.A.P.) |
| Histórico de insumos aplicados por lote | Geração de QR code por lote/produto | API pública para consulta de rastreio |
| Vinculação lote → talhão/animal | Relatórios para auditoria | Blockchain audit trail (selo de integridade) |
| Consulta básica de rastreio | Alertas de não-conformidade | Dashboard de compliance por certificação |

### Dependências

- **Core:** autenticação, tenant, fazendas
- **Cross-module:** Agrícola ou Pecuária (origem da produção), Estoque (movimentação de lotes)

### Contratação standalone?

**Não.** É um módulo de camada superior que requer dados de produção (Agrícola ou Pecuária) e movimentações (Estoque).

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Produtor que precisa atender rastreabilidade básica de compradores |
| Profissional | Exportador ou fornecedor de redes varejistas |
| Enterprise | Grandes players com exigências de certificações internacionais |

### Complexidade: **XL**

---

## 9. Compliance e Ambiental (`compliance`)

**Descrição:** Gestão de conformidade ambiental — CAR, APPs, reserva legal, monitoramento de embargos e passivos ambientais.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| Cadastro de CAR e áreas protegidas | Monitoramento de embargos (IBAMA, SEMA) | Integração com imagens de satélite para desmatamento |
| Mapa de APP e reserva legal | Gestão de licenças e condicionantes | Relatório ESG automatizado |
| Checklist de conformidade básica | Alertas de vencimento de licenças | Auditoria ambiental com evidências georreferenciadas |
| Documentos ambientais digitalizados | Plano de recuperação ambiental (PRA) | Score de risco ambiental por fazenda |

### Dependências

- **Core:** autenticação, tenant, fazendas
- **Cross-module:** Agrícola ou Pecuária (opcional — enriquece com dados de uso do solo)

### Contratação standalone?

**Sim.** Pode funcionar apenas com dados geoespaciais das fazendas (Core). A integração com módulos produtivos é opcional e enriquece os relatórios.

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Produtor que precisa organizar documentação ambiental |
| Profissional | Fazenda em processo de regularização ou com financiamento bancário |
| Enterprise | Grupos com gestão ESG, exportadores sujeitos a regulação europeia (EUDR) |

### Complexidade: **M**

---

## 10. Contabilidade (`contabilidade`)

**Descrição:** Geração do LCDPR (Livro Caixa Digital do Produtor Rural), integração com escritórios contábeis, plano de contas rural e apuração fiscal.

### Submódulos por Nível

| Essencial | Profissional | Enterprise |
|-----------|-------------|------------|
| LCDPR automático a partir do financeiro | Plano de contas rural personalizado | Integração com sistemas contábeis (API/SPED) |
| Exportação para contador (CSV/PDF) | Apuração de IRPF rural | Multi-CNPJ com consolidação fiscal |
| Classificação contábil de lançamentos | Depreciação de ativos rurais | Planejamento tributário com simulações |
| Relatório de resultado por atividade | Balancete gerencial | Auditoria contábil com trilha completa |

### Dependências

- **Core:** autenticação, tenant, fazendas
- **Cross-module:** Financeiro (fonte dos lançamentos — dependência obrigatória)

### Contratação standalone?

**Não.** Depende inteiramente do módulo Financeiro como fonte de dados. A contratação de Contabilidade exige Financeiro ativo.

### Perfis-alvo

| Nível | Perfil |
|-------|--------|
| Essencial | Produtor pessoa física que precisa entregar LCDPR |
| Profissional | Produtor com contador que exige integração digital |
| Enterprise | Grupos com departamento fiscal próprio |

### Complexidade: **S**

---

## Resumo de Dependências

| Módulo | Core | Estoque | Financeiro | Agrícola | Pecuária | Standalone? | Complexidade |
|--------|:----:|:-------:|:----------:|:--------:|:--------:|:-----------:|:------------:|
| Agrícola | ✅ | ✅ | ✅ | — | — | ❌ | L |
| Pecuária | ✅ | ✅ | ✅ | — | — | ❌ | L |
| Financeiro | ✅ | — | — | — | — | ✅ | M |
| Estoque | ✅ | — | — | — | — | ✅ | M |
| Frota | ✅ | ✅ | ✅ | — | — | ❌ | S |
| Comercialização | ✅ | ✅ | ✅ | ⚡ | ⚡ | ❌ | L |
| Pessoas/RH | ✅ | — | — | — | — | ✅ | M |
| Rastreabilidade | ✅ | ✅ | — | ⚡ | ⚡ | ❌ | XL |
| Compliance | ✅ | — | — | 〰️ | 〰️ | ✅ | M |
| Contabilidade | ✅ | — | ✅ | — | — | ❌ | S |

**Legenda:** ✅ obrigatório | ⚡ ao menos um obrigatório | 〰️ opcional (enriquece) | — não depende

---

## Regras de Provisionamento Automático

1. Ao contratar **Agrícola**, **Pecuária** ou **Frota** → provisionar **Estoque Essencial** automaticamente
2. Ao contratar **Contabilidade** → exigir **Financeiro** ativo
3. Ao contratar **Comercialização** → exigir **Financeiro** + ao menos um módulo produtivo
4. Ao contratar **Rastreabilidade** → exigir **Estoque** + ao menos um módulo produtivo
5. **Financeiro**, **Estoque**, **Pessoas/RH** e **Compliance** podem ser contratados de forma independente
