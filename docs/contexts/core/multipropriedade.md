---
modulo: Core
submodulo: Multipropriedade
nivel: core
core: true
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos: []
standalone: false
complexidade: M
assinante_alvo: todos os assinantes
---

# Multipropriedade

## Descrição Funcional

Submódulo que permite a um assinante gerenciar múltiplas fazendas sob uma única conta, com isolamento completo de dados entre propriedades e dashboard consolidado no nível do tenant. Cada fazenda opera como uma unidade independente com seus próprios talhões, safras, rebanhos e operações, enquanto relatórios consolidados oferecem visão estratégica do portfólio de propriedades. Permissões podem ser configuradas por propriedade, permitindo que um agrônomo tenha acesso total a uma fazenda e somente leitura em outra.

Este submódulo foi desenhado para a realidade do produtor rural brasileiro médio que possui 3-5 propriedades em municípios ou estados diferentes. Exemplo comum: produtor de soja em Mato Grosso com fazendas em Sorriso, Lucas do Rio Verde e Nova Mutum — cada uma com equipe local, custos e produtividade específicos, mas necessitando de visão consolidada para tomada de decisão.

O isolamento de dados é rigoroso: um colaborador vinculado apenas à Fazenda A não pode ver dados da Fazenda B, mesmo pertencendo ao mesmo tenant. O seletor de contexto no header permite troca rápida entre propriedades sem novo login.

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Gerencia o portfólio de fazendas, visualiza dashboards consolidados, controla custos e resultados de todas as propriedades. Toma decisões estratégicas baseadas em performance comparada entre fazendas.

- **Gestor Regional:** Supervisiona um grupo de fazendas em uma região, com permissões de gestão em múltiplas propriedades. Exemplo: gestor responsável por 3 fazendas no norte de Mato Grosso.

- **Gestor de Fazenda:** Acessa apenas a(s) fazenda(s) sob sua responsabilidade. Não visualiza dados de outras propriedades. Foco na operação diária da sua unidade.

- **Colaborador Multi-fazenda:** Presta serviço em mais de uma fazenda (ex: veterinário itinerante, técnico de manutenção, agrônomo consultor), com perfis diferentes por propriedade. Pode ser "Editor" na Fazenda A e "Visualizador" na Fazenda B.

- **Contador do Grupo:** Acessa todas as fazendas com perfil de visualizador para fechamento contábil consolidado. Precisa de visão transversal para apuração de ITR e LCDPR.

- **Investidor / Sócio:** Visualizador de todas as fazendas com acesso apenas a dashboards financeiros e indicadores de produtividade. Não opera o sistema.

## Dores que resolve

1. **Gestão fragmentada:** Proprietários com múltiplas fazendas usam planilhas separadas ou instâncias diferentes de software para cada propriedade, impossibilitando visão consolidada. Produtor não sabe qual fazenda é mais rentável.

2. **Vazamento de dados entre fazendas:** Sem isolamento adequado, colaboradores de uma fazenda podem ver dados de outra inadvertidamente. Exemplo: gerente da Fazenda A acessa custos da Fazenda B e compara salários.

3. **Permissões inflexíveis:** Um usuário que precisa de perfil "admin" em uma fazenda e "visualizador" em outra não consegue ter isso com perfis globais. Sistema exige vínculo por fazenda com perfil específico.

4. **Relatórios manuais:** Consolidar resultados de múltiplas fazendas exige exportações manuais e planilhas complexas. Produtor perde 2-3 dias no fechamento mensal.

5. **Custo de múltiplas assinaturas:** Sem multipropriedade, o assinante precisaria de uma conta separada para cada fazenda, pagando 3-5 assinaturas. Modelo de pricing por tenant é mais justo.

6. **Troca de contexto lenta:** Sem seletor de contexto, usuário precisa fazer logout/login para acessar outra fazenda. Perda de produtividade e risco de operar na fazenda errada.

7. **Benchmarking interno impossível:** Sem dados consolidados, produtor não compara produtividade, custos e margens entre fazendas similares. Decisões baseadas em "feeling" ao invés de dados.

## Regras de Negócio

1. **RN-MP-001:** O número máximo de fazendas por tenant é definido pelo plano contratado (campo `max_fazendas` no plano). Plano Essencial: 3 fazendas, Profissional: 10 fazendas, Enterprise: ilimitado.

2. **RN-MP-002:** Cada fazenda possui dados completamente isolados. Queries sempre incluem filtro `fazenda_id` além do `tenant_id`. `BaseService` injeta ambos automaticamente.

3. **RN-MP-003:** O seletor de fazendas no header mostra apenas fazendas em que o usuário tem vínculo (`FazendaUsuario`). Owner vê todas as fazendas ativas do tenant.

4. **RN-MP-004:** Dashboards consolidados estão disponíveis apenas para usuários com permissão `core:dashboard:consolidado` ou flag `is_owner`. Colaboradores operacionais não acessam consolidado.

