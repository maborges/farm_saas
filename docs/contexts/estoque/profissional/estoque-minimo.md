---
modulo: Estoque
submodulo: Estoque Mínimo
nivel: profissional
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-produtos.md
  - ../essencial/saldo-consulta.md
standalone: false
complexidade: S
assinante_alvo:
  - almoxarife
  - comprador
  - gestor-rural
---

# Estoque Mínimo

## Descrição Funcional

Submódulo de controle de níveis mínimos e máximos de estoque com alertas automáticos e ponto de reposição. Para cada produto/almoxarifado, define-se estoque mínimo (segurança), ponto de reposição (quando comprar) e estoque máximo (limite de armazenamento). Quando o saldo atinge o ponto de reposição, o sistema gera alerta e, opcionalmente, requisição de compra automática.

## Personas — Quem usa este submódulo

- **Almoxarife:** recebe alertas de estoque baixo, monitora níveis
- **Comprador:** age sobre alertas, inicia processo de compra
- **Gerente:** configura parâmetros de reposição, monitora ruptura
- **Financeiro:** previsão de desembolso para reposição

## Dores que resolve

- Ruptura de estoque de insumos críticos paralisando operações
- Compras emergenciais com sobrepreço por falta de planejamento
- Excesso de estoque de itens com baixo giro, imobilizando capital
- Falta de visibilidade sobre quais itens estão próximos da ruptura
- Configuração de níveis mínimos inexistente ou desatualizada

## Regras de Negócio

1. Estoque mínimo: nível de segurança; abaixo = alerta crítico
2. Ponto de reposição: estoque mínimo + (consumo médio diário × lead time em dias)
3. Estoque máximo: limite de armazenamento; acima = alerta de excesso
4. Consumo médio diário calculado automaticamente com base nos últimos 90 dias (configurável)
5. Lead time configurável por produto/fornecedor
6. Alertas enviados por: notificação in-app, e-mail (configurável)
7. Classificação de criticidade: A (ruptura para operação), B (importante), C (substituível)
8. Alerta de estoque mínimo pode gerar requisição de compra automática (Enterprise)

## Entidades de Dados Principais

- **ParametroEstoque:** id, tenant_id, produto_id, almoxarifado_id, estoque_minimo, ponto_reposicao, estoque_maximo, lead_time_dias, criticidade (A|B|C)
- **AlertaEstoque:** id, tenant_id, produto_id, almoxarifado_id, tipo (minimo|reposicao|maximo), saldo_atual, parametro_valor, data_geracao, status (ativo|resolvido), resolvido_em
- **ConsumoMedio:** id, tenant_id, produto_id, periodo_dias, consumo_medio_diario, calculado_em

## Integrações Necessárias

- **Saldo/Consulta:** Saldo atual para comparação com parâmetros
- **Movimentações:** Consumo para cálculo de consumo médio
- **Compras Integradas (Enterprise):** Geração automática de requisição
- **Notificações (Core):** Envio de alertas por e-mail e in-app

## Fluxo de Uso Principal (step-by-step)

1. Acessar Estoque > Configurações > Estoque Mínimo
2. Configurar parâmetros por produto/almoxarifado (mínimo, reposição, máximo)
3. Sistema calcula consumo médio diário automaticamente
4. Sistema monitora saldos continuamente
5. Ao atingir ponto de reposição: gera alerta para comprador
6. Ao atingir estoque mínimo: gera alerta crítico
7. Comprador age sobre o alerta (compra manual ou requisição automática)
8. Ao receber mercadoria, alerta é resolvido automaticamente

## Casos Extremos e Exceções

- **Produto sem histórico de consumo:** Não calcular consumo médio; exigir configuração manual
- **Consumo sazonal (safra vs. entressafra):** Permitir configurar período de referência do cálculo
- **Múltiplos almoxarifados com parâmetros diferentes:** Cada par produto/almoxarifado tem seus próprios níveis
- **Alerta resolvido e reaberto:** Se saldo cai novamente abaixo, novo alerta é gerado
- **Lead time variável:** Usar maior lead time entre fornecedores como padrão de segurança
- **Produto com criticidade A sem estoque:** Alerta escalado para gerente e proprietário

## Critérios de Aceite (Definition of Done)

- [ ] Configuração de parâmetros por produto/almoxarifado
- [ ] Cálculo automático de consumo médio diário
- [ ] Geração automática de alertas (mínimo, reposição, máximo)
- [ ] Painel de alertas ativos com filtros
- [ ] Resolução automática de alerta ao receber mercadoria
- [ ] Classificação de criticidade (A, B, C)
- [ ] Isolamento multi-tenant e testes

## Sugestões de Melhoria Futura

- Cálculo de estoque de segurança com modelo estatístico (desvio padrão do consumo)
- Previsão de ruptura com base em tendência de consumo
- Sugestão automática de parâmetros baseada em histórico
- Dashboard de cobertura de estoque (dias de estoque por produto)
- Integração com fornecedores para lead time dinâmico
