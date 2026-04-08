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

Este submódulo resolve um problema crítico do agronegócio brasileiro: a diversidade de unidades e convenções regionais. Um produtor de Mato Grosso trabalha com hectares e ano-safra julho-junho, enquanto um de Minas Gerais usa alqueire mineiro e outubro-setembro. Sem configuração centralizada, cada módulo precisaria pedir essas informações, gerando inconsistência.

As configurações são herdadas por todas as fazendas do tenant, mas podem ter override por fazenda quando necessário (ex: fazenda em estado com fuso horário diferente).

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Define configurações iniciais durante o onboarding e ajusta conforme necessidade. Precisa de flexibilidade para adaptar o sistema à realidade da propriedade.

- **Gestor de Fazenda:** Consulta configurações para entender unidades e períodos aplicados. Pode sugerir ajustes ao Owner mas não altera configurações globais.

- **Contador / Financeiro:** Depende da configuração de moeda e ano fiscal para fechamentos e relatórios. Precisa de consistência para apuração de ITR, LCDPR e DAP.

- **Agrônomo:** Consulta definição de ano agrícola para planejamento de safras. Épocas de plantio/colheita são vinculadas ao ano-safra configurado.

- **Operador de Campo:** Visualiza unidades configuradas (ha, alqueire) em ordens de serviço e registros. Precisa de clareza para evitar erros de aplicação.

- **Backoffice da Plataforma:** Acessa configurações de todos os tenants para suporte e troubleshooting. Identifica problemas de configuração que geram inconsistência de dados.

## Dores que resolve

1. **Inconsistência de unidades:** Sem padronização, um módulo calcula em hectares e outro em alqueires, causando erros em relatórios consolidados. Produtor não sabe qual valor está correto.

2. **Ano agrícola vs. ano civil:** O agronegócio brasileiro trabalha com ano-safra (jul/jun ou out/set), não com ano civil. Relatórios precisam respeitar esse ciclo para apuração correta de custos e receitas.

3. **Fuso horário incorreto:** Operações registradas com timestamp UTC sem conversão geram confusão em horários de aplicação de defensivos e ordenha. Exemplo: pulverização registrada às 22h (UTC) quando foi às 19h (local).

4. **Categorias rígidas:** Categorias fixas de despesas/receitas não atendem à diversidade de operações rurais regionais. Exemplo: "Frete" pode ser despesa ou custo de produção dependendo do contexto.

5. **Reconfiguração repetitiva:** Sem configuração centralizada, cada módulo pede as mesmas informações. Onboarding se torna lento e propenso a erros.

6. **Conversão manual de unidades:** Produtor anota em hectares, calculadora usa alqueire, relatório final em hectare. Conversões manuais introduzem erros de arredondamento.

7. **Relatórios fora do período fiscal:** ITR e outras obrigações usam período específico. Sem configuração de ano agrícola, relatórios não batem com obrigações acessórias.

## Regras de Negócio

1. **RN-CG-001:** O ano agrícola é definido por mês de início e mês de fim (ex: julho a junho). Padrão: julho a junho. Período deve ter 12 meses consecutivos.

2. **RN-CG-002:** A unidade de área padrão é hectare. Unidades alternativas suportadas: alqueire paulista (2,42 ha), alqueire mineiro (4,84 ha), alqueire do norte (2,72 ha). Fatores de conversão são fixos conforme INCRA.

3. **RN-CG-003:** A moeda padrão é BRL (Real). Conversão para USD e EUR disponível em relatórios (cotação consultada via API BCB). Valores são armazenados em centavos no banco.

4. **RN-CG-004:** O fuso horário padrão é o da UF da fazenda principal. Pode ser sobrescrito manualmente. Fusos suportados: America/Sao_Paulo, America/Cuiaba, America/Manaus, America/Boa_Vista, America/Porto_Velho.

5. **RN-CG-005:** Categorias customizáveis são do tipo hierárquico (categoria → subcategoria) com no máximo 2 níveis. Exemplo: "Insumos" (categoria) → "Fertilizantes" (subcategoria).

6. **RN-CG-006:** Categorias do sistema (prefixadas com `sys_`) não podem ser editadas ou excluídas pelo tenant. Exemplo: `sys_despesa_operacional`, `sys_receita_venda`.

7. **RN-CG-007:** Alteração do ano agrícola não retroage sobre safras já criadas. Aplica-se apenas a novas safras. Sistema exibe aviso claro antes de alterar.

8. **RN-CG-008:** Configurações são herdadas por todas as fazendas do tenant, mas podem ter override por fazenda quando indicado (ex: fuso horário diferente).

9. **RN-CG-009:** Casas decimais de exibição: área (4 casas), peso (3 casas), moeda (2 casas), percentual (2 casas). Armazenamento interno usa precisão máxima do tipo Decimal.

