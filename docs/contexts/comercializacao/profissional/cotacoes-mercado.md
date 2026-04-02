---
modulo: Comercialização
submodulo: Cotações de Mercado
nivel: profissional
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../essencial/registro-vendas.md
  - ./contratos-venda.md
standalone: true
complexidade: M
assinante_alvo:
  - Médio produtor rural
  - Grande produtor rural
  - Cooperativas
  - Tradings agrícolas
---

# Cotações de Mercado

## Descrição Funcional

Consulta e acompanhamento de cotações de commodities agrícolas em tempo real e histórico. Integra com as principais bolsas e indicadores: CBOT (Chicago Board of Trade) para soja, milho e trigo; ESALQ/CEPEA (USP) para indicadores nacionais; B3 para contratos futuros brasileiros. Exibe preços de referência regionais, câmbio USD/BRL, e permite comparar preços de venda do produtor com o mercado. Fundamental para tomada de decisão na comercialização.

## Personas — Quem usa este submódulo

- **Produtor rural:** Consulta cotações para decidir melhor momento de vender
- **Gerente comercial:** Acompanha tendências de mercado para estratégia de comercialização
- **Consultor agrícola:** Analisa mercado para recomendar estratégias aos clientes
- **Financeiro:** Monitora câmbio e preços para projeções de receita

## Dores que resolve

- Necessidade de consultar múltiplos sites/apps para ver cotações
- Falta de histórico de preços para análise de tendência
- Dificuldade de comparar preço obtido na venda com referência de mercado
- Tomada de decisão comercial sem informação atualizada
- Impossibilidade de configurar alertas de preço para oportunidades

## Regras de Negócio

1. Cotações são atualizadas em intervalos configuráveis (mínimo 15 minutos — delay padrão de bolsa)
2. Fontes de dados: CBOT (via API), ESALQ/CEPEA (scraping/API), B3 (via API), câmbio BCB
3. Preços exibidos na moeda original e convertidos para BRL
4. Conversão de unidades automática (bushel -> saca 60kg, ton -> saca)
5. Cotação regional = cotação de referência + base (prêmio/desconto regional)
6. Histórico de cotações armazenado para gráficos e análise
7. Alertas de preço podem ser configurados por produto e praça
8. Dados de cotação são compartilhados entre tenants (não são dados proprietários)
9. Taxa de câmbio PTAX (BCB) é referência para conversão USD/BRL
10. Cache de cotações para evitar excesso de requisições às APIs externas

## Entidades de Dados Principais

- **Cotacao:** id, produto_id, fonte (CBOT/ESALQ/B3/REGIONAL), praca, data_referencia, preco, moeda, unidade, variacao_dia_percentual, created_at
- **CotacaoHistorico:** id, produto_id, fonte, praca, data, preco_abertura, preco_fechamento, preco_minimo, preco_maximo, volume
- **AlertaPreco:** id, tenant_id, usuario_id, produto_id, praca, tipo_alerta (acima/abaixo), preco_alvo, ativo, notificado_em
- **CotacaoCambio:** id, moeda_origem, moeda_destino, data, taxa_compra, taxa_venda, fonte

## Integrações Necessárias

- **CBOT/CME Group (externa):** cotações de commodities internacionais
- **ESALQ/CEPEA (externa):** indicadores nacionais de preços agropecuários
- **B3 (externa):** contratos futuros de soja, milho, boi gordo, café
- **Banco Central do Brasil (externa):** taxa de câmbio PTAX
- **Registro de Vendas (essencial):** comparação preço obtido vs. mercado
- **Contratos de Venda (profissional):** referência para fixação de preço
- **Hedge/Derivativos (enterprise):** cotações de contratos futuros operados

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa Comercialização > Cotações de Mercado
2. Dashboard exibe cotações atuais dos principais produtos (soja, milho, boi, café, leite)
3. Cada cotação mostra preço atual, variação do dia e mini-gráfico de tendência
4. Usuário seleciona um produto para ver detalhes
5. Tela de detalhes mostra gráfico histórico com seleção de período (7d, 30d, 90d, 1a, 5a)
6. Exibe cotações de múltiplas fontes lado a lado (CBOT, ESALQ, B3, regional)
7. Seção de câmbio mostra USD/BRL e conversão do preço para BRL/saca
8. Usuário pode configurar alerta de preço clicando no ícone de sino
9. Define preço alvo (acima ou abaixo) e meio de notificação (push/e-mail)
10. Quando cotação atinge o preço alvo, sistema dispara notificação
11. No registro de venda, preço de mercado do dia é exibido como referência

## Casos Extremos e Exceções

- **API fora do ar:** exibir última cotação disponível com indicação de horário e aviso
- **Mercado fechado (finais de semana/feriados):** exibir último fechamento com flag
- **Limite circuit breaker:** bolsa suspende negociação — exibir aviso
- **Câmbio oscilando muito:** múltiplas atualizações no dia — manter histórico intraday
- **Novo produto sem fonte de cotação:** permitir cadastro manual de preço regional
- **Diferença regional muito grande:** base (prêmio/desconto) varia por praça e frete
- **Horário de verão:** ajuste de fuso horário entre CBOT (Chicago) e B3 (São Paulo)

## Critérios de Aceite (Definition of Done)

- [ ] Dashboard de cotações com atualização periódica
- [ ] Integração com pelo menos 2 fontes (ESALQ + câmbio BCB como mínimo)
- [ ] Gráfico histórico de preços com seleção de período
- [ ] Conversão automática de moeda e unidade
- [ ] Alertas de preço configuráveis por usuário
- [ ] Cache de cotações com fallback para última disponível
- [ ] Exibição de variação diária (absoluta e percentual)
- [ ] Indicação clara de horário da última atualização
- [ ] Comparação preço de venda vs. mercado no registro de vendas
- [ ] Testes de integração com mocks das APIs externas

## Sugestões de Melhoria Futura

- Push notification no mobile quando alerta de preço dispara
- Análise técnica básica (médias móveis, suporte/resistência)
- Previsão de preço por machine learning (tendência de curto prazo)
- Mapa de preços regionais interativo (calor/frio por praça)
- Widget de cotações na home/dashboard principal
- Integração com WhatsApp para envio de resumo diário de cotações
