# 🌱 context-cultivo-datas.md

## 🎯 Objetivo

Definir as regras e diretrizes para o uso de datas (início e fim) no contexto de criação de cultivo dentro do sistema, considerando que o cultivo é criado no momento da definição da safra.

---

## 🧠 Conceito Fundamental

No modelo do sistema:

- Safra funciona como contexto organizacional  
- Cultivo representa a execução real no tempo e espaço  

> Regra central:
> As datas que impactam operação, custo e produção pertencem ao cultivo.

---

## 🌿 Definição de Datas no Cultivo

Cada cultivo deve possuir os seguintes campos:

- data_inicio  
- data_fim  

---

## 📅 Data de Início

### ✔️ Obrigatoriedade

A data de início do cultivo é obrigatória no momento da criação.

### 🎯 Justificativa

A data de início é essencial para:

- ordenar eventos operacionais  
- registrar custos no tempo correto  
- validar sobreposição de cultivos no talhão  
- gerar timeline de atividades  
- permitir análises históricas  

### 📌 Regra

data_inicio deve ser sempre informada e válida.

---

## 📅 Data de Fim

### ❌ Obrigatoriedade na Criação

A data de fim não deve ser obrigatória no momento da criação do cultivo.

### 🎯 Justificativa

No contexto real do agronegócio:

- o término da produção depende de fatores variáveis (clima, pragas, mercado)  
- o produtor nem sempre sabe a data exata no início  
- culturas perenes podem não possuir data de término definida  

### 📌 Regra

data_fim pode ser nula enquanto o cultivo estiver em andamento.

---

## ⚙️ Regra de Obrigatoriedade Progressiva

A obrigatoriedade da data de fim deve depender do status do cultivo.

### Estados possíveis:

- PLANEJADO  
- EM_ANDAMENTO  
- FINALIZADO  

### Regras:

- PLANEJADO:
  - data_inicio → obrigatório  
  - data_fim → opcional  

- EM_ANDAMENTO:
  - data_inicio → obrigatório  
  - data_fim → opcional  

- FINALIZADO:
  - data_inicio → obrigatório  
  - data_fim → obrigatório  

---

## 🌾 Casos Especiais

### Culturas Temporárias

Exemplo: milho, soja

- possuem início e fim definidos  
- data_fim deve ser preenchida ao final do ciclo  

---

### Culturas Perenes

Exemplo: café

- possuem início definido  
- podem não possuir data de término  

Exemplo:

- data_inicio: 01/01/2020  
- data_fim: null  

---

## ⚠️ Boas Práticas

- não forçar o preenchimento de data_fim na criação  
- evitar uso de datas estimadas como definitivas  
- permitir atualização da data_fim ao longo do ciclo  
- garantir consistência temporal com outros cultivos no mesmo talhão  

---

## ❌ Erros Comuns

- obrigar data_fim no cadastro inicial  
- permitir cultivo sem data_inicio  
- utilizar datas da safra para controlar execução  
- registrar datas irreais apenas para validação do sistema  

---

## 🧱 Modelagem Recomendada

Estrutura da entidade Cultivo:

- id  
- safra_id  
- talhao_id  
- cultura_id  
- cultivar_id (opcional)  
- data_inicio (NOT NULL)  
- data_fim (NULLABLE)  
- status  

---

## 🚀 Evolução Recomendada (Avançado)

Para maior controle e planejamento, podem ser adicionados:

- data_inicio_planejada  
- data_inicio_real  
- data_fim_planejada  
- data_fim_real  

Isso permite:

- comparação entre planejamento e execução  
- análise de desvios  
- melhoria de previsibilidade  

---

## 🧠 Insight Final

A data de início representa um fato conhecido.  
A data de fim representa um evento futuro e incerto.

---

## 📌 Conclusão

- data_inicio é obrigatória no cultivo  
- data_fim é opcional na criação e obrigatória no encerramento  
- o controle deve ser feito no nível do cultivo  
- a flexibilidade inicial garante aderência à realidade do campo  

---

## 🔥 Regra de Ouro

Nunca obrigue o usuário a informar um dado que ele ainda não tem certeza.