10. **RN-CG-010:** Idioma padrão é português brasileiro (pt-BR). Inglês e espanhol são suportados na interface mas não em documentos fiscais.

11. **RN-CG-011:** Formato de data é DD/MM/AAAA (padrão brasileiro). Não é customizável em documentos fiscais.

12. **RN-CG-012:** Primeira configuração é obrigatória no onboarding. Tenant não acessa módulos de negócio sem configurar: ano agrícola, unidade de área, moeda e fuso horário.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `ConfiguracaoTenant` | id (UUID), tenant_id (UUID FK unique), ano_agricola_inicio (Integer 1-12), ano_agricola_fim (Integer 1-12), unidade_area (Enum: hectare/alqueire_paulista/alqueire_mineiro/alqueire_norte), moeda (Char 3: BRL/USD/EUR), fuso_horario (String 50), idioma (Char 5: pt-BR/en/es), casas_decimais_area (Integer default 4), casas_decimais_peso (Integer default 3), created_at (DateTime), updated_at (DateTime) | → Tenant, → ConfiguracaoFazenda[] |
| `ConfiguracaoFazenda` | id (UUID), fazenda_id (UUID FK unique), tenant_id (UUID FK), overrides (JSONB), updated_at (DateTime) | → Fazenda, → ConfiguracaoTenant |
| `CategoriaCustom` | id (UUID), tenant_id (UUID FK), tipo (Enum: despesa/receita/operacao/produto/insumo), nome (String 100), slug (String 100), parent_id (UUID FK nullable), is_system (Boolean), ordem (Integer), cor_hex (String 7), icone (String 50), is_active (Boolean), created_at (DateTime) | → Tenant, → CategoriaCustom (self-ref para subcategorias) |
| `UnidadeMedida` | id (UUID), tenant_id (UUID FK), nome (String 50), sigla (String 10), tipo (Enum: area/peso/volume/comprimento), fator_conversao_base (Decimal 12,6), is_system (Boolean), is_active (Boolean) | → Tenant |
| `HistoricoConfiguracao` | id (UUID), tenant_id (UUID FK), campo_alterado (String 50), valor_anterior (JSONB), valor_novo (JSONB), alterado_por (UUID FK), alterado_em (DateTime) | → Tenant, → Usuario |

## Integrações Necessárias

- **API de Cotação (BCB / Open Exchange Rates):** Conversão de moeda em relatórios multi-moeda. Cotação do dia ou histórica para fechamentos.

- **Todos os módulos de negócio:** Consomem `ConfiguracaoTenant` para unidades, fuso horário e categorias. Módulos leem configuração em cache (Redis) para performance.

- **Módulo Agrícola:** Consome `ano_agricola_inicio` e `ano_agricola_fim` para criação de safras. Safra é vinculada ao ano agrícola vigente na data de plantio.

- **Módulo Financeiro:** Consome `moeda` e categorias de despesa/receita. Lançamentos usam categorias configuradas.

- **Módulo Pecuária:** Consome unidades de peso (kg, @, tonelada) e conversões configuradas.

- **Relatórios e Dashboards:** Aplicam conversão de unidades na exibição. Dados são armazenados em unidade base (hectare, kg, BRL) e convertidos sob demanda.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Configuração inicial (onboarding)
1. Após cadastro do tenant, sistema exibe wizard de configuração inicial (obrigatório).
2. **Passo 1 — Ano agrícola:** Usuário seleciona mês de início e fim em dropdowns. Sugestão padrão: jul-jun exibida em destaque.
3. **Passo 2 — Unidade de área:** Seleciona unidade principal (hectare, alqueire paulista, alqueire mineiro, alqueire do norte). Sistema exibe fator de conversão para hectare.
4. **Passo 3 — Moeda e fuso:** Moeda BRL preenchida automaticamente. Fuso sugerido pela UF da primeira fazenda (se cadastrada) ou America/Sao_Paulo como default.
5. **Passo 4 — Categorias:** Exibe categorias do sistema pré-carregadas. Permite adicionar categorias customizadas ou pular.
6. **Passo 5 — Revisão:** Resumo das configurações selecionadas. Usuário confirma.
7. Sistema salva `ConfiguracaoTenant` e redireciona ao dashboard.
8. Wizard não pode ser ignorado — módulos de negócio permanecem bloqueados até configuração.

