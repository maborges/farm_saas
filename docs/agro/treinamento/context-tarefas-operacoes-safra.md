# 🌾 context-tarefas-operacoes-safra.md

## 🎯 Objetivo

Definir de forma clara e estruturada:

- o conceito de tarefas (planejamento)
- o conceito de atividades/operações (execução)
- como ambas se relacionam dentro do workflow de uma safra
- como impactam custos, timeline e tomada de decisão

---

# 🧠 CONCEITOS FUNDAMENTAIS

## 📌 Tarefa (Planejamento)

Representa uma intenção de ação futura.

- algo que deve ser feito
- pode ser criada manualmente ou automaticamente
- pode ser alterada, cancelada ou replanejada
- pode ter estimativas (tempo, insumo, custo)

---

## 📌 Operação / Atividade (Execução)

Representa uma ação realizada no campo.

- algo que já aconteceu
- registra dados reais
- gera custo real
- não deve ser alterada (apenas auditada)

---

# 🔄 RELAÇÃO ENTRE TAREFA E OPERAÇÃO

Tarefa → Execução → Operação

---

## 📊 Regras importantes

- uma tarefa pode gerar uma ou várias operações  
- uma operação pode existir sem tarefa (exceção)  
- uma tarefa pode nunca ser executada  
- operação é sempre a fonte da verdade para custo  

---

# 🌱 WORKFLOW COMPLETO DA SAFRA

---

## 1. PLANEJAMENTO DA SAFRA

### Entrada

- criação da safra  
- criação dos cultivos  
- definição de talhões  

---

### Geração de tarefas

Origem:

- análise de solo  
- planejamento manual  
- templates de cultivo  

---

### Exemplo

Tarefa:
- Aplicar calcário
- Adubação de base

---

## 2. PREPARO DO SOLO

### Tarefas típicas

- correção de solo  
- gradagem  
- preparo mecânico  

---

### Execução

Operador realiza atividade:

Operação:
- Aplicação de calcário
- quantidade: 2 ton/ha
- custo: R$ 3.000

---

### Relação

Tarefa (Aplicar calcário)
   ↓
Operação (execução real)

---

## 3. PLANTIO

### Tarefas

- plantio  
- adubação inicial  

---

### Operações

- registro do plantio  
- consumo de insumos  
- custo real  

---

## 4. EXECUÇÃO / MANEJO

### Tarefas

- pulverização  
- adubação de cobertura  
- controle de pragas  

---

### Operações

- aplicação de defensivos  
- aplicação de fertilizantes  

---

## 5. COLHEITA

### Tarefas

- colher cultura  

---

### Operações

- colheita realizada  
- quantidade produzida  
- custo de colheita  

---

# 🔁 INTERAÇÕES DINÂMICAS

---

## ✔️ 1. Tarefa → Operação

Fluxo padrão:

Planejamento → Execução → Registro

---

## ✔️ 2. Operação sem tarefa

Exemplo:

Aplicação emergencial

- não planejada  
- deve ser permitida  
- registrada diretamente como operação  

---

## ✔️ 3. Operação gera nova tarefa (via regra)

Exemplo:

Operação: Pulverização
→ gerar nova tarefa em 15 dias

---

## ✔️ 4. Tarefa recorrente

- inspeções periódicas  
- monitoramento  

---

# 💰 RELAÇÃO COM CUSTOS

---

## Tarefa

- custo estimado (opcional)  
- usado para planejamento  

---

## Operação

- custo real  
- usado para financeiro  

---

## Comparação

Estimado vs Realizado

---

# 📊 STATUS E CICLO DE VIDA

---

## Tarefa

- PENDENTE
- APROVADA (opcional)
- EM_EXECUCAO
- CONCLUIDA
- CANCELADA

---

## Operação

- REGISTRADA
- VALIDADA (opcional)

---

# 🧱 MODELAGEM SUGERIDA

---

## Tarefa

- id  
- cultivo_id  
- talhao_id  
- descricao  
- tipo  
- status  
- custo_estimado  
- data_prevista  

---

## Operação

- id  
- cultivo_id  
- talhao_id  
- tarefa_id (opcional)  
- tipo  
- data_execucao  
- quantidade  
- custo_real  

---

# ⚙️ REGRAS DE NEGÓCIO

---

- tarefa nunca substitui operação  
- operação nunca deve ser implícita  
- custo real só vem da operação  
- tarefa pode existir sem execução  
- operação pode existir sem tarefa  

---

# 🧠 INSIGHT ESTRUTURAL

Tarefas organizam o trabalho.  
Operações registram a realidade.

---

# 🚀 BOAS PRÁTICAS

---

## ✔️ Sempre permitir operação direta

- evita perda de dados  

---

## ✔️ Vincular operação à tarefa quando existir

- garante rastreabilidade  

---

## ✔️ Separar claramente planejamento e execução

- evita inconsistência  

---

## ✔️ Permitir comparação planejado vs realizado

- gera inteligência  

---

# 📌 CONCLUSÃO

O workflow correto da safra depende da separação clara:

- planejamento (tarefas)  
- execução (operações)  

E da integração entre eles ao longo de todo o ciclo produtivo.

---

# 🔥 REGRA DE OURO

Sem operação, não existe custo real.  
Sem tarefa, não existe organização.