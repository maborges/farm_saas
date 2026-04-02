---
modulo: "Agr\xEDcola"
submodulo: "Custos de Produ\xE7\xE3o"
nivel: profissional
core: false
dependencias_core:
  - core/auth
  - core/cadastros/fazendas
  - core/cadastros/produtos
  - core/tenant
dependencias_modulos:
  - ../essencial/safras.md
  - ../essencial/operacoes-campo.md
  - ../../financeiro/despesas.md
  - ../../operacional/estoque.md
standalone: false
complexidade: L
assinante_alvo:
  - medio-produtor
  - grande-produtor
  - cooperativa
---

# Custos de Producao

## Descricao Funcional

O submodulo de Custos de Producao consolida todos os gastos associados a uma safra e distribui por talhao, permitindo calcular o custo por hectare e o custo por unidade produzida (saca, kg, tonelada). Ele agrega dados de operacoes (insumos, maquinario, mao de obra), despesas financeiras e rateios de custos indiretos.

Este submodulo e critico para a tomada de decisao: o produtor precisa saber se esta tendo lucro ou prejuizo em cada talhao, e quais categorias de custo estao acima do esperado.

Funcionalidades principais:
- Dashboard de custos por safra com totais e breakdown por categoria
- Custo por hectare e custo por saca/kg por talhao
- Comparativo de custo entre talhoes da mesma safra
- Comparativo de custo entre safras (historico)
- Rateio de custos indiretos (administracao, arrendamento, depreciacao) por area
- Orcamento previsto vs custo realizado (requer plano Profissional/Planejamento)
- Graficos de evolucao de custo ao longo da safra
- KPIs financeiros: custo total, custo/ha, custo/saca, margem bruta

## Personas — Quem usa este submodulo

- **Produtor/Proprietario:** precisa saber se a safra deu lucro e onde pode economizar
- **Gerente de Fazenda:** monitora custos por talhao para identificar ineficiencias
- **Controller/Financeiro:** consolida custos para contabilidade e relatorios gerenciais
- **Agronomo:** avalia custo-beneficio de diferentes manejos e dosagens

## Dores que resolve

1. **Custo desconhecido:** produtor nao sabe o custo real de producao de uma saca de soja
2. **Decisao no escuro:** sem dados de custo por talhao, nao sabe quais areas sao rentaveis
3. **Rateio manual:** custos indiretos (arrendamento, depreciacao) sao rateados em planilhas com erros
4. **Comparativo impossivel:** sem dados historicos estruturados, nao consegue comparar custo entre safras
5. **Orcamento estourado:** descobre que gastou mais do que planejou apenas no final da safra

## Regras de Negocio

1. Custos diretos sao capturados automaticamente das operacoes concluidas (insumos + maquinario + mao de obra)
2. Custos indiretos podem ser lancados manualmente ou importados do modulo financeiro
3. O rateio de custos indiretos e feito por area (ha) por padrao — outros criterios (receita, producao) sao configuraveis
4. O custo por saca/kg so e calculado apos registro de producao (romaneio de colheita)
5. A margem bruta e: `receita_venda - custo_total`
6. Custos sao categorizados: insumos (sementes, fertilizantes, defensivos), maquinario, mao_de_obra, servicos_terceiros, custos_indiretos, outros
7. Nao e permitido editar custos de safras encerradas sem permissao de admin
8. O sistema deve manter rastreabilidade: cada custo aponta para a operacao, despesa ou rateio de origem
9. Moeda e BRL por padrao; valores em dolares usam cotacao do dia do lancamento
10. Permissoes: `agricola:custos:read`, `agricola:custos:create`, `agricola:custos:configure`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `CustoSafra` | id, tenant_id, safra_id, talhao_id, categoria, subcategoria, valor, data_lancamento, origem_tipo, origem_id | vinculado a safra/talhao |
| `RateioIndireto` | id, tenant_id, safra_id, descricao, valor_total, criterio_rateio, data_referencia | custo rateado entre talhoes |
| `RateioDistribuicao` | id, rateio_id, talhao_id, percentual, valor_rateado | distribuicao do rateio |
| `CustoResumoSafra` | view materializada: safra_id, talhao_id, custo_total, custo_ha, custo_saca, producao_total, receita, margem_bruta | resumo calculado |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `agricola/operacoes` | Leitura | Custos de insumos, maquinario e mao de obra por operacao |
| `agricola/safras` | Leitura | Area por talhao e dados da safra |
| `agricola/romaneios` | Leitura | Producao total para calculo de custo/saca |
| `financeiro/despesas` | Leitura | Despesas vinculadas a safra |
| `financeiro/receitas` | Leitura | Receitas de venda para calculo de margem |
| `agricola/planejamento` | Leitura | Orcamento previsto para comparativo |
| `operacional/estoque` | Leitura | Custo medio de insumos (FIFO) |

