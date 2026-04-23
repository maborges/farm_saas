# 🌱 MODELO DE APROPRIAÇÃO DE CUSTOS — TALHÃO, CULTIVO E CENTRO DE CUSTO

## 🎯 Objetivo

Definir como os custos devem ser registrados e apropriados no sistema em diferentes níveis:

- Talhão  
- Cultivo  
- Centro de Custo da Fazenda  

Garantindo análise operacional e gerencial.

---

# 🧠 PRINCÍPIO

O custo pode nascer em diferentes níveis.

Mas precisa ser apropriado no nível correto para análise.

Nem todo custo nasce no talhão.

Nem todo custo termina no talhão.

---

# 🧱 NÍVEIS DE CUSTO

## 1. CUSTO DIRETO DE TALHÃO

Custos diretamente ligados ao manejo do talhão.

Exemplos:

- adubação  
- corretivos  
- pulverização  
- sementes  
- horas-máquina  

Origem:

Operações de campo.

---

## Indicadores

- custo por hectare  
- custo por talhão  
- custo por saca produzida  

---

## 2. CUSTO DE CULTIVO

Custos compartilhados entre vários talhões do mesmo cultivo.

Exemplos:

- consultoria agronômica  
- monitoramento compartilhado  
- planejamento nutricional  
- logística do cultivo  

---

## Regra

Podem ser rateados para talhões.

Métodos:

- por hectare  
- por peso  
- por consumo  

---

## 3. CENTRO DE CUSTO DA FAZENDA

Custos indiretos ou estruturais.

Exemplos:

- administração  
- oficina  
- combustível geral  
- manutenção de pivô  
- supervisão  
- energia do sistema de irrigação

---

## Não pertencem diretamente a um talhão.

Mas podem ser:

- mantidos como overhead  
ou  
- rateados depois.

---

# 🎯 ESTRUTURA CONCEITUAL

```text
Custo
 ├── Direto Talhão
 ├── Compartilhado Cultivo
 └── Indireto Centro de Custo
```

---

# 📌 MODELO DE APROPRIAÇÃO

Cada lançamento pode ter:

- escopo_custo

Valores:

```text
TALHAO
CULTIVO
CENTRO_CUSTO
```

---

## Referências

- talhao_id (nullable)
- cultivo_id (nullable)
- centro_custo_id (nullable)

---

# 📊 EXEMPLOS

## Exemplo 1

Aplicar calcário

Escopo:

TALHAO

Vai direto para custo do talhão.

---

## Exemplo 2

Consultoria do cultivo

Escopo:

CULTIVO

Ratear para talhões.

---

## Exemplo 3

Energia do pivô central

Escopo:

CENTRO_CUSTO

Pode ficar como indireto.

Ou ratear.

---

# ⚙️ RATEIO

## Método padrão

Rateio por hectare.

```text
custo_rateado =
(area talhão / área total)
× custo total
```

---

## Métodos possíveis

- AREA
- PESO
- CONSUMO_REAL

---

# 🧠 HIERARQUIA DE ANÁLISE

Sistema deve permitir ver:

---

## Visão Operacional

Por talhão:

- custo
- produtividade
- margem

---

## Visão Agronômica

Por cultivo:

- custo consolidado
- custo médio por hectare

---

## Visão Gerencial

Por centro de custo:

- overhead
- despesas indiretas

---

# 📋 ESTRUTURAS

## Centro de Custo

Exemplos:

- Administração
- Irrigação
- Oficina
- Frota
- Infraestrutura

---

## Tabela

centro_custo

- id
- nome
- tipo
- rateavel (sim/não)

---

# 🚀 EVOLUÇÃO FUTURA

Depois pode permitir:

- custeio absorção  
- custeio variável  
- custo ABC (Activity Based Costing)

---

# 🎯 RECOMENDAÇÃO PARA MVP

Começar com:

✔ custos diretos por talhão

✔ custos compartilhados por cultivo com rateio por hectare

Centro de custo pode vir depois.

---

# ⚠️ ERRO COMUM

Jogar tudo no talhão.

Isso distorce:

- margem
- custo real
- rentabilidade

---

# 📌 CONCLUSÃO

O sistema deve suportar três níveis:

- Talhão  
- Cultivo  
- Centro de Custo

E permitir apropriação e rateio.

---

# 🔥 REGRA DE OURO

Custo nasce onde ocorre.

Custo é apropriado onde deve ser analisado.