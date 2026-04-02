---
modulo: Estoque
submodulo: Compras Integradas
nivel: enterprise
core: false
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos:
  - ../essencial/cadastro-produtos.md
  - ../essencial/movimentacoes.md
  - ../profissional/estoque-minimo.md
  - ../../financeiro/profissional/contas-pagar-receber.md
standalone: false
complexidade: L
assinante_alvo: grandes operações, cooperativas
---

# Compras Integradas

## Descrição Funcional

Submódulo que digitaliza o ciclo completo de compras de insumos: da requisição interna (gerada manual ou automaticamente por estoque mínimo) até a cotação com fornecedores, aprovação, pedido de compra, recebimento e conferência. Integra-se com Estoque (entrada automática) e Financeiro (contas a pagar).

## Personas — Quem usa este submódulo

- **Gestor de Compras:** Cria cotações, compara fornecedores, emite pedidos
- **Almoxarife:** Recebe mercadoria e confere com pedido
- **Owner/Admin:** Aprova compras acima de alçada
- **Financeiro:** Acompanha pagamentos gerados pelas compras

## Dores que resolve

1. Compras sem cotação prévia resultam em preços maiores
2. Sem requisição formal, compras são feitas sem aprovação
3. Conferência no recebimento é manual — divergências passam despercebidas
4. Sem integração, entrada no estoque e lançamento financeiro são feitos separadamente

## Regras de Negócio

1. **RN-CI-001:** Requisição pode ser gerada manualmente ou automaticamente quando estoque atinge ponto de reposição
2. **RN-CI-002:** Cotação deve ter no mínimo 3 fornecedores para compras acima de valor configurável
3. **RN-CI-003:** Aprovação por alçada: até R$ X o gestor aprova, acima requer owner
4. **RN-CI-004:** Pedido de compra gera número sequencial por fazenda/ano
5. **RN-CI-005:** Recebimento parcial é permitido — sistema rastreia saldo pendente
6. **RN-CI-006:** Ao confirmar recebimento, sistema cria automaticamente: movimentação de entrada no estoque + lançamento de conta a pagar

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Requisicao` | id, fazenda_id, solicitante_id, status, urgencia, observacao | → Fazenda, → Usuario |
| `RequisicaoItem` | id, requisicao_id, produto_id, quantidade, unidade | → Requisicao, → Produto |
| `Cotacao` | id, requisicao_id, fornecedor_id, valor_total, validade, status | → Requisicao, → Fornecedor |
| `PedidoCompra` | id, fazenda_id, cotacao_id, numero, status, aprovado_por, data_prevista | → Fazenda, → Cotacao |
| `Recebimento` | id, pedido_id, data, conferente_id, observacao | → PedidoCompra |

## Integrações Necessárias

- **Estoque:** Entrada automática ao confirmar recebimento
- **Financeiro:** Lançamento de conta a pagar ao confirmar pedido/recebimento
- **Estoque Mínimo:** Geração automática de requisições
- **Notificações:** Alertas de aprovação pendente, pedidos em atraso

## Fluxo de Uso Principal (step-by-step)

1. Estoque mínimo atingido → sistema gera requisição automática (ou operador cria manual)
2. Gestor de compras abre cotação com fornecedores cadastrados
3. Fornecedores respondem (manual input) → gestor compara preços e condições
4. Gestor seleciona melhor cotação → submete para aprovação (se necessário)
5. Aprovação concedida → pedido de compra emitido com número sequencial
6. Fornecedor entrega → almoxarife registra recebimento e confere itens
7. Confirmação de recebimento → entrada no estoque + conta a pagar criadas automaticamente

## Casos Extremos e Exceções

- **Recebimento com quantidade divergente:** Sistema registra parcial e mantém saldo pendente no pedido
- **Cotação sem resposta de fornecedor:** Após prazo configurável, cotação expira com alerta ao gestor
- **Produto recebido diferente do pedido:** Almoxarife pode rejeitar item e registrar devolução
- **Compra emergencial (sem cotação):** Flag de urgência permite pular cotação com justificativa obrigatória

## Critérios de Aceite (Definition of Done)

- [ ] Fluxo completo: requisição → cotação → aprovação → pedido → recebimento
- [ ] Entrada automática no estoque ao confirmar recebimento
- [ ] Lançamento automático de conta a pagar
- [ ] Requisição automática por estoque mínimo
- [ ] Aprovação por alçada configurável
- [ ] Recebimento parcial com saldo pendente

## Sugestões de Melhoria Futura

1. Portal de fornecedores para responder cotações online
2. Integração com marketplaces de insumos (Orbia, AgroGalaxy)
3. Análise de histórico de preços por fornecedor/produto
