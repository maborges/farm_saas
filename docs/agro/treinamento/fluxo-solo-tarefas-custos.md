# 🌱 fluxo-solo-tarefas-custos.md

## 🎯 Objetivo

Definir o fluxo completo desde a análise de solo até a execução operacional, incluindo geração automática de tarefas e apuração de custos no cultivo.

---

# 🧠 VISÃO GERAL

O sistema deve transformar:

Análise de Solo → Diagnóstico → Decisão → Tarefas → Custos → Execução → Resultado

---

# 🔄 FLUXO COMPLETO

## 1. INÍCIO DO CULTIVO (Planejamento)

### Entrada:
- talhão
- cultura
- data_inicio

---

## 📊 Sistema executa automaticamente:

### 1.1 Buscar análise de solo do talhão

- ordenar por data_coleta
- selecionar mais recente

---

### 1.2 Validar validade

- comparar com data_inicio do cultivo
- classificar:

  - 🟢 válida
  - 🟡 atenção
  - 🔴 inválida

---

### 1.3 Exibir status ao usuário

Exemplo:

"Análise encontrada (3 meses) → recomendada para uso"

---

## 2. DECISÃO DO USUÁRIO

### Opções:

- usar análise sugerida
- escolher outra análise
- continuar sem análise

---

## ⚠️ Se continuar sem análise:

- registrar decisão
- marcar cultivo como "sem base técnica"

---

## 3. INTERPRETAÇÃO AUTOMÁTICA

Se análise for utilizada:

### Sistema executa:

- buscar parâmetros por cultura
- classificar cada parâmetro

---

### Exemplo de saída:

- pH → baixo
- fósforo → médio
- potássio → baixo

---

## 4. GERAÇÃO DE RECOMENDAÇÕES

Baseado na interpretação:

### Sistema gera:

- aplicar calcário
- adubação fosfatada
- adubação potássica

---

## 5. CONVERSÃO EM TAREFAS

### Pergunta ao usuário:

"Deseja gerar tarefas automaticamente?"

---

## ✔️ Se SIM:

### Criar tarefas:

Tarefa:
- tipo: correção de solo
- cultivo_id
- talhao_id
- descrição
- data_sugerida
- status: PENDENTE

---

### Exemplos:

- Aplicar calcário
- Aplicar fósforo
- Aplicar potássio

---

## 6. CÁLCULO DE INSUMOS (opcional/avançado)

Sistema pode sugerir:

- quantidade de calcário (kg/ha)
- quantidade de adubo

---

## 7. GERAÇÃO DE CUSTOS

Ao gerar tarefas:

### Sistema pode:

#### 7.1 Criar custo estimado

Custo:
- cultivo_id
- tipo: INSUMO
- descricao
- valor_estimado
- origem: ANALISE_SOLO

---

#### 7.2 Ou aguardar execução real

---

## 8. EXECUÇÃO DAS TAREFAS

Usuário executa:

- registra operação
- informa:

  - insumos utilizados
  - quantidade
  - custo real

---

## 9. CONSOLIDAÇÃO DE CUSTOS

Sistema:

- substitui custo estimado por real (ou compara)
- vincula custo ao cultivo

---

## 10. IMPACTO NA SAFRA

Custos gerados impactam:

- custo total do cultivo
- margem
- lucro

---

# 🧱 ESTRUTURAS ENVOLVIDAS

## Cultivo

- id
- talhao_id
- safra_id
- cultura_id
- analise_solo_id

---

## AnaliseSolo

- id
- talhao_id
- data_coleta

---

## Tarefa

- id
- cultivo_id
- tipo
- descricao
- status
- data_sugerida

---

## Operacao

- id
- cultivo_id
- tarefa_id
- tipo
- data_execucao

---

## Custo

- id
- cultivo_id
- operacao_id
- valor
- tipo
- origem

---

# ⚙️ REGRAS DE NEGÓCIO

- análise é opcional, mas recomendada
- tarefas só são geradas com confirmação
- custos podem ser estimados ou reais
- operação sempre pertence ao cultivo

---

# 🚀 AUTOMAÇÕES IMPORTANTES

- sugestão automática de análise
- geração automática de tarefas
- sugestão de insumos
- estimativa de custo

---

# 📊 INDICADORES

- cultivo com análise vs sem análise
- custo de correção de solo
- impacto na produtividade
- histórico do talhão

---

# 🔥 DIFERENCIAL DO SISTEMA

Transformar análise de solo em:

- ação prática
- planejamento financeiro
- melhoria de produtividade

---

# 🧠 INSIGHT FINAL

A análise de solo não é um relatório.

Ela é o ponto de partida para todas as decisões agronômicas e financeiras do cultivo.

---

# 📌 CONCLUSÃO

O sistema deve:

- orientar o usuário
- automatizar decisões
- gerar tarefas
- conectar com custos
- garantir rastreabilidade