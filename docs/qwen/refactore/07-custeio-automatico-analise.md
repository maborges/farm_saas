# Análise: Automatização do Custeio de Safra ↔ Financeiro

**Data:** 2026-04-06
**Escopo:** Fluxo automático Operação → Custo → Despesa → Rateio → Centro de Custo

---

## 1. O que já funciona ✅

### Fluxo implementado no `OperacaoService.criar()`

```
Operação Agrícola criada
       │
       ├──→ Calcula custo_total (soma de insumos FIFO)
       │       └──→ custo_por_ha = custo_total / area_aplicada_ha
       │
       ├──→ Atualiza Safra.custo_realizado_ha (acumulado)
       │
       ├──→ Baixa estoque (FIFO)
       │       └──→ MovimentacaoEstoque (SAÍDA)
       │
       ├──→ Cria Despesa no Financeiro AUTOMATICAMENTE
       │       ├──→ descricao: "PLANTIO — Soja 24/25 (fase PLANTIO)"
       │       ├──→ valor_total: custo_total_operacao
       │       ├──→ status: "PAGO" (já quitada)
       │       ├──→ data_pagamento: data_realizada
       │       ├──→ origem_id: operacao.id
       │       ├──→ origem_tipo: "OPERACAO_AGRICOLA"
       │       └──→ plano_conta_id: busca conta CUSTEIO (fallback)
       │
       └──→ Cria entrada no Caderno de Campo (automático)
```

### Integração existente de relatórios

| Endpoint | O que faz | Arquivo |
|----------|-----------|---------|
| `GET /custos/safra/{safra_id}` | Resumo: custo total, por ha, breakdown por tipo, vs orçamento | `agricola/custos/service.py` |
| `GET /financeiro/relatorios/centro-custos` | Despesas rateadas por safra/talhão | `financeiro/services/relatorio_service.py` |
| `GET /operacoes-agricolas/safra/{id}/por-fase` | Operações agrupadas por fase com custo | `agricola/operacoes/service.py` |

### Modelo `Rateio` já existe

```python
class Rateio(Base):
    despesa_id: UUID         # ← FK para fin_despesas
    safra_id: UUID | None    # ← Centro de custo: safra
    talhao_id: UUID | None   # ← Centro de custo: talhão
    valor_rateado: float
    percentual: float
```

---

## 2. O que NÃO funciona (gaps críticos) 🔴

### G-01: Despesa automática NÃO tem rateio

**Problema:** A despesa criada automaticamente pelo `OperacaoService.criar()` (linha ~190) **não cria rateios**.

```python
# Código atual — SEM rateio:
despesa = Despesa(
    tenant_id=self.tenant_id,
    fazenda_id=fazenda_id,
    plano_conta_id=plano_id,
    descricao=descricao,
    valor_total=float(custo_total_operacao),
    status="PAGO",
    origem_id=operacao.id,
    origem_tipo="OPERACAO_AGRICOLA",
    # ← SEM rateios! Não vincula R$ à safra/talhão no financeiro
)
```

**Impacto:** O relatório `centro_custos()` do financeiro (que usa rateios) **não enxerga** os custos gerados automaticamente pelas operações. O custo aparece em `agricola/custos/` mas **não aparece** em `financeiro/relatorios/centro-custos`.

**Severidade:** 🔴 **CRÍTICA** — duplicidade de verdade: o custo existe em um lugar mas não no outro.

---

### G-02: Custo total da safra tem duas fontes divergentes

| Fonte | Cálculo | Valor |
|-------|---------|-------|
| `Safra.custo_realizado_ha` | `SUM(operacoes.custo_total) / area_plantada_ha` | ✅ Atualizado pelo service |
| `centro_custos()` financeiro | `SUM(rateios.valor_rateado)` | ❌ **ZERO** para operações automáticas (sem rateio) |

**Impacto:** Dashboard financeiro mostra custo zero enquanto dashboard agrícola mostra custo correto.

---

### G-03: Despesa automática não tem parcela

