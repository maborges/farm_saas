---
modulo: Financeiro
submodulo: Categorias e Contas
nivel: essencial
core: false
dependencias_core: []
dependencias_modulos: []
standalone: true
complexidade: XS
assinante_alvo:
  - pequeno produtor rural
  - agricultor familiar
  - administrador de fazenda
---

# Categorias e Contas

## Descrição Funcional

Submódulo que gerencia o plano de contas financeiro e as categorias de classificação de lançamentos. Fornece a estrutura hierárquica para organizar receitas e despesas, além de cadastrar as contas financeiras (bancárias, caixa físico, carteira digital) onde o dinheiro efetivamente transita.

É o primeiro submódulo a ser configurado — todos os demais do módulo Financeiro dependem dele.

## Personas — Quem usa este submódulo

- **Produtor Rural (owner):** configura suas contas bancárias e personaliza categorias conforme a realidade da propriedade.
- **Administrador da Fazenda:** cria categorias específicas para operações (ex.: "Diesel - Colheitadeira", "Ração - Gado de Corte").
- **Contador externo:** mapeia categorias do sistema para o plano de contas contábil oficial.

## Dores que resolve

1. **Gastos sem classificação:** impossível saber quanto se gasta com cada item sem categorias.
2. **Contas misturadas:** dinheiro da fazenda e pessoal no mesmo extrato sem distinção.
3. **Plano de contas genérico:** sistemas contábeis genéricos não têm categorias específicas do agro.
4. **Retrabalho para o contador:** sem categorização padronizada, contador gasta horas reclassificando.

## Regras de Negócio

1. Categorias são hierárquicas em até 3 níveis (grupo → subgrupo → categoria).
2. Cada categoria pertence a um tipo: `RECEITA` ou `DESPESA`.
3. Ao criar um tenant, o sistema gera automaticamente um plano de contas padrão agro (seed).
4. Categorias padrão (seed) são marcadas como `is_default = true` e não podem ser excluídas, apenas desativadas.
5. Categorias customizadas podem ser criadas, editadas e excluídas logicamente.
6. Contas financeiras possuem tipos: `CONTA_CORRENTE`, `POUPANCA`, `CAIXA_FISICO`, `CARTEIRA_DIGITAL`, `CARTAO_CREDITO`.
7. Cada conta pertence a um tenant e opcionalmente a uma fazenda específica.
8. Conta com lançamentos vinculados não pode ser excluída; apenas desativada.
9. Uma conta pode ser marcada como `padrao = true` para pré-seleção em novos lançamentos.
10. Código contábil opcional para integração com sistemas de contabilidade.

## Entidades de Dados Principais

### Categoria
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| parent_id | UUID | não | FK → Categoria (hierarquia) |
| nome | VARCHAR(100) | sim | Nome da categoria |
| tipo | ENUM(RECEITA, DESPESA) | sim | Tipo |
| codigo_contabil | VARCHAR(20) | não | Código para integração contábil |
| is_default | BOOLEAN | sim | Se é categoria padrão (seed) |
| ativo | BOOLEAN | sim | Se está ativa |
| ordem | INTEGER | não | Ordem de exibição |

### ContaFinanceira
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| fazenda_id | UUID | não | FK → Fazenda (se específica) |
| nome | VARCHAR(100) | sim | Nome da conta (ex.: "Banco do Brasil - CC") |
| tipo | ENUM(CONTA_CORRENTE, POUPANCA, CAIXA_FISICO, CARTEIRA_DIGITAL, CARTAO_CREDITO) | sim | Tipo da conta |
| banco | VARCHAR(100) | não | Nome do banco |
| agencia | VARCHAR(20) | não | Agência |
| numero_conta | VARCHAR(30) | não | Número da conta |
| saldo_inicial_centavos | INTEGER | sim | Saldo inicial em centavos |
| padrao | BOOLEAN | sim | Se é conta padrão para lançamentos |
| ativo | BOOLEAN | sim | Se está ativa |

## Integrações Necessárias

- **Lançamentos Básicos (essencial):** cada lançamento referencia uma categoria e opcionalmente uma conta.
- **Fluxo de Caixa (essencial):** filtros por conta e categoria.
- **Centro de Custo (profissional):** categorias podem ser associadas a centros de custo padrão.
- **Conciliação Bancária (profissional):** contas financeiras são a referência para conciliação.

## Fluxo de Uso Principal (step-by-step)

1. Ao criar o tenant, o sistema gera automaticamente categorias padrão agro (seed).
2. Usuário acessa "Configurações > Categorias" no menu Financeiro.
3. Visualiza a árvore hierárquica de categorias (receitas e despesas em abas separadas).
4. Cria nova categoria customizada, selecionando o grupo pai e o tipo.
5. Opcionalmente informa código contábil para integração com contabilidade.
6. Acessa "Configurações > Contas" para cadastrar contas financeiras.
7. Cadastra conta informando nome, tipo, banco, agência e número.
8. Informa o saldo inicial para calibrar o fluxo de caixa.
9. Marca uma conta como padrão para agilizar lançamentos.
10. Categorias e contas ficam disponíveis em todos os formulários de lançamento.

## Casos Extremos e Exceções

- **Exclusão de categoria com lançamentos:** não permitida; sugerir desativação.
- **Exclusão de categoria pai com filhas:** não permitida; excluir filhas primeiro.
- **Categoria seed desativada:** lançamentos antigos mantêm referência; novos lançamentos não podem usá-la.
- **Conta sem saldo inicial:** assumir zero.
- **Mais de uma conta padrão:** apenas a última marcada como padrão prevalece; as demais são desmarcadas automaticamente.
- **Migração de tenant:** categorias seed são recriadas se ausentes.
- **Limite de categorias:** máximo 500 por tenant para evitar degradação de performance.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de categorias com hierarquia de até 3 níveis e tenant isolation.
- [ ] CRUD de contas financeiras com tenant isolation.
- [ ] Seed automático de categorias padrão ao criar tenant.
- [ ] Validação de exclusão: não permitir se houver lançamentos vinculados.
- [ ] Conta padrão funcional: marcar uma desmarca as demais.
- [ ] Categorias filtradas por tipo (RECEITA/DESPESA) nos formulários de lançamento.
- [ ] Árvore hierárquica de categorias renderizada corretamente no frontend.
- [ ] Testes: CRUD, hierarquia, seed, validações de exclusão, tenant isolation.

## Sugestões de Melhoria Futura

- **Mapeamento contábil automático:** sugerir código contábil com base no nome da categoria.
- **Importação de plano de contas:** permitir upload de plano de contas do contador em formato padrão.
- **Categorias compartilhadas entre tenants:** templates de plano de contas por tipo de propriedade (grãos, pecuária, horticultura).
- **Integração bancária para auto-cadastro:** detectar contas automaticamente via Open Finance.
- **Ícones e cores customizáveis:** permitir personalizar a aparência das categorias para identificação visual rápida.
