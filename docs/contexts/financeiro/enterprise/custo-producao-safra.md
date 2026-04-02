---
modulo: Financeiro
submodulo: Custo de Produção por Safra
nivel: enterprise
core: false
dependencias_core:
  - categorias-contas
  - lancamentos-basicos
dependencias_modulos:
  - ../essencial/lancamentos-basicos.md
  - ../profissional/centro-custo.md
  - ../profissional/contas-pagar-receber.md
  - ../../agricola/essencial/safras.md
  - ../../agricola/essencial/talhoes.md
  - ../../operacional/essencial/estoque.md
standalone: false
complexidade: XL
assinante_alvo:
  - grande produtor rural
  - empresa agrícola
  - cooperativa
  - consultor agronômico
  - gestor de agronegócio
---

# Custo de Produção por Safra

## Descrição Funcional

Submódulo que apura o custo total de produção por safra e por talhão, consolidando todas as despesas diretas e indiretas do ciclo produtivo: insumos (sementes, fertilizantes, defensivos), operações mecanizadas (plantio, pulverização, colheita), mão de obra, custos financeiros (juros de crédito rural), depreciação de máquinas e rateio de despesas gerais.

Permite ao produtor saber exatamente quanto custou produzir cada saca/tonelada, comparar com o preço de venda e calcular a margem real de lucro por talhão, cultura e safra. É a ferramenta de decisão mais estratégica do módulo Financeiro.

## Personas — Quem usa este submódulo

- **Gestor de Agronegócio:** analisa custo por saca para negociar preço de venda; compara rentabilidade entre talhões.
- **Diretor financeiro:** consolida custo de produção de todas as fazendas do grupo para relatórios gerenciais.
- **Consultor agronômico:** avalia eficiência de manejo comparando custo/produtividade entre áreas.
- **Produtor Rural (owner):** decide quais culturas plantar na próxima safra com base na margem das anteriores.
- **Contador rural:** fecha balanço com custo de produção para estoque de produtos agrícolas (CPC 29).

## Dores que resolve

1. **"Quanto custa minha saca de soja?":** pergunta fundamental que a maioria dos produtores não consegue responder com precisão.
2. **Talhões deficitários invisíveis:** sem custo por talhão, áreas com produtividade baixa e custo alto passam despercebidas.
3. **Decisão de cultura às cegas:** sem margem histórica, decisão de plantar soja vs. milho é por intuição.
4. **Precificação de venda sem base:** vender a produção sem saber o custo é arriscar prejuízo.
5. **Prestação de contas a sócios/investidores:** impossível demonstrar rentabilidade sem custo de produção apurado.
6. **Compliance contábil:** CPC 29 exige mensuração de ativos biológicos a valor justo ou custo.

## Regras de Negócio

1. Custo de produção é apurado por safra (`safra_id`) e opcionalmente por talhão.
2. Componentes de custo:
   - **Insumos:** custos FIFO do estoque consumido (sementes, fertilizantes, defensivos).
   - **Operações mecanizadas:** custo/hora de máquinas × horas trabalhadas por talhão.
   - **Mão de obra:** rateio da folha de pagamento por centro de custo.
   - **Custos financeiros:** juros de crédito rural rateados por safra.
   - **Depreciação:** rateio de depreciação de máquinas e benfeitorias.
   - **Despesas gerais:** rateio de despesas administrativas, energia, combustível.
3. Insumos são valorados pelo custo FIFO do estoque (integração com módulo de Estoque/FIFO da Fase 3).
4. Custo por unidade = custo total ÷ produção colhida (sacas, toneladas, etc.).
5. Margem bruta = receita de venda − custo de produção.
6. Apuração pode ser parcial (safra em andamento) ou final (safra encerrada).
7. Custo previsto vs. realizado: comparar orçamento do centro de custo com custos efetivos.
8. Período de apuração segue o ciclo da safra (plantio → colheita → venda), não o ano fiscal.
9. Safra com produção zero (frustração): custo é registrado como perda.
10. Rateio de custos indiretos segue critérios configuráveis: área (ha), produção estimada ou percentual fixo.

## Entidades de Dados Principais

### CustoProducaoSafra
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| fazenda_id | UUID | sim | FK → Fazenda |
| safra_id | UUID | sim | FK → Safra |
| talhao_id | UUID | não | FK → Talhão (se apuração por talhão) |
| cultura | VARCHAR(100) | sim | Cultura (soja, milho, etc.) |
| area_hectares | DECIMAL(10,2) | sim | Área plantada |
| status | ENUM(EM_APURACAO, PARCIAL, FINALIZADO) | sim | Status da apuração |
| producao_quantidade | DECIMAL(12,2) | não | Produção colhida (sacas/ton) |
| producao_unidade | VARCHAR(20) | não | Unidade (sacas, toneladas, kg) |
| custo_total_centavos | INTEGER | sim | Custo total apurado |
| custo_por_hectare_centavos | INTEGER | não | Custo ÷ área |
| custo_por_unidade_centavos | INTEGER | não | Custo ÷ produção |
| receita_total_centavos | INTEGER | não | Receita de vendas |
| margem_bruta_centavos | INTEGER | não | Receita − custo |
| data_apuracao | DATE | sim | Data da apuração |

### CustoProducaoItem
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| custo_producao_id | UUID | sim | FK → CustoProducaoSafra |
| tipo | ENUM(INSUMO, OPERACAO_MECANIZADA, MAO_DE_OBRA, CUSTO_FINANCEIRO, DEPRECIACAO, DESPESA_GERAL) | sim | Tipo de custo |
| descricao | VARCHAR(255) | sim | Descrição do item |
| lancamento_id | UUID | não | FK → Lancamento (rastreabilidade) |
| lote_id | UUID | não | FK → Lote de estoque (para insumos FIFO) |
| valor_centavos | INTEGER | sim | Valor |
| quantidade | DECIMAL(12,4) | não | Quantidade (litros, kg, horas) |
| unidade | VARCHAR(20) | não | Unidade de medida |
| valor_unitario_centavos | INTEGER | não | Valor unitário |
| criterio_rateio | VARCHAR(50) | não | Critério usado no rateio |

