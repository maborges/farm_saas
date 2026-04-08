---
modulo: Contabilidade
submodulo: Balancete
nivel: profissional
core: false
dependencias_core:
  - Identidade e Acesso
  - Configurações Globais
dependencias_modulos:
  - ../essencial/plano-contas-rural.md
  - ../essencial/lancamentos-contabeis.md
standalone: false
complexidade: M
assinante_alvo:
  - Produtor Rural PJ
  - Contador Rural
  - Auditor
---

# Balancete de Verificação

## Descrição Funcional

O Balancete de Verificação apresenta os saldos de todas as contas contábeis em um determinado período, servindo como instrumento de conferência da escrituração contábil. Exibe saldo anterior, movimentação a débito, movimentação a crédito e saldo atual de cada conta, podendo ser emitido por período, fazenda ou centro de custo. É essencial para verificar a consistência dos lançamentos antes do fechamento e geração de demonstrações financeiras.

## Personas

- **Contador Rural:** Utiliza o balancete como principal ferramenta de conferência mensal.
- **Auditor:** Consulta o balancete para verificar saldos e identificar inconsistências.
- **Gestor Financeiro:** Acompanha a evolução de saldos de contas patrimoniais e de resultado.

## Dores que resolve

- Dificuldade em verificar se a escrituração está equilibrada (total de débitos = total de créditos).
- Falta de visão consolidada dos saldos contábeis por período.
- Necessidade de exportar dados para planilha para fazer conferência manualmente.
- Impossibilidade de comparar saldos entre períodos para identificar anomalias.

## Regras de Negócio

1. **Equilíbrio:** A soma total de saldos devedores deve ser igual à soma total de saldos credores. Se não for, o sistema sinaliza erro na escrituração.
2. **Níveis de exibição:** Balancete pode ser exibido em nível sintético (apenas contas de grupo) ou analítico (todas as contas).
3. **Período:** Balancete sempre referente a um período (mês/ano), com saldo anterior e movimentação do período.
4. **Saldo anterior:** Calculado a partir dos lançamentos de todos os períodos anteriores ao selecionado.
5. **Contas zeradas:** Por padrão, contas com saldo zero e sem movimentação são ocultadas (opção de exibir).
6. **Filtros:** Por fazenda, centro de custo, grupo de contas.
7. **Comparativo:** Balancete comparativo mostra saldos do período atual ao lado do período anterior e a variação.
8. **Consistência com DRE:** Saldos de contas de resultado devem ser consistentes com o DRE do mesmo período.

## Entidades de Dados Principais

- `Balancete` — cabeçalho: período, tipo (analítico/sintético), filtros aplicados, data de geração.
- `LinhaBalancete` — conta contábil, saldo anterior (débito/crédito), movimentação débito, movimentação crédito, saldo atual (débito/crédito).

## Integrações Necessárias

- **Plano de Contas Rural:** Estrutura hierárquica das contas exibidas.
- **Lançamentos Contábeis:** Fonte dos dados de movimentação e cálculo de saldos.
- **DRE Rural:** Validação cruzada entre saldos de contas de resultado e linhas do DRE.
- **Integração Contábil:** Balancete pode ser incluído no pacote de exportação para o contador externo.

## Fluxo de Uso Principal

1. **Seleção de parâmetros:** Escolher período (mês/ano), nível (analítico/sintético), filtros opcionais.
2. **Geração:** Sistema calcula saldos anteriores, movimentação do período e saldos atuais.
3. **Verificação:** Conferir se totais de débitos e créditos estão equilibrados.
4. **Análise:** Investigar contas com saldos inesperados — drill-down para ver lançamentos.
5. **Comparativo:** Opcionalmente, comparar com período anterior para identificar variações significativas.
6. **Exportação:** Exportar em PDF, Excel ou CSV.

## Casos Extremos e Exceções

- Balancete com saldos desequilibrados — indicativo de bug ou lançamento corrompido; sistema deve alertar e indicar a diferença.
- Conta com saldo invertido (ativo com saldo credor ou passivo com saldo devedor) — alertar como possível inconsistência.
- Primeiro período de uso (sem saldo anterior) — exigir informação de saldos iniciais ou considerar zero.
- Volume muito grande de contas analíticas (>1.000 contas) — paginação e opção de filtro por grupo.
- Período com lançamentos pendentes de aprovação — exibir aviso de balancete provisório.

## Critérios de Aceite

- [ ] Balancete analítico e sintético disponíveis.
- [ ] Soma de saldos devedores = soma de saldos credores, com alerta se desbalanceado.
- [ ] Saldo anterior calculado corretamente a partir do histórico de lançamentos.
- [ ] Drill-down de cada conta para os lançamentos do período.
- [ ] Filtro por fazenda e centro de custo funcional.
- [ ] Comparativo entre dois períodos com coluna de variação.
- [ ] Exportação em PDF, Excel e CSV.
- [ ] Contas zeradas ocultadas por padrão com opção de exibição.

## Sugestões de Melhoria Futura

- Balancete com alertas automáticos de anomalias (variações superiores a X% em relação ao período anterior).
- Balancete consolidado multi-empresa (integração com módulo Enterprise Multi-Empresa).
- Geração automática mensal com envio por e-mail ao contador.
- Visualização gráfica da composição do ativo/passivo baseada nos saldos do balancete.
- Auditoria automatizada: regras configuráveis que verificam consistência de saldos.
