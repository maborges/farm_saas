# Step 65 - Auditoria de `estoque_movimentacoes` legado para backfill em `estoque_movimentos`

## Objetivo

Medir o passivo legado em `estoque_movimentacoes` antes de qualquer backfill para `estoque_movimentos`, com foco em:

- volume;
- duplicidade;
- cobertura já existente no ledger canônico;
- risco de dupla gravação ao migrar.

Premissas desta etapa:

- nenhum dado foi migrado;
- nenhum schema foi alterado;
- nenhum script de backfill foi executado.

## Fonte do snapshot

- ambiente consultado: PostgreSQL configurado em `apps/web/services/api/.env.local`;
- data do snapshot: `2026-04-28`;
- tabelas auditadas:
  - `estoque_movimentacoes` legado;
  - `estoque_movimentos` canônico;
  - `estoque_depositos` para resolver `tenant_id` do legado.

## Resumo executivo

- `estoque_movimentacoes`: `9` linhas legadas.
- `estoque_movimentos`: `30` linhas canônicas.
- duplicidade exata dentro do legado: `0` grupos duplicados, `0` linhas excedentes.
- cobertura heurística já existente no ledger canônico: `4` de `9` linhas legadas.
- risco principal: não é volume nem duplicidade interna; é backfill duplicar movimentos que já existem no ledger por outro fluxo.

Leitura prática:

- o passivo legado está pequeno e auditável manualmente;
- os `4` movimentos de `PEDIDO_COMPRA` têm forte sinal de já estarem representados em `estoque_movimentos`;
- os `5` movimentos restantes parecem backlog real ou casos ambíguos de origem.

## Distribuição do legado

### Por tenant

| tenant_id | total |
| --- | ---: |
| `aaaaaaaa-0000-0000-0000-000000000010` | 5 |
| `aaaaaaaa-0000-0000-0000-000000000001` | 4 |

### Por tipo

| tipo | total |
| --- | ---: |
| `ENTRADA` | 6 |
| `SAIDA` | 3 |

### Por `origem_tipo`

| origem_tipo | total |
| --- | ---: |
| `<NULL>` | 4 |
| `PEDIDO_COMPRA` | 4 |
| `OPERACAO_AGRICOLA` | 1 |

### Por data

| data | total |
| --- | ---: |
| `2026-04-28` | 3 |
| `2026-04-27` | 4 |
| `2026-04-21` | 2 |

## Distribuição do ledger canônico

### Por origem e tipo

| origem | tipo_movimento | total |
| --- | --- | ---: |
| `MANUAL` | `ENTRADA` | 11 |
| `COMPRA` | `ENTRADA` | 6 |
| `TRANSFERENCIA` | `TRANSFERENCIA` | 6 |
| `AJUSTE` | `AJUSTE` | 3 |
| `MANUAL` | `SAIDA` | 3 |
| `OPERACAO_EXECUCAO` | `SAIDA` | 1 |

### Por data

| data | total |
| --- | ---: |
| `2026-04-28` | 1 |
| `2026-04-27` | 27 |
| `2026-04-20` | 2 |

## Qualidade mínima do legado

Contagem de campos críticos nulos em `estoque_movimentacoes`:

| campo | linhas nulas |
| --- | ---: |
| `deposito_id` | 0 |
| `produto_id` | 0 |
| `tipo` | 0 |
| `quantidade` | 0 |
| `data_movimentacao` | 0 |
| `origem_tipo` | 4 |
| `origem_id` | 4 |
| `lote_id` | 8 |

Leitura prática:

- não há risco estrutural por ausência de depósito, produto, tipo, quantidade ou data;
- a maior perda de rastreabilidade está em `origem_*` nulo e `lote_id` ausente;
- `8` de `9` linhas não carregam vínculo de lote, então qualquer backfill será majoritariamente em nível de produto/deposito, não de lote.

## Cobertura heurística já existente no canônico

Foi feita uma verificação conservadora por:

- `tenant_id`;
- `deposito_id`;
- `produto_id`;
- `quantidade`;
- mesma data;
- compatibilidade de direção:
  - legado `ENTRADA` versus canônico `ENTRADA/AJUSTE/SALDO_INICIAL`;
  - legado `SAIDA` versus canônico `SAIDA/TRANSFERENCIA`.

