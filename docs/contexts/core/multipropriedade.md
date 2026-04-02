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

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Gerencia o portfólio de fazendas, visualiza dashboards consolidados, controla custos e resultados de todas as propriedades.
- **Gestor Regional:** Supervisiona um grupo de fazendas em uma região, com permissões de gestão em múltiplas propriedades.
- **Gestor de Fazenda:** Acessa apenas a(s) fazenda(s) sob sua responsabilidade. Não visualiza dados de outras propriedades.
- **Colaborador Multi-fazenda:** Presta serviço em mais de uma fazenda (ex: veterinário itinerante, técnico de manutenção), com perfis diferentes por propriedade.

## Dores que resolve

1. **Gestão fragmentada:** Proprietários com múltiplas fazendas usam planilhas separadas ou instâncias diferentes de software para cada propriedade, impossibilitando visão consolidada.
2. **Vazamento de dados entre fazendas:** Sem isolamento adequado, colaboradores de uma fazenda podem ver dados de outra inadvertidamente.
3. **Permissões inflexíveis:** Um usuário que precisa de perfil "admin" em uma fazenda e "visualizador" em outra não consegue ter isso com perfis globais.
4. **Relatórios manuais:** Consolidar resultados de múltiplas fazendas exige exportações manuais e planilhas complexas.
5. **Custo de múltiplas assinaturas:** Sem multipropriedade, o assinante precisaria de uma conta separada para cada fazenda.

## Regras de Negócio

1. **RN-MP-001:** O número máximo de fazendas por tenant é definido pelo plano contratado (campo `max_fazendas` no plano).
2. **RN-MP-002:** Cada fazenda possui dados completamente isolados. Queries sempre incluem filtro `fazenda_id` além do `tenant_id`.
3. **RN-MP-003:** O seletor de fazendas no header mostra apenas fazendas em que o usuário tem vínculo (`FazendaUsuario`). Owner vê todas.
4. **RN-MP-004:** Dashboards consolidados estão disponíveis apenas para usuários com permissão `core:dashboard:consolidado` ou flag `is_owner`.
5. **RN-MP-005:** Ao criar uma nova fazenda, o Owner é automaticamente vinculado com perfil de administrador.
6. **RN-MP-006:** Transferência de fazenda entre tenants não é permitida via interface. Requer operação manual de backoffice com audit trail completo.
7. **RN-MP-007:** A opção "Todas as fazendas" no seletor de contexto só exibe dados de leitura (relatórios). Operações de escrita exigem fazenda específica selecionada.
8. **RN-MP-008:** Inativação de fazenda preserva todos os dados históricos mas remove do seletor de contexto e dos dashboards consolidados.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Fazenda` | id, tenant_id, nome, is_active, created_at | → Tenant, → FazendaUsuario[], → Talhao[] |
| `FazendaUsuario` | id, usuario_id, fazenda_id, perfil_fazenda_id, is_default | → Usuario, → Fazenda, → PerfilAcesso |
| `Tenant` | id, nome, plano_id, max_fazendas | → Fazenda[], → Usuario[] |
| `FazendaContexto` (runtime) | fazenda_id ativo na sessão do usuário | Derivado do JWT / seletor de contexto |

## Integrações Necessárias

- **Identidade e Acesso:** Perfis por fazenda via `FazendaUsuario.perfil_fazenda_id` e troca de contexto com re-emissão de JWT.
- **Planos e Assinatura:** Verificação de limite `max_fazendas` antes de permitir novo cadastro.
- **Todos os módulos de negócio:** Cada módulo deve respeitar o `fazenda_id` do contexto atual para filtrar dados.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Adição de nova fazenda ao portfólio
1. Owner acessa "Propriedades" → "Nova Propriedade".
2. Sistema verifica se `count(fazendas_ativas) < plano.max_fazendas`.
3. Se dentro do limite, prossegue com cadastro (ver Cadastro da Propriedade).
4. Se no limite, exibe mensagem: "Limite de propriedades atingido. Faça upgrade do plano."
5. Após cadastro, Owner é automaticamente vinculado via `FazendaUsuario` com perfil admin.
6. Nova fazenda aparece no seletor de contexto do header.

### Fluxo 2: Troca de contexto entre fazendas
1. Usuário clica no seletor de fazendas no header da aplicação.
2. Lista exibe fazendas vinculadas ao usuário via `FazendaUsuario` + opção "Todas" (se permitido).
3. Usuário seleciona fazenda destino.
4. Frontend envia `fazenda_id` ao backend.
5. Backend carrega `perfil_fazenda_id` (se existir override) e re-emite JWT com contexto atualizado.
6. Frontend recarrega dados do dashboard com escopo da fazenda selecionada.

### Fluxo 3: Dashboard consolidado
1. Owner seleciona "Todas as fazendas" no seletor de contexto.
2. Backend agrega dados de todas as fazendas ativas do tenant.
3. Dashboard exibe: área total sob gestão, receita consolidada, despesas por fazenda, alertas pendentes por propriedade.
4. Widgets são clicáveis — ao clicar em uma fazenda específica, troca o contexto automaticamente.

## Casos Extremos e Exceções

- **Usuário vinculado a apenas 1 fazenda:** Seletor de contexto fica oculto. Contexto é fixo na única fazenda disponível.
- **Owner remove último vínculo de um usuário:** Usuário perde acesso ao tenant (se não tiver vínculo com nenhuma fazenda). Sistema exibe confirmação antes de remover.
- **Fazenda inativada com usuários exclusivos:** Usuários que só tinham vínculo com a fazenda inativada ficam sem acesso. Sistema notifica o Owner para realocá-los.
- **Plano sofre downgrade e número de fazendas excede novo limite:** Fazendas existentes permanecem ativas (grandfather clause), mas criação de novas é bloqueada até adequação.
- **Concorrência no seletor de contexto:** Dois tabs do navegador com fazendas diferentes — cada aba mantém seu próprio contexto via JWT independente.
- **Migração de dados entre fazendas:** Não suportada automaticamente. Operação manual via backoffice para cenários como fusão de propriedades.

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

## Sugestões de Melhoria Futura

1. **Grupos de fazendas:** Permitir agrupamento lógico (ex: "Fazendas do Mato Grosso", "Fazendas Pecuárias") para dashboards por grupo.
2. **Comparativo entre fazendas:** Relatório side-by-side de produtividade, custos e margens entre propriedades.
3. **Mapa do portfólio:** Visualização geográfica de todas as fazendas com indicadores sobrepostos (saúde financeira, status de safra).
4. **Benchmark anônimo:** Comparação de desempenho (produtividade por hectare) com a média regional de fazendas similares na plataforma.
5. **Transferência assistida de fazenda:** Workflow de transferência de propriedade entre tenants com aceite do destinatário e migração automática de dados.
