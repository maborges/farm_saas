---
modulo: "Agrícola"
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

## Descrição Funcional

O submódulo de Safras é a espinha dorsal do módulo Agrícola. Ele permite criar, acompanhar e encerrar ciclos produtivos (safras) vinculados a talhões específicos de uma fazenda. Cada safra possui cultura, variedade, datas de início/fim previstas, status (planejada, em andamento, colhida, encerrada) e área plantada. A safra funciona como container para todas as operações, custos, monitoramentos e colheitas associadas.

O sistema suporta múltiplas safras simultâneas por fazenda (safra de verão e safrinha, por exemplo) e permite agrupar talhões em grupos lógicos para facilitar o manejo.

### Contexto Brasileiro

No Brasil, o sistema foi desenhado para atender a realidade da **safra dupla** predominante no Cerrado:

- **1ª Safra (Verão)**: Soja plantada entre outubro e dezembro, colhida entre janeiro e março
- **2ª Safra (Safrinha)**: Milho ou algodão plantado imediatamente após a colheita da soja (janela crítica de 30-45 dias)

O produtor do MATOPIBA (região que engloba Maranhão, Tocantins, Piauí e Bahia) enfrenta janelas ainda mais apertadas devido ao regime de chuvas, tornando o controle preciso de datas crítico para o sucesso da safra.

Funcionalidades principais:
- CRUD completo de safras com vinculação a talhões
- Kanban visual de safras por status
- Timeline cronológica de eventos da safra
- Grupos de talhões dentro de uma safra
- Dashboard com KPIs por safra (área, produtividade estimada, custo/ha)
- Navegação para sub-telas: operações, NDVI, orçamento, financeiro, estoque, monitoramento, checklist, fenologia, romaneios, beneficiamento, análises de solo

## Personas — Quem usa este submódulo

- **Produtor Rural (MT/GO/BA)**: Cria e acompanha suas safras de soja e milho safrinha, visualiza progresso e resultados para tomada de decisão de venda
- **Gerente de Fazenda (MATOPIBA)**: Monitora múltiplas safras simultâneas, compara desempenho entre talhões de 5000+ hectares
- **Agrônomo (Cooperativa - PR/RS)**: Planeja a safra, define culturas e variedades por talhão, acompanha fenologia para recomendação de defensivos
- **Operador de Campo**: Consulta qual safra está ativa em cada talhão para executar operações no momento certo

## Dores que resolve

1. **Falta de histórico**: Produtores de soja do Cerrado perdem informações de safras passadas anotadas em cadernos ou planilhas. Sem histórico, não conseguem comparar produtividade entre anos.

2. **Visão fragmentada**: Informações de custo, operações e produtividade ficam espalhadas em sistemas diferentes. O produtor de algodão em Luís Eduardo Magalhães (BA) precisa de visão unificada para calcular custo da pluma vs caroço.

3. **Dificuldade de comparação**: Sem dados estruturados, é impossível comparar safras entre anos ou talhões. Produtor de café do Cerrado Mineiro não consegue avaliar impacto de novas variedades.

4. **Controle de área**: Erros de cálculo de área plantada geram distorções em custo/ha e produtividade. Em propriedades de 10.000+ ha no MT, diferença de 5% na área representa milhões em receita.

5. **Múltiplas safras**: Produtores com safrinha ou culturas consorciadas não conseguem separar dados. Milho safrinha plantado em janeiro tem dinâmica diferente de milho de verão.

6. **Zoneamento ZARC**: Produtor precisa validar se data de plantio está dentro da janela recomendada pelo Zoneamento Agroclimático de Risco para ter acesso a seguro e crédito rural.

## Regras de Negócio

1. Uma safra pertence a exatamente um tenant (isolamento multi-tenant obrigatório)
2. Uma safra pode conter um ou mais talhões da mesma fazenda
3. O status segue o fluxo: `planejada` → `em_andamento` → `colhida` → `encerrada`
4. Não é permitido reabrir uma safra `encerrada` sem permissão de administrador
5. A área total da safra é a soma das áreas dos talhões vinculados
6. Cada talhão pode estar em no máximo uma safra ativa por cultura simultaneamente
7. **Safra dupla**: Permitir sobreposição de safras no mesmo talhão se culturas forem diferentes (ex: soja + milho safrinha)
8. **Validação ZARC**: Ao criar safra, verificar se data de plantio está dentro da janela ZARC para o município/cultura/variedade (warning, não bloqueio)
9. Ao encerrar uma safra, todas as operações pendentes devem ser finalizadas ou canceladas
10. A exclusão de uma safra só é permitida se não houver operações, romaneios ou lançamentos financeiros vinculados (soft delete preferencial)
11. Datas de início e fim devem respeitar a sazonalidade cadastrada para a cultura (warning, não bloqueio)
12. Permissões: `agricola:safras:create`, `agricola:safras:read`, `agricola:safras:update`, `agricola:safras:delete`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `Safra` | id, tenant_id, fazenda_id, nome, cultura_id, variedade, data_inicio, data_fim_prevista, data_fim_real, status, area_total_ha, observacoes, zarc_validado | pertence a Fazenda, tem muitos Talhões, tem muitas Operações |
| `SafraTalhao` | id, safra_id, talhao_id, area_ha, cultura_id, variedade | vincula Safra a Talhão |
| `GrupoTalhoes` | id, safra_id, nome, cor | agrupa talhões dentro de uma safra |
| `SafraStatus` | enum: planejada, em_andamento, colhida, encerrada | controla fluxo de vida |
| `ZarcValidacao` | id, safra_id, municipio_ibge, cultura, variedade, data_plantio, risco_climatico, indice_risco | validação ZARC |

