# Arquitetura Conceitual — SaaS de Gestão Agropecuária

## Objetivo

Definir os conceitos fundamentais que devem guiar a arquitetura da aplicação
para evitar erros estruturais comuns em ERPs agrícolas.

Este documento estabelece a separação correta entre:

- Território (ESPAÇO)
- Produção (TEMPO)
- Operação (EXECUÇÃO)
- Economia (RESULTADO)

---

# 🧠 Princípio Central

## REGRA ABSOLUTA

> O custo no agro é TEMPORAL, não territorial.

❌ Custos pertencem ao Talhão  
✅ Custos pertencem à Safra (Ciclo Produtivo)

O talhão apenas RECEBE atividades.

Quem gera resultado econômico é o ciclo.

---

# 🌎 Estrutura Territorial da Fazenda (ESPAÇO)

A estrutura territorial representa algo relativamente estático.

## Hierarquia

Fazenda
└── Gleba
    └── Talhão
        ├── Subtalhão (opcional)
        └── Zona de Manejo (opcional)

---

## Fazenda

Unidade administrativa principal.

### Atributos conceituais
- Nome
- Proprietário
- Localização
- Área total
- Tipo de exploração

Função:
> Organizar gestão administrativa.

---

## Gleba

Grande divisão física baseada em características naturais.

Critérios comuns:
- relevo
- tipo de solo
- distância logística
- matrículas rurais

Função:
> Organização macro do território.

---

## Talhão

Unidade operacional principal.

É onde as atividades acontecem.

### Características
- área delimitada
- histórico produtivo
- aptidão agrícola
- tipo de uso

IMPORTANTE:
> Talhão NÃO possui custo próprio.

Ele apenas recebe operações ao longo do tempo.

---

## Subtalhão

Divisão operacional temporária.

Usado quando:
- parte da área recebe manejo diferente
- testes agronômicos
- plantio parcial

Pode deixar de existir depois da safra.

---

## Zona de Manejo

Divisão agronômica baseada em variabilidade produtiva.

Critérios:
- fertilidade
- produtividade histórica
- mapas NDVI
- agricultura de precisão

Está no mesmo nível conceitual do subtalhão.

Diferença:

Subtalhão → operacional  
Zona de manejo → analítica/agronômica

---

# ⏳ Estrutura Temporal (PRODUÇÃO)

Aqui nasce o valor econômico.

## Ciclo Produtivo (Safra)

Elemento MAIS IMPORTANTE do sistema.

Representa:

- uma produção
- dentro de um período
- sobre uma área
- com objetivo econômico

---

## Definição

Ciclo Produtivo =
Cultura + Período + Área + Objetivo econômico

---

## Exemplos

Soja Safra 24/25 — Talhão 05  
Milho Safrinha 2025 — Talhão 03  
Engorda Bovinos Jan–Jun 2025 — Pasto Norte

---

## Regra arquitetural crítica

> Nenhuma operação pode existir sem um Ciclo Produtivo.

---

# ⚙️ Operações (EXECUÇÃO)

Operações são eventos realizados dentro do ciclo.

Exemplos:

- plantio
- adubação
- pulverização
- colheita
- vacinação
- pastejo

---

## Regra

Operação pertence a:

- 1 Ciclo Produtivo
- 1 Área executada

Nunca diretamente ao financeiro.

---

# 📦 Estoque (CONSEQUÊNCIA OPERACIONAL)

O estoque reage às operações.

Fluxo correto:

Operação → Consumo → Baixa estoque → Custo → Ciclo

Nunca:

Usuário → baixa manual → tentar descobrir custo depois.

---

# 💰 Economia do Agro (RESULTADO)

## Origem dos Custos

Custos nascem de:

- insumos utilizados
- horas máquina
- mão de obra
- serviços
- manutenção

Todos vinculados ao ciclo.

---

## Por que NÃO custo por talhão?

Porque o talhão existe por décadas.
A safra dura meses.

Misturar os dois gera:

- distorção histórica
- impossibilidade de comparação anual
- relatórios incorretos

---

## Modelo correto

Talhão = ONDE  
Safra = QUANDO  
Custo = RESULTADO DO QUANDO

---

# 📊 Indicadores Econômicos

Sempre calculados por ciclo:

- custo por hectare
- produtividade
- margem da safra
- ROI
- custo por arroba
- lucro operacional

---

# 🔄 Fluxo Conceitual Completo

TERRITÓRIO
↓
Talhão

TEMPO
↓
Ciclo Produtivo (Safra)

EXECUÇÃO
↓
Operações

RECURSOS
↓
Estoque / Máquinas / Pessoas

ECONOMIA
↓
Custos e Receitas

INTELIGÊNCIA
↓
Indicadores

---

# 🧱 Regras Arquiteturais Obrigatórias

## 1. Financeiro nunca é origem
Financeiro é consequência das operações.

---

## 2. Talhão não possui custo direto
Custos pertencem ao ciclo.

---

## 3. Operação sempre tem contexto temporal
Sem ciclo → operação inválida.

---

## 4. Estoque não gera custo sozinho
Consumo operacional gera custo.

---

## 5. Agricultura e Pecuária usam o mesmo motor
Ambos são ciclos produtivos.

---

# 🧭 Modelo Mental Final

O sistema NÃO é:

ERP + módulo agrícola.

O sistema é:

Plataforma econômica baseada em ciclos produtivos territoriais.

---

# ⭐ Norte Arquitetural

Toda informação do sistema deve responder:

ONDE aconteceu? → Área  
QUANDO aconteceu? → Ciclo  
O QUE aconteceu? → Operação  
QUAL impacto econômico? → Resultado

Se algum dado não responder essas quatro perguntas,
o modelo está errado.