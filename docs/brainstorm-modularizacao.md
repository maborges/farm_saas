# Brainstorming — Modularização AgroSaaS
**Data:** 2026-03-22
**Abordagem escolhida:** B — Mapa Completo + Implementação em Ondas

---

## Contexto Consolidado

| Item | Definição |
|---|---|
| Dor central | Produtor sem controle financeiro real → risco fiscal, inadimplência, prejuízo invisível |
| Módulo core | **Financeiro** — obrigatório para 100% dos assinantes |
| Público | Pessoa Física (CPF / Carnê-Leão) e Pessoa Jurídica (CNPJ / Lucro Presumido / Simples Nacional) |
| Modelo | Módulos independentes com dependências declaradas (billing granular por módulo) |
| Base atual | Contas a pagar/receber + DRE (esboço) — precisam de refinamento |

---

## Estado Atual do Codebase

### Backend (FastAPI)
| Módulo | Submódulos existentes | Status |
|---|---|---|
| `core/` | auth, billing, onboarding, support, config | ✅ Funcional |
| `financeiro/` | despesas, receitas, planos_conta, relatorios | ⚠️ Esboço — refinar |
| `agricola/` | a1_planejamento, safras, talhoes, operacoes, romaneios, ndvi, climatico, custos, monitoramento, prescricoes, rastreabilidade, analises_solo, agronomo, previsoes | ⚠️ Parcial |
| `pecuaria/` | lotes, manejos, piquetes | ⚠️ Esboço |
| `operacional/` | frota, estoque, oficina, compras | ⚠️ Esboço |
| `imoveis/` | propriedades | ⚠️ Esboço |

### Frontend (Next.js)
| Área | Rotas existentes | Status |
|---|---|---|
| Auth | login, register, convite | ✅ |
| Agrícola | analises_solo, apontamentos, cadastros, climatico, defensivos, mapa, monitoramento, ndvi, operacoes, prescricoes, rastreabilidade, relatorios | ⚠️ Parcial |
| Financeiro | despesas (somente) | ❌ Incompleto |
| Configurações | frota, mapas | ⚠️ |

---

## Mapa Completo de Módulos

### TIER 0 — Core Obrigatório (incluído em todos os planos)

```
CORE
├── Autenticação & RBAC (✅ existe)
├── Cadastro de Fazendas / Propriedades (refinamento)
├── Cadastro de Pessoas
│   ├── Fornecedores
│   ├── Clientes / Compradores
│   ├── Funcionários
│   └── Parceiros / Prestadores
└── Dashboard Geral
    ├── Resumo financeiro
    ├── Alertas (contas vencendo, saldo baixo)
    └── Acesso rápido por módulo contratado
```

> ⚠️ **Gap identificado:** Módulo de Pessoas (cadastro de terceiros) não existe como entidade separada. É pré-requisito para Financeiro, Compras, RH e Fiscal.

---

### TIER 1 — Módulo Financeiro (CORE — obrigatório)

```
FINANCEIRO
├── Plano de Contas
│   ├── Padrão PF Rural (categorias RFB — IN 1761/2017)
│   ├── Padrão PJ Rural (DRE gerencial)
│   └── Personalização livre
├── Contas a Pagar (refinamento)
│   ├── Lançamento manual
│   ├── Lançamento recorrente (parcelas)
│   ├── Vencimento com alerta
│   └── Baixa manual / automática (Open Finance futuro)
├── Contas a Receber (refinamento)
│   ├── Receitas de venda (grãos, leite, boi, etc.)
│   ├── Reembolsos e convênios
│   └── Previsão de recebimento
├── Livro Caixa do Produtor Rural ← NOVO
│   ├── Lançamentos conforme categorias RFB
│   ├── Suporte a múltiplas atividades (grãos, pecuária, etc.)
│   ├── Relatório mensal/anual exportável (PDF/XLS)
│   └── Base para Carnê-Leão (PF) e apuração IR (PJ)
├── Fluxo de Caixa ← NOVO
│   ├── Realizado (entradas - saídas confirmadas)
│   ├── Previsto (lançamentos futuros programados)
│   └── Projeção 30/60/90 dias
├── Centro de Custos ← NOVO
│   ├── Por fazenda
│   ├── Por safra / lote / atividade
│   └── Rateio entre centros
├── Conciliação Bancária ← FUTURO (Onda 4)
│   └── Importação OFX / integração Open Finance
├── DRE Gerencial (refinamento)
│   ├── Mensal e acumulado
│   ├── Por atividade (agrícola / pecuária / outras)
│   └── Comparativo entre períodos
└── Relatórios Fiscais
    ├── Livro Caixa PF (exportação p/ Carnê-Leão)
    ├── Resumo para Lucro Presumido (PJ)
    └── Extrato para escritório contábil
```

