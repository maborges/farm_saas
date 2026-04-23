# 🌾 CONTEXTO MESTRE — AGROSAAS (VERSÃO CONSOLIDADA)

## 🎯 Objetivo

Definir o modelo conceitual completo para um sistema SaaS de gestão agro (agricultura e pecuária), garantindo consistência entre estrutura física, ocupação do solo, operações, custos, produção e análise financeira.

Este documento é a base única para desenvolvimento, modelagem de dados, regras de negócio e uso por IA.

---

# 🧠 PRINCÍPIOS FUNDAMENTAIS

- Talhão representa espaço físico  
- Safra representa organização temporal  
- Cultivo representa ocupação real (tempo + espaço)  
- Custos, operações e produção pertencem ao cultivo  
- Cada cultura é tratada como uma unidade de negócio independente  
- Tudo que ocorre no tempo do talhão deve ser registrado  

---

# 🏢 ESTRUTURA ORGANIZACIONAL

Tenant (Produtor / Empresa)

Representa o cliente do sistema.

Um tenant pode possuir múltiplas unidades produtivas.

---

# 🚜 UNIDADE PRODUTIVA

Representa uma entidade rural operacional:

- Fazenda  
- Sítio  
- Arrendamento  
- Parceria  

Pode possuir infraestrutura própria ou compartilhada.

---

# 🌍 ESTRUTURA ESPACIAL

Hierarquia baseada em uma única tabela de áreas (estrutura auto-relacionada).

Tipos de área:

- GLEBA (raiz)
- TALHÃO (produção agrícola)
- PASTAGEM (pecuária)
- PIQUETE (subdivisão da pastagem)
- APP (área protegida)
- RESERVA LEGAL
- INFRAESTRUTURA (sede, armazém, etc.)

---

# 📏 CONCEITO DE ÁREAS

- Área Total  
- APP  
- Reserva Legal  
- Área Produtiva = Área Total - (APP + Reserva Legal)  

A área produtiva é utilizada por talhões e pastagens.

---

# 🌱 SAFRA

Safra representa um agrupador organizacional de produção.

Características:

- não ocupa espaço físico  
- pode conter múltiplos cultivos  
- datas são opcionais e servem como referência  

Estrutura:

- id  
- nome  
- data_inicio (opcional)  
- data_fim (opcional)  

---

# 🌿 CULTIVO (ENTIDADE CENTRAL)

Cultivo representa a ocupação real do solo.

Estrutura:

- safra_id  
- talhao_id  
- cultura_id (obrigatório)  
- cultivar_id (opcional)  
- area  
- data_inicio (obrigatório)  
- data_fim (opcional)  
- status  
- consorciado (boolean)  

---

# 📅 REGRAS DE DATAS NO CULTIVO

## Data de Início

- obrigatória  
- define o início da ocupação  
- base para operações, custos e validações  

## Data de Fim

- opcional na criação  
- obrigatória no encerramento  

## Regra por status

- PLANEJADO:
  - data_inicio obrigatório  
  - data_fim opcional  

- EM_ANDAMENTO:
  - data_inicio obrigatório  
  - data_fim opcional  

- FINALIZADO:
  - data_inicio obrigatório  
  - data_fim obrigatório  

## Culturas Perenes

- data_fim pode permanecer nula por tempo indeterminado  

---

# 🌾 REGRAS DE OCUPAÇÃO

Para um talhão:

- soma das áreas simultâneas ≤ área total  
- exceção: consórcio  

---

# 🌿 CONSÓRCIO

Cultivos que compartilham a mesma área no mesmo período.

Regras:

- consorciado = true  
- permite sobreposição total ou parcial  
- custos e produção permanecem separados  

---

# 🔁 ROTAÇÃO DE CULTURAS

Alternância de culturas no tempo no mesmo talhão.

Exemplo:

- Soja → Milho → Braquiária  

---

# 🌿 POUSIO (DESCANSO DO SOLO)

Período sem produção agrícola.

Deve ser modelado como cultura técnica:

- cultura = POUSIO  

Permite rastreabilidade e análise.

---

# ⚙️ OPERAÇÕES

Toda operação pertence a um cultivo.

Tipos:

- plantio  
- adubação  
- pulverização  
- colheita  

---

## 🔁 OPERAÇÕES COMPARTILHADAS

Devem ser rateadas entre cultivos.

Estrutura:

OperacaoRateio:
- operacao_id  
- cultivo_id  
- percentual  

---

# 💰 CUSTOS

Todo custo pertence ao cultivo.

Tipos:

- direto  
- indireto (rateado)  

---

## 🔁 RATEIO

Pode ser baseado em:

- área  
- percentual manual  
- uso real  

---

# 🌾 COLHEITA

Sempre por cultivo.

Estrutura:

- cultivo_id  
- quantidade  
- unidade  

Produção nunca deve ser agregada por talhão.

---

# 📦 COMMODITIES

Produto final disponível para comercialização.

Origem:

- colheita  

Atributos:

- tipo  
- unidade  
- peso por unidade  
- qualidade  

---

# 🐄 PECUÁRIA

Baseada em:

- pastagem  
- piquete  
- lote de animais  

Produção:

- peso  
- volume  

---

# 💰 APURAÇÃO DE RESULTADO

Sempre no nível do cultivo:

- custo total  
- produção  
- receita  
- lucro  

---

# 🔄 FLUXO OPERACIONAL

1. Criar unidade produtiva  
2. Criar estrutura espacial  
3. Criar safra  
4. Criar cultivos  
5. Definir área e datas  
6. Registrar operações  
7. Registrar custos  
8. Registrar colheita  
9. Gerar commodities  
10. Apurar resultados  

---

# 🧠 VALIDAÇÕES ESSENCIAIS

- impedir excesso de área  
- validar sobreposição temporal  
- permitir consórcio  
- garantir rastreabilidade  

---

# 🚀 NÍVEL AVANÇADO

## Subárea (CultivoArea)

Permite subdividir talhão.

- cultivo_id  
- area  
- geometria  

---

## Georreferenciamento

Permite:

- mapas  
- agricultura de precisão  
- controle espacial  

---

## Automação

- rateio automático  
- recomendação de cultura  
- análise de solo  
- previsão de produtividade  

---

# 🌐 VISÃO DE ECOSSISTEMA

Evolução do sistema:

- marketplace de insumos  
- comercialização de produção  
- serviços agrícolas  
- crédito rural  
- profissionais e empregos  

---

# 🔥 INSIGHT FINAL

O sistema deve tratar cada cultivo como uma unidade de negócio independente, garantindo controle total de tempo, espaço, custo e produção.

---

# 📌 CONCLUSÃO

Este modelo garante:

- consistência de dados  
- rastreabilidade completa  
- análise financeira real  
- base para inteligência agrícola  

---

# 🧠 REGRA DE OURO

Talhão = espaço  
Safra = organização  
Cultivo = realidade operacional