### CustoProducaoComparativo
| Campo | Tipo | Descrição |
|-------|------|-----------|
| safra_id | UUID | Safra |
| talhao_id | UUID | Talhão |
| custo_previsto_centavos | INTEGER | Orçamento (do centro de custo) |
| custo_realizado_centavos | INTEGER | Custo apurado |
| variacao_percentual | DECIMAL(5,2) | % de variação |

## Integrações Necessárias

- **Centro de Custo (profissional):** orçamento por centro é a base para custo previsto; rateio usa centros de custo.
- **Lançamentos Básicos (essencial):** cada item de custo referencia um lançamento para rastreabilidade.
- **Estoque/FIFO (operacional):** valoração de insumos pelo custo FIFO dos lotes consumidos.
- **Módulo Agrícola — Safras:** vinculação ao ciclo da safra (plantio, tratos, colheita).
- **Módulo Agrícola — Talhões:** apuração por talhão; dados de área e produtividade.
- **Módulo Agrícola — Operações:** horas de operações mecanizadas por talhão.
- **Crédito Rural (enterprise):** juros de financiamento como componente de custo financeiro.
- **Módulo Operacional — Frota:** custo/hora de máquinas para valoração de operações.

## Fluxo de Uso Principal (step-by-step)

1. Gestor acessa "Custo de Produção" no menu Financeiro.
2. Seleciona safra e opcionalmente talhão para apuração.
3. Sistema consolida automaticamente os custos a partir de:
   - Movimentações de estoque (insumos aplicados) valoradas por FIFO.
   - Lançamentos vinculados ao centro de custo da safra/talhão.
   - Operações mecanizadas registradas no módulo Agrícola.
4. Custos indiretos (mão de obra, depreciação, despesas gerais) são rateados conforme critério configurado.
5. Sistema exibe breakdown por tipo de custo (insumos, operações, mão de obra, etc.).
6. Usuário pode adicionar/ajustar itens manualmente se necessário.
7. Após colheita, informa a produção obtida.
8. Sistema calcula custo por hectare e custo por unidade produzida.
9. Ao registrar vendas da produção, sistema calcula margem bruta.
10. Relatório comparativo mostra custo previsto vs. realizado e benchmarks entre talhões/safras.

## Casos Extremos e Exceções

- **Safra em andamento (apuração parcial):** custo é calculado com base nos dados disponíveis; marcado como PARCIAL.
- **Safra frustrada (produção zero):** custo é registrado como perda; custo por unidade = infinito (exibir "N/A").
- **Insumo aplicado em múltiplos talhões:** rateio proporcional à dose por hectare aplicada.
- **Operação mecanizada sem registro de horas:** estimar por área (ha) × taxa padrão da máquina.
- **Lançamento sem centro de custo:** não é incluído na apuração automaticamente; alerta para classificar.
- **Depreciação sem critério definido:** rateio padrão por área (ha); gestor pode ajustar.
- **Estoque sem lote FIFO:** usar custo médio como fallback.
- **Mudança de cultura no talhão durante a safra:** apurar separadamente para cada cultura.
- **Venda parcial da produção:** margem calculada proporcionalmente ao volume vendido.
- **Custo previsto não configurado:** comparativo exibe apenas realizado com nota "Sem orçamento".

## Critérios de Aceite (Definition of Done)

- [ ] Apuração automática de custo consolidando insumos (FIFO), operações, mão de obra e custos indiretos.
- [ ] Rateio de custos indiretos com critérios configuráveis (área, produção, percentual).
- [ ] Cálculo de custo por hectare e custo por unidade produzida.
- [ ] Cálculo de margem bruta (receita − custo).
- [ ] Comparativo custo previsto vs. realizado.
- [ ] Comparativo entre talhões da mesma safra.
- [ ] Comparativo entre safras do mesmo talhão (histórico).
- [ ] Breakdown detalhado por tipo de custo com drill-down até o lançamento.
- [ ] Rastreabilidade: cada item de custo referencia o lançamento e/ou lote de estoque de origem.
- [ ] Suporte a apuração parcial (safra em andamento) e final (safra encerrada).
- [ ] Tratamento de safra frustrada (produção zero).
- [ ] Exportação de relatório em PDF e CSV.
- [ ] Tenant isolation em todos os endpoints.
- [ ] Testes: apuração, rateio, FIFO, margem, comparativos, safra frustrada, tenant isolation.

## Sugestões de Melhoria Futura

- **Custo por operação:** detalhar custo de cada operação (plantio, pulverização, colheita) separadamente.
- **Benchmarking regional:** comparar custo de produção com médias regionais (CONAB, Cepea).
- **Projeção de custo:** estimar custo da próxima safra com base em histórico e preços atuais de insumos.
- **Integração com bolsa:** cruzar custo de produção com cotação futura (B3) para calcular margem projetada.
- **Custo por estágio fenológico:** detalhar custos por fase da cultura (vegetativo, reprodutivo, maturação).
- **Dashboard visual:** gráfico de Waterfall mostrando composição do custo e margem por cultura.
- **Exportação contábil:** gerar lançamentos contábeis de custo de produção no formato do ERP do contador.
- **Custo ambiental:** incluir custos de compliance ambiental (reserva legal, APP) na apuração.
