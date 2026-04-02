---
modulo: Pessoas e RH
submodulo: Indicadores de RH
nivel: enterprise
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-colaboradores.md
  - ../essencial/controle-presenca.md
  - ../profissional/folha-simplificada.md
  - ../profissional/treinamentos.md
standalone: false
complexidade: L
assinante_alvo:
  - Grande produtor rural
  - Cooperativas
  - Agroindústrias
  - Grupos empresariais rurais
---

# Indicadores de RH

## Descrição Funcional

Painel de indicadores (KPIs) de recursos humanos para gestão estratégica de pessoas na fazenda. Calcula e exibe métricas como turnover (rotatividade), absenteísmo, custo per capita, horas extras sobre total de horas, índice de treinamento, frequência de acidentes e produtividade por colaborador. Permite comparação entre fazendas, períodos e setores. Fundamental para decisões de gestão de pessoas baseadas em dados.

## Personas — Quem usa este submódulo

- **Diretor/Proprietário:** Visão estratégica de gestão de pessoas e custos
- **Gerente de RH:** Acompanha indicadores para ações corretivas
- **Gerente de fazenda:** Compara desempenho de equipes entre fazendas
- **Controller/Financeiro:** Analisa custo de pessoal sobre receita

## Dores que resolve

- Falta de dados para entender por que a rotatividade é alta
- Desconhecimento do custo real de pessoal por fazenda/setor/atividade
- Impossibilidade de comparar produtividade entre equipes
- Tomada de decisão sobre pessoal baseada em intuição, não em dados
- Falta de benchmark para saber se indicadores estão bons ou ruins

## Regras de Negócio

1. Turnover = (admissões + desligamentos) / 2 / headcount médio x 100 (período)
2. Absenteísmo = horas de ausência / horas previstas x 100 (período)
3. Custo per capita = custo total de pessoal / headcount médio (período)
4. Índice de horas extras = horas extras / horas normais x 100 (período)
5. Índice de treinamento = horas de treinamento / headcount (período)
6. Taxa de frequência de acidentes = (acidentes x 1.000.000) / horas-homem trabalhadas
7. Taxa de gravidade = (dias perdidos x 1.000.000) / horas-homem trabalhadas
8. Todos indicadores podem ser filtrados por: fazenda, setor, função, período
9. Comparação período atual vs. anterior (mês, trimestre, ano)
10. Indicadores calculados com base em dados reais do sistema (não input manual)
11. Meta configurável por indicador para visualização de desempenho (verde/amarelo/vermelho)

## Entidades de Dados Principais

- **IndicadorRH:** id, tenant_id, fazenda_id, tipo_indicador, periodo_referencia, valor, meta, tendencia (melhora/piora/estavel), calculado_em
- **MetaIndicador:** id, tenant_id, tipo_indicador, fazenda_id (null = todas), valor_meta, cor_verde_ate, cor_amarela_ate, vigencia_inicio, vigencia_fim
- **SnapshotRH:** id, tenant_id, fazenda_id, periodo, headcount, admissoes, desligamentos, horas_normais, horas_extras, horas_ausencia, horas_treinamento, custo_total_pessoal, acidentes, dias_perdidos_acidentes

## Integrações Necessárias

- **Cadastro de Colaboradores (essencial):** headcount, admissões, desligamentos
- **Controle de Presença (essencial):** horas trabalhadas, ausências
- **Folha Simplificada (profissional):** custo de pessoal
- **Treinamentos (profissional):** horas de treinamento por colaborador
- **EPI/Segurança (essencial):** acidentes e dias perdidos
- **Financeiro (receitas):** custo de pessoal sobre receita bruta

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa Pessoas > Indicadores de RH
2. Dashboard exibe cards com indicadores principais do mês atual
3. Cada card mostra: valor atual, meta, variação vs. mês anterior, semáforo (verde/amarelo/vermelho)
4. Clicar em um indicador abre detalhamento com gráfico histórico
5. Filtros permitem segmentar por fazenda, setor e função
6. Seção de comparativo exibe indicadores lado a lado entre fazendas
7. Usuário pode configurar metas por indicador
8. Relatório mensal consolidado pode ser exportado em PDF/Excel
9. Alertas automáticos quando indicador ultrapassa limites configurados
10. Análise de tendência mostra se indicador está melhorando ou piorando

## Casos Extremos e Exceções

- **Fazenda nova (sem histórico):** exibir apenas dados acumulados, sem comparativo
- **Headcount zero em algum mês:** evitar divisão por zero nos cálculos
- **Safristas distorcem turnover:** opção de excluir contratos temporários do cálculo
- **Transferência entre fazendas:** não contar como desligamento + admissão (distorce turnover)
- **Mês com feriados prolongados:** absenteísmo pode parecer alto — considerar dias úteis reais
- **Acidente com terceirizado:** separar indicadores de próprios vs. terceiros
- **Dados incompletos:** indicador calculado parcialmente — sinalizar com aviso

## Critérios de Aceite (Definition of Done)

- [ ] Dashboard com indicadores principais: turnover, absenteísmo, custo per capita, horas extras, acidentes
- [ ] Cálculo automático a partir dos dados do sistema
- [ ] Gráficos históricos com seleção de período
- [ ] Filtros por fazenda, setor e função
- [ ] Comparativo entre fazendas
- [ ] Metas configuráveis com semáforo visual
- [ ] Exportação de relatório em PDF/Excel
- [ ] Alertas quando indicador ultrapassa meta
- [ ] Tratamento de edge cases (divisão por zero, dados incompletos)
- [ ] Isolamento por tenant
- [ ] Testes de cálculo com cenários reais

## Sugestões de Melhoria Futura

- Benchmark com médias do setor agropecuário por região
- Predição de turnover por machine learning (colaboradores com risco de sair)
- People analytics: correlação entre treinamento e produtividade
- Relatório de clima organizacional integrado (pesquisa de satisfação)
- Custo de turnover calculado (recrutamento + treinamento + perda de produtividade)
- Integração com BI externo (Power BI, Metabase) via API