**Problema:** A despesa é criada como `PAGO` com `valor_total` direto. Se o produtor pagou a operação parcelado (comum no agro: "semente em 3x", "fertilizante em 60 dias"), não há suporte.

**Severidade:** 🟡 Média — muitos produtores pagam insumos a prazo.

---

### G-04: Plano de conta é fallback genérico

```python
# Busca qualquer conta com categoria_rfb == "CUSTEIO"
stmt_pc = select(PlanoConta.id).where(
    PlanoConta.categoria_rfb == "CUSTEIO",
    PlanoConta.ativo == True,
).order_by(PlanoConta.natureza).limit(1)
```

**Problema:** Não diferencia PLANTIO de PULVERIZAÇÃO de COLHEITA. Tudo cai na mesma conta contábil.

**Severidade:** 🟡 Média — perde granularidade contábil.

---

### G-05: Custo de mão de obra e máquina não entra no financeiro

O `custo_total` da operação atualmente soma apenas **insumos** (via FIFO). Não inclui:

| Item | Calculado? | Vai pro financeiro? |
|------|-----------|-------------------|
| Insumos (sementes, fertilizantes) | ✅ FIFO | ✅ (parcial — sem rateio) |
| Mão de obra (operador) | ❌ | ❌ |
| Hora-máquina (depreciação, combustível) | ❌ | ❌ |
| Implemento | ❌ | ❌ |

**Impacto:** Custo real da safra está **subestimado** — só considera insumos.

---

### G-06: Sem integração com `CustosService.get_resumo_safra()`

O `CustosService` lê apenas `OperacaoAgricola.custo_total`. Não lê `Despesa` do financeiro. Se o usuário criar uma despesa manual (ex: "frete para grãos") vinculada à safra via rateio, ela **não aparece** no resumo agrícola.

**Impacto:** Dois silos de custo que não se conversam.

---

## 3. Fluxo Ideal (como deveria ser)

```
┌────────────────────────────────────────────────────────────┐
│                   OPERAÇÃO AGRÍCOLA                         │
│   Tipo: PLANTIO  |  Safra: Soja 24/25  |  Talhão: T-01     │
│   Insumos: Semente (20kg × R$ 150) = R$ 3.000              │
│   Insumos: Fertilizante (300kg × R$ 1.200/t) = R$ 360      │
│   MO: Operador (8h × R$ 25/h) = R$ 200                     │
│   Máquina: Trator (4h × R$ 85/h) = R$ 340                  │
│   ──────────────────────────────────────                    │
│   CUSTO TOTAL: R$ 3.900  |  R$ 32,50/ha (120 ha)           │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                   FINANCEIRO (automático)                   │
│                                                             │
│   Despesa #D-0401: "PLANTIO — Soja 24/25"                  │
│   ├── Valor: R$ 3.900                                      │
│   ├── Status: PAGO                                         │
│   ├── Plano de conta: 4.1.01 — Custeio Agrícola            │
│   ├── Origem: OPERACAO_AGRICOLA #OP-0201                    │
│   │                                                        │
│   ├── Rateios:                                             │
│   │   ├── Safra Soja 24/25: R$ 3.900 (100%)               │
│   │   └── Talhão T-01: R$ 3.900 (100%)                    │
│   │                                                        │
│   └── Breakdown (metadados):                               │
│       ├── Insumos: R$ 3.360 (86,2%)                        │
│       ├── Mão de obra: R$ 200 (5,1%)                       │
│       └── Máquinas: R$ 340 (8,7%)                          │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                   CENTRO DE CUSTO                           │
│                                                             │
│   Safra: Soja 24/25                                         │
│   ├── Plantio: R$ 3.900 (120 ha → R$ 32,50/ha)             │
│   ├── Pulverização: R$ 1.200 (120 ha → R$ 10,00/ha)       │
│   ├── Colheita: R$ 2.400 (120 ha → R$ 20,00/ha)           │
│   ├── ───────────────────────────────────────               │
│   ├── CUSTO TOTAL: R$ 7.500                                │
│   ├── CUSTO/HA: R$ 62,50                                   │
│   ├── Orçamento: R$ 8.400 (R$ 70/ha × 120 ha)              │
│   └── Desvio: -10,7% (dentro do orçamento ✅)               │
└────────────────────────────────────────────────────────────┘
```

