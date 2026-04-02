---
modulo: Financeiro
submodulo: Centro de Custo
nivel: profissional
core: false
dependencias_core:
  - categorias-contas
  - lancamentos-basicos
dependencias_modulos:
  - ../essencial/lancamentos-basicos.md
dependencias_modulos_externos:
  - ../../agricola/essencial/safras.md
  - ../../pecuaria/essencial/lotes.md
standalone: true
complexidade: M
assinante_alvo:
  - médio produtor rural
  - gestor financeiro rural
  - empresa agrícola
  - cooperativa
---

# Centro de Custo

## Descrição Funcional

Submódulo que permite classificar e ratear custos e receitas por unidades de negócio da propriedade rural: talhões, safras, lotes de animais, atividades ou projetos específicos. Essencial para o produtor que precisa saber exatamente quanto custa produzir em cada área, quanto cada rebanho gera de despesa, ou qual atividade é mais rentável.

O centro de custo funciona como uma dimensão adicional de classificação, complementar às categorias. Um lançamento pode ser rateado entre múltiplos centros de custo com percentuais ou valores fixos.

## Personas — Quem usa este submódulo

- **Gestor Financeiro:** configura centros de custo e analisa rentabilidade por unidade de negócio.
- **Administrador da Fazenda:** rateia despesas operacionais (diesel, mão de obra) entre talhões e atividades.
- **Produtor Rural (owner):** compara custos entre safras, áreas e atividades para decidir onde investir.
- **Consultor agrícola:** analisa relatórios de custo por centro para recomendar otimizações.

## Dores que resolve

1. **"Quanto custa produzir neste talhão?":** impossível responder sem rateio de custos por área.
2. **Atividades deficitárias invisíveis:** sem centro de custo, uma atividade lucrativa mascara outra que dá prejuízo.
3. **Rateio manual em planilhas:** complexo, propenso a erros e impossível de manter atualizado.
4. **Tomada de decisão às cegas:** sem saber o custo por unidade, decisões de expansão/redução são arriscadas.
5. **Prestação de contas a sócios:** propriedades com múltiplos sócios precisam demonstrar custos por área/atividade.

## Regras de Negócio

1. Centros de custo são hierárquicos em até 3 níveis.
2. Tipos de centro: `TALHAO`, `SAFRA`, `LOTE_ANIMAL`, `ATIVIDADE`, `PROJETO`, `FAZENDA`, `CUSTOM`.
3. Centros de custo do tipo `TALHAO`, `SAFRA` e `LOTE_ANIMAL` podem ser vinculados automaticamente às respectivas entidades dos módulos Agrícola e Pecuária.
4. Um lançamento pode ser rateado entre 1 a N centros de custo.
5. Rateio por percentual: a soma dos percentuais deve ser exatamente 100%.
6. Rateio por valor fixo: a soma dos valores deve ser igual ao valor do lançamento.
7. Se nenhum centro de custo for informado, o lançamento fica como "Não classificado".
8. Relatórios de custo respeitam a hierarquia: custo de um grupo = soma dos custos dos filhos.
9. Centro de custo com lançamentos vinculados não pode ser excluído; apenas desativado.
10. Cada centro pertence a um `tenant_id`.

## Entidades de Dados Principais

### CentroCusto
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| fazenda_id | UUID | sim | FK → Fazenda |
| parent_id | UUID | não | FK → CentroCusto (hierarquia) |
| nome | VARCHAR(150) | sim | Nome do centro |
| tipo | ENUM(TALHAO, SAFRA, LOTE_ANIMAL, ATIVIDADE, PROJETO, FAZENDA, CUSTOM) | sim | Tipo |
| referencia_id | UUID | não | FK genérico para entidade vinculada (talhão, safra, lote) |
| referencia_tipo | VARCHAR(50) | não | Tipo da entidade vinculada |
| ativo | BOOLEAN | sim | Se está ativo |
| orcamento_centavos | INTEGER | não | Orçamento planejado |

### LancamentoRateio
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| lancamento_id | UUID | sim | FK → Lancamento |
| centro_custo_id | UUID | sim | FK → CentroCusto |
| percentual | DECIMAL(5,2) | não | Percentual do rateio |
| valor_centavos | INTEGER | sim | Valor rateado em centavos |

## Integrações Necessárias

- **Lançamentos Básicos (essencial):** cada lançamento pode ter rateio para centros de custo.
- **Contas a Pagar/Receber (profissional):** contas podem ter rateio definido; baixas herdam o rateio.
- **Módulo Agrícola:** talhões e safras podem ser centros de custo automaticamente.
- **Módulo Pecuária:** lotes de animais podem ser centros de custo automaticamente.
- **Custo de Produção por Safra (enterprise):** centros de custo são a base para apuração de custo.

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa "Centros de Custo" no menu Financeiro.
2. Cria centros de custo manualmente ou importa automaticamente de talhões/safras/lotes existentes.
3. Organiza hierarquicamente (ex.: Fazenda Norte → Talhão A1 → Safra 24/25).
4. Opcionalmente define orçamento planejado para cada centro.
5. Ao criar um lançamento, seleciona "Ratear por Centro de Custo".
6. Seleciona os centros e define percentuais ou valores para cada um.
7. Sistema valida que a soma = 100% (ou valor total).
8. Acessa relatório de custos por centro, com filtro por período.
9. Compara custos realizados vs. orçamento planejado.
10. Analisa rentabilidade cruzando receitas e despesas por centro de custo.

## Casos Extremos e Exceções

- **Rateio que não soma 100%:** rejeitar e exibir diferença para o usuário ajustar.
- **Centro de custo vinculado a talhão excluído:** centro permanece ativo com nota "(talhão removido)".
- **Lançamento com rateio editado:** recalcular valores das parcelas do rateio.
- **Centro de custo sem lançamentos:** permitir exclusão física.
- **Importação automática com talhões duplicados:** detectar e evitar duplicidade por `referencia_id`.
- **Orçamento estourado:** alerta visual quando custos realizados ultrapassam 80% e 100% do orçamento.
- **Migração entre safras:** ao encerrar safra, centros podem ser clonados para a nova safra.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de centros de custo com hierarquia e tenant isolation.
- [ ] Rateio de lançamentos por percentual e por valor fixo.
- [ ] Validação de que rateio soma 100% / valor total.
- [ ] Importação automática de talhões, safras e lotes como centros de custo.
- [ ] Relatório de custos por centro com filtro de período.
- [ ] Comparativo realizado vs. orçamento.
- [ ] Alerta de orçamento estourado.
- [ ] Testes: rateio, hierarquia, importação, validações, tenant isolation.

## Sugestões de Melhoria Futura

- **Rateio automático por regras:** definir regras de rateio automático (ex.: "diesel sempre 60% Talhão A, 40% Talhão B").
- **Custo por hectare/cabeça:** calcular automaticamente custo unitário cruzando com área do talhão ou quantidade de animais.
- **Benchmarking:** comparar custos por centro com médias regionais ou de outros produtores (anonimizado).
- **Alocação de mão de obra:** integrar com pontual/horas trabalhadas para rateio automático de custo de pessoal.
- **Dashboard visual:** mapa da propriedade colorido por rentabilidade de cada talhão/área.
