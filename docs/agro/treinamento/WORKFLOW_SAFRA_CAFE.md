# Workflow: Criação e Gestão de Safra de Café

## 🎯 Visão Geral

O fluxo de uma safra de café na aplicação segue **7 fases principais** com páginas de suporte para planejamento, execução, monitoramento e finalização. Cada fase marca um ponto crítico no ciclo produtivo.

---

## 📋 Fases da Safra e Workflow

### **FASE 1: PLANEJADA** (Preparação)
**Objetivo:** Definir a safra, alocar recursos, planejar custos e operações.

#### Páginas envolvidas:
1. **Safras** (`/agricola/safras`)
   - Criar nova safra de café
   - Selecionar cultura: "Café"
   - Indicar talhão/área onde será plantada
   - Definir: ano safra, cultivar, data prevista de plantio

2. **Orçamento/Planejamento** (`/safras/[id]/orcamento`)
   - Criar itens de orçamento por categoria:
     - **SEMENTE:** Sementes ou mudas de café (exemplo: 200kg de sementes)
     - **FERTILIZANTE:** Adubos necessários (ex: 500kg de NPK)
     - **DEFENSIVO:** Fungicidas, inseticidas (ex: 50L de defensivo)
     - **COMBUSTIVEL:** Diesel e gasolina para operações
     - **MAO_DE_OBRA:** Salários de trabalhadores
     - **SERVICO:** Terceirizações (preparação de solo, transporte)
     - **OUTROS:** Imprevistos
   - Visualizar custo total previsto por hectare

3. **Financeiro** (`/safras/[id]/financeiro`)
   - Acompanhar despesas já realizadas
   - Desvio entre orçado vs realizado

#### ✅ Status do Fluxo: **CORRETO**
- O usuário pode criar safra, alocar recursos e fazer previsões financeiras
- Faltaria: "Checklist de preparação" para guiar o usuário (ex: "Solo foi analisado?")

---

### **FASE 2: PREPARO_SOLO** (Preparação de Solo)
**Objetivo:** Preparar a terra para o plantio.

#### Páginas envolvidas:
1. **Analises Solo** (`/safras/[id]/analises-solo`)
   - Registrar análise de solo (pH, nutrientes)
   - Decidir se precisa de correção (calcário, etc.)
   - Registrar quando a correção foi aplicada

2. **Operações** (`/safras/[id]/operacoes`)
   - Registrar operações de preparo:
     - Aração
     - Gradagem
     - Destoca (remoção de raízes)
     - Calagem (se necessário)
   - Cada operação: data, tipo, custo, responsável

3. **Checklist** (`/safras/[id]/checklist`)
   - Completar checklist da fase "PREPARO_SOLO"
   - Exemplos de itens: "Solo analisado?", "Calcário aplicado?", "Terreno gradeado?"

#### ✅ Status do Fluxo: **INCOMPLETO**
- ❌ Não há vinculação automática de checklist por fase
- ⚠️ Operações devem mostrar filtro por fase/tipo

---

### **FASE 3: PLANTIO** (Plantio)
**Objetivo:** Efetuar o plantio das mudas/sementes.

#### Páginas envolvidas:
1. **Operações** (`/safras/[id]/operacoes`)
   - Registrar operação de plantio:
     - Data real de plantio
     - Quantidade de mudas/sementes usadas
     - Espaçamento (ex: 3,5m x 0,7m para café)
     - Custo da operação
   
2. **Safra Detail** (`/safras/[id]`)
   - Atualizar `data_plantio_real` automaticamente quando fase muda para PLANTIO
   - Ou registrar manualmente na operação

3. **Caderno** (`/safras/[id]/caderno`)
   - Registrar observações do plantio
   - Condições climáticas no dia
   - Problemas encontrados

#### ✅ Status do Fluxo: **CORRETO**
- O fluxo funciona, mas poderia ter confirmação visual de que plantio foi realizado

---

### **FASE 4: DESENVOLVIMENTO** (Crescimento)
**Objetivo:** Acompanhar o desenvolvimento da planta até a colheita.