### Fluxo 2: Ajuste de configuração existente
1. Owner acessa "Configurações" no menu lateral.
2. Altera parâmetro desejado (ex: unidade de área de hectare para alqueire).
3. Sistema exibe aviso: "Dados existentes serão exibidos na nova unidade. Valores armazenados não são alterados. Exemplo: 100,0000 ha será exibido como 41,3223 alq. paulista."
4. Owner confirma. Sistema atualiza `ConfiguracaoTenant` e registra em `HistoricoConfiguracao`.
5. Todos os módulos passam a exibir valores convertidos na nova unidade.
6. Relatórios já gerados não são recalculados retroativamente.

### Fluxo 3: Criação de categoria customizada
1. Owner acessa "Configurações" → "Categorias".
2. Seleciona tipo (despesa, receita, operação ou produto).
3. Clica em "Nova Categoria", preenche nome e opcionalmente seleciona categoria-pai.
4. Opcionalmente define cor e ícone para identificação visual.
5. Categoria é salva com `is_system = false` e slug único (gerado automaticamente).
6. Categoria fica disponível em todos os módulos que usam aquele tipo.
7. Subcategorias podem ser criadas sob a categoria pai (máximo 2 níveis).

### Fluxo 4: Override de configuração por fazenda
1. Owner acessa detalhes da fazenda → aba "Configurações".
2. Clica em "Personalizar Configurações".
3. Seleciona quais configurações sobrescrever (ex: apenas fuso horário).
4. Define valor específico para aquela fazenda.
5. Sistema salva em `ConfiguracaoFazenda.overrides` como JSONB.
6. Quando usuário está no contexto daquela fazenda, sistema aplica overrides.

## Casos Extremos e Exceções

- **Alteração de ano agrícola com safras em andamento:** Safras existentes mantêm o ano agrícola vigente na criação. Apenas novas safras usam a nova configuração. Exibe aviso claro: "X safras ativas permanecerão no ano agrícola atual."

- **Exclusão de categoria customizada em uso:** Bloqueada. Exibe lista de registros vinculados: "Esta categoria está em uso em 15 lançamentos financeiros. Inative ao invés de excluir." Alternativa: inativação (soft delete), que oculta a categoria de novas entradas mas mantém nos registros históricos.

- **Fazenda em fuso horário diferente do tenant:** Override por fazenda via `ConfiguracaoFazenda.overrides`. Registros dessa fazenda usam fuso local. Exemplo: tenant em São Paulo (America/Sao_Paulo) tem fazenda em Mato Grosso (America/Cuiaba).

- **Tenant sem configuração (bug):** Sistema aplica defaults (ano jul-jun, hectare, BRL, America/Sao_Paulo) e loga warning. Backoffice é notificado para regularizar.

- **Conversão de unidade com perda de precisão:** Sistema armazena sempre em unidade base (hectare, kg, centavos) internamente. Conversão para exibição usa casas decimais configuradas (padrão: 4 para área).

- **Categoria com nome duplicado:** Validação impede nomes duplicados dentro do mesmo tipo e tenant. Mensagem: "Já existe uma categoria de despesa com este nome."

- **Mudança de moeda com lançamentos existentes:** Permitida, mas valores históricos permanecem na moeda original. Relatórios multi-moeda convertem valores históricos usando cotação da data do lançamento.

- **Configuração inválida detectada:** Sistema valida configurações periodicamente. Se detecta inconsistência (ex: ano agrícola com 13 meses), notifica Owner e backoffice.

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
- [ ] Histórico de alterações de configuração registrado em `HistoricoConfiguracao`.
- [ ] Validação de ano agrícola (período de 12 meses consecutivos).
- [ ] Cache de configurações em Redis para performance.

## Sugestões de Melhoria Futura

1. **Perfis de configuração reutilizáveis:** Templates de configuração (ex: "Fazenda de grãos no MT", "Pecuária no MS", "Café em MG") para agilizar onboarding de novos tenants com perfis similares.

2. **Configuração de casas decimais por contexto:** Permitir que o tenant defina precisão de exibição (2, 3 ou 4 casas) para diferentes contextos (área, peso, moeda, percentual).

3. **Calendário agrícola visual:** Timeline interativo do ano-safra com marcos de plantio, manejo e colheita sobrepostos. Exportação para Google Calendar/Outlook.

4. **Multi-idioma:** Suporte a espanhol e inglês para fazendas com gestores estrangeiros. Tradução de interface e relatórios, exceto documentos fiscais (sempre em pt-BR).

5. **Importação de tabela de categorias:** Upload de CSV com categorias customizadas para onboarding em massa. Template disponível para download.

6. **Sugestão automática de configuração:** Sistema analisa primeira fazenda cadastrada e sugere configurações baseadas em UF, tipo de produção e região.

7. **Validação de conformidade fiscal:** Alerta se configurações estão em desacordo com normas da Receita Federal (ex: ano agrícola diferente do exigido para ITR).

8. **Exportação de configurações:** Backup das configurações em JSON para migração entre tenants ou restauração.
