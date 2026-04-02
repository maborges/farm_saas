---
modulo: Estoque
submodulo: Overview
nivel: essencial
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos: []
standalone: true
complexidade: M
assinante_alvo:
  - gestor-rural
  - almoxarife
  - comprador
---

# Estoque — Visão Geral do Módulo

## Descrição Funcional

O módulo Estoque gerencia o controle de insumos, produtos e materiais utilizados nas operações da fazenda. Desde o cadastro básico de produtos e movimentações (entradas, saídas, transferências) até funcionalidades avançadas como FIFO, estoque mínimo com alertas, rastreabilidade de lotes com validade, compras integradas e integração fiscal com NF-e.

O nível Essencial cobre cadastro de produtos, movimentações e consulta de saldo. O Profissional adiciona FIFO/custo médio, estoque mínimo com alertas e rastreabilidade de lotes. O Enterprise entrega compras integradas (requisição-cotação-pedido), inventário automatizado e integração fiscal.

## Personas — Quem usa este submódulo

- **Almoxarife:** controle diário de entradas e saídas, organização do estoque
- **Gerente de Fazenda:** visão geral de saldos, aprovação de requisições
- **Comprador:** cotações, pedidos de compra, negociação com fornecedores
- **Financeiro:** custo de insumos, valoração de estoque, conciliação com NF-e
- **Operador de campo:** requisição de insumos para operações

## Dores que resolve

- Falta de controle de estoque levando a compras emergenciais com sobrepreço
- Produtos vencidos no almoxarifado por falta de controle de validade
- Custo real dos insumos desconhecido por falta de método de custeio
- Desvio e furto de insumos sem rastreabilidade
- Retrabalho na entrada de notas fiscais manual

## Regras de Negócio

1. Todo produto pertence a um tenant e pode estar em múltiplos almoxarifados
2. Movimentações são imutáveis; correções feitas via estorno
3. Saldo não pode ficar negativo (configurável por tenant)
4. Transferência entre almoxarifados gera saída na origem e entrada no destino
5. Custeio padrão: FIFO; alternativa: custo médio ponderado (configurável)

## Entidades de Dados Principais

- `Produto` — insumo ou material com unidade, categoria e dados fiscais
- `Almoxarifado` — local físico de armazenamento
- `Movimentacao` — entrada, saída ou transferência
- `LoteProduto` — lote com data de fabricação, validade e fornecedor
- `SaldoEstoque` — saldo atual por produto/almoxarifado

## Integrações Necessárias

- **Core:** Autenticação, Tenants, Fazendas
- **Pecuária:** Baixa de vacinas, medicamentos, ração
- **Agrícola:** Baixa de sementes, fertilizantes, defensivos
- **Frota:** Baixa de combustível, peças, lubrificantes
- **Financeiro:** Custo de insumos, contas a pagar
- **Fiscal:** NF-e de entrada, XML auto-import

## Fluxo de Uso Principal (step-by-step)

1. Cadastrar almoxarifados e categorias de produtos
2. Cadastrar produtos com unidade, categoria e dados fiscais
3. Registrar entradas (compra, produção, devolução)
4. Registrar saídas (consumo, perda, devolução a fornecedor)
5. Consultar saldos e movimentações por produto ou almoxarifado
6. Monitorar alertas de estoque mínimo e validade
7. Gerar relatórios de consumo e valoração de estoque

## Casos Extremos e Exceções

- Produto com múltiplas unidades de medida: conversão configurável
- Entrada sem nota fiscal: permitir com flag de regularização pendente
- Saldo negativo por erro de sequência: alerta e bloqueio configurável
- Almoxarifado desativado com saldo: bloquear desativação
- Transferência entre fazendas: gerar movimentações em ambas

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de Produto e Almoxarifado com isolamento tenant
- [ ] Movimentações de entrada, saída e transferência
- [ ] Consulta de saldo em tempo real
- [ ] Testes de isolamento multi-tenant
- [ ] API documentada no Swagger

## Sugestões de Melhoria Futura

- Leitor de código de barras para entrada e saída rápida
- App mobile para almoxarife com leitura offline
- Integração com e-commerce agrícola para compra direta
- Dashboard de consumo com previsão de reposição via ML
- Integração com cooperativas para pedido automático