#### Páginas envolvidas:
1. **Fenologia** (`/safras/[id]/fenologia`)
   - **CRÍTICO para café!** Rastreia o desenvolvimento:
     - Brotação
     - Floração
     - Granação
     - Maturação
   - Cada estágio marca progresso importante

2. **Operações** (`/safras/[id]/operacoes`)
   - Registrar operações de manutenção:
     - Adubações (normalmente 3-4 ao ano para café)
     - Aplicações de defensivos contra pragas/doenças
     - Capinas
     - Podas
     - Desbrota

3. **Monitoramento** (`/safras/[id]/monitoramento`)
   - Rastrear pragas: ferrugem, broca, acaro da mancha
   - Registrar doenças: oidio, antracnose
   - Acompanhar pressão de pragas ao longo da safra

4. **NDVI** (`/safras/[id]/ndvi`)
   - Imagens de satélite para avaliar saúde da plantação
   - Detectar áreas com problemas (nutrientes, água, doenças)

5. **Caderno** (`/safras/[id]/caderno`)
   - Anotações diárias do campo
   - Observações de clima, pragas, desenvolvimento

#### ✅ Status do Fluxo: **BOAPPROXIMADAMENTE CORRETO**
- Fenologia existe mas precisa de melhor integração visual
- ⚠️ Falta integração entre fenologia e operações (operações devem sugerir base em estágio fenológico)

---

### **FASE 5: COLHEITA** (Colheita)
**Objetivo:** Efetuar a colheita dos frutos e registrar lotes.

#### Menu: `Agricultura → ③ Colheita → Romaneios (Colheita)`

#### Páginas envolvidas:
1. **Operações** 
   - Menu: `Agricultura → ② Operação → Operações de Campo`
   - Registrar operação de colheita:
     - Data de início/fim
     - Método: manual ou mecanizada
     - Quantidade colhida (sacas/kg)
     - Custo da colheita

2. **Romaneios (Colheita)** 
   - Menu: `Agricultura → ③ Colheita → Romaneios (Colheita)`
   - **CRÍTICO!** Registrar cada lote colhido:
     - Talhão de origem
     - Data da colheita
     - Quantidade em kg ou sacas
     - Qualidade (bica corrida, cereja, etc.)
     - Transporte: local de armazenagem
   - ✅ **Botão "Processar" (🏭):** Cria automaticamente lote de beneficiamento
   - Este é o ponto de origem para geração de commodity

3. **Financeiro** 
   - Menu: `Agricultura → ① Planejamento → Orçamento` ou Dashboard específico
   - Acompanhar custos da colheita

#### ✅ Status do Fluxo: **COMPLETO**
- ✅ Romaneios com integração clara para iniciar beneficiamento (botão "Processar")
- ✅ Fluxo automático: Romaneio → Lote de Beneficiamento
- ✅ Commodity gerada automaticamente a partir de lote beneficiado

---

### **FASE 6: POS_COLHEITA** (Pós-Colheita / Beneficiamento)
**Objetivo:** Processar o café colhido até ficar pronto para venda.

#### Menu: `Agricultura → ④ Pós-Colheita → Beneficiamento`

#### Páginas envolvidas:

1. **Romaneios (origem dos lotes)** 
   - Menu: `Agricultura → ③ Colheita → Romaneios (Colheita)`
   - Visualizar lotes colhidos
   - Botão 🏭 **"Processar":** Cria lote beneficiamento pré-populado (Int. 0)
   - Fluxo: Romaneio → Lote de Beneficiamento

