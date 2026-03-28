# Workflow Completo — Gestão de Safra
## Exemplo: Café Colino (Coffea arabica, variedade Colino)

> Documento de referência para onboarding, treinamento e validação do produto.
> Mapeia cada etapa do ciclo agrícola ao módulo/endpoint correspondente no sistema.

---

## Visão Geral do Ciclo

```
PRÉ-SAFRA                    SAFRA EM ANDAMENTO                  PÓS-COLHEITA
─────────────────────────────────────────────────────────────────────────────
[1] Cadastros Base
[2] Planejamento
[3] Preparo Solo     →  [4] Plantio  →  [5] Desenvolvimento  →  [6] Colheita  →  [7] Encerramento
                                              ↕                        ↕
                                    [Monitoramento NDE]       [Romaneios/Qualidade]
                                    [Fenologia]               [Financeiro]
```

---

## FASE 0 — Cadastros Base (Pré-requisitos)
> Deve ser feito **uma única vez** ao configurar a fazenda. Sem isso, nada funciona.

### 0.1 Propriedade e Talhões
| O que fazer | Onde no sistema | Status |
|---|---|---|
| Cadastrar a Fazenda (nome, localização, CNPJ/CPF) | `POST /core/fazendas` | ✅ |
| Criar Áreas Rurais hierarquicamente: Fazenda → Gleba → Talhão | `POST /cadastros/propriedades` | ✅ |
| Definir área em hectares de cada talhão | Campo `area_hectares` na AreaRural | ✅ |
| Registrar matrícula do imóvel (CAR, NIRF) | `MatriculaImovel` | ✅ |

**Exemplo Café Colino:**
```
Fazenda Colino (150 ha total)
  └── Gleba Alta (80 ha)
        ├── Talhão A1 — 20 ha (café em produção, 5 anos)
        ├── Talhão A2 — 25 ha (café novo, 2 anos)
        └── Talhão A3 — 35 ha (reforma)
  └── Gleba Baixa (70 ha)
        ├── Talhão B1 — 30 ha (café adulto, 8 anos)
        └── Talhão B2 — 40 ha (pastagem em conversão)
```

### 0.2 Insumos e Produtos
| O que fazer | Onde no sistema | Status |
|---|---|---|
| Cadastrar fertilizantes (NPK, micronutrientes) | `POST /cadastros/produtos` tipo=FERTILIZANTE | ✅ |
| Cadastrar defensivos (herbicidas, fungicidas, inseticidas) | `POST /cadastros/produtos` tipo=DEFENSIVO | ✅ |
| Cadastrar sementes/mudas | `POST /cadastros/produtos` tipo=SEMENTE | ✅ |
| Definir preço médio de cada produto | Campo `preco_medio` | ✅ |
| Associar cultura ao produto (dose recomendada, carência) | `ProdutoAgricola` | ✅ |

**Exemplo Café Colino — insumos essenciais:**
- Nitrogênio (ureia 45% N) — 300 kg/ha/ano parcelado em 3×
- Superfosfato simples — 80 kg/ha no plantio
- Cloreto de potássio — 150 kg/ha/ano parcelado em 2×
- Herbicida pré-emergente (ex: oxyfluorfen)
- Fungicida sistêmico (ex: tebuconazole para ferrugem)
- Inseticida (bicho-mineiro, broca do café)

### 0.3 Pessoas e Equipe
| O que fazer | Onde no sistema | Status |
|---|---|---|
| Cadastrar agrônomo responsável | `POST /cadastros/pessoas` + perfil agronomo | ✅ |
| Cadastrar operadores/colhedores | `POST /cadastros/pessoas` + RH | ✅ |
| Cadastrar fornecedores de insumos | `POST /cadastros/pessoas` tipo=FORNECEDOR | ✅ |
| Cadastrar compradores/tradings | `POST /cadastros/pessoas` tipo=CLIENTE | ✅ |

### 0.4 Equipamentos e Frota
| O que fazer | Onde no sistema | Status |
|---|---|---|
| Cadastrar tratores, pulverizadores, colhedoras | `POST /cadastros/equipamentos` | ✅ |
| Vincular documentos (CRLV, seguro) | `DocumentoEquipamento` | ✅ |

