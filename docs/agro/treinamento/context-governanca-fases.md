# 🌱 CONTEXTO — GOVERNANÇA DE FASES, CHECKLISTS, TAREFAS E GATES DA SAFRA

## 🎯 Objetivo

Definir o modelo de governança operacional da safra com base em fases da linha do tempo, checklists por fase, tarefas por fase, operações de execução e regras de avanço entre fases (gates), garantindo que a safra avance com controle, mas sem engessar o processo.

## 🧠 Princípio Central

As fases da safra não são apenas etapas visuais. Cada fase representa uma macro-etapa de negócio e deve possuir critérios de prontidão, critérios de execução e regras para liberar a próxima fase.

## 🧱 Estrutura Conceitual

Cada Safra possui:

Safra  
└── Fases  
&nbsp;&nbsp;&nbsp;&nbsp;├── Checklist da Fase  
&nbsp;&nbsp;&nbsp;&nbsp;├── Tarefas da Fase  
&nbsp;&nbsp;&nbsp;&nbsp;└── Operações (via tarefas)

## 📍 Fases da Safra

- Planejamento  
- Preparo do Solo  
- Plantio  
- Desenvolvimento  
- Colheita  
- Pós-Colheita  
- Encerramento  

## 📋 Checklists por Fase

Checklist não é execução. Checklist é verificação. Ele responde:

“Estamos prontos para avançar?”

Cada fase possui seu próprio checklist.

Cada item do checklist possui:

- descrição  
- obrigatório?  
- concluído?  
- observação  
- gera tarefa se pendente? (opcional)

Exemplo — Checklist da fase Planejamento:

- análise de solo revisada  
- correções avaliadas  
- insumos planejados  
- recursos disponíveis  
- orçamento validado  

Regra do checklist:

A próxima fase só pode ser liberada quando todos os itens obrigatórios estiverem concluídos.

## ⚙️ Tarefas por Fase

Tarefa é trabalho executável dentro da fase.

Ela responde:

“O que precisa ser feito?”

Toda tarefa pertence a uma fase.

Exemplo:

Fase: Preparo do Solo

Tarefas:

- aplicar calcário  
- subsolar área  
- revisar umidade  

Atributos mínimos da tarefa:

- descrição  
- fase_id  
- status  
- responsável  
- prioridade  
- criticidade  
- origem (manual, automática, template)

Status mínimos:

- PENDENTE  
- EM_EXECUCAO  
- CONCLUIDA  
- CANCELADA  

Opcional:

- APROVACAO_PENDENTE  
- APROVADA  

## 🚨 Criticidade das Tarefas

Nem toda tarefa deve bloquear avanço.

Cada tarefa deve possuir criticidade:

- CRITICA  
- NORMAL  
- OPCIONAL  

ou atributo:

bloqueia_avanco_fase = true/false

## 🚦 Regra de Avanço entre Fases (Gate)

A safra NÃO deve exigir 100% de todas as tarefas concluídas.

Isso engessa o processo.

Regra correta:

A safra avança quando:

- checklist obrigatório concluído  
E  
- todas as tarefas críticas concluídas

Fórmula do gate:

IF checklist_obrigatorio = 100%  
AND tarefas_criticas = 100%  
THEN liberar próxima fase

## 📌 Tarefas não críticas

Tarefas normais ou opcionais podem:

- permanecer pendentes  
- ser concluídas depois  
- ser reprogramadas  
- ser canceladas  

sem bloquear avanço.

Exemplo:

Aplicar calcário → crítica → concluída  
Subsolagem → crítica → concluída  
Atualizar fotos → opcional → pendente  

Resultado:

✔ pode avançar de fase.

## 🚜 Operações

Operação registra execução real.

Ela responde:

“O que foi realmente feito?”

Exemplo:

Tarefa:

Aplicar calcário 2 t/ha

Operação executada:

- 1,8 t/ha aplicado  
- custo real registrado  
- insumo consumido do estoque  

Regra:

Planejado fica na tarefa.

Realizado fica na operação.

## 🔄 Fluxo de Execução

Criar tarefa  
→ atribuir responsável  
→ executar  
→ registrar operação  
→ concluir tarefa

## 🧠 Origem das Tarefas

Manual:

Criadas pelo agrônomo.

Automática:

Geradas por regras.

Exemplo:

pH baixo  
→ gerar tarefa: Aplicar calcário

Template:

Criadas automaticamente ao entrar em uma fase.

## ⚠️ Regras Importantes

Não misturar:

- checklist com tarefa  
- tarefa com operação  

São objetos distintos.

Relação correta:

Checklist valida.

Tarefa executa.

Operação registra.

## 🎯 Resumo de Governança

Checklist = validar prontidão

Tarefa = executar trabalho

Operação = registrar execução real

Gate = controlar avanço

## 📌 Conclusão

A passagem entre fases deve depender de:

✔ checklist obrigatório concluído  
✔ tarefas críticas concluídas  

e NÃO de 100% de todas as tarefas.

Isso cria um workflow robusto, flexível e aderente ao negócio real.

## 🔥 Regra de Ouro

Checklist pergunta:

Estamos prontos?

Tarefa pergunta:

O que precisa ser feito?

Operação responde:

O que foi feito?

Gate decide:

Podemos avançar?