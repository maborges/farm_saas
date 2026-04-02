---
modulo: Estoque
submodulo: Movimentações
nivel: essencial
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ./cadastro-produtos.md
standalone: false
complexidade: M
assinante_alvo:
  - almoxarife
  - gestor-rural
  - operador-campo
---

# Movimentações

## Descrição Funcional

Submódulo de registro de todas as movimentações de estoque: entradas (compra, produção, devolução de campo), saídas (consumo em operação, perda, devolução a fornecedor) e transferências entre almoxarifados. Cada movimentação é atômica, imutável e rastreável, formando a base do controle de saldo e custeio do estoque.

Suporta movimentações individuais e em lote, com possibilidade de vincular a origem (nota fiscal, ordem de serviço, manejo).

## Personas — Quem usa este submódulo

- **Almoxarife:** registro diário de entradas e saídas, conferência
- **Operador de campo:** solicitação de saída de insumos para operação
- **Gerente:** aprovação de movimentações de alto valor, visão de fluxo
- **Financeiro:** conciliação de movimentações com notas fiscais

## Dores que resolve

- Saídas de insumos não registradas levando a divergência de saldo
- Falta de rastreabilidade de quem retirou o quê e quando
- Transferências entre almoxarifados sem controle gerando "sumiço" de material
- Impossibilidade de vincular consumo de insumos a operações específicas
- Estornos feitos por exclusão, perdendo histórico

## Regras de Negócio

1. Tipos de movimentação: ENTRADA, SAIDA, TRANSFERENCIA, ESTORNO
2. Movimentação é imutável após confirmação; correções via ESTORNO
3. Estorno gera movimentação inversa referenciando a original
4. Saldo não pode ficar negativo após saída (configurável)
5. Transferência gera duas movimentações: saída na origem + entrada no destino
6. Toda movimentação registra: produto, quantidade, almoxarifado, responsável, data, motivo
7. Movimentações podem ser vinculadas a documento de origem (NF, OS, manejo)
8. Data da movimentação não pode ser futura; retroativa permitida até 30 dias

## Entidades de Dados Principais

- **Movimentacao:** id, tenant_id, fazenda_id, tipo (ENTRADA|SAIDA|TRANSFERENCIA|ESTORNO), produto_id, almoxarifado_id, quantidade, unidade_medida_id, custo_unitario, motivo, documento_origem_tipo, documento_origem_id, responsavel_id, data, estorno_de_id, created_at
- **Almoxarifado:** id, tenant_id, fazenda_id, nome, tipo (central|campo|oficina), status
- **MovimentacaoItem:** id, movimentacao_id, lote_produto_id, quantidade, custo_unitario (para movimentações com múltiplos lotes)

## Integrações Necessárias

- **Cadastro de Produtos:** Produtos como itens das movimentações
- **Saldo/Consulta:** Atualização de saldo em tempo real
- **Pecuária:** Baixa de insumos em manejos (vacinas, medicamentos)
- **Agrícola:** Baixa de insumos em operações (defensivos, fertilizantes)
- **Frota:** Baixa de combustível e peças
- **Financeiro:** Custo das entradas para contas a pagar

## Fluxo de Uso Principal (step-by-step)

1. Acessar Estoque > Movimentações > Nova Movimentação
2. Selecionar tipo: Entrada, Saída ou Transferência
3. Selecionar almoxarifado (e destino, se transferência)
4. Adicionar produtos com quantidade e, para entradas, custo unitário
5. Informar motivo e documento de origem (opcional)
6. Confirmar movimentação; sistema atualiza saldos
7. Para estorno: localizar movimentação original e confirmar estorno com justificativa
8. Consultar histórico de movimentações com filtros

## Casos Extremos e Exceções

- **Saída maior que saldo:** Bloquear (padrão) ou permitir com alerta (configurável)
- **Estorno de movimentação já estornada:** Bloquear; movimentação só pode ser estornada uma vez
- **Transferência com almoxarifado destino de outra fazenda:** Gerar duas movimentações com flag inter-fazenda
- **Movimentação retroativa que inverte saldo em data passada:** Recalcular saldos históricos
- **Produto com unidade diferente da principal:** Converter automaticamente usando fator cadastrado
- **Movimentação em lote (múltiplos produtos):** Atômica; se um item falhar, nenhum é processado

## Critérios de Aceite (Definition of Done)

- [ ] Registro de entradas, saídas e transferências
- [ ] Estorno com rastreabilidade da movimentação original
- [ ] Atualização de saldo em tempo real
- [ ] Vínculo com documento de origem (NF, OS, manejo)
- [ ] Validação de saldo negativo (configurável)
- [ ] Histórico com filtros por tipo, produto, período, responsável
- [ ] Isolamento multi-tenant e testes

## Sugestões de Melhoria Futura

- Movimentação via leitura de código de barras
- Aprovação workflow para saídas acima de valor configurável
- Movimentação recorrente programada (ex.: saída diária de ração)
- Integração com balança para entrada por peso
- Notificação push para almoxarife ao receber transferência