## Fluxo de Uso Principal (step-by-step)

1. Usuario acessa `/agricola/custos` ou `/agricola/safras/[id]/financeiro`
2. Seleciona a safra e visualiza dashboard com KPIs: custo total, custo/ha, margem bruta
3. Visualiza breakdown por categoria em grafico de pizza ou barras
4. Navega para detalhamento por talhao — compara custo/ha entre talhoes
5. Identifica que talhao X tem custo de defensivos 40% acima da media
6. Clica para ver operacoes de pulverizacao desse talhao — identifica aplicacao extra por praga
7. Acessa comparativo historico: custo da safra atual vs safra anterior
8. Se plano Profissional, visualiza orcamento previsto vs realizado com variancia
9. Lanca custo indireto (ex: arrendamento anual) e configura rateio por area
10. Sistema distribui automaticamente entre talhoes proporcionalmente a area
11. Exporta relatorio de custos para analise gerencial ou financiamento bancario

## Casos Extremos e Excecoes

- **Safra sem producao:** perda total — custo/saca e indefinido (exibir "N/A", nao dividir por zero)
- **Custo negativo:** devolucao de insumo — registrar como custo negativo na categoria correspondente
- **Cambio:** insumos comprados em dolar — converter na data do lancamento e registrar cotacao usada
- **Rateio circular:** custo indireto que depende de producao que ainda nao foi colhida — permitir rateio provisorio com recalculo posterior
- **Talhao adicionado mid-safra:** novo talhao entra na safra apos inicio — ratear custos indiretos apenas a partir da data de inclusao
- **Multiplas culturas no talhao:** consorcio soja+milho — permitir alocacao percentual de custo por cultura
- **Custo retroativo:** despesa descoberta apos encerramento — permitir lancamento com flag `retroativo` e justificativa

## Criterios de Aceite (Definition of Done)

- [ ] Agregacao automatica de custos de operacoes (insumos + maquinario + mao de obra)
- [ ] Dashboard com KPIs: custo total, custo/ha, custo/saca, margem bruta
- [ ] Breakdown por categoria com graficos
- [ ] Comparativo entre talhoes (custo/ha)
- [ ] Comparativo historico entre safras
- [ ] Rateio de custos indiretos por area com distribuicao automatica
- [ ] Orcamento previsto vs realizado (quando planejamento disponivel)
- [ ] Rastreabilidade de origem de cada custo (operacao, despesa, rateio)
- [ ] Exportacao de relatorio de custos
- [ ] Tenant isolation e RBAC testados
- [ ] Tratamento de divisao por zero quando producao = 0

## Sugestoes de Melhoria Futura

1. **Custeio ABC:** alocar custos por atividade em vez de apenas por area
2. **Benchmark cooperativa:** comparar custo/saca com media da cooperativa (anonimizado)
3. **Projecao de custo:** com base no consumo parcial, projetar custo total ao fim da safra
4. **Integracao bancaria:** exportar dados no formato exigido por bancos para comprovacao de custeio
5. **Dashboard multi-safra:** visao consolidada de todas as safras ativas com ranking de rentabilidade
6. **Alertas de desvio:** notificar quando custo realizado ultrapassa X% do orcamento
7. **Custo ambiental:** incluir metricas de pegada de carbono por talhao/safra