Resultado:

- linhas legadas avaliadas: `9`;
- linhas legadas com algum possível correspondente canônico: `4`.

### Cobertura por `origem_tipo`

| origem_tipo | linhas legadas | com match heurístico |
| --- | ---: | ---: |
| `<NULL>` | 4 | 0 |
| `PEDIDO_COMPRA` | 4 | 4 |
| `OPERACAO_AGRICOLA` | 1 | 0 |

### Buckets recentes ainda sem match heurístico

| origem_tipo | data | total |
| --- | --- | ---: |
| `<NULL>` | `2026-04-28` | 2 |
| `OPERACAO_AGRICOLA` | `2026-04-28` | 1 |
| `<NULL>` | `2026-04-21` | 2 |

## Leitura qualitativa dos 9 registros

### Grupo 1: `PEDIDO_COMPRA` com forte chance de já estar no ledger

- `4` linhas;
- todas `ENTRADA`;
- mesmo padrão operacional de compras;
- já existe cobertura canônica heurística para as `4`.

Conclusão:

- esse grupo não deve entrar em backfill cego;
- a tendência correta é tratá-lo como já absorvido por fluxo novo de compra/recebimento;
- qualquer migração futura deve usar regra determinística de exclusão, não apenas semelhança por quantidade/data.

### Grupo 2: origem nula

- `4` linhas;
- `2` saídas em `2026-04-21`;
- `2` entradas em `2026-04-28`;
- nenhuma encontrou match heurístico no canônico.

Conclusão:

- esse grupo parece passivo real, mas com baixa rastreabilidade;
- exige política explícita antes do backfill:
  - mapear para `MANUAL`; ou
  - classificar como `LEGADO`, se o catálogo de origem de estoque passar a aceitar essa distinção.

### Grupo 3: `OPERACAO_AGRICOLA`

- `1` linha;
- `SAIDA`;
- sem match heurístico no canônico;
- possui melhor sinal de origem operacional do que o grupo nulo, mas ainda no nome legado.

Conclusão:

- esse caso deve ser remapeado com cuidado para a origem canônica equivalente;
- a hipótese mais provável é conversão para `OPERACAO_EXECUCAO`, desde que exista vínculo determinístico com a execução real.

## Riscos identificados

### 1. Risco baixo de volume

- só existem `9` linhas legadas;
- permite conferência manual e dry-run detalhado antes de qualquer insert.

### 2. Risco baixo de duplicidade interna

- não apareceram grupos duplicados exatos dentro de `estoque_movimentacoes`.

### 3. Risco médio/alto de dupla contagem cross-ledger

- `PEDIDO_COMPRA` já aparece com cobertura heurística total;
- uma regra fraca de correspondência pode reinserir no canônico algo que já foi gravado por fluxo novo.

### 4. Risco médio de ambiguidade de origem

- `4` linhas estão com `origem_tipo/origem_id` nulos;
- sem política clara, o backfill pode inventar rastreabilidade que o legado não tinha.

### 5. Risco médio de perda de granularidade por lote

- `8` de `9` linhas não têm `lote_id`;
- o backfill pode ser suficiente para auditoria contábil/operacional, mas não vai restaurar rastreabilidade fina de lote nesses casos.

### 6. Risco alto se a deduplicação usar chave heurística fraca

Foi observado que a heurística de `produto + depósito + quantidade + dia` é suficiente para indicar sobreposição provável, mas não para decidir idempotência de escrita. Ela é útil para auditoria, não para chave final de migração.

## Política oficial de elegibilidade do backfill - Step 66

O backfill futuro de `estoque_movimentacoes` para `estoque_movimentos` deve classificar cada linha legada em exatamente uma destas categorias:

- `IGNORAR`
- `MIGRAR`
- `MARCAR_COMO_LEGADO`
- `REVISAR_MANUALMENTE`

### 1. `IGNORAR`

Devem ser ignoradas, para evitar dupla contagem, as linhas legadas que já estejam materialmente representadas no ledger canônico por fluxo novo.

Regra oficial inicial:

- `PEDIDO_COMPRA` legado deve ser `IGNORAR` quando já existir movimento canônico compatível de entrada de compra no mesmo contexto operacional.

Critério mínimo para exclusão:

- mesma empresa (`tenant_id`);
- mesmo `deposito_id`;
- mesmo `produto_id`;
- mesma direção econômica;
- mesma quantidade;
- mesma janela operacional coerente com o evento de compra;
- vínculo de origem compatível com compra canônica.

Observação:

- a heurística de `produto + depósito + quantidade + dia` pode sinalizar sobreposição, mas não é chave suficiente para idempotência;
- o script futuro deve usar identificador legado e regra determinística de negócio, não só aproximação por semelhança.

### 2. `MIGRAR`

Devem ser migradas as linhas legadas que:

- não tenham cobertura canônica equivalente;
- tenham semântica de movimento ainda válida;
- possuam mapeamento aceito para `tipo_movimento` e origem canônica;
- não gerem dupla contagem com fluxos já estabilizados.

Regra oficial inicial:

- movimentos com `origem_tipo = NULL` e sem match canônico podem ser `MIGRAR` apenas se o time aceitar convertê-los para origem manual legítima;
- movimentos com origem operacional legada só podem ser `MIGRAR` quando houver remapeamento determinístico para a origem canônica correspondente.

### 3. `MARCAR_COMO_LEGADO`

Esta categoria é reservada para carga histórica que precisa entrar no ledger, mas sem origem operacional confiável.

Regra oficial:

- usar `LEGADO` apenas quando a linha precisar ser preservada no ledger e não houver base confiável para classificá-la como operacional;
- `LEGADO` não substitui exclusão de duplicata;
- `LEGADO` não deve ser usado para mascarar linha já coberta por fluxo canônico.

Aplicação prática:

- `origem_tipo = NULL` sem vínculo operacional recuperável deve preferir `LEGADO` em vez de inventar rastreabilidade operacional;
- `MANUAL` deve ficar reservado para movimentos efetivamente manuais do domínio, não para todo resíduo histórico.

## Política oficial de `LEGADO` no ledger de estoque - Step 67

### Decisão

`LEGADO` deve ser aceito como origem oficial em `estoque_movimentos` para carga histórica sem origem operacional confiável.

### Escopo de uso

`LEGADO` fica restrito a:

- backfill de `estoque_movimentacoes`;
- importações históricas;
- migrações controladas de dados antigos;
- correções documentais de acervo legado sem evento operacional recuperável.

`LEGADO` não deve ser usado em:

- novos fluxos operacionais;
- lançamentos manuais normais do estoque;
- atalhos para evitar mapear uma origem operacional conhecida.

### Distinção oficial entre `MANUAL` e `LEGADO`

- `MANUAL`: movimento criado conscientemente no domínio atual, por ação manual legítima do usuário ou rotina operacional equivalente.
- `LEGADO`: movimento histórico preservado no ledger por necessidade de reconciliação/auditoria, mas sem origem operacional confiável no modelo canônico.

### Regras obrigatórias para `LEGADO`

- `origem = 'LEGADO'` só pode ser usado por rotinas de migração/importação explícitas.
- `origem_id` pode permanecer `NULL` quando não houver identificador confiável de origem.
- o movimento deve carregar trilha de auditoria suficiente em `observacoes`, incluindo referência ao `id` legado quando existir.
- `LEGADO` não autoriza duplicar movimento já coberto por `COMPRA`, `OPERACAO_EXECUCAO`, `COLHEITA`, `AJUSTE`, `TRANSFERENCIA` ou `MANUAL`.

### Implicação técnica imediata

A constraint atual do schema ainda não aceita `LEGADO` em `estoque_movimentos.origem`.

Estado atual da constraint em `step18_estoque_movimentos.py`:

- `origem IN ('OPERACAO_EXECUCAO','COMPRA','COLHEITA','AJUSTE','MANUAL','TRANSFERENCIA')`

Portanto:

- a política de negócio do Step 67 fica aprovada desde já;
- o backfill não deve ser escrito/executado antes de uma migration específica ampliar a constraint para incluir `LEGADO`;
- essa futura migration deve ser tratada como pré-requisito explícito do Step de backfill.

