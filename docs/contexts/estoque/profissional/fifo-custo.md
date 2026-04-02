---
modulo: Estoque
submodulo: FIFO e Custo
nivel: profissional
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-produtos.md
  - ../essencial/movimentacoes.md
  - ../essencial/saldo-consulta.md
standalone: false
complexidade: L
assinante_alvo:
  - financeiro
  - gestor-rural
  - contador
---

# FIFO e Custo

## Descrição Funcional

Submódulo de custeio de estoque implementando os métodos FIFO (First In, First Out — Primeiro a Entrar, Primeiro a Sair) e Custo Médio Ponderado. Rastreia o custo de cada unidade em estoque com base na ordem de entrada, calcula o custo de saída conforme o método ativo e mantém histórico completo de custos para auditoria. Essencial para valoração precisa do estoque e cálculo correto do custo de produção.

## Personas — Quem usa este submódulo

- **Financeiro / Controller:** valoração de estoque, custo de produção, conciliação contábil
- **Contador:** relatórios fiscais com custeio correto
- **Gerente:** análise de custo de insumos por operação
- **Comprador:** avaliação de impacto de preço de compra no custo médio

## Dores que resolve

- Custo de insumos calculado de forma errada distorcendo custo de produção
- Valoração de estoque incorreta no balanço patrimonial
- Impossibilidade de auditar custo de saídas passadas
- FIFO manual em planilha com alta chance de erro
- Custo médio não atualizado após cada entrada

## Regras de Negócio

1. FIFO: saída consome primeiro as unidades mais antigas (menor custo de entrada mais antigo)
2. Custo Médio Ponderado: custo recalculado a cada entrada = (saldo_valor + entrada_valor) / (saldo_qtd + entrada_qtd)
3. Método configurável por tenant; troca de método exige reprocessamento
4. Cada entrada cria um "lote de custo" com quantidade e custo unitário
5. Saída FIFO consome lotes em ordem cronológica; lote parcialmente consumido mantém saldo residual
6. Estorno de saída devolve unidades ao lote original com custo original
7. Relatório de custo por período mostra custo médio de saída e variação
8. Auditoria de custo: trilha completa de entrada > alocação > saída por lote

## Entidades de Dados Principais

- **LoteCusto:** id, tenant_id, produto_id, almoxarifado_id, movimentacao_entrada_id, quantidade_original, quantidade_disponivel, custo_unitario, data_entrada
- **CustoSaida:** id, movimentacao_saida_id, lote_custo_id, quantidade_consumida, custo_unitario
- **CustoMedioProduto:** id, tenant_id, produto_id, almoxarifado_id, custo_medio_atual, ultima_atualizacao
- **ConfiguracaoCusteio:** id, tenant_id, metodo (FIFO|CUSTO_MEDIO), data_ativacao

## Integrações Necessárias

- **Movimentações:** Entradas alimentam lotes de custo; saídas consomem
- **Saldo/Consulta:** Valoração de saldo com custo correto
- **Lotes/Validade (Profissional):** Lote de custo vinculado ao lote físico
- **Financeiro:** Custo de saída para cálculo de custo de produção
- **Fiscal (Enterprise):** Custo de entrada via NF-e

## Fluxo de Uso Principal (step-by-step)

1. Configurar método de custeio do tenant (FIFO ou Custo Médio)
2. Sistema cria lotes de custo automaticamente a cada entrada
3. A cada saída, sistema consome lotes conforme método (FIFO: mais antigo primeiro)
4. Consultar custo unitário de cada saída e custo médio do período
5. Visualizar lotes de custo em aberto (FIFO) com quantidade disponível
6. Gerar relatório de valoração de estoque por método
7. Auditar trilha de custo: entrada > lote > saída

## Casos Extremos e Exceções

- **Entrada com custo zero:** Permitir com alerta; não distorcer custo médio (excluir do cálculo)
- **Estorno de saída após novo consumo do lote:** Recalcular fila FIFO considerando devolução
- **Troca de método FIFO para Custo Médio:** Reprocessar todo o histórico; operação irreversível sem backup
- **Lote FIFO totalmente consumido:** Marcar como esgotado; manter para auditoria
- **Múltiplas entradas no mesmo dia com custos diferentes:** Cada entrada gera lote de custo separado
- **Saída de quantidade maior que lote mais antigo:** Consumir múltiplos lotes em sequência

## Critérios de Aceite (Definition of Done)

- [ ] Implementação de FIFO com lotes de custo
- [ ] Implementação de Custo Médio Ponderado
- [ ] Configuração de método por tenant
- [ ] Cálculo correto de custo de saída por ambos os métodos
- [ ] Trilha de auditoria de custo completa
- [ ] Relatório de valoração de estoque
- [ ] Testes com cenários de múltiplas entradas e saídas
- [ ] Isolamento multi-tenant

## Sugestões de Melhoria Futura

- Custo de reposição como terceiro método
- Simulação de impacto de troca de método
- Alerta de variação de custo acima de threshold
- Integração com ERP para conciliação contábil automática
- Dashboard de evolução de custo médio por produto ao longo do tempo