---

## 4. Tarefas para fechar o gap

### 4.1. Correção urgente (Sprint RF-01 ou RF-02)

| # | Tarefa | Arquivo | Esforço |
|---|--------|---------|---------|
| CF-01 | Criar `Rateio` automaticamente ao criar despesa pela operação | `operacoes/service.py` | 1h |
| CF-02 | Mapear tipo de operação → plano de conta específico | `operacoes/service.py` + lookup table | 2h |
| CF-03 | `CustosService.get_resumo_safra()` ler também despesas rateadas do financeiro | `custos/service.py` | 2h |
| CF-04 | Testes de integração: operação → despesa → rateio → centro de custos | `tests/` | 2h |

**Total:** ~7h

### 4.2. Melhoria importante (Sprint RF-02 ou RF-03)

| # | Tarefa | Arquivo | Esforço |
|---|--------|---------|---------|
| CF-05 | Lookup table `operacao_tipo_fase` incluir mapping para plano de conta | migration + admin | 1h |
| CF-06 | Suporte a custo de mão de obra na operação (operador × horas × valor/hora) | `operacoes/models.py` + `service.py` | 3h |
| CF-07 | Suporte a custo de máquina na operação (horas × tarifa) | `operacoes/models.py` + `service.py` | 3h |
| CF-08 | Campo `metodo_custo` em `Safra`: OPERACOES (atual) ou FINANCEIRO (rateios) | `safras/models.py` | 1h |

**Total:** ~8h

### 4.3. Melhoria avançada (Sprint RF-04)

| # | Tarefa | Arquivo | Esforço |
|---|--------|---------|---------|
| CF-09 | Suporte a despesa parcelada a partir de operação | `operacoes/service.py` | 2h |
| CF-10 | Dashboard unificado: custo agrícola + financeiro lado a lado | Frontend | 4h |
| CF-11 | Alerta de divergência: custo agrícola ≠ custo financeiro | Backend | 2h |

**Total:** ~8h

---

## 5. Resumo do Gap

| Aspecto | Implementado | Gap | Severidade |
|---------|-------------|-----|-----------|
| Custo de insumos calculado via FIFO | ✅ | — | — |
| Despesa criada automaticamente | ✅ | Sem rateio | 🔴 |
| `Safra.custo_realizado_ha` atualizado | ✅ | Só insumos | 🟡 |
| Rateio automático (safra/talhão) | ❌ | **FALTANDO** | 🔴 |
| Plano de conta específico por operação | ❌ | Fallback genérico | 🟡 |
| Custo MO e máquina na operação | ❌ | Só insumos | 🟡 |
| `CustosService` lê despesas do financeiro | ❌ | Silo isolado | 🟡 |
| Despesa parcelada a partir de operação | ❌ | Sempre à vista | 🟢 |
| Dashboard unificado agrícola/financeiro | ❌ | Separados | 🟡 |

**Conformidade do custeio automático: ~40%**

O mecanismo base existe e é sólido (FIFO, baixa estoque, criação de despesa). Mas o **elo rateio** — que conecta o custo operacional ao centro de custo financeiro — está faltando, criando um sistema com dois caminhos paralelos que não se encontram.

---

## 6. Recomendação

**Incluir CF-01 a CF-04 na Sprint RF-01 ou RF-02.** São ~7h de esforço que resolvem o gap mais crítico: a desconexão entre custo operacional e centro de custo financeiro.

Sem isso, o produtor rural verá:
- Dashboard agrícola: "Custo da safra: R$ 45.000"
- Dashboard financeiro: "Custo por centro de custo: R$ 0,00"

Essa divergência destrói confiança no sistema.
