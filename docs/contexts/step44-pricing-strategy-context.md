# Step 44 - Pricing e Estrutura Comercial dos Planos Agrícolas

## Objetivo

Transformar a monetização técnica do módulo Agricultura em planos comerciais claros, vendáveis e fáceis de explicar para produtor rural, cooperativa e empresa agrícola.

## Diretriz comercial

- `A1_PLANEJAMENTO` deve funcionar como porta de entrada acessível.
- `PROFISSIONAL` deve ser o plano principal de receita.
- `ENTERPRISE` deve ser venda assistida, com valor alto e escopo consultivo.
- Evitar multiplicação excessiva de planos, add-ons ou regras complexas.
- O pricing deve parecer uma escada de valor, não uma lista de features.

## Posicionamento comercial

- **A1 Planejamento**: entrada acessível para digitalizar a operação base e criar hábito de uso.
- **PROFISSIONAL**: plano de crescimento e principal motor de receita, voltado a ganho de decisão e produtividade.
- **ENTERPRISE**: plano de contrato e expansão, com implantação, suporte assistido e negociação comercial.

## Estrutura sugerida

| Plano | Preço mensal | Preço anual | Limites comerciais | Público principal | Posicionamento |
|---|---:|---:|---|---|---|
| A1 Planejamento | R$ 99/mês | R$ 990/ano | até 2 usuários, até 2 fazendas, leitura/registro base, caderno operacional, safra base, relatórios simples | produtor rural pequeno e médio | porta de entrada acessível |
| PROFISSIONAL | R$ 349/mês | R$ 3.490/ano | até 8 usuários, até 10 fazendas, cenários, comparativo, dashboard executivo, IA de solo, previsões, alertas, templates, NDVI, beneficiamento | produtor em expansão, cooperativa pequena/média | plano principal de receita |
| ENTERPRISE | a partir de R$ 1.250/mês | sob proposta | usuários e fazendas sob contrato, rastreabilidade, VRA, exportação/assinatura, multiunidade avançado, auditoria, integrações, suporte assistido | cooperativas grandes e grupos agrícolas | alto valor com venda assistida |

## Proposta de valor por plano

### A1 Planejamento

- Mantém a operação base ativa.
- Fazenda, safra, caderno e leitura operacional.
- Serve para reduzir fricção de entrada e converter uso em hábito.
- Ideal para quem quer começar sem overengineering.

### PROFISSIONAL

- Libera inteligência executiva para decidir melhor.
- Cenários econômicos, comparativo, dashboards avançados e automações.
- É onde o cliente percebe ganho de produtividade e passa a justificar upgrade.
- Deve ser o plano que melhor equilibra valor e recorrência.

### ENTERPRISE

- Fecha o ciclo com rastreabilidade, assinatura, VRA e fluxos multiunidade.
- Voltado a operações complexas, times maiores e contrato assistido.
- Deve ser tratado como solução sob proposta, não como cartão de preço simples.
- Indicado para cooperativas, grupos agrícolas e operações com compliance e auditoria.

## Estratégia de desconto anual

- A1 Planejamento: desconto anual sugerido na faixa de 15% a 20%.
- PROFISSIONAL: desconto anual sugerido na faixa de 15% a 20%.
- ENTERPRISE: desconto negociado caso a caso.
- Para ENTERPRISE, priorizar implantação, treinamento e onboarding como parte do valor, em vez de desconto agressivo.
- O desconto anual deve reduzir atrito de compra, não canibalizar o MRR.

## Regras de monetização

- Limites devem ser simples de entender: usuários, fazendas e escopo de módulo.
- A1 deve limitar crescimento sem parecer capado demais.
- PROFISSIONAL deve liberar o pacote de valor recorrente.
- ENTERPRISE deve remover atrito operacional e permitir contratação sob medida.
- Add-ons devem ser evitados no início; só incluir se houver necessidade real de monetização complementar.
- Se houver negociação com múltiplas fazendas, o contrato deve ser por tenant/CNPJ, não por recurso avulso.
- Feature gate continua sendo a fonte de verdade técnica; a tabela comercial só traduz a regra em linguagem de venda.

## Concorrência e ancoragem

- O mercado agro SaaS já trabalha com faixas baixas de entrada, plano intermediário como principal motor e enterprise consultivo.
- Referências públicas de mercado mostram planos de entrada na faixa de dezenas de dólares por mês e enterprise sob proposta.
- A lógica comercial recomendada aqui segue esse padrão: preço acessível de entrada, plano de valor mais forte no meio, contrato assistido no topo.

## Justificativa de pricing

- O A1 precisa ser baixo o suficiente para reduzir barreira de entrada.
- O PROFISSIONAL precisa concentrar a maior parte da receita porque entrega o salto de valor real: decisão, comparação e automação.
- O ENTERPRISE precisa justificar preço elevado com implantação, rastreabilidade, auditoria e suporte assistido.
- A escada é intencional: A1 vende adesão, PROFISSIONAL vende expansão e ENTERPRISE vende complexidade operacional.

## Critérios de decisão

- Se houver dúvida entre reduzir preço ou aumentar valor, priorizar clareza de valor.
- Se houver dúvida entre mais um plano ou simplificar, simplificar.
- Se houver dúvida entre desconto e serviço, preferir serviço no enterprise.

## Regra de manutenção

- Novas telas, CTAs e tabelas comerciais devem refletir esta estrutura.
- A documentação comercial deve usar os nomes canônicos: `A1 Planejamento`, `PROFISSIONAL`, `ENTERPRISE`.
- Não abrir novos tiers sem revisão de monetização completa.