5. **RN-MP-005:** Ao criar uma nova fazenda, o Owner é automaticamente vinculado via `FazendaUsuario` com perfil de administrador. Vínculo não pode ser removido se for único owner.

6. **RN-MP-006:** Transferência de fazenda entre tenants não é permitida via interface. Requer operação manual de backoffice com audit trail completo e aprovação jurídica.

7. **RN-MP-007:** A opção "Todas as fazendas" no seletor de contexto só exibe dados de leitura (relatórios). Operações de escrita exigem fazenda específica selecionada.

8. **RN-MP-008:** Inativação de fazenda preserva todos os dados históricos mas remove do seletor de contexto e dos dashboards consolidados. Fazenda inativa pode ser reativada.

9. **RN-MP-009:** Usuário pode ter vínculo com 0 (zero) fazendas — caso de backoffice ou contador que acessa apenas relatórios consolidados.

10. **RN-MP-010:** Limite de fazendas é verificado no momento do cadastro. Se `count(fazendas_ativas) >= max_fazendas`, sistema bloqueia com mensagem de upgrade.

11. **RN-MP-011:** Downgrade de plano com número de fazendas acima do novo limite é permitido (grandfather clause), mas criação de novas fazendas é bloqueada até adequação.

12. **RN-MP-012:** Exclusão de tenant em cascata inativa todas as fazendas vinculadas. Dados são preservados por 90 dias para exportação.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Fazenda` | id (UUID), tenant_id (UUID FK), nome (String 100), is_active (Boolean), created_at (DateTime) | → Tenant, → FazendaUsuario[], → Talhao[], → ImovelRural[] |
| `FazendaUsuario` | id (UUID), usuario_id (UUID FK), fazenda_id (UUID FK), perfil_fazenda_id (UUID FK), is_default (Boolean), data_vinculo (Date), data_expiracao (Date nullable) | → Usuario, → Fazenda, → PerfilAcesso |
| `Tenant` | id (UUID), nome (String), plano_id (UUID FK), max_fazendas (Integer), status (Enum), created_at (DateTime) | → Fazenda[], → Usuario[], → Plano |
| `FazendaContexto` (runtime) | fazenda_id ativo na sessão do usuário, tenant_id, perfil_fazenda_id efetivo | Derivado do JWT / seletor de contexto — não persistido |
| `DashboardConsolidado` (view) | tenant_id, fazenda_id, area_total_ha, custo_total, receita_total, margem_percentual | View materializada atualizada diariamente |

## Integrações Necessárias

- **Identidade e Acesso:** Perfis por fazenda via `FazendaUsuario.perfil_fazenda_id` e troca de contexto com re-emissão de JWT.

- **Planos e Assinatura:** Verificação de limite `max_fazendas` antes de permitir novo cadastro. Upgrade de plano libera limite imediatamente.

- **Todos os módulos de negócio:** Cada módulo deve respeitar o `fazenda_id` do contexto atual para filtrar dados. Queries sem `fazenda_id` só são permitidas em dashboards consolidados.

- **Notificações e Alertas:** Alertas de limite de fazendas (80% do máximo) e notificação de upgrade necessário.

- **Banco de Dados (PostgreSQL):** Views materializadas para dashboards consolidados com atualização agendada (diária ou sob demanda).

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Adição de nova fazenda ao portfólio
1. Owner acessa "Propriedades" → "Nova Propriedade".
2. Sistema verifica se `count(fazendas_ativas) < plano.max_fazendas`.
3. Se dentro do limite, prossegue com cadastro (ver Cadastro da Propriedade).
4. Se no limite, exibe mensagem: "Limite de propriedades atingido (X fazendas). Faça upgrade do plano para adicionar mais propriedades."
5. Botão "Ver Planos" redireciona para página de assinatura.
6. Após cadastro, Owner é automaticamente vinculado via `FazendaUsuario` com perfil admin.
7. Nova fazenda aparece no seletor de contexto do header.

### Fluxo 2: Troca de contexto entre fazendas
1. Usuário clica no seletor de fazendas no header da aplicação (dropdown).
2. Lista exibe fazendas vinculadas ao usuário via `FazendaUsuario` + opção "Todas" (se Owner ou com permissão).
3. Cada item mostra nome da fazenda, município/UF e status (ativa/inativa).
4. Usuário seleciona fazenda destino.
5. Frontend envia `fazenda_id` ao backend via endpoint `/api/v1/auth/trocar-contexto`.
6. Backend carrega `perfil_fazenda_id` (se existir override) e re-emite JWT com contexto atualizado.
7. Frontend substitui token e recarrega dados do dashboard com escopo da fazenda selecionada.
8. URL muda para incluir `fazenda_id` (ex: `/fazenda/{id}/dashboard`).

### Fluxo 3: Dashboard consolidado
1. Owner seleciona "Todas as fazendas" no seletor de contexto.
2. Backend agrega dados de todas as fazendas ativas do tenant.
3. Dashboard exibe: área total sob gestão (soma de todas as fazendas), receita consolidada, despesas por fazenda, alertas pendentes por propriedade.
4. Widgets são clicáveis — ao clicar em uma fazenda específica no gráfico, troca o contexto automaticamente.
5. Comparativo de produtividade entre fazendas é exibido em ranking.
6. Botão "Exportar Consolidado" gera PDF/Excel com resumo do portfólio.

### Fluxo 4: Configuração de permissões por fazenda
1. Owner acessa "Usuários" → seleciona usuário → aba "Fazendas".
2. Lista de fazendas do tenant é exibida com checkboxes e seletor de perfil por fazenda.
3. Owner marca fazendas em que o usuário terá acesso e seleciona perfil para cada.
4. Exemplo: "João" tem perfil "Gerente" na Fazenda A, "Visualizador" na Fazenda B, sem acesso na Fazenda C.
5. Sistema cria/atualiza registros em `FazendaUsuario` para cada vínculo.
6. Usuário verá apenas fazendas marcadas no seletor de contexto.

## Casos Extremos e Exceções

- **Usuário vinculado a apenas 1 fazenda:** Seletor de contexto fica oculto. Contexto é fixo na única fazenda disponível. Exceção: Owner sempre vê seletor mesmo com 1 fazenda.

- **Owner remove último vínculo de um usuário:** Usuário perde acesso ao tenant (se não tiver vínculo com nenhuma fazenda). Sistema exibe confirmação antes de remover: "Este usuário perderá acesso ao tenant. Confirmar?"

- **Fazenda inativada com usuários exclusivos:** Usuários que só tinham vínculo com a fazenda inativada ficam sem acesso. Sistema notifica o Owner para realocá-los: "3 usuários perderam acesso. Vincule-os a outra fazenda."

- **Plano sofre downgrade e número de fazendas excede novo limite:** Fazendas existentes permanecem ativas (grandfather clause), mas criação de novas é bloqueada até adequação. Owner recebe notificação: "Você tem X fazendas mas seu plano atual permite Y. Exclua ou inative Z fazendas para criar novas."

- **Concorrência no seletor de contexto:** Dois tabs do navegador com fazendas diferentes — cada aba mantém seu próprio contexto via JWT independente. Troca em uma aba não afeta a outra.

- **Migração de dados entre fazendas:** Não suportada automaticamente. Operação manual via backoffice para cenários como fusão de propriedades ou transferência de talhões.

- **Usuário com 0 fazendas vinculadas:** Caso de contador ou backoffice. Seletor exibe apenas "Todas as fazendas" (consolidado). Operações de escrita são bloqueadas.

- **Fazenda com dados inconsistentes (bug):** Dashboard consolidado detecta anomalias (ex: área negativa) e exclui fazenda do cálculo, notificando backoffice.

## Critérios de Aceite (Definition of Done)

- [ ] Seletor de contexto de fazenda funcional no header, listando apenas fazendas com vínculo.
- [ ] Troca de contexto re-emite JWT com `fazenda_id` e `perfil_fazenda_id` corretos.
- [ ] Verificação de limite `max_fazendas` antes de permitir cadastro de nova propriedade.
- [ ] Dashboard consolidado ("Todas as fazendas") com dados agregados para Owner.
- [ ] Isolamento completo de dados por `fazenda_id` em todos os módulos de negócio.
- [ ] Perfis por fazenda funcionais — override de permissões ao trocar contexto.
- [ ] Opção "Todas as fazendas" restrita a leitura (sem operações de escrita).
- [ ] Testes de isolamento garantindo que dados de Fazenda A não vazam para Fazenda B.
- [ ] Inativação de fazenda preservando dados históricos.
- [ ] Notificação de limite de fazendas atingido (80% e 100%).
- [ ] View materializada de dashboard consolidado atualizada diariamente.

## Sugestões de Melhoria Futura

1. **Grupos de fazendas:** Permitir agrupamento lógico (ex: "Fazendas do Mato Grosso", "Fazendas Pecuárias", "Fazendas Arrendadas") para dashboards por grupo e permissões em lote.

2. **Comparativo entre fazendas:** Relatório side-by-side de produtividade, custos e margens entre propriedades selecionadas. Benchmarking interno com ranking.

3. **Mapa do portfólio:** Visualização geográfica de todas as fazendas com indicadores sobrepostos (saúde financeira, status de safra, alertas pendentes).

4. **Benchmark anônimo:** Comparação de desempenho (produtividade por hectare) com a média regional de fazendas similares na plataforma. Dados anonimizados e agregados.

5. **Transferência assistida de fazenda:** Workflow de transferência de propriedade entre tenants com aceite do destinatário e migração automática de dados.

6. **Herança de configurações:** Configurações padrão (categorias, unidades) são herdadas da "fazenda modelo" para novas propriedades, acelerando onboarding.

7. **Alertas cross-fazenda:** Notificação quando uma fazenda tem desempenho significativamente inferior à média do grupo (detecção automática de anomalias).

8. **Rateio de custos compartilhados:** Custos de máquinas/equipe que atendem múltiplas fazendas são rateados proporcionalmente à área ou uso.
