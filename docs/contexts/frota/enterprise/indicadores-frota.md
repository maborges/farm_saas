---
modulo: Frota e Máquinas
submodulo: Indicadores de Frota
nivel: enterprise
core: false
dependencias_core: [Identidade e Acesso, Cadastro da Propriedade]
dependencias_modulos: [../essencial/cadastro-equipamentos.md, ../profissional/manutencao-preventiva.md, ../profissional/custo-hora-maquina.md, ../enterprise/telemetria.md]
standalone: false
complexidade: L
assinante_alvo: [grande produtor, cooperativa, empresa agricola]
---

# Indicadores de Frota

## Descricao Funcional

Dashboard executivo com indicadores-chave de performance (KPIs) da frota: MTBF (tempo medio entre falhas), MTTR (tempo medio de reparo), disponibilidade mecanica, taxa de utilizacao, TCO (custo total de propriedade) e custo por hectare trabalhado. Permite benchmarking entre equipamentos e tomada de decisao baseada em dados para renovacao, descarte ou ampliacao da frota.

## Personas

- **Proprietario/Diretor:** visao executiva para decisoes estrategicas de investimento
- **Gestor de frota:** analise detalhada de performance por equipamento
- **Financeiro/Controller:** consolidacao de TCO e custo operacional
- **Gestor agricola:** custo de mecanizacao por talhao e cultura

## Dores que resolve

- Decisoes de compra/venda de equipamentos sem dados objetivos
- Desconhecimento do custo total de propriedade (aquisicao + operacao + manutencao)
- Impossibilidade de identificar equipamentos que deveriam ser substituidos
- Falta de benchmarking entre equipamentos do mesmo tipo
- Relatorios manuais demorados e imprecisos

## Regras de Negocio

1. MTBF = horas totais trabalhadas / numero de falhas (OS corretivas) no periodo
2. MTTR = soma de horas de reparo / numero de reparos no periodo
3. Disponibilidade Mecanica (%) = (horas disponiveis - horas em manutencao) / horas disponiveis * 100
4. Taxa de Utilizacao (%) = horas efetivamente trabalhadas / horas disponiveis * 100
5. TCO = valor aquisicao + custos operacionais acumulados + custos manutencao acumulados - valor residual estimado
6. Custo por hectare = custo total da maquina no periodo / hectares trabalhados
7. Indicadores calculados automaticamente com base em dados de outros submodulos
8. Periodos de analise: mensal, trimestral, anual, safra, vida util
9. Benchmark: comparar equipamentos do mesmo tipo/modelo dentro do tenant
10. Meta de disponibilidade mecanica configuravel por tipo (padrao 85%)

## Entidades de Dados Principais

- **IndicadorFrotaPeriodo:** id, tenant_id, equipamento_id, periodo_inicio, periodo_fim, mtbf_horas, mttr_horas, disponibilidade_pct, taxa_utilizacao_pct, tco_acumulado, custo_hectare, horas_trabalhadas, hectares_trabalhados, num_falhas, num_manutencoes_preventivas
- **MetaIndicador:** id, tenant_id, tipo_equipamento, indicador, valor_meta, ativo
- **SnapshotFrotaMensal:** id, tenant_id, mes_referencia, total_equipamentos, equipamentos_ativos, disponibilidade_media_pct, custo_total_mes, custo_medio_hora

## Integracoes Necessarias

- **Manutencao Preventiva:** OS corretivas (falhas) e preventivas, tempo de reparo
- **Custo/Hora Maquina:** custos operacionais detalhados
- **Telemetria:** horas trabalhadas automaticas, hectares cobertos
- **Cadastro de Equipamentos:** dados de aquisicao, idade, tipo
- **Abastecimento:** custo de combustivel por equipamento
- **Agricola (Operacoes):** hectares trabalhados por equipamento

## Fluxo de Uso Principal

1. Sistema coleta dados automaticamente dos demais submodulos
2. Ao final de cada periodo, calcula e armazena indicadores por equipamento
3. Dashboard exibe cards com KPIs principais e tendencias
4. Gestor filtra por tipo de equipamento, fazenda ou periodo
5. Detalhamento por equipamento mostra evolucao historica de cada indicador
6. Benchmark compara equipamentos similares lado a lado
7. Alertas quando indicador fica abaixo da meta configurada

## Casos Extremos e Excecoes

- Equipamento novo sem historico suficiente: exibir indicadores como "insuficiente" ate completar periodo minimo (30 dias)
- Equipamento parado por periodo prolongado (entressafra): excluir periodo de ociosidade planejada do calculo de disponibilidade
- Falha registrada sem OS (ex: pane em campo resolvida informalmente): permitir registro retroativo de evento de falha
- Equipamento com telemetria vs. sem telemetria: indicar confiabilidade dos dados (automatico vs. manual)
- Mudanca de propriedade (compra de equipamento usado): TCO inicia da data de aquisicao pelo tenant

## Criterios de Aceite

- [ ] Calculo automatico de MTBF, MTTR, disponibilidade e utilizacao
- [ ] Dashboard com cards de KPIs e graficos de tendencia
- [ ] TCO acumulado por equipamento com decomposicao de custos
- [ ] Custo por hectare trabalhado por equipamento
- [ ] Benchmark entre equipamentos do mesmo tipo
- [ ] Metas configuraveis com alertas
- [ ] Filtros por tipo, fazenda e periodo
- [ ] Snapshot mensal consolidado da frota
- [ ] Isolamento por tenant

## Sugestoes de Melhoria Futura

- Previsao de falhas com base em tendencia de MTBF (analytics preditivo)
- Recomendacao automatica de substituicao quando TCO excede valor de mercado
- Exportacao de relatorios em PDF para apresentacao a diretoria
- Integracao com mercado de maquinas usadas para estimativa de valor residual
- Comparativo com benchmarks de mercado (frota similar em outras fazendas, anonimizado)
