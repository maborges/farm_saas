---
modulo: "Agrícola"
submodulo: Custos de Produção
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

# Custos de Produção

## Descrição Funcional

O submódulo de Custos de Produção consolida todos os gastos associados a uma safra e distribui por talhão, permitindo calcular o custo por hectare e o custo por unidade produzida (saca, kg, tonelada). Ele agrega dados de operações (insumos, maquinário, mão de obra), despesas financeiras e rateios de custos indiretos.

Este submódulo é crítico para a tomada de decisão: o produtor precisa saber se está tendo lucro ou prejuízo em cada talhão, e quais categorias de custo estão acima do esperado.

### Contexto Brasileiro

#### Estrutura de Custos da Agricultura Brasileira

A estrutura de custos típica para soja no Cerrado brasileiro (dados CONAB 2024):

| Categoria | % do Custo Total | Principais Itens |
|-----------|-----------------|------------------|
| Insumos | 55-65% | Sementes, fertilizantes (NPK), defensivos |
| Operações Agrícolas | 15-20% | Preparo de solo, plantio, pulverizações, colheita |
| Mão de Obra | 8-12% | Salários, encargos, terceirizados |
| Custos Indiretos | 10-15% | Arrendamento, depreciação, administração, energia |
| Outros | 3-5% | Seguro, assistência técnica, frete |

#### Custo por Saca — Indicador Crítico

O **custo por saca** (R$/sc de 60kg para soja/milho) é o principal indicador de competitividade:

- **MT (Sorriso, Lucas do Rio Verde)**: R$ 45-55/sc — menor custo do Brasil
- **GO/BA (MATOPIBA)**: R$ 50-60/sc — custo médio
- **PR/RS**: R$ 55-70/sc — custo mais elevado

Se o preço de mercado da soja está R$ 120/sc e seu custo é R$ 55/sc, você tem margem de R$ 65/sc.

#### Custeio via FIFO do Estoque

No Brasil, o custo de insumos deve seguir critérios contábeis:
- **FIFO (PEPS)**: Primeiro que entra é o primeiro que sai — lote mais antigo é consumido primeiro
- **Custo Médio**: Alternativa permitida, mas menos precisa para rastreabilidade
- O sistema usa FIFO por padrão, alinhado com normas contábeis (CPC 16)

#### Ponto de Equilíbrio (Break-even)

O **ponto de equilíbrio** em sacas/hectare indica quantas sacas o produtor precisa produzir para cobrir custos:

```
Ponto de Equilíbrio (sc/ha) = Custo Total (R$/ha) ÷ Preço de Venda (R$/sc)
```

Se custo é R$ 3.300/ha e soja está R$ 120/sc:
- Ponto de equilíbrio: 27,5 sc/ha
- Se produtividade esperada é 55 sc/ha → margem de segurança de 100%

Funcionalidades principais:
- Dashboard de custos por safra com totais e breakdown por categoria
- Custo por hectare e custo por saca/kg por talhão
- Comparativo de custo entre talhões da mesma safra
- Comparativo de custo entre safras (histórico)
- Rateio de custos indiretos (administração, arrendamento, depreciação) por área
- Orçamento previsto vs custo realizado (requer plano Profissional/Planejamento)
- Gráficos de evolução de custo ao longo da safra
- KPIs financeiros: custo total, custo/ha, custo/saca, margem bruta
- Ponto de equilíbrio (break-even) em sc/ha
- Exportação para contador (DRE rural)

## Personas — Quem usa este submódulo

- **Produtor/Proprietário**: Precisa saber se a safra deu lucro e onde pode economizar. Usa custo/saca para negociar venda com trading.

- **Gerente de Fazenda**: Monitora custos por talhão para identificar ineficiências. Talhão com custo de defensivos 40% acima da média precisa de investigação.

- **Controller/Financeiro**: Consolida custos para contabilidade e relatórios gerenciais. Prepara DRE (Demonstração de Resultado do Exercício) para banco.

- **Agrônomo**: Avalia custo-benefício de diferentes manejos e dosagens. Compara custo de aplicação de fungicida vs ganho de produtividade.

- **Cooperativa**: Compara custo de associados para identificar oportunidades de redução (compra consolidada de insumos).

## Dores que resolve

1. **Custo desconhecido**: Produtor não sabe o custo real de produção de uma saca de soja. Vende a R$ 120/sc achando que tem lucro, mas custo é R$ 125/sc.

