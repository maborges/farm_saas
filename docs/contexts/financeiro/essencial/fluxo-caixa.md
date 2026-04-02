---
modulo: Financeiro
submodulo: Fluxo de Caixa
nivel: essencial
core: false
dependencias_core:
  - categorias-contas
  - lancamentos-basicos
dependencias_modulos: []
standalone: true
complexidade: S
assinante_alvo:
  - pequeno produtor rural
  - agricultor familiar
  - administrador de fazenda
---

# Fluxo de Caixa

## Descrição Funcional

Submódulo que consolida todos os lançamentos efetivados em uma visão temporal de entradas, saídas e saldo acumulado. Permite ao produtor visualizar a saúde financeira da propriedade em diferentes granularidades (diária, semanal, mensal, anual) e projetar o caixa futuro com base em lançamentos previstos.

O fluxo de caixa opera em duas visões: **Realizado** (apenas lançamentos efetivados) e **Projetado** (realizado + previstos), permitindo ao produtor antecipar períodos de aperto financeiro e planejar investimentos.

## Personas — Quem usa este submódulo

- **Produtor Rural (owner):** verifica diariamente se há saldo suficiente para compromissos; planeja compras de insumos com base na projeção.
- **Administrador da Fazenda:** monitora o fluxo semanal para garantir que a operação não pare por falta de caixa.
- **Gestor Financeiro:** analisa tendências mensais e sazonalidade para planejamento de safra.
- **Contador externo:** exporta relatórios de fluxo de caixa para fechamento fiscal e demonstrativos.

## Dores que resolve

1. **"Não sei quanto tenho em caixa":** falta de visão consolidada das finanças em tempo real.
2. **Surpresas de fim de mês:** compromissos esquecidos que causam inadimplência.
3. **Sazonalidade não planejada:** safra agrícola tem ciclos longos; sem projeção, produtor fica sem caixa na entressafra.
4. **Decisões por intuição:** sem dados consolidados, investimentos são feitos "no feeling".
5. **Múltiplas contas bancárias:** difícil somar saldos de diferentes bancos manualmente.

## Regras de Negócio

1. O fluxo de caixa é calculado em tempo real a partir dos lançamentos — não é uma entidade separada.
2. Saldo inicial é configurável por fazenda (migração de dados históricos).
3. Visão "Realizado" considera apenas lançamentos com `status = EFETIVADO`.
4. Visão "Projetado" inclui lançamentos com `status = PREVISTO` somados ao realizado.
5. Granularidades suportadas: diária, semanal, mensal, anual.
6. Filtros por: fazenda, conta, categoria, período.
7. Saldo negativo projetado gera alerta visual (vermelho) na interface.
8. Exportação em PDF e CSV disponível para qualquer período/filtro.
9. O fluxo respeita multi-tenancy: cada tenant vê apenas seus dados.
10. Cache de 5 minutos para cálculos de períodos longos (> 1 ano); invalidado ao criar/editar lançamento.

## Entidades de Dados Principais

### FluxoCaixaConfig
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| fazenda_id | UUID | sim | FK → Fazenda |
| saldo_inicial_centavos | INTEGER | sim | Saldo inicial em centavos |
| data_saldo_inicial | DATE | sim | Data de referência do saldo inicial |

### FluxoCaixaPeriodo (view/cálculo, não persistido)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| periodo | DATE | Data de referência do período |
| total_receitas_centavos | INTEGER | Soma de receitas efetivadas no período |
| total_despesas_centavos | INTEGER | Soma de despesas efetivadas no período |
| saldo_periodo_centavos | INTEGER | receitas - despesas |
| saldo_acumulado_centavos | INTEGER | Saldo acumulado desde o início |
| receitas_previstas_centavos | INTEGER | Receitas previstas (projeção) |
| despesas_previstas_centavos | INTEGER | Despesas previstas (projeção) |
| saldo_projetado_centavos | INTEGER | Saldo acumulado + previstos |

## Integrações Necessárias

- **Lançamentos Básicos (essencial):** fonte primária de dados; todo lançamento efetivado alimenta o fluxo.
- **Categorias e Contas (essencial):** filtros por categoria e conta no fluxo.
- **Contas a Pagar/Receber (profissional):** parcelas futuras alimentam a projeção com maior precisão.
- **Conciliação Bancária (profissional):** saldos bancários conciliados enriquecem a visão de caixa.

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa "Fluxo de Caixa" no menu Financeiro.
2. Sistema exibe visão mensal do mês corrente por padrão.
3. Usuário vê barras de receitas (verde) e despesas (vermelho) com linha de saldo acumulado.
4. Alterna entre granularidades (dia/semana/mês/ano) via seletor.
5. Ativa/desativa a visão "Projetado" via toggle para incluir lançamentos previstos.
6. Aplica filtros por fazenda, conta ou categoria para análise segmentada.
7. Identifica período com saldo projetado negativo (destacado em vermelho).
8. Clica em um período para ver o detalhamento dos lançamentos.
9. Exporta o relatório em PDF ou CSV para compartilhar com contador ou banco.
10. Opcionalmente configura o saldo inicial da fazenda na primeira utilização.

## Casos Extremos e Exceções

- **Nenhum lançamento no período:** exibir saldo acumulado anterior com mensagem "Sem movimentação no período".
- **Saldo inicial não configurado:** considerar zero; exibir banner sugerindo configurar.
- **Período muito longo (> 5 anos):** limitar a consulta e sugerir granularidade anual.
- **Lançamento editado retroativamente:** recalcular fluxo a partir da data alterada; invalidar cache.
- **Múltiplas fazendas:** visão consolidada (todas) ou individual; default é consolidada.
- **Moeda fracionária:** todos os cálculos em centavos (integer) para evitar erros de arredondamento.
- **Timezone:** datas sempre em UTC no banco; conversão para timezone do tenant na exibição.

## Critérios de Aceite (Definition of Done)

- [ ] Endpoint de fluxo de caixa retorna dados agregados por período com tenant isolation.
- [ ] Granularidades diária, semanal, mensal e anual funcionando corretamente.
- [ ] Visão "Realizado" e "Projetado" com toggle funcional.
- [ ] Filtros por fazenda, conta, categoria e período.
- [ ] Saldo acumulado calculado corretamente a partir do saldo inicial.
- [ ] Alertas visuais para saldo projetado negativo.
- [ ] Exportação em PDF e CSV.
- [ ] Configuração de saldo inicial por fazenda.
- [ ] Cache implementado para consultas de períodos longos.
- [ ] Gráfico de barras com receitas/despesas e linha de saldo acumulado no frontend.
- [ ] Testes: cálculo correto de saldos, filtros, projeção e tenant isolation.

## Sugestões de Melhoria Futura

- **Comparativo entre períodos:** sobrepor fluxo de caixa de anos/safras diferentes para análise de sazonalidade.
- **Metas de caixa:** definir meta de saldo mínimo e receber alertas quando projeção ficar abaixo.
- **Integração com previsão de colheita:** projetar receitas futuras baseado em estimativa de produção por talhão.
- **Dashboard com indicadores:** DFC resumido no dashboard principal com semáforo (verde/amarelo/vermelho).
- **Fluxo de caixa por safra:** visão financeira isolada por ciclo de safra, do plantio à venda.
- **Notificações push:** alertar o produtor quando saldo projetado para os próximos 7 dias ficar negativo.
