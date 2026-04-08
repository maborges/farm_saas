---
modulo: Contabilidade
submodulo: Lançamentos Contábeis
nivel: essencial
core: false
dependencias_core:
  - Identidade e Acesso
  - Configurações Globais
dependencias_modulos:
  - ./plano-contas-rural.md
  - ../../financeiro/essencial/despesas.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: M
assinante_alvo:
  - Produtor Rural PF
  - Produtor Rural PJ
  - Contador Rural
---

# Lançamentos Contábeis

## Descrição Funcional

O submódulo de Lançamentos Contábeis implementa a escrituração por partidas dobradas, garantindo que todo registro contábil tenha débitos e créditos equilibrados. Os lançamentos podem ser gerados automaticamente a partir do módulo financeiro (despesas pagas, receitas recebidas) ou inseridos manualmente pelo contador. Suporta lançamentos simples (1 débito, 1 crédito) e compostos (múltiplas partidas), com histórico detalhado e rastreabilidade completa.

## Personas

- **Produtor Rural:** Visualiza lançamentos gerados automaticamente a partir das movimentações financeiras.
- **Contador Rural:** Insere lançamentos manuais, revisa os automáticos, faz ajustes e estornos.
- **Auditor:** Consulta lançamentos com filtros avançados para verificar conformidade.

## Dores que resolve

- Escrituração manual em planilhas sem garantia de equilíbrio débito/crédito.
- Falta de rastreabilidade entre o evento financeiro e o lançamento contábil.
- Dificuldade em identificar e corrigir erros de classificação.
- Impossibilidade de fechar período contábil com segurança.
- Retrabalho do contador ao receber dados desorganizados do produtor.

## Regras de Negócio

1. **Partidas dobradas:** A soma dos débitos deve ser igual à soma dos créditos em cada lançamento. O sistema deve impedir lançamentos desbalanceados.
2. **Contas analíticas:** Lançamentos somente em contas analíticas do plano de contas.
3. **Data de competência e data de caixa:** Cada lançamento registra ambas as datas para suportar regime de competência e caixa.
4. **Status do lançamento:** Rascunho → Pendente → Aprovado → Estornado. Lançamentos aprovados não podem ser editados, apenas estornados.
5. **Estorno:** Gera um lançamento inverso vinculado ao original, com histórico de motivo.
6. **Fechamento mensal:** Após fechamento do período, nenhum lançamento pode ser inserido ou estornado naquele mês sem reabertura autorizada.
7. **Lançamentos automáticos:** Gerados a partir de eventos do financeiro (pagamento, recebimento, baixa) com regra de mapeamento conta financeira → conta contábil.
8. **Numeração sequencial:** Lançamentos recebem numeração sequencial por exercício fiscal, sem gaps.
9. **Histórico obrigatório:** Todo lançamento deve conter histórico descritivo.
10. **Multi-fazenda:** Lançamentos podem ser filtrados e consolidados por fazenda.

## Entidades de Dados Principais

- `LancamentoContabil` — cabeçalho: número, data competência, data caixa, histórico, status, tipo (manual/automático), origem (id do evento financeiro se automático), usuário responsável.
- `PartidaLancamento` — linha do lançamento: conta contábil, valor, tipo (D/C), complemento do histórico, centro de custo opcional.
- `FechamentoPeriodo` — registro de períodos fechados por mês/ano.
- `RegraLancamentoAutomatico` — mapeamento entre categoria financeira e contas contábeis (débito/crédito).

## Integrações Necessárias

- **Plano de Contas Rural:** Referência de contas para cada partida.
- **Financeiro (Despesas/Receitas):** Origem dos lançamentos automáticos ao registrar pagamento/recebimento.
- **LCDPR:** Lançamentos no regime de caixa alimentam o LCDPR.
- **DRE Rural:** Lançamentos de receitas e despesas compõem o DRE.
- **Balancete:** Saldos calculados a partir dos lançamentos.
- **Estoque:** Movimentações de estoque podem gerar lançamentos contábeis (ex.: consumo de insumos).

## Fluxo de Uso Principal

1. **Configuração:** Definir regras de mapeamento para lançamentos automáticos (categoria financeira → contas contábeis).
2. **Geração automática:** Ao registrar pagamento/recebimento no financeiro, o sistema gera lançamento contábil correspondente com status "Pendente".
3. **Lançamento manual:** Contador insere lançamentos adicionais (ajustes, provisões, depreciações) diretamente.
4. **Revisão:** Contador revisa lançamentos pendentes, ajusta classificações se necessário.
5. **Aprovação:** Contador aprova lançamentos revisados, tornando-os definitivos.
6. **Fechamento:** Ao final do mês, contador fecha o período, impedindo novas alterações.
7. **Estorno:** Se necessário corrigir lançamento aprovado, gerar estorno e novo lançamento correto.

## Casos Extremos e Exceções

- Lançamento automático gerado com conta inativa — deve ser sinalizado para revisão manual.
- Estorno de lançamento em período já fechado — exige permissão especial e reabertura do período.
- Lançamento composto com mais de 10 partidas (ex.: rateio de despesa entre múltiplas fazendas).
- Exclusão de evento financeiro que já gerou lançamento contábil aprovado — deve impedir exclusão ou exigir estorno prévio.
- Importação em lote de lançamentos via CSV (migração de outro sistema).
- Lançamento com moeda estrangeira (contratos de exportação) — conversão na data do fato.

## Critérios de Aceite

- [ ] Lançamentos sempre equilibrados (soma débitos = soma créditos), impedindo gravação desbalanceada.
- [ ] Lançamentos automáticos gerados corretamente a partir de pagamentos/recebimentos do financeiro.
- [ ] Fluxo de status funcional: Rascunho → Pendente → Aprovado → Estornado.
- [ ] Estorno gera lançamento inverso vinculado ao original.
- [ ] Fechamento de período impede alterações em lançamentos do mês fechado.
- [ ] Filtros por data, conta, status, fazenda e tipo (manual/automático) funcionais.
- [ ] Numeração sequencial sem gaps por exercício fiscal.
- [ ] Histórico obrigatório em todos os lançamentos.

## Sugestões de Melhoria Futura

- Lançamentos recorrentes agendados (ex.: depreciação mensal automática).
- Sugestão de classificação por IA baseada no histórico de lançamentos similares.
- Importação de lançamentos via integração com ERPs de terceiros (API).
- Visualização gráfica do fluxo de lançamentos por conta (razão visual).
- Alertas quando lançamentos automáticos não são revisados após X dias.
