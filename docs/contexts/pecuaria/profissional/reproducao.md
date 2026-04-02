---
modulo: Pecuária
submodulo: Reprodução
nivel: profissional
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-rebanho.md
  - ../essencial/manejos-basicos.md
standalone: false
complexidade: L
assinante_alvo:
  - pecuarista
  - veterinario
  - gestor-rural
---

# Reprodução

## Descrição Funcional

Submódulo de gestão reprodutiva do rebanho, cobrindo todo o ciclo desde o protocolo de IATF (Inseminação Artificial em Tempo Fixo), monta natural e repasse, até diagnóstico de gestação e previsão de partos. Permite criar protocolos reprodutivos com cronograma de aplicações hormonais, registrar inseminações com dados do sêmen (touro, central, partida), acompanhar taxas de concepção e planejar estações de monta.

Fornece indicadores reprodutivos essenciais: taxa de prenhez, intervalo entre partos (IEP), taxa de concepção à primeira IA e índice de serviço.

## Personas — Quem usa este submódulo

- **Veterinário:** elaboração e execução de protocolos de IATF, diagnóstico de gestação via ultrassom
- **Gerente de Fazenda:** planejamento de estação de monta, alocação de touros
- **Proprietário:** acompanhamento de indicadores reprodutivos e decisão sobre descarte
- **Inseminador:** registro de inseminações com dados do sêmen utilizado

## Dores que resolve

- Falta de controle sobre datas de protocolo hormonal e inseminação
- Impossibilidade de calcular taxa de prenhez por touro, inseminador ou lote
- Ausência de previsão de partos para planejamento de manejo
- Perda de dados de sêmen utilizado (touro, partida) para avaliação genética
- Intervalo entre partos desconhecido, mascarando ineficiência reprodutiva

## Regras de Negócio

1. Protocolo IATF segue cronograma com D0, D8, D10 (ou customizado); sistema gera alertas para cada etapa
2. Inseminação registra: matriz, touro (sêmen), inseminador, data/hora, partida do sêmen
3. Diagnóstico de gestação (DG) registra: data, resultado (positivo/negativo/absorção), dias de gestação estimados
4. Taxa de prenhez = matrizes prenhas / matrizes protocoladas × 100
5. Monta natural registra: matriz, touro, data início e fim de exposição
6. Repasse com touro após IATF: período configurável (45-60 dias padrão)
7. Previsão de parto = data da IA + 285 dias (bovinos); ajustável por raça
8. Matrizes com 3+ IAs sem concepção: alerta de descarte reprodutivo

## Entidades de Dados Principais

- **ProtocoloReproducao:** id, tenant_id, nome, tipo (IATF|monta_natural), cronograma_json, estacao_monta_id
- **EstacaoMonta:** id, tenant_id, fazenda_id, data_inicio, data_fim, tipo
- **Inseminacao:** id, tenant_id, matriz_id, touro_semen, central_semen, partida, inseminador_id, data, protocolo_id
- **DiagnosticoGestacao:** id, tenant_id, matriz_id, data, resultado, dias_gestacao, metodo (palpacao|ultrassom)
- **MontaNatural:** id, tenant_id, touro_id, lote_matrizes_id, data_inicio, data_fim
- **PrevisaoParto:** id, inseminacao_id, data_prevista, data_real, observacoes

## Integrações Necessárias

- **Cadastro de Rebanho:** Matrizes e touros como entidades centrais
- **Manejos Básicos:** Manejo reprodutivo como subtipo de manejo
- **Estoque:** Controle de doses de sêmen e hormônios
- **Genética (Enterprise):** Seleção de touros por DEPs e mérito genético
- **Financeiro (opcional):** Custo por prenhez (sêmen + hormônio + mão de obra)

## Fluxo de Uso Principal (step-by-step)

1. Criar estação de monta com datas de início e fim
2. Selecionar matrizes aptas (idade, ECC, dias pós-parto)
3. Definir protocolo IATF com cronograma hormonal
4. Sistema gera agenda de manejos com alertas por etapa (D0, D8, D10, IA)
5. Registrar inseminação com dados do sêmen e inseminador
6. Agendar diagnóstico de gestação (30-60 dias pós-IA)
7. Registrar resultado do DG; sistema calcula taxa de prenhez
8. Para vazias: alocar para repasse com touro ou novo protocolo
9. Para prenhas: sistema gera previsão de parto
10. Acompanhar dashboard reprodutivo com indicadores

## Casos Extremos e Exceções

- **Matriz inseminada sem protocolo:** Permitir registro avulso (IA convencional)
- **DG positivo seguido de absorção embrionária:** Registrar perda com data; remover previsão de parto
- **Touro com baixa fertilidade:** Alerta se taxa de concepção < 40% após 20+ IAs
- **Sêmen de touro morto:** Permitir uso; manter registro histórico do touro
- **Gêmeos detectados no DG:** Campo para indicar gestação gemelar
- **Parto prematuro ou tardio:** Registrar data real; calcular desvio da previsão

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de Protocolo Reprodutivo com cronograma configurável
- [ ] Registro de inseminação com dados completos do sêmen
- [ ] Diagnóstico de gestação com cálculo de taxa de prenhez
- [ ] Previsão de partos automática
- [ ] Dashboard com indicadores: taxa de prenhez, IEP, concepção 1ª IA
- [ ] Alertas de etapas do protocolo IATF
- [ ] Isolamento multi-tenant em todas as entidades
- [ ] Testes para cálculos reprodutivos e regras de alerta

## Sugestões de Melhoria Futura

- Integração com aparelho de ultrassom para importação automática de DG
- Seleção assistida de touro baseada em DEPs e complementaridade genética
- Análise econômica por estação de monta (custo por bezerro nascido)
- Calendário reprodutivo visual com Gantt de protocolos
- Benchmark de indicadores reprodutivos entre fazendas
