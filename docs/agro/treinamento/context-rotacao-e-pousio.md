# 🌱 context-rotacao-e-pousio.md

## 🎯 Objetivo

Definir os conceitos e regras para modelagem de **rotação de culturas (rodízio)** e **descanso do solo (pousio)** dentro de um sistema de gestão agrícola, garantindo consistência temporal, rastreabilidade e suporte a decisões agronômicas.

---

## 🧠 Conceitos Fundamentais

- Talhão representa o espaço físico
- Safra representa o tempo
- Cultivo representa a ocupação real do talhão ao longo do tempo

> Regra central:
> Tudo que acontece no tempo de um talhão deve ser registrado, inclusive períodos sem produção.

---

## 🔁 Rotação de Culturas (Rodízio)

Rotação de culturas é a prática de alternar diferentes culturas no mesmo talhão ao longo do tempo.

### 📊 Exemplo

Talhão 01:
- 2024 → Soja  
- 2025 → Milho  
- 2026 → Braquiária  

Neste caso:
- o talhão é o mesmo  
- as culturas mudam ao longo das safras  
- não há sobreposição no tempo  

---

## 🎯 Objetivos da Rotação

- melhorar fertilidade do solo  
- reduzir incidência de pragas e doenças  
- equilibrar uso de nutrientes  
- aumentar produtividade ao longo do tempo  

---

## 🧠 Conceito Importante

Rotação é uma estratégia planejada baseada na sequência temporal de cultivos em um talhão.

---

## 🌿 Descanso do Solo (Pousio)

Descanso do solo, ou pousio, é o período em que o talhão não possui cultivo produtivo.

### 📊 Exemplo

Talhão 01:
- 2024 → Soja  
- 2025 → Pousio  
- 2026 → Milho  

Neste caso:
- o ano de 2025 representa um período de recuperação do solo  

---

## ⚠️ Observação Importante

Pousio não significa abandono do solo. Pode envolver:

- cobertura vegetal natural  
- manejo mínimo  
- controle de vegetação espontânea  

---

## 📌 Diferença entre Rotação e Pousio

Rotação envolve substituição de culturas ao longo do tempo.  
Pousio envolve ausência de cultivo produtivo em determinado período.

---

## 🧱 Modelagem de Rotação

A rotação é naturalmente representada pela sequência de cultivos no tempo.

Estrutura:

Cultivo:
- talhao_id
- safra_id
- cultura_id
- data_inicio
- data_fim

A alternância de cultura ao longo do tempo caracteriza a rotação.

---

## 🌿 Modelagem de Pousio

Existem duas abordagens possíveis:

### ❌ Abordagem 1 (não recomendada)

Não registrar cultivo no período.

Problemas:
- perda de histórico  
- impossibilidade de análise  
- inconsistência de dados  

---

### ✅ Abordagem 2 (recomendada)

Criar um cultivo com cultura técnica representando o estado do solo.

Exemplo:

Cultura:
- POUSIO  
- COBERTURA VEGETAL  

---

### 📊 Exemplo modelado

Talhão 01:
- 2024 → Soja  
- 2025 → Pousio  
- 2026 → Milho  

Neste caso, o pousio é registrado como um cultivo válido.

---

## 💰 Impacto em Custos

### Rotação

- cada cultura possui seus próprios custos  
- permite análise de rentabilidade por cultura  

---

### Pousio

Pode gerar custos, como:

- controle de ervas daninhas  
- manejo do solo  
- implantação de cobertura vegetal  

---

## 📈 Benefícios de Registrar Pousio

- histórico completo do talhão  
- análise de produtividade ao longo do tempo  
- base para recomendação agronômica  
- rastreabilidade  

---

## ⚙️ Extensões de Modelagem (Opcional)

Para maior controle, pode-se incluir:

Cultivo:
- tipo_manejo

Valores possíveis:
- PRODUCAO  
- POUSIO  
- COBERTURA  
- ROTACAO  

---

## 🧠 Planejamento Agrícola (Avançado)

Pode-se implementar um modelo de planejamento:

PlanejamentoTalhao:
- talhao_id
- sequencia de culturas planejadas
- período

Isso permite:

- prever safras futuras  
- sugerir culturas ideais  
- evitar práticas agronômicas inadequadas  

---

## ⚠️ Erros Comuns

- tratar pousio como ausência de dado  
- não registrar períodos sem cultivo  
- misturar pousio com consórcio  
- ignorar histórico de uso do solo  

---

## 🔥 Regra de Ouro

Tudo que ocorre no tempo de um talhão deve ser registrado, inclusive períodos sem produção.

---

## 📌 Conclusão

- Rotação é a alternância de culturas ao longo do tempo  
- Pousio é o período sem cultivo produtivo  
- Ambos devem ser modelados no nível de cultivo  
- Pousio deve ser tratado como cultura técnica  
- O histórico do talhão é essencial para análise agronômica  

---

## 🧠 Insight Final

A correta modelagem de rotação e pousio permite transformar o sistema em uma plataforma de inteligência agrícola, indo além da gestão operacional.