**Dependências do Financeiro:**
- `CORE.Pessoas` (fornecedores/clientes nos lançamentos)
- `CORE.Fazendas` (centro de custo por propriedade)

---

### TIER 2 — Módulos Opcionais

#### Módulo Agrícola
```
AGRICOLA (depende de: CORE + FINANCEIRO)
├── A1 — Planejamento de Safras (refinamento)
│   ├── Criação de safras por talhão/gleba
│   ├── Planejamento de custos e receitas esperadas
│   └── Comparativo planejado vs realizado
├── A2 — Monitoramento e Insumos
│   ├── NDVI (imagens de satélite)
│   ├── Dados climáticos / previsão
│   ├── Análises de solo
│   └── Receituário agronômico / Prescrições
├── A3 — Operações de Campo
│   ├── Apontamentos (aplicações, pulverizações, adubações)
│   ├── Controle de defensivos
│   └── Rastreabilidade de operações
└── A4 — Colheita e Comercialização
    ├── Romaneios de colheita
    ├── Contratos de venda de grãos
    └── Integração com Financeiro (receitas de venda)
```

#### Módulo Pecuário
```
PECUARIA (depende de: CORE + FINANCEIRO)
├── P1 — Rebanho
│   ├── Cadastro de animais (individual / lote)
│   ├── Raça, categoria, genealogia
│   └── SISBOV / rastreabilidade (futuro)
├── P2 — Manejo Sanitário e Reprodutivo
│   ├── Vacinações, vermifugações, tratamentos
│   ├── IATF, monta natural, diagnóstico de gestação
│   └── Histórico por animal
├── P3 — Produção
│   ├── Controle de leite (diário/mensal)
│   ├── Peso e ganho de peso (pesagens)
│   └── Engorda / confinamento
└── P4 — Piquetes e Pastagens
    ├── Cadastro de piquetes
    ├── Rotação de pastagens
    └── Capacidade de suporte
```

#### Módulo Operacional
```
OPERACIONAL (depende de: CORE + FINANCEIRO)
├── O1 — Compras (depende de: Estoque + Financeiro + Pessoas)
│   ├── Pedidos de compra
│   ├── Cotação de fornecedores
│   ├── Recebimento de mercadorias
│   └── Integração automática com Contas a Pagar e Estoque
├── O2 — Estoque
│   ├── Insumos agrícolas (sementes, defensivos, fertilizantes)
│   ├── Combustível e lubrificantes
│   ├── Peças e materiais de manutenção
│   ├── Estoque de produtos (grãos, etc.)
│   └── Movimentações (entrada, saída, transferência)
└── O3 — Frota e Oficina (depende de: Estoque + Financeiro)
    ├── Cadastro de máquinas e veículos
    ├── Controle de abastecimento
    ├── Ordens de serviço / manutenção
    ├── Histórico de manutenções
    └── Custos por equipamento
```

#### Módulo RH Simplificado ← NOVO (não existe)
```
RH (depende de: CORE.Pessoas + FINANCEIRO)
├── Cadastro de funcionários (CLT, parceiro, diarista)
├── Controle de ponto / diárias
├── Adiantamentos e descontos
├── Folha de pagamento simplificada
└── Integração com Contas a Pagar (pagamento de salários)
```

#### Módulo Imóveis / Propriedades (refinamento)
```
IMOVEIS (CORE — base de tudo)
├── Cadastro de fazendas e sedes
├── Talhões / glebas (com geolocalização)
├── Piquetes e pastagens
├── Benfeitorias (casas, galpões, silos, etc.)
└── Documentação legal
    ├── CAR (Cadastro Ambiental Rural)
    ├── ITR (Imposto Territorial Rural)
    ├── CCIR e NIRF
    └── Georreferenciamento
```

---

### TIER 3 — Integrações

| Integração | Módulo beneficiado | Prioridade |
|---|---|---|
| **Open Finance / OFX bancário** | Financeiro (conciliação) | Alta — Onda 4 |
| **Receita Federal (Carnê-Leão Web)** | Financeiro fiscal PF | Alta — Onda 4 |
| **NF-e / NFS-e (emissão)** | Financeiro + Compras | Média — Onda 4 |
| **CEPEA / ESALQ (preços commodities)** | Agrícola (comercialização) | Média — Onda 3 |
| **INMET / Clima (dados oficiais)** | Agrícola (climático) | Já existe parcialmente |
| **SISBOV (rastreabilidade bovina)** | Pecuário | Baixa — Onda 5 |
| **eSocial Rural (simplificado)** | RH | Baixa — Onda 5 |
| **API de Escritório Contábil** | Financeiro (exportação) | Média — Onda 4 |
| **Mapbox / MapLibre** | Imoveis + Agrícola | Já existe |

