---
modulo: "Agr\xEDcola"
submodulo: Safras
nivel: essencial
core: false
dependencias_core:
  - core/auth
  - core/cadastros/fazendas
  - core/cadastros/produtos
  - core/tenant
dependencias_modulos:
  - ../essencial/operacoes-campo.md
standalone: false
complexidade: M
assinante_alvo:
  - pequeno-produtor
  - medio-produtor
  - grande-produtor
  - cooperativa
---

# Safras

## Descricao Funcional

O submodulo de Safras e a espinha dorsal do modulo Agricola. Ele permite criar, acompanhar e encerrar ciclos produtivos (safras) vinculados a talhoes especificos de uma fazenda. Cada safra possui cultura, variedade, datas de inicio/fim previstas, status (planejada, em andamento, colhida, encerrada) e area plantada. A safra funciona como container para todas as operacoes, custos, monitoramentos e colheitas associadas.

O sistema suporta multiplas safras simultaneas por fazenda (safra de verao e safrinha, por exemplo) e permite agrupar talhoes em grupos logicos para facilitar o manejo.

Funcionalidades principais:
- CRUD completo de safras com vinculacao a talhoes
- Kanban visual de safras por status
- Timeline cronologica de eventos da safra
- Grupos de talhoes dentro de uma safra
- Dashboard com KPIs por safra (area, produtividade estimada, custo/ha)
- Navegacao para sub-telas: operacoes, NDVI, orcamento, financeiro, estoque, monitoramento, checklist, fenologia, romaneios, beneficiamento, analises de solo

## Personas — Quem usa este submodulo

- **Produtor Rural:** cria e acompanha suas safras, visualiza progresso e resultados
- **Gerente de Fazenda:** monitora multiplas safras simultaneas, compara desempenho entre talhoes
- **Agronomo:** planeja a safra, define culturas e variedades por talhao, acompanha fenologia
- **Operador de Campo:** consulta qual safra esta ativa em cada talhao para executar operacoes

## Dores que resolve

1. **Falta de historico:** produtores perdem informacoes de safras passadas anotadas em cadernos ou planilhas
2. **Visao fragmentada:** informacoes de custo, operacoes e produtividade ficam espalhadas em sistemas diferentes
3. **Dificuldade de comparacao:** sem dados estruturados, e impossivel comparar safras entre anos ou talhoes
4. **Controle de area:** erros de calculo de area plantada geram distorcoes em custo/ha e produtividade
5. **Multiplas safras:** produtores com safrinha ou culturas consorciadas nao conseguem separar dados

## Regras de Negocio

1. Uma safra pertence a exatamente um tenant (isolamento multi-tenant obrigatorio)
2. Uma safra pode conter um ou mais talhoes da mesma fazenda
3. O status segue o fluxo: `planejada` → `em_andamento` → `colhida` → `encerrada`
4. Nao e permitido reabrir uma safra `encerrada` sem permissao de administrador
5. A area total da safra e a soma das areas dos talhoes vinculados
6. Cada talhao pode estar em no maximo uma safra ativa por cultura simultaneamente
7. Ao encerrar uma safra, todas as operacoes pendentes devem ser finalizadas ou canceladas
8. A exclusao de uma safra so e permitida se nao houver operacoes, romaneios ou lancamentos financeiros vinculados (soft delete preferencial)
9. Datas de inicio e fim devem respeitar a sazonalidade cadastrada para a cultura (warning, nao bloqueio)
10. Permissoes: `agricola:safras:create`, `agricola:safras:read`, `agricola:safras:update`, `agricola:safras:delete`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `Safra` | id, tenant_id, fazenda_id, nome, cultura_id, variedade, data_inicio, data_fim_prevista, data_fim_real, status, area_total_ha, observacoes | pertence a Fazenda, tem muitos Talhoes, tem muitas Operacoes |
| `SafraTalhao` | id, safra_id, talhao_id, area_ha, cultura_id, variedade | vincula Safra a Talhao |
| `GrupoTalhoes` | id, safra_id, nome, cor | agrupa talhoes dentro de uma safra |
| `SafraStatus` | enum: planejada, em_andamento, colhida, encerrada | controla fluxo de vida |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `core/cadastros/fazendas` | Leitura | Obtem fazendas e talhoes disponiveis |
| `core/cadastros/produtos` | Leitura | Obtem culturas e variedades |
| `agricola/operacoes` | Bidirecional | Operacoes sao vinculadas a safra/talhao |
| `agricola/custos` | Leitura | Custos agregados por safra |
| `agricola/romaneios` | Leitura | Produtividade real via romaneios de colheita |
| `financeiro/receitas` | Leitura | Receitas de venda da safra |
| `financeiro/despesas` | Leitura | Despesas vinculadas a safra |