### 4. `REVISAR_MANUALMENTE`

Entram aqui as linhas que não podem ser decididas com segurança por regra automatizada.

Casos típicos:

- origem operacional legada sem correspondência canônica determinística;
- divergência entre quantidade/data/origem e possível match no ledger;
- necessidade de decidir entre `OPERACAO_AGRICOLA` legado versus `OPERACAO_EXECUCAO` canônico.

## Regras objetivas por origem atual

### `PEDIDO_COMPRA`

- `IGNORAR` se já existir cobertura canônica compatível de compra.
- `REVISAR_MANUALMENTE` se houver conflito, multiplicidade ou ausência de vínculo suficiente para concluir cobertura.
- `MIGRAR` só em caso excepcional, quando ficar provado que o movimento de compra não entrou no ledger canônico.

### `OPERACAO_AGRICOLA`

- `MIGRAR` somente se o vínculo para `OPERACAO_EXECUCAO` puder ser resolvido de forma determinística.
- `REVISAR_MANUALMENTE` quando esse vínculo não puder ser provado.
- Não converter automaticamente para `MANUAL`.

### `origem_tipo = NULL`

- `MARCAR_COMO_LEGADO` quando a linha precisar ser preservada e não houver origem operacional confiável.
- `MIGRAR` como `MANUAL` apenas se houver decisão explícita de negócio de que o evento foi realmente manual.
- `REVISAR_MANUALMENTE` se houver indício de que a linha deriva de fluxo operacional hoje rastreável, mas sem prova suficiente.

## Decisão operacional para o snapshot atual

Aplicando a política do Step 66 ao snapshot de `2026-04-28`:

- `4` linhas `PEDIDO_COMPRA`: candidatas a `IGNORAR`, porque já têm cobertura canônica provável e representam o maior risco de dupla contagem.
- `1` linha `OPERACAO_AGRICOLA`: candidata a `REVISAR_MANUALMENTE` até existir remapeamento determinístico para `OPERACAO_EXECUCAO`.
- `4` linhas com `origem_tipo = NULL`: candidatas a `MARCAR_COMO_LEGADO`, salvo decisão explícita posterior de tratá-las como `MANUAL`.

## Requisitos obrigatórios para o script futuro

### Idempotência forte

O script futuro não deve depender só de heurística de negócio. Precisa de um marcador determinístico por linha legada, por exemplo:

- tabela auxiliar de controle de backfill com `legacy_movimentacao_id`; ou
- marcação explícita em `observacoes` do `estoque_movimentos` com o `id` legado; ou
- outra estratégia equivalente que permita `WHERE NOT EXISTS` por identificador legado.

### Dry-run obrigatório antes de qualquer insert

O dry-run deve mostrar, no mínimo:

- quantas linhas serão excluídas por já estarem cobertas;
- quantas serão migradas;
- quantas irão para revisão manual;
- projeção de impacto por tenant, produto, depósito, tipo e data.

### Validação obrigatória após eventual backfill

Após eventual migração futura, validar:

- contagem de movimentos migrados versus elegíveis;
- ausência de duplicação por `legacy_movimentacao_id`;
- saldo por produto/deposito antes e depois;
- visibilidade correta em leituras já adaptadas para `estoque_movimentos`.

## Conclusão

O passivo legado de `estoque_movimentacoes` está pequeno, sem duplicidade interna relevante e viável para backfill conservador.

O principal cuidado não é “como migrar tudo”, e sim “como não duplicar no ledger o que compras já passou a gravar corretamente”. A política do Step 66 fecha a elegibilidade e o Step 67 fecha a semântica: `PEDIDO_COMPRA` coberto deve ser ignorado; histórico sem origem confiável deve entrar como `LEGADO` apenas se realmente precisar ser preservado; e origem operacional ambígua deve ficar fora da automação até prova determinística.

Próximo passo seguro:

1. criar migration específica para incluir `LEGADO` na constraint de `estoque_movimentos.origem`;
2. decidir se algum caso `origem_tipo = NULL` pode ser promovido a `MANUAL` por regra de negócio;
3. só então implementar script idempotente com dry-run obrigatório.