### 0.5 Plano de Contas Financeiro
| O que fazer | Onde no sistema | Status |
|---|---|---|
| Criar contas de custeio (insumos, mão de obra, maquinário) | `POST /financeiro/planos-conta` categoria_rfb=CUSTEIO | ✅ |
| Criar contas de receita (venda de grãos, subprodutos) | `POST /financeiro/planos-conta` categoria_rfb=RECEITA_ATIVIDADE | ✅ |

> ⚠️ **Pré-requisito crítico:** sem ao menos 1 plano de conta CUSTEIO e 1 RECEITA_ATIVIDADE ativos, as integrações automáticas (operações → despesa, romaneio → receita) **não criam lançamentos**.

### 0.6 Escalas Fenológicas (seed)
```bash
# Executar uma vez por tenant para Café
python -m agricola.fenologia.seed_escalas <tenant_id>
```
> ⚠️ **Falta implementar:** escalas fenológicas do café (BBCH para Coffea arabica). Atualmente só há Soja e Milho.

---

## FASE 1 — Planejamento da Safra

### 1.1 Criar a Safra
```
POST /safras
{
  "cultura": "Café",
  "cultivar_nome": "Colino",
  "ano_safra": "2025/2026",
  "data_plantio_prevista": "2025-10-01",   // se replantio/reforma
  "data_colheita_prevista": "2026-05-01",
  "produtividade_meta_sc_ha": 40,           // 40 sc/ha = meta boa para Colino
  "area_plantada_ha": 75,                   // talhões A1 + A2 + B1
  "status": "PLANEJADA"
}
```

### 1.2 Vincular Talhões à Safra
```
PUT /safras/{id}/talhoes
{
  "talhao_ids": ["uuid-A1", "uuid-A2", "uuid-B1"],
  "areas_ha": {
    "uuid-A1": 20,
    "uuid-A2": 25,
    "uuid-B1": 30
  }
}
```
> O primeiro talhão será marcado como **principal**. A soma das áreas determina a produtividade sc/ha nos romaneios.

### 1.3 Orçamento de Custeio
```
POST /agricola/planejamento/orcamentos
```
Itens do orçamento padrão para Café Colino (75 ha):

| Item | Qtd/ha | Unit | Custo/ha | Total |
|---|---|---|---|---|
| Ureia 45% N | 300 kg | R$ 3,20 | R$ 960 | R$ 72.000 |
| Superfosfato simples | 80 kg | R$ 2,80 | R$ 224 | R$ 16.800 |
| KCl | 150 kg | R$ 3,50 | R$ 525 | R$ 39.375 |
| Herbicida (oxyfluorfen) | 2 L | R$ 45 | R$ 90 | R$ 6.750 |
| Fungicida (tebuconazole) | 3 aplicações | R$ 120 | R$ 360 | R$ 27.000 |
| Inseticida | 2 aplicações | R$ 80 | R$ 160 | R$ 12.000 |
| Mão de obra colheita | 40 dias/ha | R$ 180 | R$ 7.200 | R$ 540.000 |
| **Total estimado** | | | **R$ 9.519/ha** | **R$ 713.925** |

### 1.4 Checklist de Planejamento
O sistema gera automaticamente os itens de checklist para a fase `PLANEJADA`:
- [ ] Análise de solo atualizada (< 2 anos)
- [ ] Orçamento aprovado
- [ ] Contratos de insumos assinados
- [ ] ART do agrônomo emitida

---

## FASE 2 — Preparo do Solo
> Avançar safra: `POST /safras/{id}/avancar-fase/PREPARO_SOLO`

### 2.1 Análise de Solo (obrigatório antes de qualquer adubação)
```
POST /analises-solo
{
  "safra_id": "...",
  "talhao_id": "uuid-A1",
  "data_coleta": "2025-08-01",
  "ph_cacl2": 5.8,
  "ph_agua": 6.3,
  "p_mehlich": 18,        // mg/dm³
  "k_cmol": 0.25,
  "ca_cmol": 3.2,
  "mg_cmol": 1.1,
  "al_cmol": 0.1,
  "h_al_cmol": 4.5,
  "mo_dag_kg": 3.2,
  "argila_pct": 55
}
```
O sistema calcula automaticamente:
- **CTC** = Ca + Mg + K + H+Al = 9.05 cmolc/dm³
- **V%** = (Ca + Mg + K) / CTC × 100 = 50.3%
- **Recomendação de calagem** se V% < 60% → calcário necessário
- Classificação de P, K, pH

