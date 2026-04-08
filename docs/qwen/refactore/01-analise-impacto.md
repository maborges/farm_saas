# Análise de Impacto — Conceito Arquitetural vs Implementação Atual

**Data:** 2026-04-06
**Referências:**
- `docs/architecture/agro-conceitos-arquitetura.md`
- `docs/contexts/core/cadastro-propriedade-conceitos.md`
- `docs/qwen/01-arquitetura.md`
- `docs/qwen/02-modulos.md`

---

## 1. Veredito Geral

A implementação atual segue **~70% do conceito arquitetural**. Os eixos TEMPORAL (`Safra`) e EXECUÇÃO (`OperacaoAgricola`) **existem e são robustos**. O problema não é de arquitetura, mas de **consistência conceitual** e **validações** que permitem uso incorreto.

### Regra Absoluta: "O custo é TEMPORAL, não territorial"

| Regra do conceito | Implementação | Conformidade |
|-------------------|--------------|-------------|
| Custos pertencem ao Ciclo (Safra) | ✅ `OperacaoAgricola.custo_total` + `Safra.custo_realizado_ha` auto-atualizado | ✅ 95% |
| Talhão NÃO possui custo direto | ✅ `AreaRural` não tem campo de custo | ✅ 100% |
| Operação sempre tem contexto temporal | ✅ `OperacaoAgricola.safra_id` é NOT NULL | ✅ 100% |
| Operação = 1 Ciclo + 1 Área | ✅ `safra_id` + `talhao_id` na operação | ✅ 100% |
| Financeiro é consequência | ✅ Custo nasce dos insumos da operação | ✅ 90% |
| Estoque reage às operações | ✅ FIFO deduction implementado | ✅ 85% |
| Agricultura + Pecuária = mesmo motor | ❌ Módulos separados | ❌ 30% |

---

## 2. Análise por Dimensão Conceitual

### 2.1. ESPAÇO (Território) — `AreaRural`

```
Implementado:                    Conceito ideal:
┌─────────────────────┐          ┌──────────────────────────┐
│ AreaRural           │          │ AreaRural                │
│ ├─ PROPRIEDADE ✅   │          │ ├─ PROPRIEDADE ✅        │
│ ├─ GLEBA ✅         │          │ ├─ GLEBA ✅              │
│ ├─ TALHAO ✅        │          │ │   ├─ TALHAO ✅         │
│ ├─ PASTAGEM ✅      │          │ │   ├─ SUBTALHAO ❌      │
│ ├─ PIQUETE ✅       │          │ │   │   └─ ZONA_MANEJO ❌│
│ ├─ APP ✅           │          │ │   └─ PIQUETE ✅        │
│ ├─ RESERVA_LEGAL ✅ │          │ ├─ APP ✅                │
│ ├─ UNIDADE_PROD ✅  │          │ ├─ RESERVA_LEGAL ✅      │
│ ├─ AREA ✅          │          │ └─ UNIDADE_PRODUTIVA ✅  │
│ ├─ SEDE ✅          │          │                          │
│ ├─ ARMAZEM ✅       │          │ SUBTALHAO ❌ FALTANDO    │
│ ├─ INFRAESTRUTURA ✅│          │ ZONA_DE_MANEJO ❌ FALT.  │
│ └─ parent_id ✅     │          │ validação hierarquia ❌  │
└─────────────────────┘          └──────────────────────────┘
```

| Gap | Impacto | Severidade |
|-----|---------|------------|
| Sem tipo `SUBTALHAO` | Não há semântica para variação interna ao talhão | 🔴 |
| Sem tipo `ZONA_DE_MANEJO` | Sem unidade analítica para VRA | 🔴 |
| Sem validação de hierarquia | Pode criar PIQUETE dentro de APP | 🟡 |
| Atributos de solo em `dados_extras` JSON | Não é queryável | 🟡 |
| `area_hectares` usa Float | Precisão fiscal comprometida | 🟡 |

### 2.2. TEMPO (Ciclo Produtivo) — `Safra`