---

## Grafo de Dependências

```
CORE (Fazendas + Pessoas + Auth)
    └── FINANCEIRO (obrigatório)
            ├── AGRICOLA
            │       └── Romaneios → Financeiro (receitas)
            │       └── Custos → Financeiro (despesas)
            ├── PECUARIO
            │       └── Produção → Financeiro (receitas leite/boi)
            │       └── Sanitário → Compras → Financeiro
            ├── OPERACIONAL
            │       ├── Compras → Financeiro (CP) + Estoque
            │       ├── Estoque → (independente, alimenta Compras)
            │       └── Frota → Estoque (combustível) + Financeiro
            └── RH → Financeiro (pagamentos) + CORE.Pessoas
```

---

## Implementação em Ondas

### Onda 1 — Core Sólido + Financeiro Completo (prioridade máxima)
**Objetivo:** Produto vendável imediatamente. Todo produtor rural encontra valor no dia 1.

| # | O que fazer | Esforço |
|---|---|---|
| 1.1 | Módulo **Pessoas** (fornecedores, clientes, funcionários) — NOVO | Alto |
| 1.2 | Refinamento **Imóveis/Fazendas** (base para centro de custos) | Médio |
| 1.3 | **Plano de Contas** PF e PJ com categorias RFB | Médio |
| 1.4 | Refinamento **Contas a Pagar/Receber** (parcelas, recorrências, alertas) | Alto |
| 1.5 | **Livro Caixa do Produtor Rural** (relatório fiscal) | Alto |
| 1.6 | **Fluxo de Caixa** (realizado + previsto) | Alto |
| 1.7 | **Centro de Custos** (por fazenda/atividade) | Médio |
| 1.8 | Refinamento **DRE** (por atividade, comparativo) | Médio |
| 1.9 | **Relatórios fiscais** (exportação p/ Carnê-Leão / contabilidade) | Médio |
| 1.10 | **Dashboard** com alertas financeiros | Médio |

### Onda 2 — Agrícola Completo + Pecuário Completo
**Objetivo:** Valor para produtores de grãos e pecuaristas.

| # | O que fazer |
|---|---|
| 2.1 | Refinamento safras + planejamento vs realizado |
| 2.2 | Integração Agrícola → Financeiro (custos de safra → despesas) |
| 2.3 | Comercialização de grãos → Financeiro (receitas de venda) |
| 2.4 | Módulo Pecuário completo (rebanho, manejo, produção) |
| 2.5 | Integração Pecuário → Financeiro (receitas leite/boi, despesas sanitárias) |

### Onda 3 — Operacional (Compras + Estoque + Frota) + RH
**Objetivo:** Controle operacional integrado ao financeiro.

| # | O que fazer |
|---|---|
| 3.1 | Módulo Estoque completo |
| 3.2 | Módulo Compras com integração Estoque + Financeiro |
| 3.3 | Módulo Frota / Oficina com integração Estoque + Financeiro |
| 3.4 | Módulo RH Simplificado |

### Onda 4 — Integrações Externas
**Objetivo:** Automatização e compliance fiscal.

| # | O que fazer |
|---|---|
| 4.1 | Importação OFX / Conciliação Bancária |
| 4.2 | Exportação para Carnê-Leão Web (RFB) |
| 4.3 | NF-e / NFS-e (emissão e recebimento) |
| 4.4 | API para escritório contábil |
| 4.5 | CEPEA (preços de commodities) |

### Onda 5 — Avançado
| # | O que fazer |
|---|---|
| 5.1 | SISBOV / rastreabilidade bovina |
| 5.2 | eSocial Rural simplificado |
| 5.3 | BI / relatórios avançados |
| 5.4 | App mobile (coleta offline em campo) |

---

## Gaps Críticos Identificados

1. **Módulo Pessoas** — não existe, bloqueia Financeiro, Compras, RH
2. **Livro Caixa RFB** — não existe, é o principal relatório fiscal do produtor rural PF
3. **Fluxo de Caixa** — não existe como tela/relatório
4. **Frontend Financeiro** — só tem rota `/financeiro/despesas`, falta toda a estrutura
5. **Centro de Custos** — não existe no modelo de dados
6. **Módulo RH** — não existe no backend nem frontend