2. **Decisão no escuro**: Sem dados de custo por talhão, não sabe quais áreas são rentáveis. Talhão com solo fértil pode ter custo menor e ser mais lucrativo.

3. **Rateio manual**: Custos indiretos (arrendamento, depreciação) são rateados em planilhas com erros. Rateio incorreto distorce custo por talhão.

4. **Comparativo impossível**: Sem dados históricos estruturados, não consegue comparar custo entre safras. Safra atual está mais cara ou mais barata?

5. **Orçamento estourado**: Descobre que gastou mais do que planejou apenas no final da safra. Tarde demais para corrigir.

6. **Financiamento bancário**: Banco exige DRE e custo de produção para renovar crédito. Produtor não consegue comprovar viabilidade.

7. **Venda de safra**: Trading pergunta "qual seu custo de produção?" para definir preço. Produtor sem dado fica em desvantagem na negociação.

## Regras de Negócio

1. Custos diretos são capturados automaticamente das operações concluídas (insumos + maquinário + mão de obra)
2. Custos indiretos podem ser lançados manualmente ou importados do módulo financeiro
3. O rateio de custos indiretos é feito por área (ha) por padrão — outros critérios (receita, produção) são configuráveis
4. O custo por saca/kg só é calculado após registro de produção (romaneio de colheita)
5. A margem bruta é: `receita_venda - custo_total`
6. Custos são categorizados: insumos (sementes, fertilizantes, defensivos), maquinário, mão_de_obra, serviços_terceiros, custos_indiretos, outros
7. Não é permitido editar custos de safras encerradas sem permissão de admin
8. O sistema deve manter rastreabilidade: cada custo aponta para a operação, despesa ou rateio de origem
9. Moeda é BRL por padrão; valores em dólares usam cotação do dia do lançamento (para insumos importados)
10. **Custeio FIFO**: Insumos consumidos usam custo do lote mais antigo (primeiro a entrar no estoque)
11. **Depreciação de máquinas**: Calcular depreciação por hora trabalhada (valor da máquina ÷ vida útil em horas)
12. **Arrendamento**: Ratear valor anual de arrendamento por área cultivada
13. Permissões: `agricola:custos:read`, `agricola:custos:create`, `agricola:custos:configure`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `CustoSafra` | id, tenant_id, safra_id, talhao_id, categoria, subcategoria, valor, data_lancamento, origem_tipo, origem_id | vinculado a safra/talhão |
| `RateioIndireto` | id, tenant_id, safra_id, descricao, valor_total, criterio_rateio, data_referencia | custo rateado entre talhões |
| `RateioDistribuicao` | id, rateio_id, talhao_id, percentual, valor_rateado | distribuição do rateio |
| `CustoResumoSafra` | view materializada: safra_id, talhao_id, custo_total, custo_ha, custo_saca, producao_total, receita, margem_bruta | resumo calculado |
| `DepreciacaoMaquina` | id, equipamento_id, valor_aquisicao, vida_util_horas, horas_trabalhadas, valor_depreciado | depreciação por uso |
| `ArrendamentoRateio` | id, tenant_id, imovel_id, valor_anual, area_total_ha, valor_ha | rateio de arrendamento |

## Integrações Necessárias

| Sistema/Modulo | Tipo | Descrição |
|----------------|------|-----------|
| `agricola/operacoes` | Leitura | Custos de insumos, maquinário e mão de obra por operação |
| `agricola/safras` | Leitura | Área por talhão e dados da safra |
| `agricola/romaneios` | Leitura | Produção total para cálculo de custo/saca |
| `financeiro/despesas` | Leitura | Despesas vinculadas à safra |
| `financeiro/receitas` | Leitura | Receitas de venda para cálculo de margem |
| `agricola/planejamento` | Leitura | Orçamento previsto para comparativo |
| `operacional/estoque` | Leitura | Custo médio de insumos (FIFO) |
| `operacional/frota` | Leitura | Dados de máquinas para depreciação |

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa `/agricola/custos` ou `/agricola/safras/[id]/financeiro`
2. Seleciona a safra e visualiza dashboard com KPIs: custo total, custo/ha, margem bruta
3. Visualiza breakdown por categoria em gráfico de pizza ou barras
4. **Insumos (60%)**: Detalhado em sementes, fertilizantes (N, P, K), defensivos (herbicidas, fungicidas, inseticidas)
5. Navega para detalhamento por talhão — compara custo/ha entre talhões
6. Identifica que talhão X tem custo de defensivos 40% acima da média
7. Clica para ver operações de pulverização desse talhão — identifica aplicação extra por praga
8. Acessa comparativo histórico: custo da safra atual vs safra anterior
9. Se plano Profissional, visualiza orçamento previsto vs realizado com variância
10. Lança custo indireto (ex: arrendamento anual) e configura rateio por área
11. Sistema distribui automaticamente entre talhões proporcionalmente à área
12. **Depreciação**: Sistema calcula depreciação de máquinas por horas trabalhadas
13. **Ponto de equilíbrio**: Sistema calcula break-even em sc/ha
14. Exporta relatório de custos para análise gerencial ou financiamento bancário
15. **DRE Rural**: Gera Demonstração de Resultado no formato para contador

