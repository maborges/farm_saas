---
modulo: Contabilidade
submodulo: Plano de Contas Rural
nivel: essencial
core: false
dependencias_core:
  - Identidade e Acesso
  - Configurações Globais
dependencias_modulos:
  - ../../financeiro/essencial/despesas.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: S
assinante_alvo:
  - Produtor Rural PF
  - Produtor Rural PJ
  - Contador Rural
---

# Plano de Contas Rural

## Descrição Funcional

O Plano de Contas Rural fornece uma estrutura hierárquica de contas contábeis adaptada às especificidades da atividade rural brasileira. O sistema oferece um modelo padrão baseado nas normas do CFC (Conselho Federal de Contabilidade) e nas práticas recomendadas para contabilidade rural, permitindo personalização por fazenda ou grupo. É a base para toda a escrituração contábil do módulo.

## Personas

- **Produtor Rural:** Utiliza o plano padrão sem necessidade de conhecimento contábil aprofundado.
- **Contador Rural:** Personaliza o plano conforme a realidade do cliente e as exigências fiscais.
- **Administrador do Sistema:** Configura o plano padrão disponibilizado para novos tenants.

## Dores que resolve

- Falta de plano de contas específico para atividade rural nos sistemas genéricos.
- Dificuldade em separar custos de custeio, investimento e depreciação conforme exigido pela legislação rural.
- Incompatibilidade entre o plano de contas interno e as categorias exigidas pelo LCDPR e SPED.
- Retrabalho ao adaptar plano de contas genérico para cada fazenda.

## Regras de Negócio

1. **Modelo padrão:** Ao ativar o módulo, um plano de contas rural padrão é criado automaticamente para o tenant.
2. **Estrutura hierárquica:** Contas organizadas em níveis (grupo, subgrupo, conta analítica) com código numérico hierárquico.
3. **Natureza da conta:** Cada conta possui natureza (devedora/credora) e tipo (ativo, passivo, receita, despesa, patrimônio líquido).
4. **Contas sintéticas vs. analíticas:** Lançamentos somente em contas analíticas (último nível). Contas sintéticas agregam saldos.
5. **Mapeamento LCDPR:** Contas analíticas devem ter campo de mapeamento para a conta LCDPR correspondente.
6. **Imutabilidade parcial:** Contas com lançamentos não podem ser excluídas, apenas desativadas.
7. **Multi-fazenda:** Plano de contas pode ser compartilhado entre fazendas do mesmo tenant ou personalizado por fazenda.
8. **Contas obrigatórias:** Determinadas contas são obrigatórias e não podem ser removidas (ex.: Caixa, Bancos, Receita de Vendas).

## Entidades de Dados Principais

- `PlanoContas` — cabeçalho do plano (nome, versão, tenant, fazenda opcional).
- `ContaContabil` — registro de conta com: código, nome, nível, natureza, tipo, conta-pai, status (ativa/inativa), mapeamento LCDPR.
- `GrupoContas` — agrupamento de contas para facilitar navegação e relatórios.
- `PlanoContasModelo` — templates de plano de contas padrão fornecidos pelo sistema.

## Integrações Necessárias

- **Lançamentos Contábeis:** Contas são referenciadas em cada partida de lançamento.
- **LCDPR:** Mapeamento entre conta contábil e conta LCDPR da Receita Federal.
- **DRE Rural:** Estrutura do DRE é derivada da hierarquia de contas de receitas e despesas.
- **Balancete:** Saldos são calculados com base nas contas do plano.
- **Financeiro:** Categorias financeiras podem ser vinculadas a contas contábeis para lançamento automático.

## Fluxo de Uso Principal

1. **Ativação:** Ao ativar o módulo Contabilidade, o plano de contas padrão rural é criado automaticamente.
2. **Personalização:** Contador revisa o plano e adiciona/ajusta contas conforme a realidade do produtor.
3. **Mapeamento:** Vincular contas analíticas às contas LCDPR e categorias do financeiro.
4. **Uso contínuo:** Contas são utilizadas nos lançamentos contábeis, relatórios e exportações.
5. **Manutenção:** Novas contas podem ser adicionadas; contas sem uso podem ser desativadas.

## Casos Extremos e Exceções

- Migração de plano de contas de outro sistema (importação via CSV).
- Produtor com atividades rurais diversificadas (agricultura, pecuária, agroindústria) necessitando contas específicas para cada atividade.
- Mudança na legislação que exige reestruturação do plano de contas.
- Conta com lançamentos que precisa ser reclassificada (mover para outro grupo).
- Fusão de fazendas com planos de contas diferentes.

## Critérios de Aceite

- [ ] Plano de contas padrão rural criado automaticamente ao ativar o módulo.
- [ ] Estrutura hierárquica de pelo menos 4 níveis navegável em árvore.
- [ ] Contas analíticas aceitam lançamentos; sintéticas apenas agregam.
- [ ] Mapeamento para contas LCDPR disponível em cada conta analítica.
- [ ] Contas com lançamentos não podem ser excluídas (apenas desativadas).
- [ ] Importação de plano de contas via CSV funcional.
- [ ] Busca por código ou nome da conta funcional.

## Sugestões de Melhoria Futura

- Planos de contas pré-configurados por tipo de atividade rural (grãos, pecuária de corte, pecuária leiteira, fruticultura, etc.).
- Versionamento do plano de contas com histórico de alterações.
- Sugestão automática de contas ao criar novos tipos de despesa/receita.
- Comparação entre plano de contas do produtor e modelo padrão, com sugestões de adequação.