## Integrações Necessárias

| Sistema/Modulo | Tipo | Descrição |
|----------------|------|-----------|
| `core/cadastros/fazendas` | Leitura | Obtém fazendas e talhões disponíveis |
| `core/cadastros/produtos` | Leitura | Obtém culturas e variedades registradas no RNC (Registro Nacional de Cultivares) |
| `agricola/operacoes` | Bidirecional | Operações são vinculadas à safra/talhão |
| `agricola/custos` | Leitura | Custos agregados por safra |
| `agricola/romaneios` | Leitura | Produtividade real via romaneios de colheita |
| `financeiro/receitas` | Leitura | Receitas de venda da safra |
| `financeiro/despesas` | Leitura | Despesas vinculadas à safra |
| `api/zarc` | Leitura | Validação de época de plantio conforme Zoneamento Agroclimático |

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa `/agricola/safras` e visualiza lista/kanban de safras
2. Clica em "Nova Safra" e preenche: nome, fazenda, cultura, variedade, data início/fim prevista
3. **Validação ZARC**: Sistema consulta ZARC para verificar se data de plantio está na janela recomendada para o município
4. Seleciona os talhões que participarão da safra e confirma as áreas
5. **Safra dupla**: Se talhão já tem safra ativa, sistema verifica se culturas são compatíveis (ex: soja + milho safrinha)
6. Sistema cria a safra com status `planejada`
7. Quando o plantio inicia, usuário altera status para `em_andamento`
8. Durante a safra, registra operações, monitora NDVI, anota caderno de campo
9. Ao iniciar colheita, registra romaneios e acompanha produtividade (sc/ha)
10. Quando toda a colheita termina, altera status para `colhida`
11. Após conciliação financeira, encerra a safra (`encerrada`)
12. Safra encerrada fica disponível para consulta histórica e comparativos

## Casos Extremos e Exceções

- **Talhão em duas safras**: Se o produtor faz safrinha, o mesmo talhão pode ter safra de soja (jan-abr) e milho safrinha (mar-jul) com sobreposição de datas — o sistema deve permitir desde que sejam culturas diferentes

- **Safra sem colheita**: Perda total por clima (geada no PR, seca no MT) ou praga — usuário encerra safra com produtividade zero e justificativa para seguro rural

- **Mudança de área**: Talhão teve parte alagada (comum no RS) — permitir ajuste de área efetiva na safra sem alterar cadastro do talhão

- **Safra multi-fazenda**: Atualmente não suportada; cada safra pertence a uma fazenda. Comparativos cross-fazenda são feitos via dashboard

- **Exclusão de talhão vinculado**: Se um talhão é removido do cadastro, safras históricas devem manter referência (soft delete)

- **Concorrência**: Dois usuários editando a mesma safra simultaneamente — usar optimistic locking (version field)

- **Variedade não adaptada**: Produtor planta variedade não recomendada para a região — alerta baseado em dados da Embrapa/CONAB

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de safras com validação de tenant isolation
- [ ] Vinculação de talhões à safra com cálculo automático de área total
- [ ] Transição de status com validações de regra de negócio
- [ ] Kanban visual funcional com drag-and-drop de status
- [ ] Timeline cronológica renderizando eventos da safra
- [ ] Dashboard com KPIs: área total, produtividade estimada vs real, custo/ha
- [ ] Navegação para todas as sub-telas da safra (operações, NDVI, etc.)
- [ ] Validação ZARC integrada na criação de safra
- [ ] Suporte a safra dupla (sobreposição de culturas diferentes)
- [ ] Testes de integração cobrindo tenant isolation
- [ ] Permissões RBAC aplicadas em todas as rotas
- [ ] Paginação e filtros (por status, cultura, fazenda, período)

## Sugestões de Melhoria Futura

1. **Safra multi-fazenda**: Permitir safras que englobem talhões de fazendas diferentes do mesmo tenant

2. **Templates de safra**: Criar safras a partir de templates com operações pré-configuradas por cultura/região (ex: template "Soja MT 2000ha")

3. **Comparativo entre safras**: Dashboard dedicado para comparar KPIs entre safras/anos com benchmark regional (CONAB)

4. **Integração clima**: Vincular dados meteorológicos automaticamente ao período da safra (INMET, estações locais)

5. **Exportação para financiamento**: Gerar relatório de safra no formato exigido por bancos para comprovação de custeio (Plano Safra)

6. **Alertas automáticos**: Notificar quando uma safra passa da data prevista de colheita sem romaneios

7. **Integração CONAB**: Comparar produtividade da safra com média regional publicada pela CONAB

8. **Histórico de variedades**: Manter registro de variedades plantadas por ano para análise de adaptação
