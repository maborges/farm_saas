---
modulo: Pessoas e RH
submodulo: Escalas e Tarefas
nivel: profissional
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-colaboradores.md
  - ../essencial/controle-presenca.md
  - ./treinamentos.md
standalone: false
complexidade: M
assinante_alvo:
  - Médio produtor rural
  - Grande produtor rural
  - Cooperativas
---

# Escalas de Trabalho e Tarefas

## Descrição Funcional

Gestão de escalas de trabalho e atribuição de tarefas aos colaboradores da fazenda. Permite criar escalas (5x1, 6x1, 12x36, plantão), atribuir colaboradores a turnos, planejar tarefas diárias/semanais por equipe ou individualmente, e acompanhar execução. Contempla a sazonalidade rural: escalas diferenciadas em período de plantio, colheita e entressafra. Conecta mão de obra com operações agrícolas e pecuárias.

## Personas — Quem usa este submódulo

- **Gerente de fazenda:** Planeja escalas e distribui tarefas entre equipes
- **Encarregado de campo:** Consulta escala do dia, atribui tarefas, reporta execução
- **Colaborador:** Consulta sua escala e tarefas atribuídas
- **RH:** Garante conformidade de jornada e descansos obrigatórios

## Dores que resolve

- Escalas feitas de cabeça ou em papel — esquecimentos e conflitos
- Colaboradores sem saber o que fazer no dia — esperam ordens do encarregado
- Falta de visibilidade sobre quem está onde e fazendo o quê
- Dificuldade de redistribuir equipe quando alguém falta
- Desconformidade de jornada (trabalho excessivo sem folga) sem perceber

## Regras de Negócio

1. Escala deve respeitar jornada máxima legal (8h/dia, 44h/semana — ou acordo coletivo)
2. DSR obrigatório: mínimo 1 folga a cada 7 dias trabalhados (preferencialmente domingo)
3. Intervalo entre jornadas: mínimo 11 horas (CLT art. 66)
4. Escala 12x36: permitida por acordo — 12h de trabalho, 36h de descanso
5. Tarefa de risco só pode ser atribuída a colaborador com treinamento válido
6. Tarefa pode ser individual ou por equipe
7. Status da tarefa: Planejada -> Em Andamento -> Concluída -> Verificada
8. Tarefa não concluída pode ser reagendada com justificativa
9. Escala pode variar por período (safra vs. entressafra)
10. Colaborador afastado/férias não pode ser escalado

## Entidades de Dados Principais

- **EscalaTrabalho:** id, fazenda_id, tenant_id, nome, tipo (5x1/6x1/12x36/plantao/personalizada), turno_inicio, turno_fim, intervalo_inicio, intervalo_fim, dias_trabalho, dias_folga, periodo_vigencia_inicio, periodo_vigencia_fim, created_at
- **EscalaColaborador:** id, escala_id, colaborador_id, data_inicio, data_fim, ativo
- **Tarefa:** id, fazenda_id, tenant_id, titulo, descricao, tipo_atividade, local (talhao/piquete/area), prioridade (baixa/media/alta/urgente), data_prevista, data_conclusao, responsavel_id, equipe_ids, status, observacoes, created_at, updated_at
- **TarefaExecucao:** id, tarefa_id, colaborador_id, data_execucao, horas_gastas, percentual_concluido, observacoes

## Integrações Necessárias

- **Cadastro de Colaboradores (essencial):** lista de colaboradores disponíveis
- **Controle de Presença (essencial):** verificar quem está presente para redistribuir
- **Treinamentos (profissional):** validar treinamento para tarefas de risco
- **Operações Agrícolas (agrícola):** tarefas vinculadas a operações em talhões
- **Manejos (pecuária):** tarefas de manejo animal
- **Frota (operacional):** alocação de máquinas/veículos junto com operador

## Fluxo de Uso Principal (step-by-step)

1. Gerente acessa Pessoas > Escalas e Tarefas
2. Cria ou seleciona uma escala de trabalho (ex: 6x1 turno diurno)
3. Atribui colaboradores à escala
4. Sistema gera calendário de trabalho e folgas para cada colaborador
5. Para planejar tarefas: clica em "Nova Tarefa"
6. Define: título, local (talhão, piquete), data, prioridade e responsável/equipe
7. Sistema valida se responsável tem treinamento necessário (se tarefa de risco)
8. Encarregado consulta painel de tarefas do dia no campo
9. Ao iniciar tarefa, marca como "Em Andamento"
10. Ao concluir, marca como "Concluída" com observações
11. Gerente verifica tarefas concluídas e valida
12. Tarefas não concluídas são reagendadas automaticamente ou manualmente

## Casos Extremos e Exceções

- **Falta inesperada:** colaborador faltou — sistema sugere substituto disponível da mesma escala
- **Chuva/intempérie:** tarefas de campo canceladas — reagendar em lote
- **Urgência (ex: gado solto):** tarefa urgente criada e atribuída imediatamente fora da escala
- **Colaborador em duas escalas:** não permitido — conflito de horário
- **Período de colheita:** escala estendida com horas extras autorizadas
- **Menor aprendiz:** restrição de horário e atividades — sistema deve bloquear escalas noturnas
- **Folga compensatória:** colaborador trabalhou domingo — sistema deve garantir folga compensatória
- **Tarefa com dependência:** tarefa B só pode iniciar após conclusão da tarefa A

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de escalas com tipos pré-definidos e personalizados
- [ ] Atribuição de colaboradores a escalas com validação de conflitos
- [ ] Geração de calendário de trabalho/folga por colaborador
- [ ] Validação de jornada máxima e intervalo entre jornadas
- [ ] CRUD de tarefas com atribuição individual ou por equipe
- [ ] Fluxo de status de tarefa (Planejada -> Concluída -> Verificada)
- [ ] Validação de treinamento para tarefas de risco
- [ ] Painel de tarefas do dia por fazenda
- [ ] Reagendamento de tarefas não concluídas
- [ ] Isolamento por tenant e fazenda
- [ ] Testes de integração

## Sugestões de Melhoria Futura

- App mobile para encarregado gerenciar tarefas no campo (offline-first)
- Mapa da fazenda com tarefas geolocalizadas
- Kanban visual de tarefas por equipe/área
- Sugestão automática de escala baseada em histórico de demanda
- Integração com previsão do tempo para reagendamento proativo
- Relatório de produtividade por colaborador/equipe
