---
modulo: Financeiro
submodulo: Contas a Pagar e Receber
nivel: profissional
core: false
dependencias_core:
  - categorias-contas
  - lancamentos-basicos
dependencias_modulos: []
standalone: true
complexidade: M
assinante_alvo:
  - médio produtor rural
  - administrador de fazenda
  - gestor financeiro rural
---

# Contas a Pagar e Receber

## Descrição Funcional

Submódulo que gerencia obrigações financeiras futuras da propriedade rural — contas a pagar (fornecedores, parcelas, financiamentos) e contas a receber (vendas a prazo, contratos de entrega futura). Permite controle de vencimentos, parcelamento automático, baixas parciais ou totais, e geração de alertas de inadimplência.

Diferente dos lançamentos básicos que registram o que já aconteceu, este submódulo foca no que está por vir, dando previsibilidade financeira ao produtor.

## Personas — Quem usa este submódulo

- **Gestor Financeiro:** controla vencimentos diariamente; prioriza pagamentos; negocia prazos com fornecedores.
- **Administrador da Fazenda:** registra compras a prazo de insumos; acompanha recebíveis de vendas.
- **Produtor Rural (owner):** visualiza compromissos futuros para tomar decisões de investimento.
- **Assistente financeiro:** realiza as baixas diárias; envia cobranças de recebíveis atrasados.

## Dores que resolve

1. **Vencimentos esquecidos:** multas e juros por pagamentos atrasados que poderiam ser evitados.
2. **Sem visão de compromissos futuros:** produtor não sabe quanto vai precisar nos próximos meses.
3. **Parcelas descontroladas:** compras parceladas perdidas em anotações avulsas.
4. **Clientes inadimplentes:** falta de controle de recebíveis impede cobrança efetiva.
5. **Fluxo de caixa impreciso:** sem contas a pagar/receber, projeção financeira é incompleta.

## Regras de Negócio

1. Toda conta (pagar/receber) pertence a um `tenant_id` e `fazenda_id`.
2. Tipos: `PAGAR` ou `RECEBER`.
3. Uma conta pode ter múltiplas parcelas (`ContaParcela`).
4. Ao criar conta com parcelamento, o sistema gera automaticamente as parcelas com vencimentos calculados.
5. Cada parcela pode ser baixada independentemente (baixa parcial ou total).
6. Baixa de parcela gera automaticamente um lançamento efetivado no submódulo de Lançamentos Básicos.
7. Status da conta: `ABERTA`, `PARCIALMENTE_PAGA`, `QUITADA`, `CANCELADA`, `VENCIDA`.
8. Status é calculado automaticamente com base no estado das parcelas.
9. Parcelas vencidas há mais de 1 dia são automaticamente marcadas como `VENCIDA`.
10. Juros e multas por atraso podem ser informados manualmente na baixa (não calculados automaticamente na v1).
11. Vinculação opcional a um fornecedor/cliente (`pessoa_id`).
12. Alertas de vencimento: 7 dias antes, no dia, e 1 dia após o vencimento.

## Entidades de Dados Principais

### ContaPagarReceber
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| fazenda_id | UUID | sim | FK → Fazenda |
| tipo | ENUM(PAGAR, RECEBER) | sim | Tipo da conta |
| pessoa_id | UUID | não | FK → Pessoa (fornecedor/cliente) |
| categoria_id | UUID | sim | FK → Categoria |
| descricao | VARCHAR(255) | sim | Descrição da conta |
| valor_total_centavos | INTEGER | sim | Valor total em centavos |
| num_parcelas | INTEGER | sim | Número de parcelas (min: 1) |
| data_emissao | DATE | sim | Data de emissão/criação |
| status | ENUM(ABERTA, PARCIALMENTE_PAGA, QUITADA, CANCELADA, VENCIDA) | sim | Status calculado |
| observacao | TEXT | não | Observação |
| documento_referencia | VARCHAR(100) | não | NF, contrato, etc. |

