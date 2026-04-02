---
modulo: Financeiro
submodulo: Crédito Rural
nivel: enterprise
core: false
dependencias_core:
  - categorias-contas
  - lancamentos-basicos
dependencias_modulos:
  - ../profissional/contas-pagar-receber.md
  - ../profissional/centro-custo.md
standalone: true
complexidade: L
assinante_alvo:
  - grande produtor rural
  - empresa agrícola
  - cooperativa
  - consultor de crédito rural
---

# Crédito Rural

## Descrição Funcional

Submódulo dedicado ao controle de contratos de crédito rural — custeio, investimento e comercialização — linhas de financiamento específicas do agronegócio brasileiro (Plano Safra, PRONAF, PRONAMP, BNDES, FCO, etc.). Permite ao produtor acompanhar contratos, parcelas, períodos de carência, taxas de juros subsidiadas, e garantir compliance com as exigências de prestação de contas aos agentes financeiros.

O crédito rural tem regras complexas (carência, taxa controlada vs. livre, indexadores, garantias) que não se encaixam em um módulo genérico de contas a pagar. Este submódulo trata essas particularidades.

## Personas — Quem usa este submódulo

- **Produtor Rural (owner):** acompanha seus contratos de financiamento; planeja safra com base no crédito disponível.
- **Gestor Financeiro:** controla vencimentos de parcelas de crédito; prepara prestação de contas ao banco.
- **Consultor de crédito rural:** auxilia o produtor na simulação e acompanhamento de contratos.
- **Contador rural:** fecha balanço incluindo dívidas de crédito rural no passivo.

## Dores que resolve

1. **Contratos em gaveta:** produtor perde prazos de carência e vencimentos por falta de controle digital.
2. **Prestação de contas ao banco:** exigência de comprovar aplicação do crédito é trabalhosa sem ferramenta.
3. **Juros desnecessários:** perder prazo de carência ou não aplicar recurso corretamente resulta em juros maiores.
4. **Planejamento de safra desconectado do financiamento:** sem visão integrada, produtor não sabe quanto de crédito tem disponível.
5. **Complexidade de linhas de crédito:** cada programa (PRONAF, PRONAMP, etc.) tem regras diferentes; difícil acompanhar.

## Regras de Negócio

1. Cada contrato pertence a um `tenant_id` e `fazenda_id`.
2. Linhas de crédito suportadas: `CUSTEIO`, `INVESTIMENTO`, `COMERCIALIZACAO`.
3. Programas cadastrados: PRONAF, PRONAMP, BNDES, FCO, FNE, FNO, Plano Safra (extensível).
4. Contrato possui: valor total, valor liberado, saldo devedor, taxa de juros, indexador.
5. Período de carência: durante a carência, não há amortização; pode haver pagamento de juros (conforme contrato).
6. Parcelas são geradas automaticamente com base nas condições do contrato (carência + amortização).
7. Cada liberação de recurso gera lançamento de receita (entrada do crédito na conta).
8. Cada pagamento de parcela gera lançamento de despesa (amortização + juros).
9. Garantias vinculadas ao contrato: penhor de safra, hipoteca, alienação fiduciária.
10. Prestação de contas: vincular lançamentos de despesa ao contrato para comprovar aplicação do recurso.
11. Alertas: vencimento de parcela (30, 15, 7 dias), fim de carência, prazo de prestação de contas.
12. Saldo devedor é recalculado a cada pagamento considerando juros e amortização.

## Entidades de Dados Principais

### ContratoCreditoRural
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| fazenda_id | UUID | sim | FK → Fazenda |
| numero_contrato | VARCHAR(50) | sim | Número do contrato no banco |
| banco | VARCHAR(100) | sim | Agente financeiro |
| linha_credito | ENUM(CUSTEIO, INVESTIMENTO, COMERCIALIZACAO) | sim | Linha de crédito |
| programa | VARCHAR(50) | não | Programa (PRONAF, PRONAMP, etc.) |
| valor_contratado_centavos | INTEGER | sim | Valor total contratado |
| valor_liberado_centavos | INTEGER | sim | Valor efetivamente liberado |
| saldo_devedor_centavos | INTEGER | sim | Saldo devedor atual |
| taxa_juros_anual | DECIMAL(6,4) | sim | Taxa de juros anual (%) |
| indexador | ENUM(PREFIXADO, IPCA, SELIC, IGP_M, TJLP) | não | Indexador |
| data_contratacao | DATE | sim | Data do contrato |
| data_primeiro_vencimento | DATE | sim | Data da primeira parcela |
| meses_carencia | INTEGER | sim | Meses de carência |
| num_parcelas | INTEGER | sim | Número de parcelas |
| status | ENUM(EM_CARENCIA, AMORTIZANDO, QUITADO, INADIMPLENTE, RENEGOCIADO) | sim | Status |
| safra_referencia | VARCHAR(10) | não | Safra de referência (ex.: "24/25") |