## Fluxo de Uso Principal (step-by-step)

1. Usuario acessa `/agricola/safras` e visualiza lista/kanban de safras
2. Clica em "Nova Safra" e preenche: nome, fazenda, cultura, variedade, data inicio/fim prevista
3. Seleciona os talhoes que participarao da safra e confirma as areas
4. Sistema cria a safra com status `planejada`
5. Quando o plantio inicia, usuario altera status para `em_andamento`
6. Durante a safra, registra operacoes, monitora NDVI, anota caderno de campo
7. Ao iniciar colheita, registra romaneios e acompanha produtividade
8. Quando toda a colheita termina, altera status para `colhida`
9. Apos conciliacao financeira, encerra a safra (`encerrada`)
10. Safra encerrada fica disponivel para consulta historica e comparativos

## Casos Extremos e Excecoes

- **Talhao em duas safras:** se o produtor faz safrinha, o mesmo talhao pode ter safra de soja (jan-abr) e milho safrinha (mar-jul) com sobreposicao de datas — o sistema deve permitir desde que sejam culturas diferentes
- **Safra sem colheita:** perda total por clima ou praga — usuario encerra safra com produtividade zero e justificativa
- **Mudanca de area:** talhao teve parte alagada — permitir ajuste de area efetiva na safra sem alterar cadastro do talhao
- **Safra multi-fazenda:** atualmente nao suportada; cada safra pertence a uma fazenda. Comparativos cross-fazenda sao feitos via dashboard
- **Exclusao de talhao vinculado:** se um talhao e removido do cadastro, safras historicas devem manter referencia (soft delete)
- **Concorrencia:** dois usuarios editando a mesma safra simultaneamente — usar optimistic locking (version field)

## Criterios de Aceite (Definition of Done)

- [ ] CRUD completo de safras com validacao de tenant isolation
- [ ] Vinculacao de talhoes a safra com calculo automatico de area total
- [ ] Transicao de status com validacoes de regra de negocio
- [ ] Kanban visual funcional com drag-and-drop de status
- [ ] Timeline cronologica renderizando eventos da safra
- [ ] Dashboard com KPIs: area total, produtividade estimada vs real, custo/ha
- [ ] Navegacao para todas as sub-telas da safra (operacoes, NDVI, etc.)
- [ ] Testes de integracao cobrindo tenant isolation
- [ ] Permissoes RBAC aplicadas em todas as rotas
- [ ] Paginacao e filtros (por status, cultura, fazenda, periodo)

## Sugestoes de Melhoria Futura

1. **Safra multi-fazenda:** permitir safras que englobem talhoes de fazendas diferentes do mesmo tenant
2. **Templates de safra:** criar safras a partir de templates com operacoes pre-configuradas
3. **Comparativo entre safras:** dashboard dedicado para comparar KPIs entre safras/anos
4. **Integracao clima:** vincular dados meteorologicos automaticamente ao periodo da safra
5. **Exportacao:** gerar relatorio PDF/Excel da safra completa para bancos e seguradoras
6. **Alertas automaticos:** notificar quando uma safra passa da data prevista de colheita sem romaneios
