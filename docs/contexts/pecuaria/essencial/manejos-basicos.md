---
modulo: Pecuária
submodulo: Manejos Básicos
nivel: essencial
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ./cadastro-rebanho.md
standalone: false
complexidade: M
assinante_alvo:
  - pecuarista
  - gestor-rural
  - vaqueiro
  - veterinario
---

# Manejos Básicos

## Descrição Funcional

Submódulo de registro dos manejos operacionais do dia a dia: pesagem, vacinação e movimentação de animais. Cada manejo é registrado com data, responsável, animais envolvidos e observações, formando o histórico zootécnico do rebanho. A pesagem calcula automaticamente o GMD (Ganho Médio Diário) comparando com a pesagem anterior. A vacinação registra produto, lote da vacina e via de aplicação. A movimentação controla transferências de animais entre piquetes, lotes ou fazendas.

Manejos podem ser registrados individualmente ou em lote (todos os animais do curral), otimizando o trabalho de campo.

## Personas — Quem usa este submódulo

- **Vaqueiro / Peão:** registro de pesagens na balança, aplicação de vacinas, movimentação de gado entre piquetes
- **Gerente de Fazenda:** planejamento de manejos, acompanhamento de GMD e calendário vacinal
- **Veterinário:** prescrição e supervisão de protocolos vacinais
- **Proprietário:** acompanhamento de indicadores de desempenho do rebanho

## Dores que resolve

- Pesagens anotadas em papel e perdidas ou transcritas com erro
- Falta de cálculo automático de GMD para decisão de venda
- Vacinações sem rastreabilidade do lote de vacina usado
- Impossibilidade de saber onde cada animal está (em qual piquete)
- Ausência de histórico consolidado de manejos por animal

## Regras de Negócio

1. Toda pesagem deve registrar peso (kg) e, opcionalmente, escore de condição corporal (1-5)
2. GMD = (peso_atual - peso_anterior) / dias_entre_pesagens; exibido automaticamente
3. Vacinação exige: produto, lote_vacina, dose (ml), via (subcutânea/intramuscular)
4. Vacinação em lote aplica mesma vacina a todos os animais selecionados
5. Movimentação entre piquetes atualiza alocação atual e gera histórico
6. Movimentação entre fazendas exige geração de GTA (quando SISBOV ativo)
7. Manejos não podem ser deletados; apenas estornados com justificativa
8. Data do manejo não pode ser futura; máximo retroativo: 30 dias (configurável)

## Entidades de Dados Principais

- **Manejo:** id, tenant_id, fazenda_id, tipo (pesagem|vacinacao|movimentacao), data, responsavel_id, observacoes, estornado, created_at
- **ManejoPesagem:** manejo_id, animal_id, peso_kg, escore_corporal, gmd_calculado
- **ManejoVacinacao:** manejo_id, animal_id, produto, lote_vacina, dose_ml, via_aplicacao
- **ManejoMovimentacao:** manejo_id, animal_id, piquete_origem_id, piquete_destino_id, motivo
- **ManejoLote:** manejo_id, lote_id — agrupa manejos realizados no mesmo evento

## Integrações Necessárias

- **Cadastro de Rebanho:** Animais e lotes como alvo dos manejos
- **Piquetes/Pastagens:** Destino e origem de movimentações
- **Estoque:** Baixa de vacinas/medicamentos utilizados
- **Financeiro (opcional):** Custo de insumos aplicados por animal

## Fluxo de Uso Principal (step-by-step)

1. Acessar Pecuária > Manejos > Novo Manejo
2. Selecionar tipo: Pesagem, Vacinação ou Movimentação
3. Selecionar animais (individual, por lote ou leitura de brinco)
4. Preencher dados específicos do tipo de manejo
5. Confirmar e salvar; sistema calcula GMD (pesagem) ou atualiza localização (movimentação)
6. Visualizar histórico de manejos por animal ou por lote
7. Consultar indicadores: GMD médio do lote, cobertura vacinal, taxa de movimentação

## Casos Extremos e Exceções

- **Pesagem com valor discrepante:** Alerta se peso variar mais de 20% em relação à pesagem anterior; solicitar confirmação
- **Vacina com lote vencido:** Bloquear aplicação se data de validade do lote cadastrado no estoque já expirou
- **Movimentação para piquete superlotado:** Alerta mas permite, registrando excedente
- **Manejo retroativo:** Permitido até 30 dias; recalcular GMD dos manejos subsequentes
- **Estorno de vacinação:** Não reverte efeito biológico, apenas registra que houve erro administrativo
- **Animal não encontrado no lote:** Pode ter sido movido; sugerir busca global

## Critérios de Aceite (Definition of Done)

- [ ] Registro de pesagem com cálculo automático de GMD
- [ ] Registro de vacinação com rastreabilidade de lote de vacina
- [ ] Registro de movimentação com atualização de localização
- [ ] Manejo em lote (múltiplos animais de uma vez)
- [ ] Histórico de manejos por animal com timeline
- [ ] Estorno de manejo com justificativa obrigatória
- [ ] Isolamento multi-tenant em todos os endpoints
- [ ] Testes para cálculo de GMD e regras de validação

## Sugestões de Melhoria Futura

- Integração com balança eletrônica via Bluetooth/USB
- Registro de manejo por voz (assistente de campo)
- Manejo offline no app mobile com sincronização posterior
- Alertas automáticos de vacinação pendente via push notification
- Comparativo de GMD entre lotes em gráfico temporal