---

## Impacto no Banco de Dados (Overview Onda 1)

### Novas tabelas necessárias:
- `pessoas` (fornecedores/clientes/funcionários — entidade unificada)
- `tipos_pessoa` (PF/PJ, categoria: fornecedor/cliente/funcionário/parceiro)
- `fluxo_caixa_previsoes` (projeções futuras)
- `centros_custo` (por fazenda/atividade)
- `lancamentos_livro_caixa` (visão fiscal dos lançamentos)
- `plano_contas_itens` (categorias do plano de contas)

### Tabelas existentes que precisam de migration:
- `despesas` → adicionar: `pessoa_id`, `centro_custo_id`, `categoria_rfb`, `nf_numero`
- `receitas` → adicionar: `pessoa_id`, `centro_custo_id`, `categoria_rfb`, `nf_numero`
- `fazendas` → adicionar: `tipo_tributacao` (PF/PJ), `cpf_cnpj`, `inscricao_estadual`

---

## Modelo de Assinatura — Feature Flags por Plano

### Tabela de Planos

| Funcionalidade | Básico | Profissional | Premium |
|---|---|---|---|
| Contas a pagar/receber + fluxo básico | ✅ | ✅ | ✅ |
| Livro Caixa + relatórios simples | ✅ | ✅ | ✅ |
| Conciliação bancária | Manual | Automática | Auto + regras customizadas |
| Rateio por safra/talhão | ❌ ou básico | ✅ automático | Ilimitado + templates salvos |
| Fluxo de caixa projetado | Básico (30d) | Sim + cenários | Sim + IA preditiva |
| Categorias personalizáveis | Limitado (10) | ✅ | Ilimitado |
| BI / Dashboards custom | ❌ | Básico | Completo + cruzamentos |
| Benchmarking (Compare Safras) | ❌ | ❌ | ✅ |
| Usuários por tenant | 1–2 | 5–10 | Ilimitado |
| Propriedades / fazendas | 1 | Múltiplas | Ilimitado |

### Tipos de Limitação Identificados

O sistema precisa suportar **3 tipos de feature flag** — impacto direto na arquitetura do billing:

| Tipo | Exemplos | Como implementar |
|---|---|---|
| **Boolean** (liga/desliga) | BI, Benchmarking, Conciliação auto | `modulos[]` no JWT + `require_module()` |
| **Quantity** (limites numéricos) | max_usuarios, max_fazendas, max_categorias | Campo na `AssinaturaTenant` + check no service |
| **Quality** (versão da feature) | Conciliação manual vs auto, Fluxo básico vs IA | Sub-flag dentro do módulo (ex: `FINANCEIRO:CONCILIACAO:AUTO`) |

### Mapeamento de Módulos por Plano

```
BÁSICO — módulos ativos:
  CORE (obrigatório)
  FINANCEIRO:BASICO
    → contas_pagar, contas_receber, livro_caixa, fluxo_caixa_basico
    → conciliacao_manual, categorias_limitadas (10)
  Limite: 2 usuários, 1 fazenda

PROFISSIONAL — módulos ativos:
  Tudo do Básico +
  FINANCEIRO:AVANCADO
    → conciliacao_automatica, rateio_automatico, fluxo_cenarios
    → categorias_ilimitadas, bi_basico
  AGRICOLA (se contratado)
  PECUARIO (se contratado)
  Limite: 10 usuários, múltiplas fazendas

PREMIUM — módulos ativos:
  Tudo do Profissional +
  FINANCEIRO:PREMIUM
    → conciliacao_regras_custom, fluxo_ia_preditivo
    → bi_completo, benchmarking_mercado
  OPERACIONAL (se contratado)
  RH (se contratado)
  Limite: ilimitado
```

### Impacto no JWT / Constants

Novos módulos a adicionar em `core/constants.py`:

```python
class Modulos:
    # Financeiro (tiers)
    F1_FINANCEIRO_BASICO = "F1_FINANCEIRO_BASICO"       # Básico
    F2_FINANCEIRO_AVANCADO = "F2_FINANCEIRO_AVANCADO"   # Profissional
    F3_FINANCEIRO_PREMIUM = "F3_FINANCEIRO_PREMIUM"     # Premium

    # Módulos opcionais (add-on)
    A1_AGRICOLA = "A1_AGRICOLA"
    P1_PECUARIO = "P1_PECUARIO"
    O1_OPERACIONAL = "O1_OPERACIONAL"
    O2_RH = "O2_RH"
    O3_BI = "O3_BI"
    O4_BENCHMARKING = "O4_BENCHMARKING"
```