**Para Café Colino:** V% ideal ≥ 60-65%. pH ideal 5.5–6.5 (CaCl₂).

### 2.2 Operações de Preparo
```
POST /operacoes
{
  "safra_id": "...",
  "talhao_id": "uuid-A1",
  "tipo": "CALAGEM",
  "data_realizada": "2025-08-15",
  "area_aplicada_ha": 20,
  "insumos": [{
    "insumo_id": "uuid-calcario",
    "dose_por_ha": 2000,   // 2 t/ha de calcário dolomítico
    "unidade": "kg"
  }]
}
```
> ✅ Automaticamente cria `Despesa` no financeiro com `origem_tipo=OPERACAO_AGRICOLA`

Operações típicas de preparo:
1. `CALAGEM` — se necessário (pós análise de solo)
2. `GESSAGEM` — se Al trocável alto
3. `ROÇAGEM` — limpeza das entrelinhas
4. `ADUBACAO` — adubação de fundação (P e K)

---

## FASE 3 — Plantio (ou manutenção para café adulto)
> Avançar safra: `POST /safras/{id}/avancar-fase/PLANTIO`

> ⚠️ **Nota importante para Café:** diferente de culturas anuais, o café é **perene**. Numa safra de café adulto, a fase "Plantio" corresponde ao **manejo de pós-colheita da safra anterior** (poda, esqueletamento, recepa).

### 3.1 Operações de Plantio/Manutenção
```
POST /operacoes
{
  "tipo": "PODA",          // ou PLANTIO para lavoura nova
  "data_realizada": "...",
  "insumos": []            // sem insumos na poda
}
```

Operações típicas desta fase:
1. `PODA` — Esqueletamento, recepa ou poda de producao
2. `PLANTIO` — Só para lavouras novas (mudas Colino)
3. `ADUBACAO` — Adubação de cova no plantio

### 3.2 Registro Fenológico (início do monitoramento)
```
POST /fenologia/registros
{
  "safra_id": "...",
  "talhao_id": "uuid-A1",
  "escala_id": "uuid-escala-VE",   // Emergência / Ponteiro
  "data_observacao": "2025-09-01",
  "percentual_area": 80,
  "observacoes": "Ponteiro em desenvolvimento após poda"
}
```

---

## FASE 4 — Desenvolvimento
> Avançar safra: `POST /safras/{id}/avancar-fase/DESENVOLVIMENTO`

Esta é a fase mais longa do café (~8 meses). Aqui concentra-se a maior parte das operações.

### 4.1 Adubações Parceladas (N-P-K)
Café Colino requer **4-6 adubações** ao longo do desenvolvimento:

| Época | Operação | Insumo principal | Dose/ha |
|---|---|---|---|
| Set/Out | Adubação 1/4 N | Ureia | 75 kg |
| Nov/Dez | Adubação 2/4 N | Ureia | 75 kg |
| Jan/Fev | Adubação 3/4 N | Ureia + K | 75 kg + 75 kg KCl |
| Mar/Abr | Adubação 4/4 N | Ureia + K | 75 kg + 75 kg KCl |

```
POST /operacoes  (para cada aplicação)
{
  "tipo": "ADUBACAO",
  "fase_safra": "DESENVOLVIMENTO",
  "data_realizada": "2025-10-15",
  "insumos": [
    { "insumo_id": "uuid-ureia", "dose_por_ha": 75, "unidade": "kg" }
  ]
}
```

### 4.2 Manejo Fitossanitário (Monitoramento NDE)
O café tem 3 pragas/doenças principais:

