---
modulo: Core
submodulo: Configurações Globais
nivel: core
core: true
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos: []
standalone: false
complexidade: S
assinante_alvo: todos os assinantes
---

# Configurações Globais

## Descrição Funcional

Submódulo que centraliza todas as configurações transversais da plataforma para cada tenant: definição de ano agrícola/safra, unidades de medida (hectare, alqueire paulista, alqueire mineiro), moeda, fuso horário, categorias customizáveis (categorias de despesa, tipos de operação, classificações de produtos) e preferências de exibição. Essas configurações alimentam todos os módulos de negócio, garantindo consistência nos cálculos, relatórios e interfaces.

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Define configurações iniciais durante o onboarding e ajusta conforme necessidade.
- **Gestor de Fazenda:** Consulta configurações para entender unidades e períodos aplicados. Pode sugerir ajustes ao Owner.
- **Contador / Financeiro:** Depende da configuração de moeda e ano fiscal para fechamentos e relatórios.
- **Agrônomo:** Consulta definição de ano agrícola para planejamento de safras.

## Dores que resolve

1. **Inconsistência de unidades:** Sem padronização, um módulo calcula em hectares e outro em alqueires, causando erros em relatórios consolidados.
2. **Ano agrícola vs. ano civil:** O agronegócio brasileiro trabalha com ano-safra (jul/jun ou out/set), não com ano civil. Relatórios precisam respeitar esse ciclo.
3. **Fuso horário incorreto:** Operações registradas com timestamp UTC sem conversão geram confusão em horários de aplicação de defensivos e ordenha.
4. **Categorias rígidas:** Categorias fixas de despesas/receitas não atendem à diversidade de operações rurais regionais.
5. **Reconfiguração repetitiva:** Sem configuração centralizada, cada módulo pede as mesmas informações.

## Regras de Negócio

1. **RN-CG-001:** O ano agrícola é definido por mês de início e mês de fim (ex: julho a junho). Padrão: julho a junho.
2. **RN-CG-002:** A unidade de área padrão é hectare. Unidades alternativas suportadas: alqueire paulista (2,42 ha), alqueire mineiro (4,84 ha), alqueire do norte (2,72 ha).
3. **RN-CG-003:** A moeda padrão é BRL (Real). Conversão para USD e EUR disponível em relatórios (cotação consultada via API externa).
4. **RN-CG-004:** O fuso horário padrão é o da UF da fazenda principal. Pode ser sobrescrito manualmente.
5. **RN-CG-005:** Categorias customizáveis são do tipo hierárquico (categoria → subcategoria) com no máximo 2 níveis.
6. **RN-CG-006:** Categorias do sistema (prefixadas com `sys_`) não podem ser editadas ou excluídas pelo tenant.
7. **RN-CG-007:** Alteração do ano agrícola não retroage sobre safras já criadas. Aplica-se apenas a novas safras.
8. **RN-CG-008:** Configurações são herdadas por todas as fazendas do tenant, mas podem ter override por fazenda quando indicado.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `ConfiguracaoTenant` | id, tenant_id, ano_agricola_inicio (mês), ano_agricola_fim (mês), unidade_area, moeda, fuso_horario, idioma | → Tenant |
| `ConfiguracaoFazenda` | id, fazenda_id, overrides (JSONB) | → Fazenda, → ConfiguracaoTenant |
| `CategoriaCustom` | id, tenant_id, tipo (despesa/receita/operação/produto), nome, parent_id, is_system, ordem | → Tenant, → CategoriaCustom (self-ref) |
| `UnidadeMedida` | id, tenant_id, nome, sigla, fator_conversao_ha, is_system | → Tenant |

## Integrações Necessárias

