---
modulo: Estoque
submodulo: Saldo e Consulta
nivel: essencial
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ./cadastro-produtos.md
  - ./movimentacoes.md
standalone: false
complexidade: S
assinante_alvo:
  - almoxarife
  - gestor-rural
  - comprador
  - financeiro
---

# Saldo e Consulta

## Descrição Funcional

Submódulo de consulta de saldos de estoque em tempo real, oferecendo visão por produto, por almoxarifado e consolidada por fazenda. Apresenta posição atual do estoque, valoração (quantidade x custo unitário), e histórico de movimentações por produto. Serve como painel central de visibilidade do estoque para tomada de decisão de compra e alocação.

## Personas — Quem usa este submódulo

- **Almoxarife:** conferência diária de saldos, identificação de discrepâncias
- **Gerente:** visão consolidada para planejamento de compras
- **Comprador:** identificação de itens com saldo baixo para reposição
- **Financeiro:** valoração do estoque para contabilidade e balanço

## Dores que resolve

- Desconhecimento do saldo real de insumos levando a compras emergenciais
- Valor total do estoque desconhecido para fins contábeis
- Dificuldade em identificar produtos parados (sem giro)
- Falta de visão consolidada quando há múltiplos almoxarifados
- Histórico de movimentações de um produto disperso e difícil de consultar

## Regras de Negócio

1. Saldo calculado em tempo real pela soma de entradas menos saídas
2. Saldo mantido por produto + almoxarifado (nível mais granular)
3. Consulta consolidada soma saldos de todos os almoxarifados da fazenda
4. Valoração usa custo do método ativo (FIFO ou custo médio ponderado)
5. Saldo zerado mantém o produto visível; remoção apenas se inativo e sem movimentação
6. Consulta por data: recalcula saldo até a data informada (posição histórica)
7. Curva ABC calculada pelo valor total em estoque (A=80%, B=15%, C=5%)

## Entidades de Dados Principais

- **SaldoEstoque:** id, tenant_id, produto_id, almoxarifado_id, quantidade, custo_unitario_medio, valor_total, ultima_movimentacao_data, updated_at
- **SnapshotEstoque:** id, tenant_id, fazenda_id, data, produto_id, almoxarifado_id, quantidade, valor_total (para consultas históricas)

## Integrações Necessárias

- **Movimentações:** Fonte dos dados de saldo
- **Cadastro de Produtos:** Dados do produto e unidade de medida
- **FIFO/Custo (Profissional):** Método de custeio para valoração
- **Estoque Mínimo (Profissional):** Comparação saldo vs. ponto de reposição
- **Financeiro:** Valoração para balanço patrimonial

## Fluxo de Uso Principal (step-by-step)

1. Acessar Estoque > Saldo
2. Selecionar visão: por produto, por almoxarifado ou consolidada
3. Aplicar filtros: categoria, almoxarifado, status, data
4. Visualizar tabela de saldos com quantidade e valor
5. Clicar em produto para ver histórico de movimentações
6. Exportar relatório de posição de estoque (PDF/Excel)
7. Consultar curva ABC para priorização de gestão

## Casos Extremos e Exceções

- **Saldo negativo (se permitido):** Exibir em vermelho com alerta de regularização
- **Produto sem movimentação há >90 dias:** Marcar como "sem giro" para revisão
- **Consulta em data passada:** Recalcular a partir do snapshot ou das movimentações
- **Almoxarifado desativado:** Saldo congelado; exibir com flag de inativo
- **Divergência entre saldo calculado e inventário:** Apontar diferença para ajuste

## Critérios de Aceite (Definition of Done)

- [ ] Consulta de saldo por produto e almoxarifado
- [ ] Visão consolidada por fazenda
- [ ] Valoração com custo unitário
- [ ] Histórico de movimentações por produto
- [ ] Filtros por categoria, almoxarifado, data
- [ ] Exportação PDF/Excel
- [ ] Isolamento multi-tenant

## Sugestões de Melhoria Futura

- Dashboard visual com gráficos de composição e evolução do estoque
- Previsão de ruptura baseada em tendência de consumo
- Comparativo de estoque entre fazendas do grupo
- Alerta inteligente de produtos com alta variação de preço
- Integração com BI externo via API