### Limites Quantitativos no Schema

Campos a adicionar em `AssinaturaTenant`:
```python
max_usuarios: int           # 2 / 10 / -1 (ilimitado)
max_fazendas: int           # 1 / -1 / -1
max_categorias_plano: int   # 10 / -1 / -1
```

---

## Decisão Arquitetural Final — Modelo Tier × Módulo

### Princípio
O **Tier do plano** governa a **profundidade da integração financeira** em TODOS os módulos.
O **Add-on de módulo** controla se o módulo está ativo ou não.

```
check_acesso(feature) = modulo_ativo(ADD_ON) AND tier_suficiente(TIER)
```

### Exemplos por módulo

| Módulo | Básico | Profissional | Premium |
|---|---|---|---|
| Financeiro | Lançamentos simples, Livro Caixa | + Rateio automático, conciliação auto | + IA preditiva, benchmarking |
| Agrícola (add-on) | Custo de safra como lançamento | + Rateio por talhão automático | + Projeção IA + Compare Safras |
| Pecuário (add-on) | Receita de venda de boi/leite | + Custo por lote/piquete rateado | + Benchmarking de rebanho |
| Operacional (add-on) | Compras → CP simples | + Estoque integrado com custo automático | + Análise de giro/custo médio |
| RH (add-on) | Registro de pagamentos | + Custo por centro de custo/safra | + Projeção de folha |

### Implementação no Backend

```python
# core/constants.py — substituir módulos atuais por:

class PlanTier(str, Enum):
    BASICO = "BASICO"
    PROFISSIONAL = "PROFISSIONAL"
    PREMIUM = "PREMIUM"

class Modulos(str, Enum):
    # Core (sempre ativo)
    FINANCEIRO = "FINANCEIRO"          # tier controla a profundidade

    # Add-ons opcionais
    AGRICOLA = "AGRICOLA"
    PECUARIO = "PECUARIO"
    OPERACIONAL = "OPERACIONAL"
    RH = "RH"
    BI = "BI"                          # Premium only
    BENCHMARKING = "BENCHMARKING"      # Premium only

# Novo JWT payload:
{
  "sub": "user_id",
  "tenant_id": "uuid",
  "plan_tier": "PROFISSIONAL",         # <- NOVO
  "modulos": ["FINANCEIRO", "AGRICOLA"],
  "max_usuarios": 10,                  # <- NOVO
  "max_fazendas": -1,                  # <- NOVO (-1 = ilimitado)
  "fazendas": [...],
  "is_owner": true
}
```

### Campos a adicionar em AssinaturaTenant
```python
plan_tier: PlanTier                   # BASICO / PROFISSIONAL / PREMIUM
max_usuarios: int                     # 2 / 10 / -1
max_fazendas: int                     # 1 / -1 / -1
max_categorias_plano: int             # 10 / -1 / -1
```

### Nova dependência no router
```python
# Exemplo: rateio automático por talhão
@router.post("/lancamentos/rateio",
    dependencies=[
        Depends(require_module("AGRICOLA")),
        Depends(require_tier("PROFISSIONAL"))   # <- nova dependency
    ]
)
```

---

## Próximos Passos

### Onda 1 — ordem de implementação recomendada

| # | Tarefa | Motivo |
|---|---|---|
| 1 | `PlanTier` + `require_tier()` dependency | Desbloqueia controle por tier em todo sistema |
| 2 | Campos `plan_tier`, `max_*` em `AssinaturaTenant` + migration | Base do billing |
| 3 | Módulo **Pessoas** (fornecedores/clientes/funcionários) | Desbloqueador de Financeiro, Compras, RH |
| 4 | Refinamento **Contas a Pagar/Receber** (parcelas, recorrências, alertas) | Core do produto |
| 5 | **Plano de Contas** com categorias RFB (PF e PJ) | Base para Livro Caixa |
| 6 | **Livro Caixa do Produtor Rural** | Principal relatório fiscal |
| 7 | **Fluxo de Caixa** (realizado + previsto 30d no Básico) | Maior dor do produtor |
| 8 | **Centro de Custos** por fazenda/atividade | Pré-requisito do rateio (Profissional) |
| 9 | Refinamento **DRE** | Completar relatórios |
| 10 | **Dashboard financeiro** com alertas | UX de entrada |

---

*Documento gerado em brainstorming — 2026-03-22*
*Status: Brainstorming concluído — aguardando confirmação para implementar*