2. **Beneficiamento** 
   - Menu: `Agricultura → ④ Pós-Colheita → Beneficiamento`
   - **CRÍTICO PARA CAFÉ! Processos:**
     - **Recebimento:** Registrar lotes chegando (cereja, bica, etc.)
     - **Separação:** Separar por qualidade, tipo
     - **Secagem:** Monitorar teor de umidade (ideal: 11-12%)
     - **Descascamento:** Remover casca
     - **Classificação:** Grãos miúdos, peneira 16, etc.
     - **Embalagem:** Sacos de 60kg padrão
   - **Perdas Detalhadas:** Registrar perdas por secagem, quebra, defeito
   - **Novo Dashboard "Relatório de Rendimento"** (Int. 1):
     - Visualizar breakdown por método (NATURAL, LAVADO, HONEY, DESCASCADO)
     - Eficiência % com badges coloridas (verde ≥95%, amarelo ≥80%, vermelho <80%)
   - **Botão 📦 "Armazenar"** (Int. 3, status=ARMAZENADO):
     - Cria SKU rastreável em estoque
   - **Botão 🛒 "Gerar Venda"** (Int. 0, status=ARMAZENADO + lote_estoque):
     - Cria ComercializacaoCommodity em RASCUNHO

3. **Blending (Opcional)** 
   - Menu: `Agricultura → ④ Pós-Colheita → Beneficiamento` (botão "Processar Selecionados")
   - Agrupar múltiplos romaneios em 1 lote (Int. 2)
   - Exemplo: 3 romaneios de qualidades diferentes → 1 lote blend

4. **Estoque** 
   - Menu: `Operacional → ② Estoque → Inventário`
   - Controlar estoque de café beneficiado
   - Rastrear movimentações
   - Rastreabilidade: ver qual lote beneficiamento originou cada SKU

#### ✅ Status do Fluxo: **COMPLETO** (4 Integrações Implementadas - 2026-04-15)

**Integração 0: Romaneios → Beneficiamento → Comercialização**
- ✅ Botão "Processar" (🏭) em cada romaneio cria lote beneficiamento pré-populado
- ✅ Lote herda: safra_id, talhao_id, peso_entrada, umidade do romaneio
- ✅ Botão "Gerar Venda" (🛒) quando status=ARMAZENADO cria ComercializacaoCommodity
- ✅ Rastreabilidade completa: Romaneio → Lote → Venda

**Integração 1: Relatório de Rendimento**
- ✅ Dashboard "Relatório de Rendimento por Método" mostra:
  - Peso entrada/saída por método (NATURAL, LAVADO, HONEY, DESCASCADO)
  - Fator de redução real vs esperado
  - **Eficiência %** = (fator_esperado / fator_real) × 100
  - Perdas detalhadas: secagem, quebra, defeito (em kg)
- ✅ Badges coloridas: verde ≥95%, amarelo ≥80%, vermelho <80%
- ✅ Endpoint: `GET /beneficiamento/relatorio-rendimento?safra_id=`

**Integração 2: Agrupamento de Múltiplos Romaneios (Blend)**
- ✅ Criar 1 lote de 2+ romaneios da mesma safra (ex: blending de lotes)
- ✅ Peso de entrada = soma de todos os romaneios
- ✅ Rastreabilidade N:N mantida via tabela `cafe_lote_beneficiamento_romaneios`
- ✅ Endpoint: `POST /beneficiamento/from-romaneios`

**Integração 3: Armazenagem em Estoque (SKU Rastreável)**
- ✅ Botão "Armazenar" (📦) quando status=ARMAZENADO
- ✅ Cria `LoteEstoque` no módulo estoque com rastreabilidade completa
- ✅ Cria `MovimentacaoEstoque` tipo=ENTRADA, origem_tipo=BENEFICIAMENTO
- ✅ Bidirectional FKs: Lote.lote_estoque_id ↔ Estoque.lote_beneficiamento_id
- ✅ Endpoint: `POST /beneficiamento/{id}/armazenar`

---

### **FASE 7: ENCERRADA** (Finalização)
**Objetivo:** Encerrar safra e gerar relatórios finais.

#### Páginas envolvidas:
1. **Safra Detail** (`/safras/[id]`)
   - Registrar produtividade real
   - Marcar como ENCERRADA
   - Gerar resumo final

2. **Financeiro** (`/safras/[id]/financeiro`)
   - Resultado financeiro completo
   - Margem bruta (receita - custos)

3. **Operações** (`/safras/[id]/operacoes`)
   - Registro de limpeza pós-colheita

#### ✅ Status do Fluxo: **CORRETO**
- Funciona bem, mas poderia ter relatório consolidado

---

## 🔄 Fluxo de Commodity (Geração do Produto Final)