### CreditoRuralParcela
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| contrato_id | UUID | sim | FK → ContratoCreditoRural |
| numero_parcela | INTEGER | sim | Sequência |
| data_vencimento | DATE | sim | Vencimento |
| valor_amortizacao_centavos | INTEGER | sim | Valor de amortização |
| valor_juros_centavos | INTEGER | sim | Valor de juros |
| valor_total_centavos | INTEGER | sim | Total (amortização + juros) |
| data_pagamento | DATE | não | Data efetiva de pagamento |
| valor_pago_centavos | INTEGER | não | Valor pago |
| status | ENUM(PENDENTE, PAGA, VENCIDA, EM_CARENCIA) | sim | Status |
| lancamento_id | UUID | não | FK → Lancamento |

### CreditoRuralGarantia
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| contrato_id | UUID | sim | FK → ContratoCreditoRural |
| tipo | ENUM(PENHOR_SAFRA, HIPOTECA, ALIENACAO_FIDUCIARIA, AVAL, CPR) | sim | Tipo de garantia |
| descricao | VARCHAR(255) | sim | Descrição da garantia |
| valor_centavos | INTEGER | não | Valor estimado da garantia |

## Integrações Necessárias

- **Contas a Pagar/Receber (profissional):** parcelas de crédito rural aparecem como contas a pagar.
- **Lançamentos Básicos (essencial):** liberações e pagamentos geram lançamentos.
- **Centro de Custo (profissional):** crédito de custeio é vinculado à safra/talhão financiado.
- **Custo de Produção por Safra (enterprise):** juros de crédito rural compõem o custo financeiro da safra.
- **Módulo Agrícola:** safra de referência vincula o contrato ao ciclo produtivo.

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa "Crédito Rural" no menu Financeiro.
2. Clica em "Novo Contrato" e preenche dados do contrato (banco, linha, valor, taxa, carência, parcelas).
3. Sistema gera automaticamente o cronograma de parcelas (carência + amortização).
4. Usuário registra garantias vinculadas ao contrato.
5. Ao receber a liberação do recurso, registra no sistema; lançamento de receita é gerado.
6. Durante a carência, sistema exibe contagem regressiva e alerta de fim de carência.
7. Ao vencer parcela, sistema alerta; usuário registra pagamento (baixa).
8. Baixa gera lançamento de despesa separando amortização e juros.
9. Saldo devedor é recalculado automaticamente.
10. Para prestação de contas, usuário vincula lançamentos de despesa (insumos, operações) ao contrato.

## Casos Extremos e Exceções

- **Renegociação de contrato:** criar novo contrato vinculado ao anterior; manter histórico.
- **Liberação parcial:** valor liberado < valor contratado; parcelas recalculadas proporcionalmente.
- **Parcela paga com atraso:** registrar juros de mora manualmente (cálculo automático na v2).
- **Troca de indexador:** contratos com indexador variável precisam de atualização periódica da taxa.
- **Contrato com múltiplas fazendas:** permitir rateio do contrato entre fazendas via centro de custo.
- **Inadimplência:** parcela vencida > 30 dias altera status do contrato para INADIMPLENTE; alerta crítico.
- **Quitação antecipada:** permitir quitar contrato antes do prazo; recalcular desconto de juros.
- **Safra frustrada:** situação de emergência; contrato pode ser prorrogado — registrar como renegociação.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de contratos de crédito rural com geração automática de parcelas.
- [ ] Suporte a período de carência com status EM_CARENCIA.
- [ ] Registro de liberações com geração de lançamento de receita.
- [ ] Baixa de parcela com separação amortização/juros e geração de lançamento.
- [ ] Cálculo automático de saldo devedor.
- [ ] Cadastro de garantias vinculadas ao contrato.
- [ ] Vinculação de lançamentos ao contrato para prestação de contas.
- [ ] Alertas de vencimento e fim de carência.
- [ ] Dashboard com resumo: total contratado, saldo devedor, próximos vencimentos.
- [ ] Tenant isolation em todos os endpoints.
- [ ] Testes: criação, parcelas, carência, baixa, saldo devedor, tenant isolation.

## Sugestões de Melhoria Futura

- **Simulador de crédito:** simular diferentes cenários (taxa, prazo, carência) antes de contratar.
- **Integração com SICOR:** importar dados de contratos do Sistema de Operações do Crédito Rural do Banco Central.
- **Cálculo automático de juros de mora:** aplicar taxa de mora automaticamente em parcelas atrasadas.
- **CPR digital:** emissão de Cédula de Produto Rural digital vinculada ao contrato.
- **Relatório para banco:** gerar relatório de prestação de contas no formato exigido pelo agente financeiro.
- **Alerta de oportunidade:** notificar quando novas linhas de crédito com condições favoráveis estiverem disponíveis (Plano Safra).