| Agente | NDE padrão | Frequência monitoramento |
|---|---|---|
| Bicho-mineiro (*Leucoptera coffeella*) | 30% folhas com minas ativas | Quinzenal |
| Broca do café (*Hypothenemus hampei*) | 3% frutos brocados | Semanal (floração→colheita) |
| Ferrugem laranja (*Hemileia vastatrix*) | 5% folhas com pústulas | Quinzenal |
| Cercosporiose (*Cercospora coffeicola*) | 10% folhas com manchas | Mensal |

```
POST /monitoramentos
{
  "safra_id": "...",
  "talhao_id": "uuid-A1",
  "agente_nome": "Ferrugem laranja",
  "agente_tipo": "DOENCA",
  "nivel_infestacao": 6.5,     // 6.5% > NDE de 5% → alerta!
  "nde_cultura": 5.0,
  "estagio_fenologico_codigo": "R1",
  "data_registro": "2025-11-20"
}
```
> ✅ Se `nivel_infestacao >= nde_cultura`, `atingiu_nde=True` e aparece no **Dashboard como alerta crítico**.

### 4.3 Aplicações de Defensivos
Após NDE atingido, registrar a aplicação:
```
POST /operacoes
{
  "tipo": "APLICACAO_FUNGICIDA",
  "insumos": [{
    "insumo_id": "uuid-tebuconazole",
    "dose_por_ha": 0.75,
    "unidade": "L",
    "carencia_dias": 14
  }]
}
```

### 4.4 Acompanhamento Fenológico
Estágios do café (BBCH adaptado) que precisam de seed:
- `10` — Gema dormente
- `51` — Botão floral fechado
- `60` — Início floração (popcorn)
- `65` — Plena floração
- `71` — Frutificação (chumbinho)
- `75` — Expansão do fruto (verde)
- `81` — Início maturação (verde-cana)
- `85` — Cereja (maturação plena)
- `89` — Passa/seco (sobrematuração)

> ⚠️ **Gap identificado:** seed de escalas fenológicas do Café ainda não existe. Precisa criar `seed_escalas_cafe.py`.

### 4.5 Checklist da Fase Desenvolvimento
- [ ] Adubações 1ª e 2ª parcela realizadas
- [ ] Monitoramento quinzenal ativo
- [ ] Receituário agronômico emitido para aplicações
- [ ] Manutenção preventiva das máquinas realizada

---

## FASE 5 — Colheita
> Avançar safra: `POST /safras/{id}/avancar-fase/COLHEITA`

### 5.1 Determinação do Ponto de Colheita
O café Colino é colhido quando **≥ 70% dos frutos estão no estágio cereja (R85)**.

Registrar no monitoramento:
```
POST /monitoramentos
{
  "agente_nome": "Ponto de maturação",
  "agente_tipo": "DOENCA",    // usar categoria OBSERVACAO quando disponível
  "nivel_infestacao": 75,     // 75% cereja
  "observacoes": "Aprovado para iniciar colheita"
}
```

### 5.2 Tipos de Colheita para Café
| Método | Quando usar | Passagem |
|---|---|---|
| **Derriça manual** | Lavouras íngremes, alta qualidade | 1-2 passagens |
| **Derriça mecânica** | Terrenos planos, alto volume | 1-2 passagens |
| **Colheita seletiva** | Cafés especiais, grãos maduros | 3-4 passagens |

### 5.3 Registrar Romaneio de Colheita
**Por cada carga/talhão colhido:**
```
POST /romaneios
{
  "safra_id": "...",
  "talhao_id": "uuid-A1",
  "data_colheita": "2026-05-10",
  "numero_romaneio": "ROM-001",
  "turno": "MANHA",
  "peso_bruto_kg": 12000,      // 12 t brutas
  "tara_kg": 200,              // peso do transporte
  "umidade_pct": 55,           // café cereja: 55-65% umidade
  "impureza_pct": 2.5,
  "preco_saca": 950            // R$ 950/sc de 60 kg
}
```

**O sistema calcula automaticamente:**
- Peso líquido = 12000 - 200 = 11800 kg
- Desconto umidade = (55-14) × 0.014 × 11800 = 6779 kg
  > ⚠️ **Gap:** o cálculo de desconto atual usa padrão de grãos secos (14%). Para café cereja (55% umidade), a fórmula de conversão é diferente: **fator de conversão cereja→seco = 4,5:1 a 5:1**. Precisa de ajuste para café.