**Caminho COMPLETO (2026-04-15):**
```
Safra → Fenologia → Operações → Colheita
   ↓                              ↓
Planejamento                   Romaneios (registra lotes)
   ↓                              ↓ [Int.2: blend/multi-romaneio]
Financeiro                    Beneficiamento (processa)
                                  ↓
                          [Int.1: Relatório Rendimento]
                                  ↓
                          [Int.3: Armazenar em Estoque]
                                  ↓
                              Estoque (café pronto, SKU)
                                  ↓ [Int.0: Gerar Venda]
                            Comercialização (RASCUNHO)
                                  ↓
                              Venda (APROVADA)
```

**Status de Resolução:**
- ✅ **Link Romaneios → Beneficiamento:** Botão "Processar" cria lote pré-populado
- ✅ **Link Beneficiamento → Commodity:** Botão "Gerar Venda" cria ComercializacaoCommodity
- ✅ **Rastreamento de perda:** Relatório de Rendimento mostra eficiência % por método
- ✅ **Integração estoque:** LoteEstoque criado com rastreabilidade para Beneficiamento
- ✅ **Rastreabilidade completa:** Romaneio → Lote Beneficiamento → Estoque → Comercialização

---

## ⚠️ Avaliação Crítica do Fluxo (Atualizado 2026-04-15)

### O que **FUNCIONA bem:**
✅ Planejamento (Orçamento) - Criação de safra, custeio  
✅ Operações - Registro de atividades de campo  
✅ Fenologia - Rastreamento de estágios (se usado)  
✅ Financeiro - Acompanhamento de custos vs orçado  
✅ Análises Solo - Registro de dados técnicos  
✅ **Colheita (Romaneios)** - Registra lotes colhidos com rastreabilidade completa
✅ **Beneficiamento** - Fluxo completo com 4 integrações (veja acima)
✅ **Estoque** - Café beneficiado rastreável como SKU
✅ **Comercialização** - Geração automática de vendas a partir de lotes

### O que **AINDA PODERIA MELHORAR:**
⚠️ **Transição automática de fases:** User ainda deve clicar manualmente para COLHEITA  
⚠️ **Dashboard consolidado:** Falta visão única de Safra → Produção → Venda → Rentabilidade  
⚠️ **Alertas de eficiência:** Poderia notificar se rendimento < esperado para método  
⚠️ **Histórico de preços:** Falta tracking de evolução de preço de venda por safra/período  
❌ **SKU/Lote final:** Sem geração de identificador para venda  

---

## 🔧 Recomendações para Completar o Fluxo

| Prioridade | Ação | Impacto |
|---|---|---|
| **P0** | Integrar Romaneios com Beneficiamento (lotes automáticos) | Sem isso, café não sai do campo |
| **P0** | Criar "Lote Final" (commodity) após beneficiamento | Sem isso, não há rastreamento do produto |
| **P1** | Adicionar cálculo de rendimento por tipo | Entender eficiência do processamento |
| **P1** | Adicionar checklist visual por fase | Guiar usuário no workflow |
| **P2** | Integração estoque com safra | Melhor rastreamento |
| **P2** | Relatório final consolidado | Análise pós-safra |

---

## 📖 Resumo para Usuário Leigo

**O que é uma Safra?**  
É o registro completo de um plantio: do preparo da terra até a venda do produto final. No sistema, você segue etapas:

1. **Cria a safra** → Indica cultura, talhão, data
2. **Planeja custos** → Define quanto vai gastar (sementes, adubo, mão-de-obra)
3. **Executa operações** → Registra cada atividade (plantio, adubação, pulverização)
4. **Monitora** → Acompanha saúde (pragas, fenologia, satellite)
5. **Colhe** → Registra colheita por lote (romaneios)
6. **Processa** (café) → Beneficia (seca, descasca, classifica)
7. **Vende** → Gera commodity final rastreável

**Para café especificamente:**  
O diferencial é a fase de **beneficiamento** — onde o café cereja (fresco) vira café beneficiado (pronto para vender). Sem isso integrado, o sistema não completa o ciclo.
