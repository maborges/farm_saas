# 🌱 context-analise-solo.md

## 🎯 Objetivo

Definir o modelo conceitual e as regras de negócio para o módulo de **Análise de Solo**, permitindo registrar dados laboratoriais, interpretar resultados com base em cultura e região, e gerar recomendações para apoio à decisão do produtor.

---

## 🧠 Princípios Fundamentais

- A análise de solo é composta por dados laboratoriais objetivos  
- Os valores medidos são independentes de cultura  
- A interpretação dos resultados depende de cultura, região e contexto agronômico  
- O sistema deve separar claramente dados, interpretação e recomendação  
- O produtor deve poder customizar parâmetros, com controle  

---

## 🧱 Estrutura do Módulo

O módulo é composto por três camadas principais:

1. Dados da análise (medição)  
2. Parâmetros de interpretação  
3. Recomendação agronômica  

---

## 🧪 1. Análise de Solo (Registro)

Representa uma coleta de solo realizada em um local e momento específicos.

### Estrutura

AnaliseSolo:
- id  
- talhao_id  
- cultivo_id (opcional)  
- data_coleta  
- laboratorio (opcional)  
- observacoes  

---

## 🧬 2. Resultados da Análise

Representa os valores medidos no laboratório.

### Estrutura

AnaliseSoloResultado:
- id  
- analise_id  
- parametro  
- valor  
- unidade  

---

### 📊 Exemplos de parâmetros

- pH  
- Fósforo (P)  
- Potássio (K)  
- Cálcio (Ca)  
- Magnésio (Mg)  
- Matéria Orgânica  
- CTC  
- Saturação por Bases (V%)  

---

## 🧠 Regra Importante

Os valores registrados são **neutros e universais**.  
Não devem depender de cultura ou região.

---

## 🌿 3. Parâmetros de Interpretação

Definem como os valores devem ser classificados.

### Estrutura

ParametroInterpretacao:
- id  
- cultura_id  
- regiao (opcional)  
- parametro  
- faixa_min  
- faixa_max  
- classificacao (baixo, médio, alto)  

---

## 📊 Exemplo

Para Fósforo:

- 0 a 5 → baixo  
- 5 a 15 → médio  
- acima de 15 → alto  

---

## 🌍 Variação Regional

Os parâmetros podem variar por:

- região geográfica  
- tipo de solo  
- bioma  

Se não houver parâmetro regional, utilizar padrão geral.

---

## 🧑‍🌾 4. Customização por Cliente

Permitir que cada cliente (tenant) sobrescreva parâmetros padrão.

### Estrutura

ParametroInterpretacaoCustom:
- id  
- tenant_id  
- cultura_id  
- parametro  
- faixa_min  
- faixa_max  
- classificacao  

---

## 🔁 Hierarquia de Aplicação

1. Parâmetro customizado do cliente  
2. Parâmetro padrão por cultura/região  
3. Parâmetro padrão global  

---

## ⚠️ Regra

Customizações devem sobrescrever, nunca substituir completamente a base padrão.

---

## 🌾 5. Interpretação dos Resultados

Processo de transformar valores em classificações.

### Entrada

- resultados da análise  
- cultura associada (via cultivo)  
- região (se aplicável)  

---

### Saída

- classificação por parâmetro  
- diagnóstico do solo  

---

## 📊 Exemplo

pH = 5.2

- Café → adequado  
- Soja → baixo  

---

## 🌱 6. Recomendação Agronômica

Baseada na interpretação dos parâmetros.

### Estrutura

Recomendacao:
- id  
- cultura_id  
- parametro  
- classificacao  
- acao_recomendada  
- descricao  

---

### 📌 Exemplos de ações

- aplicar calcário  
- corrigir fósforo  
- ajustar adubação  
- manter manejo atual  

---

## 📄 7. Relatório de Análise

O sistema deve gerar um relatório contendo:

- dados da análise  
- classificação de cada parâmetro  
- recomendações  
- histórico do talhão  

---

## 🔄 Fluxo do Módulo

1. Registrar análise de solo  
2. Inserir resultados laboratoriais  
3. Associar ao talhão e cultivo  
4. Buscar parâmetros de interpretação  
5. Classificar resultados  
6. Gerar recomendações  
7. Exibir relatório  

---

## 🧠 Regras de Negócio

- análise deve estar vinculada ao talhão  
- pode estar vinculada ao cultivo  
- parâmetros são independentes da análise  
- interpretação depende de cultura  
- customização deve respeitar hierarquia  

---

## ⚠️ Erros Comuns

- misturar dado bruto com interpretação  
- não considerar variação regional  
- permitir configuração irrestrita  
- não manter histórico de análises  

---

## 🚀 Evolução do Módulo

- recomendação automática de adubação  
- integração com clima e produtividade  
- análise histórica do solo  
- sugestão de cultura ideal  
- integração com sensores  

---

## 🧠 Insight Final

O valor da análise de solo não está no dado coletado, mas na interpretação e na decisão gerada.

---

## 📌 Conclusão

- dados são universais  
- interpretação é contextual  
- recomendação é estratégica  
- o sistema deve separar claramente essas camadas  

---

## 🔥 Regra de Ouro

Dados são fixos.  
Interpretação é variável.  
Decisão é inteligente.