```python
# Problema crítico: talhao_id é NOT NULL
class Safra(Base):
    talhao_id: UUID = mapped_column(nullable=False)  # ← ANTI-PADRÃO
    # Quando deveria usar SafraTalhao (N:N já existe)
```

| Gap | Impacto | Severidade |
|-----|---------|------------|
| `talhao_id` obrigatório | Obriga 1 safra por talhão; não permite safra multi-talhão | 🔴 |
| Sem `objetivo_economico` | Não diferencia comercial, consumo próprio, experimento | 🟡 |
| `ano_safra` é String | Deveria ser estruturado | 🟢 |
| Sem vínculo com Gleba | Safra não pode abranger gleba inteira | 🟡 |

### 2.3. EXECUÇÃO (Operação) — `OperacaoAgricola`

| Gap | Impacto | Severidade |
|-----|---------|------------|
| Aceita qualquer tipo de `talhao_id` | Pode vincular operação a GLEBA, SEDE, APP | 🟡 |
| Sem vínculo com Subtalhão/Zona | Quando existirem, operação não restringe tipo | 🟡 |
| `custo_total` derivado dos insumos | ✅ Correto | ✅ |
| Integração com estoque FIFO | ✅ Implementado | ✅ |

### 2.4. RESULTADO (Economia)

| Gap | Impacto | Severidade |
|-----|---------|------------|
| Sem cálculo de margem líquida | `receita - custo` não é automático | 🟡 |
| Sem ROI da safra | `(receita - custo) / custo` não existe | 🟡 |
| `resumo_planejado_realizado` existe | ✅ Comparativo básico funciona | ✅ |
| Dashboard agrícola com KPIs | ✅ Safras ativas, custo acumulado, sacas | ✅ |

---

## 3. O que NÃO mexer (risco > benefício)

| Mudança | Por quê | Alternativa |
|---------|---------|-------------|
| Renomear `Safra` → `CicloProdutivo` | 50+ FKs, 7 módulos, frontend todo | Manter `Safra`, criar `CicloPecuaria` paralelo |
| Unificar Agricultura + Pecuária | 200h+, risco altíssimo | Unificar só nos indicadores de custo |
| Migrar `dados_extras` JSON → colunas | Migration complexa, dados existentes | Adicionar colunas novas gradualmente |
| Reescrever módulo pecuário | Conceitualmente diferente | Adapter de custos que lê ambos |

---

## 4. Matriz de Esforço vs Valor

```
         VALOR ↑
                │
         ALTO   │  ● SUBTALHAO/ZONA    ● Hierarquia UI
                │  ● VRA por zona      ● Validação hierárquica
                │
                │  ● AmostraSolo       ● RN-CP-004 bloqueante
                │  ● HistoricoUso      ● Campos precisão
         MÉDIO  │
                │
                │  ● modulos_fiscais   ● Mapa na página detalhe
                │  ● Editar propriedade
                │
         BAIXO  │  ● Empty state CTA   ● Grid de cards
                │
                └────────────────────────────────────→
                  BAIXO        MÉDIO         ALTO
                          ESFORÇO
```

**Quadrante prioritário (alto valor, baixo esforço):**
- Adicionar tipos `SUBTALHAO` + `ZONA_DE_MANEJO` ao enum
- Validação de hierarquia no `AreaRuralService`
- `Safra.talhao_id` → nullable
- Campos de precisão no `AreaRural`

---

## 5. Conformidade Final por Dimensão

| Dimensão | Entidade | Antes → Depois | Gap restante |
|----------|----------|---------------|-------------|
| **ESPAÇO** | `AreaRural` | 75% → **95%** | modulos_fiscais |
| **TEMPO** | `Safra` | 85% → **92%** | objetivo_economico |
| **EXECUÇÃO** | `OperacaoAgricola` | 95% → **98%** | restrição tipo área |
| **RESULTADO** | `resumo_*` | 70% → **85%** | margem, ROI |
| **UNIFICADO** | Agro = Agri + Pec | 30% → **35%** | Adiado |
