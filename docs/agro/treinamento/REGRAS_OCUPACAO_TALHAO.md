# 🌱 context-safra-talhao-interseccao.md

## 🎯 Objetivo

Definir as regras e conceitos para modelagem de **safras, talhões e cultivos**, garantindo consistência na ocupação de área, controle temporal e suporte a cenários reais do agronegócio como sucessão de culturas, sobreposição e consórcios.

---

## 🧠 Conceitos Fundamentais

- **Talhão** representa o espaço físico (área geográfica)
- **Safra** representa o tempo (período produtivo)
- **Cultivo** representa a interseção entre espaço e tempo

> Regra central:  
> **Safra não ocupa espaço. Quem ocupa espaço é o cultivo.**

---

## 🧱 Estrutura Conceitual

Talhão → define a área disponível  
Safra → define o período  
Cultivo → conecta talhão + safra + cultura + área + tempo

---

## 🌱 Uso do Talhão por Safras

Um mesmo talhão pode ser utilizado por múltiplas safras.

### ✔️ Cenário válido — uso sequencial

Talhão 01:
- Safra 2024 → Soja  
- Safra 2025 → Milho  

Neste caso, o talhão é reutilizado ao longo do tempo.

---

## 🔁 Sobreposição de Safras

Safras podem se sobrepor no tempo, desde que a ocupação física seja consistente.

### ✔️ Cenário válido — culturas diferentes em períodos sobrepostos

Talhão 01:
- Café (perene, contínuo)  
- Milho (temporário, período parcial)  

Neste caso:
- há interseção temporal  
- há coexistência física controlada  

---

## 🌿 Consórcio de Culturas

Consórcio ocorre quando duas ou mais culturas ocupam a mesma área simultaneamente.

### ✔️ Cenário válido

Talhão 01:
- Safra 2025 → Milho + Braquiária  

Regras:
- mesma área pode ser compartilhada  
- culturas devem ser marcadas como consorciadas  

---

## 🚫 Restrições de Ocupação

### ❌ Cenário inválido

Talhão 01 (50 ha):
- Soja ocupando 50 ha  
- Milho ocupando 50 ha  
- mesmo período  
- sem consórcio  

Isso gera inconsistência física.

---

## 🔥 Regra de Validação de Área

Para um determinado talhão e período:

A soma das áreas dos cultivos ativos não pode ultrapassar a área total do talhão.

### Exceção:
Cultivos marcados como consorciados podem compartilhar a mesma área.

---

## 🧱 Modelagem Recomendada

Entidade Cultivo:

- safra_id
- talhao_id
- cultura_id
- area
- data_inicio
- data_fim
- consorciado (boolean)

---

## 🧠 Validação Temporal e Espacial

Para cada talhão:

1. Identificar cultivos ativos em um intervalo de tempo  
2. Somar as áreas desses cultivos  
3. Validar:

- se não consorciado → soma ≤ área do talhão  
- se consorciado → permitido sobrepor  

---

## 📊 Exemplos Práticos

### ✔️ Exemplo 1 — válido

Talhão 01 (50 ha):
- Café → 40 ha (perene)  
- Milho → 10 ha (temporário)  

Resultado: válido

---

### ✔️ Exemplo 2 — válido com sobreposição

Talhão 01:
- Soja → out/2025 a fev/2026 (30 ha)  
- Milho → jan/2026 a jun/2026 (30 ha)  

Se as áreas forem distintas ou controladas → válido

---

### ❌ Exemplo 3 — inválido

Talhão 01 (50 ha):
- Soja → 50 ha  
- Milho → 50 ha  
- mesmo período  
- não consorciado  

Resultado: inválido

---

## ⚙️ Regras de Negócio

- Safra não controla ocupação física  
- Talhão não controla tempo  
- Cultivo controla ocupação real (tempo + espaço)  
- Validações devem ocorrer sempre no nível do cultivo  

---

## 🧠 Insight Estratégico

> O erro comum em sistemas é validar conflito no nível da safra.  
> O correto é validar no nível do cultivo.

---

## 🔮 Evolução Recomendada

Para maior precisão:

- utilizar subáreas dentro do talhão  
- aplicar georreferenciamento  
- validar interseções espaciais reais  
- automatizar regras de consistência  

---

## 📌 Conclusão

- Safras podem compartilhar o mesmo talhão  
- Safras podem se sobrepor no tempo  
- Cultivos são responsáveis pela ocupação real  
- A validação deve considerar área + tempo  
- Consórcio é a única exceção para sobreposição total  

---

## 🧠 Regra de Ouro

> **Talhão = espaço  
> Safra = tempo  
> Cultivo = ocupação real**