- **API de Cotação (BCB / Open Exchange Rates):** Conversão de moeda em relatórios multi-moeda.
- **Todos os módulos de negócio:** Consomem `ConfiguracaoTenant` para unidades, fuso horário e categorias.
- **Módulo Agrícola:** Consome `ano_agricola_inicio` e `ano_agricola_fim` para criação de safras.
- **Módulo Financeiro:** Consome `moeda` e categorias de despesa/receita.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Configuração inicial (onboarding)
1. Após cadastro do tenant, sistema exibe wizard de configuração inicial.
2. **Passo 1 — Ano agrícola:** Usuário seleciona mês de início e fim (sugestão padrão: jul-jun).
3. **Passo 2 — Unidade de área:** Seleciona unidade principal (hectare, alqueire paulista, etc.).
4. **Passo 3 — Moeda e fuso:** Moeda BRL preenchida automaticamente. Fuso sugerido pela UF da primeira fazenda.
5. **Passo 4 — Categorias:** Exibe categorias do sistema. Permite adicionar categorias customizadas.
6. Sistema salva `ConfiguracaoTenant` e redireciona ao dashboard.

### Fluxo 2: Ajuste de configuração existente
1. Owner acessa "Configurações" no menu lateral.
2. Altera parâmetro desejado (ex: unidade de área de hectare para alqueire).
3. Sistema exibe aviso: "Dados existentes serão exibidos na nova unidade. Valores armazenados não são alterados."
4. Owner confirma. Sistema atualiza `ConfiguracaoTenant`.
5. Todos os módulos passam a exibir valores convertidos na nova unidade.

### Fluxo 3: Criação de categoria customizada
1. Owner acessa "Configurações" → "Categorias".
2. Seleciona tipo (despesa, receita, operação ou produto).
3. Clica em "Nova Categoria", preenche nome e opcionalmente seleciona categoria-pai.
4. Categoria é salva com `is_system = false` e disponível em todos os módulos que usam aquele tipo.

## Casos Extremos e Exceções

- **Alteração de ano agrícola com safras em andamento:** Safras existentes mantêm o ano agrícola vigente na criação. Apenas novas safras usam a nova configuração. Exibe aviso claro.
- **Exclusão de categoria customizada em uso:** Bloqueada. Exibe lista de registros vinculados. Alternativa: inativação (soft delete), que oculta a categoria de novas entradas mas mantém nos registros históricos.
- **Fazenda em fuso horário diferente do tenant:** Override por fazenda via `ConfiguracaoFazenda.overrides`. Registros dessa fazenda usam fuso local.
- **Tenant sem configuração (bug):** Sistema aplica defaults (ano jul-jun, hectare, BRL, America/Sao_Paulo) e loga warning.
- **Conversão de unidade com perda de precisão:** Sistema armazena sempre em hectare internamente. Conversão para exibição usa 4 casas decimais.

## Critérios de Aceite (Definition of Done)

- [ ] Wizard de configuração inicial funcional durante onboarding.
- [ ] CRUD de `ConfiguracaoTenant` com validação de campos.
- [ ] Seleção de ano agrícola por mês de início/fim com padrão jul-jun.
- [ ] Suporte a unidades de área: hectare, alqueire paulista, alqueire mineiro, alqueire do norte.
- [ ] CRUD de categorias customizáveis com hierarquia de 2 níveis.
- [ ] Categorias do sistema (`is_system = true`) protegidas contra edição/exclusão.
- [ ] Override de configuração por fazenda via `ConfiguracaoFazenda`.
- [ ] Conversão de unidades aplicada em todos os módulos de exibição.
- [ ] Testes unitários para conversão de unidades (precisão de 4 casas decimais).

## Sugestões de Melhoria Futura

1. **Perfis de configuração reutilizáveis:** Templates de configuração (ex: "Fazenda de grãos no MT", "Pecuária no MS") para agilizar onboarding.
2. **Configuração de casas decimais por contexto:** Permitir que o tenant defina precisão de exibição (2, 3 ou 4 casas) para diferentes contextos (área, peso, moeda).
3. **Calendário agrícola visual:** Timeline interativo do ano-safra com marcos de plantio, manejo e colheita sobrepostos.
4. **Multi-idioma:** Suporte a espanhol e inglês para fazendas com gestores estrangeiros.
5. **Importação de tabela de categorias:** Upload de CSV com categorias customizadas para onboarding em massa.
