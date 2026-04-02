---
modulo: Comercialização
submodulo: Hedge e Derivativos
nivel: enterprise
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../profissional/contratos-venda.md
  - ../profissional/cotacoes-mercado.md
  - ../../financeiro/essencial/receitas.md
  - ../../financeiro/essencial/despesas.md
standalone: false
complexidade: XL
assinante_alvo:
  - Grande produtor rural
  - Tradings agrícolas
  - Cooperativas com mesa de operações
  - Fundos de investimento agro
---

# Hedge e Derivativos

## Descrição Funcional

Gestão de operações de hedge em bolsa de commodities e derivativos agrícolas. Permite registrar e acompanhar posições em contratos futuros (B3, CBOT/CME), opções (calls e puts) e operações de basis trading. Calcula margem de garantia, resultado de posições (mark-to-market), e consolida a posição comercial total do produtor (físico + derivativos). Essencial para proteção de preço de grandes volumes de produção.

## Personas — Quem usa este submódulo

- **Produtor rural (grande porte):** Protege preço da produção via hedge em bolsa
- **Mesa de operações:** Executa e monitora operações em bolsa em tempo real
- **Gerente comercial:** Define estratégia de hedge e percentual da produção a proteger
- **Diretor financeiro/CFO:** Monitora exposição, margem e resultado consolidado
- **Consultor de commodities:** Recomenda estratégias e acompanha execução

## Dores que resolve

- Falta de visão consolidada: posição física (estoque + contratos) vs. posição em bolsa
- Risco de over-hedge ou under-hedge sem controle integrado
- Dificuldade de calcular resultado real da comercialização (preço final = físico + hedge)
- Chamadas de margem inesperadas por falta de acompanhamento
- Impossibilidade de avaliar eficácia da estratégia de hedge ao final da safra

## Regras de Negócio

1. Operações devem ser registradas com: bolsa, contrato, vencimento, quantidade (lotes), preço, tipo (compra/venda)
2. Posição líquida = lotes comprados - lotes vendidos por contrato/vencimento
3. Mark-to-market diário: resultado = (preço atual - preço entrada) x quantidade x multiplicador do contrato
4. Hedge ratio = volume em derivativos / volume de produção física — alerta se > 100% (over-hedge)
5. Margem de garantia = posição x margem por contrato (B3 publica diariamente)
6. Opções: prêmio pago/recebido, strike, vencimento, tipo (call/put), estado (ITM/ATM/OTM)
7. Resultado de opção no vencimento: max(0, spot - strike) para call; max(0, strike - spot) para put
8. Basis = preço local - preço futuro — monitorar variação de basis para operações de basis trading
9. Operação encerrada (zerada) deve registrar resultado realizado
10. Resultado total da comercialização = resultado físico + resultado derivativos

## Entidades de Dados Principais

- **OperacaoDerivativo:** id, fazenda_id, tenant_id, bolsa (B3/CBOT/CME), tipo_instrumento (futuro/opcao), contrato_codigo, vencimento, tipo_operacao (compra/venda), quantidade_lotes, preco_entrada, preco_atual, multiplicador, moeda, corretora, conta_corretora, data_operacao, data_encerramento, preco_saida, resultado_realizado, status (aberta/encerrada/exercida/expirada), observacoes, created_at, updated_at
- **OperacaoOpcao:** id, operacao_id, tipo_opcao (call/put), strike, premio, data_exercicio
- **PosicaoConsolidada:** id, fazenda_id, tenant_id, safra_id, produto_id, volume_fisico_total, volume_contratado, volume_hedge, hedge_ratio, resultado_fisico, resultado_derivativos, resultado_total, data_calculo
- **MargemGarantia:** id, tenant_id, corretora, data, margem_requerida, margem_depositada, saldo

## Integrações Necessárias

- **Cotações de Mercado (profissional):** preços atuais para mark-to-market
- **Contratos de Venda (profissional):** posição física contratada
- **Registro de Vendas (essencial):** vendas realizadas (posição executada)
- **Estoque (operacional):** posição física em estoque
- **Safras (agrícola):** produção estimada para cálculo de hedge ratio
- **Receitas/Despesas (financeiro):** resultado de operações, custos de corretagem e margem
- **Corretoras (externa):** importação de extratos de operações (via arquivo ou API)

## Fluxo de Uso Principal (step-by-step)

1. Gerente comercial define estratégia: proteger X% da safra a preço Y
2. Mesa de operações executa operação na corretora/bolsa
3. Acessa Comercialização > Hedge > Nova Operação
4. Registra: bolsa, contrato, vencimento, quantidade de lotes, preço, tipo (compra/venda)
5. Para opções: informa tipo (call/put), strike e prêmio
6. Sistema calcula posição consolidada (físico + derivativos)
7. Dashboard exibe hedge ratio e alerta se over/under-hedge
8. Diariamente, sistema atualiza preços (mark-to-market) e calcula resultado não-realizado
9. Quando operação é encerrada (zerada), registra preço de saída e resultado realizado
10. Para opções no vencimento: sistema calcula se exercida ou expirada
11. Ao final da safra, relatório consolida resultado total da comercialização
12. Resultado = preço médio obtido (vendas físicas) + resultado líquido de derivativos

## Casos Extremos e Exceções

- **Chamada de margem:** margem insuficiente — alerta urgente para depósito adicional
- **Over-hedge:** posição em bolsa maior que posição física — risco especulativo, alerta
- **Rolagem de posição:** encerrar vencimento próximo e abrir no seguinte — registrar como operações separadas
- **Exercício antecipado de opção americana:** opção exercida antes do vencimento
- **Opção expirada sem valor:** registrar perda do prêmio pago
- **Operação em bolsa estrangeira (CBOT):** câmbio adiciona camada de risco — registrar hedge cambial
- **Corretora diferente:** posições em múltiplas corretoras devem ser consolidadas
- **Ajuste diário B3:** débito/crédito diário de ajuste — registrar automaticamente

## Critérios de Aceite (Definition of Done)

- [ ] Registro de operações em futuros e opções
- [ ] Cálculo de posição líquida por contrato/vencimento
- [ ] Mark-to-market diário com resultado não-realizado
- [ ] Registro de encerramento com resultado realizado
- [ ] Cálculo de hedge ratio (derivativos vs. produção física)
- [ ] Alerta de over-hedge e under-hedge
- [ ] Dashboard de posição consolidada (físico + derivativos)
- [ ] Controle de margem de garantia
- [ ] Relatório de resultado total da comercialização por safra
- [ ] Isolamento por tenant e fazenda
- [ ] Testes de integração com cálculos financeiros

## Sugestões de Melhoria Futura

- Importação automática de extratos de corretoras (OFX/CSV)
- Integração com APIs de corretoras para execução de ordens
- Simulador de cenários (stress test: e se preço cair/subir X%?)
- Painel de risco consolidado com VaR (Value at Risk)
- Hedge cambial integrado (NDF/forward de dólar)
- Relatório de eficácia do hedge conforme normas contábeis (CPC 48/IFRS 9)