- Sacas padrão (60 kg)
- Produtividade sc/ha
- Receita total
- Lançamento automático em `fin_receitas` ✅

### 5.4 Processamento Pós-Colheita (gap futuro)
O café passa por beneficiamento antes de virar saca:
- **Via seca** (natural): secar no terreiro/secador mecânico
- **Via úmida** (lavado/despolpado): despolpar → fermentar → lavar → secar
- **Honey process**: despolpar sem fermentação

> ⚠️ **Gap:** processamento pós-colheita não tem módulo. Sugere-se criar `agricola/beneficiamento/` para controle de lotes, secagem, armazenagem e classificação SCAA.

---

## FASE 6 — Pós-Colheita / Encerramento
> Avançar safra: `POST /safras/{id}/avancar-fase/POS_COLHEITA`
> Encerrar safra: `POST /safras/{id}/avancar-fase/ENCERRADA`

### 6.1 Análise de Solo Pós-Safra
Repetir análise de solo para planejamento da próxima safra.

### 6.2 Fechamento Financeiro
Consultar:
```
GET /romaneios/kpis?safra_id=...
GET /agricola/custos/safra/{safra_id}
GET /operacoes/safra/{safra_id}  (resumo por fase)
```

**Indicadores finais Café Colino (75 ha, meta 40 sc/ha):**
| KPI | Meta | Como calcular |
|---|---|---|
| Produtividade real | 40 sc/ha | Total sacas / área total |
| Receita bruta | R$ 2.850.000 | 3.000 sc × R$ 950 |
| Custo total | R$ 713.925 | Soma despesas `origem_tipo=OPERACAO_AGRICOLA` |
| Margem bruta | R$ 2.136.075 | Receita - Custo |
| Custo por saca | R$ 237,97 | Custo total / sacas |
| Break-even | 751 sc | Custo total / preço saca |

### 6.3 Rastreabilidade (gap parcial)
Associar cada romaneio ao lote de venda:
- Qual insumo foi aplicado em qual talhão
- Período de carência respeitado
- Número do receituário agronômico
> ⚠️ **Gap:** módulo de rastreabilidade tem backend mas sem frontend.

---

## Resumo de Gaps Identificados

| # | Gap | Impacto | Prioridade |
|---|---|---|---|
| G1 | Escalas fenológicas do café não seedadas | Médio — fenologia não funciona para café | Alta |
| G2 | Cálculo de desconto de umidade do café (cereja: ~55% → seco: ~12%) usa fórmula errada | Alto — sacas calculadas errado | Alta |
| G3 | Módulo de beneficiamento/processamento pós-colheita inexistente | Alto para cafés especiais | Média |
| G4 | Frontend de rastreabilidade inexistente | Médio | Média |
| G5 | Orçamento de custeio sem UI para adicionar itens manualmente | Médio | Média |
| G6 | Monitoramento não tem categoria "OBSERVACAO" (só PRAGA/DOENCA/INVASORA) | Baixo | Baixa |
| G7 | NDVI sem frontend | Baixo | Baixa |

---

## Checklist de Onboarding (ordem de execução)

```
□ 0.1  Cadastrar fazenda e talhões com áreas (ha)
□ 0.2  Cadastrar insumos com preço médio e dados agronômicos
□ 0.3  Cadastrar equipe (agrônomo, operadores, fornecedores)
□ 0.4  Cadastrar equipamentos
□ 0.5  Criar plano de contas (≥1 CUSTEIO + ≥1 RECEITA_ATIVIDADE)
□ 0.6  Executar seed de escalas fenológicas (+ criar seed do Café)
□ 1.1  Criar safra
□ 1.2  Vincular talhões à safra
□ 1.3  Criar orçamento de custeio
□ 2.1  Registrar análise de solo por talhão
□ 2.2  Registrar operações de preparo (calagem, gessagem)
□ 3.x  Avançar para PLANTIO e registrar operações
□ 4.x  Registrar adubações + monitoramentos quinzenais + fenologia
□ 5.x  Avançar para COLHEITA e lançar romaneios
□ 6.x  Encerrar safra e gerar relatório final
```