## Casos Extremos e Exceções

- **Safra sem produção**: Perda total (geada, seca) — custo/saca é indefinido (exibir "N/A", não dividir por zero)

- **Custo negativo**: Devolução de insumo — registrar como custo negativo na categoria correspondente

- **Câmbio**: Insumos comprados em dólar (importados) — converter na data do lançamento e registrar cotação usada

- **Rateio circular**: Custo indireto que depende de produção que ainda não foi colhida — permitir rateio provisório com recálculo posterior

- **Talhão adicionado mid-safra**: Novo talhão entra na safra após início — ratear custos indiretos apenas a partir da data de inclusão

- **Múltiplas culturas no talhão**: Consórcio soja+milho — permitir alocação percentual de custo por cultura

- **Custo retroativo**: Despesa descoberta após encerramento — permitir lançamento com flag `retroativo` e justificativa

- **Inflação de insumos**: Fertilizante sofre reajuste de 30% no meio da safra — custo FIFO reflete preço mais antigo, não o atual

- **Maquinário próprio vs terceirizado**: Operações com máquina própria (depreciação) vs terceirizada (custo direto) — categorizar corretamente

## Critérios de Aceite (Definition of Done)

- [ ] Agregação automática de custos de operações (insumos + maquinário + mão de obra)
- [ ] Dashboard com KPIs: custo total, custo/ha, custo/saca, margem bruta
- [ ] Breakdown por categoria com gráficos
- [ ] Comparativo entre talhões (custo/ha)
- [ ] Comparativo histórico entre safras
- [ ] Rateio de custos indiretos por área com distribuição automática
- [ ] Orçamento previsto vs realizado (quando planejamento disponível)
- [ ] Rastreabilidade de origem de cada custo (operação, despesa, rateio)
- [ ] Cálculo de ponto de equilíbrio (break-even) em sc/ha
- [ ] Custeio FIFO para insumos
- [ ] Depreciação de máquinas por horas trabalhadas
- [ ] Exportação de relatório de custos
- [ ] Geração de DRE Rural para contador
- [ ] Tenant isolation e RBAC testados
- [ ] Tratamento de divisão por zero quando produção = 0

## Sugestões de Melhoria Futura

1. **Custeio ABC**: Alocar custos por atividade em vez de apenas por área

2. **Benchmark cooperativa**: Comparar custo/saca com média da cooperativa (anonimizado)

3. **Projeção de custo**: Com base no consumo parcial, projetar custo total ao fim da safra

4. **Integração bancária**: Exportar dados no formato exigido por bancos para comprovação de custeio

5. **Dashboard multi-safra**: Visão consolidada de todas as safras ativas com ranking de rentabilidade

6. **Alertas de desvio**: Notificar quando custo realizado ultrapassa X% do orçamento

7. **Custo ambiental**: Incluir métricas de pegada de carbono por talhão/safra

8. **Integração com CEPEA/ESALQ**: Puxar preços de referência de insumos e commodities

9. **Simulador de preço de venda**: "Se eu vender a R$ X/sc, qual meu lucro?"

10. **Rateio por produtividade**: Ratear custos indiretos proporcionalmente à produtividade (talhão mais produtivo absorve mais custo)

11. **Custo de oportunidade**: Comparar rentabilidade da safra com CDI ou outras aplicações

12. **Relatório para seguro**: Gerar relatório de custo para contratação de seguro rural (PSR)