### ContaParcela
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| conta_id | UUID | sim | FK → ContaPagarReceber |
| numero_parcela | INTEGER | sim | Sequência (1, 2, 3...) |
| valor_centavos | INTEGER | sim | Valor da parcela |
| data_vencimento | DATE | sim | Data de vencimento |
| data_pagamento | DATE | não | Data do efetivo pagamento |
| valor_pago_centavos | INTEGER | não | Valor efetivamente pago |
| juros_centavos | INTEGER | não | Juros/multa aplicados |
| desconto_centavos | INTEGER | não | Desconto concedido |
| status | ENUM(PENDENTE, PAGA, VENCIDA, CANCELADA) | sim | Status da parcela |
| lancamento_id | UUID | não | FK → Lancamento (gerado na baixa) |

## Integrações Necessárias

- **Lançamentos Básicos (essencial):** baixa de parcela gera lançamento efetivado automaticamente.
- **Categorias e Contas (essencial):** categorias classificam a conta; conta financeira recebe a baixa.
- **Fluxo de Caixa (essencial):** parcelas pendentes alimentam a projeção do fluxo.
- **Centro de Custo (profissional):** contas a pagar podem ser rateadas entre centros de custo.
- **Conciliação Bancária (profissional):** baixas devem ser conciliadas com o extrato bancário.
- **Estoque (operacional):** compra de insumos a prazo gera conta a pagar automaticamente.

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa "Contas a Pagar" ou "Contas a Receber" no menu Financeiro.
2. Clica em "Nova Conta".
3. Seleciona tipo, informa descrição, valor total, categoria e fornecedor/cliente.
4. Define número de parcelas e data do primeiro vencimento.
5. Sistema calcula automaticamente os vencimentos das parcelas (mensal por padrão).
6. Usuário revisa e ajusta valores/datas de parcelas individuais se necessário.
7. Salva a conta; parcelas aparecem na listagem com status "Pendente".
8. No dia do pagamento, usuário seleciona a parcela e clica em "Baixar".
9. Informa a conta financeira, valor efetivamente pago (pode diferir por juros/desconto), e data.
10. Sistema gera lançamento efetivado automaticamente e atualiza o status da conta.

## Casos Extremos e Exceções

- **Baixa parcial:** valor pago menor que o valor da parcela; parcela permanece como "Pendente" com saldo restante.
- **Pagamento com juros:** valor pago > valor original; diferença registrada como `juros_centavos`.
- **Pagamento com desconto:** valor pago < valor original com desconto informado; registrado em `desconto_centavos`.
- **Cancelamento de conta com parcelas pagas:** parcelas já pagas mantêm lançamentos; parcelas pendentes são canceladas.
- **Estorno de baixa:** reverte o lançamento gerado e reabre a parcela; requer permissão de admin.
- **Parcela com vencimento em fim de semana/feriado:** sistema não ajusta automaticamente na v1; campo editável.
- **Conta sem parcelas pagas excluída:** exclusão lógica; restaurável.
- **Fornecedor/cliente removido:** conta mantém referência; exibe "(removido)" na interface.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de contas a pagar/receber com geração automática de parcelas.
- [ ] Baixa de parcela gerando lançamento efetivado automaticamente.
- [ ] Status da conta calculado automaticamente (ABERTA → PARCIALMENTE_PAGA → QUITADA).
- [ ] Marcação automática de parcelas vencidas.
- [ ] Filtros: tipo, status, período de vencimento, fornecedor/cliente, categoria.
- [ ] Dashboard com resumo: total a pagar, total a receber, vencidos.
- [ ] Baixa parcial funcional.
- [ ] Registro de juros e descontos na baixa.
- [ ] Tenant isolation em todos os endpoints.
- [ ] Testes: criação, parcelamento, baixa, estorno, status calculado, tenant isolation.

## Sugestões de Melhoria Futura

- **Cálculo automático de juros/multa:** configurar taxa de juros e multa por atraso por fornecedor.
- **Boleto e Pix integrado:** gerar boletos e QR codes Pix para contas a receber.
- **Régua de cobrança:** envio automático de lembretes por e-mail/WhatsApp antes e após vencimento.
- **Aprovação de pagamentos:** workflow de aprovação para pagamentos acima de determinado valor.
- **Antecipação de recebíveis:** integração com plataformas de antecipação para antecipar recebíveis de venda.
- **Renegociação:** permitir renegociar dívidas, gerando novas parcelas e mantendo histórico.
