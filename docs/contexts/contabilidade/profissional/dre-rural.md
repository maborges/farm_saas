---
modulo: Contabilidade
submodulo: DRE Rural
nivel: profissional
core: false
dependencias_core:
  - Identidade e Acesso
  - Configurações Globais
dependencias_modulos:
  - ../essencial/plano-contas-rural.md
  - ../essencial/lancamentos-contabeis.md
  - ../../financeiro/essencial/despesas.md
  - ../../financeiro/essencial/receitas.md
  - ../../agricola/safras.md
standalone: false
complexidade: M
assinante_alvo:
  - Produtor Rural PJ
  - Contador Rural
  - Gestor de Fazenda
---

# DRE Rural — Demonstração do Resultado do Exercício da Atividade Rural

## Descrição Funcional

O DRE Rural gera a Demonstração do Resultado do Exercício adaptada às especificidades da atividade rural brasileira. Permite visualizar o resultado por safra, por fazenda, por cultura ou consolidado, separando receitas de venda de produção, custos de custeio, investimentos, depreciações e resultado líquido. Suporta comparativo entre períodos e entre safras para análise de rentabilidade.

## Personas

- **Gestor de Fazenda:** Analisa a rentabilidade de cada safra e cultura para tomar decisões de plantio.
- **Produtor Rural PJ:** Acompanha o resultado da atividade para planejamento tributário.
- **Contador Rural:** Gera o DRE oficial para demonstrações financeiras e obrigações acessórias.
- **Investidor/Banco:** Solicita o DRE para análise de crédito rural.

## Dores que resolve

- Impossibilidade de saber o resultado real de cada safra individualmente.
- DRE genérico que não separa custos de custeio, investimento e depreciação conforme exigido na atividade rural.
- Falta de comparativo entre safras para identificar tendências de rentabilidade.
- Dificuldade em ratear custos indiretos entre culturas e fazendas.
- Desconhecimento do ponto de equilíbrio por cultura.

## Regras de Negócio

1. **Estrutura rural:** O DRE segue a estrutura específica para atividade rural: Receita Bruta de Vendas → Deduções → Receita Líquida → Custo dos Produtos Vendidos (CPV) → Lucro Bruto → Despesas Operacionais → Resultado Operacional → Resultado Financeiro → Resultado antes IR → Provisão IR → Resultado Líquido.
2. **Dimensões de análise:** DRE disponível por: período, fazenda, safra, cultura, talhão, ou consolidado.
3. **Regime de competência:** O DRE utiliza regime de competência (diferente do LCDPR que usa caixa).
4. **Rateio de custos indiretos:** Custos que não são diretamente atribuíveis a uma safra/cultura devem ser rateados conforme critério configurável (área, produção, receita).
5. **Comparativo:** Permitir comparação lado a lado entre períodos ou safras.
6. **Análise vertical/horizontal:** Percentuais sobre receita líquida (vertical) e variação entre períodos (horizontal).
7. **Ativos biológicos:** Segregar variação do valor justo de ativos biológicos conforme CPC 29.
8. **Fechamento:** DRE só pode ser considerado definitivo após fechamento do período contábil.

## Entidades de Dados Principais

- `DREReport` — cabeçalho do relatório: período, dimensão (fazenda/safra/consolidado), status (rascunho/definitivo).
- `DRELinha` — linha do DRE: grupo contábil, descrição, valor, percentual sobre receita.
- `CriterioRateio` — configuração de rateio de custos indiretos (tipo, percentual por dimensão).
- `DREComparativo` — estrutura para comparação entre dois DREs.

## Integrações Necessárias

- **Plano de Contas Rural:** Estrutura do DRE derivada da hierarquia de contas de resultado.
- **Lançamentos Contábeis:** Valores calculados a partir dos lançamentos aprovados no período.
- **Agrícola (Safras/Talhões):** Dimensão de análise para DRE por safra/cultura.
- **Financeiro:** Dados de receitas e despesas por competência.
- **Estoque:** Custo dos produtos vendidos (CPV) baseado no custo FIFO/médio do estoque.

## Fluxo de Uso Principal

1. **Seleção de parâmetros:** Escolher período, dimensão (fazenda, safra, cultura, consolidado) e tipo de regime.
2. **Configuração de rateio:** Definir critério de rateio de custos indiretos (se aplicável).
3. **Geração:** Sistema calcula o DRE a partir dos lançamentos contábeis do período.
4. **Análise:** Usuário visualiza o DRE com análise vertical (percentuais) e drill-down por conta.
5. **Comparativo:** Opcionalmente, gerar comparação com período/safra anterior.
6. **Exportação:** Exportar em PDF, Excel ou incluir no pacote de integração contábil.

## Casos Extremos e Exceções

- Safra que abrange dois exercícios fiscais — prorratear ou atribuir ao exercício de colheita.
- Custos de formação de lavoura perene (café, citros) — capitalizar como ativo biológico, não como despesa.
- Receita de venda futura (contratos a termo) — reconhecer na data de entrega/faturamento.
- Fazenda com múltiplas culturas consorciadas — rateio complexo de custos compartilhados.
- DRE com resultado negativo em período de formação de lavoura (esperado e documentável).
- Variação cambial em contratos de exportação — segregar no resultado financeiro.

## Critérios de Aceite

- [ ] DRE gerado com estrutura específica para atividade rural.
- [ ] Disponível por fazenda, safra, cultura e consolidado.
- [ ] Análise vertical (% sobre receita) presente em todas as linhas.
- [ ] Comparativo entre dois períodos/safras lado a lado.
- [ ] Rateio de custos indiretos configurável e aplicado corretamente.
- [ ] Drill-down de cada linha para os lançamentos que a compõem.
- [ ] Exportação em PDF e Excel funcional.
- [ ] Valores conferem com o balancete do mesmo período.

## Sugestões de Melhoria Futura

- DRE projetado com base em orçamento e dados históricos.
- Análise de ponto de equilíbrio por cultura com gráfico interativo.
- Benchmark: comparar rentabilidade com médias regionais (dados públicos da CONAB).
- DRE automatizado mensal com envio por e-mail ao gestor.
- Integração com dashboards BI para visualização avançada.
