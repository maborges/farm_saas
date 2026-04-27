# Step 49 - Plano de Migração Incremental Cross-Módulo

## Objetivo

Planejar a remoção incremental das duplicidades críticas entre módulos do SaaS agro, migrando os novos fluxos para as fontes canônicas definidas em:

- `docs/contexts/step47-existing-modules-inventory-context.md`
- `docs/contexts/step48-cross-module-ownership-context.md`

Este documento é deliberadamente um plano técnico. Ele não implementa código, não cria migrations, não altera gates e não remove tabelas existentes.

## Escopo e premissas

- Core permanece como base comum de identidade, cadastros e permissões.
- Agricultura e Pecuária continuam como módulos produtivos equivalentes.
- Estoque, Financeiro e Frota/Máquinas são módulos integradores.
- Novas implementações devem consumir fontes canônicas antes de criar novas tabelas.
- Tabelas legadas podem continuar existindo durante janelas de compatibilidade.
- Depreciação física só deve ocorrer em etapa futura, com migration dedicada, testes e aceite explícito.

## Estratégia geral

As migrações devem seguir uma sequência conservadora:

1. Congelar a fonte canônica por entidade.
2. Identificar registros duplicados e chaves naturais de reconciliação.
3. Criar plano de correspondência entre legado e canônico.
4. Adaptar novos writes para a fonte canônica.
5. Manter leitura compatível para APIs/frontends existentes.
6. Backfill idempotente dos dados legados.
7. Validar saldos, custos, origem e relatórios.
8. Marcar legado como depreciado.
9. Remover legado apenas em fase futura.

## Ordem recomendada macro

| Ordem | Migração | Motivo da prioridade |
| --- | --- | --- |
| 0 | Congelamento operacional | Evita novas duplicidades enquanto as migrações são preparadas. |
| 1 | `compras_fornecedores` -> `cadastros_pessoas` | Reduz duplicidade de pessoa jurídica e melhora Compras, Financeiro e Fiscal. |
| 2 | Novos fluxos em `estoque_movimentos` | Garante ledger único antes de ampliar integrações produtivas. |
| 3 | `origem_tipo/origem_id` cross-módulo | Permite rastreabilidade de custos, receitas e estoque. |
| 4 | `pec_piquetes` -> `cadastros_areas_rurais` | Unifica geografia produtiva entre Agricultura e Pecuária. |
| 5 | `culturas` legado -> `cadastros_culturas` | Remove duplicidade agronômica antes de novos cadastros agrícolas. |
| 6 | `maquinario_id` -> `equipamento_id` | Padroniza Frota/Máquinas sobre equipamento canônico. |
| 7 | Centro de custo geral | Depende de origem e ledger mais estáveis para não nascer inconsistente. |

## 0. Congelamento operacional

### Estado atual

O repositório já possui fontes canônicas definidas no Step 48, mas ainda existem fluxos e nomes legados em módulos operacionais. Os principais pontos são:

- Pessoas canônicas em `cadastros_pessoas`, mas fornecedores duplicados em `compras_fornecedores`.
- Estoque com `estoque_movimentacoes` e `estoque_movimentos`.
- Financeiro com campos de origem em `fin_despesas` e `fin_receitas`, mas uso irregular por módulo.
- Geografia produtiva canônica em `cadastros_areas_rurais`, mas piquetes legados em `pec_piquetes`.
- Cultura canônica em `cadastros_culturas`, mas tabela legada `culturas`.
- Equipamentos canônicos em `cadastros_equipamentos`, mas aliases `maquinario_id` em Frota.

### Risco

Sem congelamento, novas telas, endpoints ou jobs podem reforçar tabelas duplicadas e tornar a migração mais cara.

### Estratégia de migração

- Registrar este documento como diretriz para novas histórias técnicas.
- Proibir, em revisão técnica, novas tabelas por módulo para entidades já canônicas.
- Tratar tabelas legadas como compatibilidade, não como fonte de verdade.
- Exigir que novos fluxos informem `tenant_id`, fonte canônica e, quando aplicável, `origem_tipo/origem_id`.

### Impacto em API/frontend/testes

- Não exige alteração imediata.
- Novos contratos de API devem preferir ids canônicos.
- Testes futuros devem validar que novos fluxos não escrevem em cadastros duplicados.

### Critérios de aceite

- Novas histórias técnicas citam a fonte canônica antes de modelar entidades compartilhadas.
- Nenhum novo módulo cria tabela própria para pessoa, produto, estoque, fazenda, área rural ou equipamento.
- Legados são tratados explicitamente como compatibilidade.

## 1. `compras_fornecedores` -> `cadastros_pessoas` com papel `FORNECEDOR`

### Estado atual

- Fonte canônica: `cadastros_pessoas`, em `services/api/core/cadastros/pessoas/models.py`.
- Papel/relacionamento canônico: relacionamentos de pessoa no mesmo módulo de cadastros.
- Legado duplicado: `compras_fornecedores`, modelado em `services/api/operacional/models/compras.py`.
- Consumo operacional: rotas de Compras em `services/api/operacional/routers/compras.py`.

### Risco

- CNPJ/CPF duplicado entre Core e Compras.
- Fornecedor financeiro/fiscal diferente do fornecedor operacional.
- Dificuldade de conciliação com notas fiscais e integrações externas.
- Relatórios por pessoa e por fornecedor podem divergir.

### Estratégia de migração

1. Levantar fornecedores duplicados por `tenant_id`, CNPJ/CPF, razão social e nome fantasia.
2. Definir regra de match:
   - CNPJ/CPF válido tem precedência.
   - Na ausência de documento, usar nome normalizado apenas como sugestão, exigindo revisão.
3. Criar, em fase futura, vínculo entre fornecedor legado e pessoa canônica.
4. Fazer backfill de `compras_fornecedores` para `cadastros_pessoas`.
5. Garantir relacionamento/papel `FORNECEDOR` para cada pessoa migrada.
6. Adaptar novos writes de fornecedores para criar/atualizar `cadastros_pessoas`.
7. Manter endpoints antigos de Compras como fachada de compatibilidade.
8. Marcar `compras_fornecedores` como depreciado após estabilidade.

### Impacto em API

- Endpoints atuais de Compras devem permanecer compatíveis durante a transição.
- Respostas podem passar a expor `pessoa_id` como identificador canônico.
- Criação de fornecedor via Compras deve resolver ou criar pessoa canônica.
- Validações de unicidade devem migrar de fornecedor local para pessoa por tenant/documento.

### Impacto em frontend

- Telas atuais de fornecedor podem continuar consumindo rotas de Compras na primeira fase.
- Novas telas devem usar seletor de pessoa com papel `FORNECEDOR`.
- Formulários devem evitar cadastro paralelo quando já existir pessoa com mesmo documento.

### Impacto em testes

- Testar criação idempotente por documento.
- Testar manutenção do contrato antigo de Compras.
- Testar que o mesmo fornecedor é reutilizado em Compras, Financeiro e Fiscal.
- Testar isolamento por `tenant_id`.

### Critérios de aceite

- Todo novo fornecedor de Compras possui pessoa canônica associada.
- Pessoa com papel `FORNECEDOR` é a fonte de verdade.
- `compras_fornecedores` não recebe novos cadastros independentes.
- Relatórios e pedidos de compra resolvem fornecedor via pessoa canônica.

## 2. Novos fluxos de estoque usando `estoque_movimentos` como ledger único

### Estado atual

- Modelos de Estoque ficam em `services/api/operacional/models/estoque.py`.
- Existem `estoque_movimentacoes` e `estoque_movimentos`.
- O Step 48 definiu `estoque_movimentos` como ledger canônico para novos fluxos.
- `estoque_saldos` representa saldo operacional.
- `estoque_lotes` representa lote/rastreabilidade.
- `services/api/operacional/services/estoque_ledger.py` já indica intenção de ledger.

### Risco

- Movimentos duplicados ou divergentes entre tabelas.
- Saldos inconsistentes por depósito, lote, produto ou módulo de origem.
- Baixa rastreabilidade de consumo agrícola, pecuário e operacional.
- Risco fiscal e contábil quando estoque e financeiro não conciliam.

### Estratégia de migração

1. Congelar `estoque_movimentos` como destino de novos writes de ledger.
2. Manter `estoque_movimentacoes` apenas como legado/compatibilidade enquanto necessário.
3. Definir contrato mínimo do ledger:
   - `tenant_id`
   - produto/insumo canônico
   - depósito/local
   - lote, quando aplicável
   - quantidade
   - direção ou tipo de movimento
   - custo unitário ou valor total, quando aplicável
   - `origem_tipo`
   - `origem_id`
   - data do movimento
4. Fazer backfill idempotente de movimentos legados para o ledger.
5. Ajustar novos consumos de Agricultura, Pecuária, Compras, Vendas e Frota para registrar no ledger.
6. Reconciliar `estoque_saldos` contra o somatório do ledger.
7. Definir divergências aceitáveis apenas por regra documentada, nunca silenciosamente.

### Impacto em API

- APIs atuais de estoque podem continuar retornando saldos e movimentos legados durante a transição.
- Novas APIs de integração devem escrever em `estoque_movimentos`.
- Endpoints que movimentam estoque por Compras, Produção ou Vendas devem informar origem.

### Impacto em frontend

- Telas operacionais de movimentação podem manter comportamento inicial.
- Novas telas de rastreabilidade devem consultar ledger canônico.
- Indicadores de saldo devem explicitar depósito, lote e data de referência.

### Impacto em testes

- Testar que cada novo fluxo gera exatamente um movimento canônico esperado.
- Testar que saldo calculado a partir do ledger bate com `estoque_saldos`.
- Testar idempotência de backfill.
- Testar rastreabilidade por `origem_tipo/origem_id`.

### Critérios de aceite

- Novos fluxos produtivos e operacionais não escrevem ledger paralelo.
- `estoque_movimentos` permite rastrear entrada, consumo, ajuste e saída.
- `estoque_saldos` é reconciliável a partir do ledger.
- Movimentos sem origem só são aceitos quando classificados como manuais.

## 3. Padronizar `origem_tipo/origem_id` em Pecuária, Frota, Compras e Vendas

### Estado atual

- Financeiro possui despesas e receitas em modelos como `fin_despesas` e `fin_receitas`.
- Os campos de origem existem ou são previstos no domínio financeiro, mas o uso ainda é irregular.
- Agricultura já possui padrão mais claro de origem em operações e integrações.
- Pecuária, Frota, Compras e Vendas ainda precisam padronizar a origem dos lançamentos e movimentos.

Arquivos relevantes do inventário:

- Pecuária: `services/api/pecuaria/services/manejo_service.py`.
- Frota: `services/api/operacional/services/abastecimento_service.py` e `services/api/operacional/services/frota_service.py`.
- Compras: `services/api/operacional/routers/compras.py`.
- Vendas/comercialização: modelos de comercialização financeira e romaneios agrícolas mapeados no Step 47.

### Risco

- Custos e receitas sem rastreabilidade até o evento operacional.
- Dashboards executivos com números corretos, mas sem explicação auditável.
- Dificuldade para apurar margem por safra, lote, rebanho, máquina, compra ou venda.
- Backfills futuros mais caros por falta de vínculo de origem.

### Estratégia de migração

1. Definir catálogo controlado de `origem_tipo` para novos fluxos:
   - `OPERACAO_AGRICOLA`
   - `MANEJO_PECUARIO`
   - `EVENTO_ANIMAL`
   - `ABASTECIMENTO`
   - `ORDEM_SERVICO`
   - `PEDIDO_COMPRA`
   - `RECEBIMENTO_COMPRA`
   - `COMERCIALIZACAO`
   - `ROMANEIO_COLHEITA`
   - `AJUSTE_ESTOQUE`
   - `MANUAL`
2. Usar `origem_id` como id do registro que causou o lançamento ou movimento.
3. Escrever origem em todo novo lançamento financeiro e movimento de estoque gerado por módulo operacional.
4. Backfill por vínculo direto quando existir FK ou campo equivalente.
5. Backfill por heurística apenas como sugestão auditável.
6. Manter registros sem origem confiável como `MANUAL` ou `LEGADO`, conforme decisão futura.

### Impacto em API

- Novos endpoints que geram estoque ou financeiro devem exigir origem quando a ação for operacional.
- Endpoints manuais podem aceitar `MANUAL`.
- Respostas financeiras e de estoque devem expor origem para drill-down.

### Impacto em frontend

- Telas de detalhe financeiro/estoque devem conseguir navegar para a origem.
- Formulários operacionais não devem pedir origem ao usuário quando ela é inferível pelo fluxo.
- Telas manuais devem deixar clara a classificação manual.

### Impacto em testes

- Testar cada módulo gerador:
  - Pecuária cria origem de manejo/evento.
  - Frota cria origem de abastecimento ou ordem de serviço.
  - Compras cria origem de pedido/recebimento.
  - Vendas cria origem de comercialização/romaneio.
- Testar que origem inválida é rejeitada.
- Testar que relatórios conseguem agrupar por origem.

### Critérios de aceite

- Todo novo lançamento financeiro operacional possui `origem_tipo/origem_id`.
- Todo novo movimento de estoque operacional possui `origem_tipo/origem_id`.
- Dashboards conseguem rastrear custo/receita até o evento operacional.
- Registros legados sem origem confiável ficam identificados como legado/manual.

## 4. `pec_piquetes` -> `cadastros_areas_rurais` tipo `PIQUETE`

### Estado atual

- Fonte canônica de áreas rurais: `cadastros_areas_rurais`, em `services/api/core/cadastros/propriedades/models.py`.
- Piquete legado: `pec_piquetes`, em `services/api/pecuaria/models/piquete.py`.
- `LoteAnimal.area_id` já aponta para `cadastros_areas_rurais`.
- Serviços de lote ainda podem aceitar `piquete_id` e validar contra piquete legado.

### Risco

- Geografia pecuária separada da geografia produtiva central.
- Capacidade, área, lotação e mapas podem divergir.
- Agricultura e Pecuária deixam de compartilhar a mesma leitura territorial da fazenda.
- Custos por área ficam inconsistentes.

### Estratégia de migração

1. Inventariar todos os `pec_piquetes` por tenant e unidade produtiva.
2. Criar correspondência com `cadastros_areas_rurais` por nome, fazenda/unidade e tipo.
3. Para piquetes sem área correspondente, planejar criação futura de área rural tipo `PIQUETE`.
4. Migrar referências operacionais para `area_id`.
5. Manter `piquete_id` apenas como alias temporário de entrada em APIs.
6. Adaptar seleção de piquetes no frontend para consultar áreas rurais tipo `PIQUETE`.
7. Depreciar `pec_piquetes` após todos os manejos e lotes usarem `area_id`.

### Impacto em API

- Endpoints novos devem usar `area_id`.
- Endpoints antigos podem aceitar `piquete_id` durante transição.
- Respostas devem preferir `area_id` e metadados da área rural canônica.

### Impacto em frontend

- Seletores de piquete devem migrar para seletor de área rural filtrado por tipo `PIQUETE`.
- Mapas, lotação e manejo devem usar a mesma árvore territorial do Core.
- Interfaces podem manter rótulo "Piquete", mas não fonte de dados separada.

### Impacto em testes

- Testar criação/edição de lote com `area_id`.
- Testar compatibilidade temporária com `piquete_id`.
- Testar que a área rural tipo `PIQUETE` aparece em relatórios pecuários.
- Testar isolamento por unidade produtiva e tenant.

### Critérios de aceite

- Novos lotes e manejos pecuários referenciam `cadastros_areas_rurais`.
- Nenhum fluxo novo depende de `pec_piquetes` como fonte da verdade.
- Relatórios territoriais usam a mesma hierarquia para Agricultura e Pecuária.

## 5. `culturas` legado -> `cadastros_culturas`

### Estado atual

- Fonte canônica: `cadastros_culturas`, em `services/api/core/cadastros/produtos/models.py`.
- Legado agrícola: tabela `culturas`, em `services/api/agricola/cadastros/models.py`.
- `Cultivo` já referencia cultura/cultivar canônica em parte do modelo agrícola.

### Risco

- Duplicidade de cultura por tenant.
- Parâmetros agronômicos divergentes.
- Cultivos e produtos colhidos podem apontar para catálogos diferentes.
- Dificuldade de comparar produtividade e margem por cultura.

### Estratégia de migração

1. Inventariar culturas legadas por tenant.
2. Fazer match com `cadastros_culturas` por nome normalizado e metadados agronômicos.
3. Planejar criação futura das culturas faltantes no cadastro canônico.
4. Migrar referências de cultivos e cadastros agrícolas para `cadastros_culturas`.
5. Manter endpoints legados como leitura compatível ou alias temporário.
6. Depreciar tabela `culturas` apenas após todos os cultivos usarem a fonte canônica.

### Impacto em API

- Novos endpoints agrícolas devem aceitar cultura canônica.
- APIs legadas podem expor `cultura_id` antigo apenas durante transição.
- Respostas devem incluir id canônico quando houver compatibilidade.

### Impacto em frontend

- Seletores agrícolas devem migrar para culturas canônicas.
- Telas de cultivo, safra e planejamento devem evitar criação de cultura local.
- Relatórios por cultura devem agrupar somente por `cadastros_culturas`.

### Impacto em testes

- Testar match idempotente por tenant e nome.
- Testar criação de cultivo com cultura canônica.
- Testar que culturas legadas não são recriadas em fluxos novos.
- Testar relatórios por cultura após migração.

### Critérios de aceite

- Novos cultivos usam `cadastros_culturas`.
- Tabela `culturas` não recebe novos cadastros independentes.
- Relatórios agrícolas agrupam por cultura canônica.

## 6. `maquinario_id` -> `equipamento_id` em Frota

### Estado atual

- Fonte canônica: `cadastros_equipamentos`, em `services/api/core/cadastros/equipamentos/models.py`.
- Frota/Máquinas deve consumir equipamento canônico.
- O inventário identificou divergência de nomenclatura: modelos tendem a usar `equipamento_id`, enquanto serviços/schemas podem expor ou aceitar `maquinario_id`.

### Risco

- Bugs de integração por nomes diferentes para a mesma entidade.
- Frontend e API podem divergir sobre o identificador correto.
- Dificuldade de consolidar custos de abastecimento, manutenção e uso operacional por equipamento.
- Possível criação futura de novo cadastro de máquinas por engano.

### Estratégia de migração

1. Congelar `equipamento_id` como nome canônico.
2. Mapear todos os contratos que ainda usam `maquinario_id`.
3. Adotar compatibilidade temporária:
   - aceitar `maquinario_id` em entrada antiga;
   - converter internamente para `equipamento_id`;
   - responder preferencialmente com `equipamento_id`.
4. Atualizar frontends e hooks em fase futura para enviar apenas `equipamento_id`.
5. Marcar `maquinario_id` como depreciado em documentação de API.
6. Remover alias somente após compatibilidade validada.

### Impacto em API

- Contrato canônico deve ser `equipamento_id`.
- Alias `maquinario_id` pode existir temporariamente para não quebrar clientes.
- Erros de validação devem mencionar o identificador canônico.

### Impacto em frontend

- Formulários de Frota devem migrar para `equipamento_id`.
- Componentes compartilhados devem consumir equipamentos do Core.
- Telas podem manter o rótulo "Máquina" ou "Veículo", mas o id técnico é de equipamento.

### Impacto em testes

- Testar entrada com `equipamento_id`.
- Testar compatibilidade temporária com `maquinario_id`.
- Testar custo operacional agrupado por equipamento.
- Testar que não há criação de cadastro paralelo de máquina/veículo.

### Critérios de aceite

- Novos fluxos de Frota usam `equipamento_id`.
- `maquinario_id` é apenas alias de compatibilidade.
- Custos de Frota, Máquinas e operações produtivas consolidam por `cadastros_equipamentos`.

## 7. Centro de custo geral cross-módulo

### Estado atual

- O inventário não identificou uma tabela canônica única de centro de custo cross-módulo.
- Financeiro possui estruturas relacionadas, como planos de conta e rateios.
- Agricultura possui alocações/custos produtivos próprios.
- Operações de Pecuária, Frota, Compras e Vendas ainda dependem de origem e rateios para consolidar custo.

### Risco

- Custos comparáveis apenas dentro de cada módulo.
- Dashboards executivos com visões divergentes de margem.
- Rateios manuais sem vínculo claro com safra, lote, rebanho, equipamento ou unidade produtiva.
- Criação precipitada de centro de custo pode duplicar plano de contas ou áreas produtivas.

### Estratégia de migração

1. Não criar centro de custo geral antes de estabilizar:
   - pessoas canônicas em Compras;
   - ledger único de estoque;
   - `origem_tipo/origem_id`;
   - áreas e equipamentos canônicos.
2. Produzir RFC técnico específico para centro de custo.
3. Avaliar dois caminhos:
   - tabela canônica nova `centros_custo` sob domínio Financeiro/Core operacional;
   - evolução de rateios financeiros existentes com referência cross-módulo.
4. Definir granularidade mínima:
   - tenant;
   - unidade produtiva;
   - módulo origem;
   - entidade produtiva opcional;
   - equipamento opcional;
   - safra/lote/rebanho opcional;
   - vigência;
   - status.
5. Planejar migração a partir de rateios financeiros e alocações agrícolas.
6. Exigir compatibilidade com `origem_tipo/origem_id`.

### Impacto em API

- Inicialmente não deve haver mudança.
- Após RFC, APIs financeiras devem conseguir associar rateios a centro de custo canônico.
- APIs produtivas não devem criar centros locais.

### Impacto em frontend

- Inicialmente sem mudança.
- Futuramente, seletores de centro de custo devem ser compartilhados.
- Dashboards devem usar a mesma dimensão de centro de custo para Agricultura, Pecuária, Frota, Compras e Vendas.

### Impacto em testes

- Testar rateio por centro de custo quando a entidade existir.
- Testar custo por unidade produtiva, safra, lote/rebanho e equipamento.
- Testar que centro de custo não substitui plano de contas indevidamente.
- Testar compatibilidade com origens operacionais.

### Critérios de aceite

- Existe decisão arquitetural específica antes de criar tabela ou migration.
- Centro de custo geral não duplica plano de contas, área rural ou entidade produtiva.
- Custos cross-módulo podem ser agrupados por uma dimensão única.

## Dependências entre migrações

| Migração | Depende de | Bloqueia |
| --- | --- | --- |
| Fornecedor canônico | Pessoa canônica existente | Compras, Fiscal e Financeiro consistentes por fornecedor |
| Ledger único de estoque | Produto/insumo canônico | Rastreabilidade produtiva e conciliação de saldo |
| Origem padronizada | Serviços geradores de estoque/financeiro | Drill-down executivo e centro de custo confiável |
| Piquete como área rural | Áreas rurais canônicas | Custo e lotação por território |
| Cultura canônica | Produtos/culturas canônicos | Relatórios agrícolas por cultura |
| Equipamento canônico | Cadastro de equipamentos | Custo operacional de Frota/Máquinas |
| Centro de custo geral | Origem, estoque, financeiro e entidades canônicas | Margem cross-módulo |

## Critérios gerais de aceite

- Cada duplicidade crítica tem fonte canônica documentada e ordem de migração.
- Nenhuma etapa exige alteração imediata de schema, migrations ou gates.
- Cada item define estado atual, risco, estratégia, impactos e aceite.
- Novos fluxos evitam cadastros paralelos.
- Legados são preservados temporariamente apenas como compatibilidade.
- Agricultura e Pecuária continuam integradas pela mesma base de Core, Estoque, Financeiro e Frota/Máquinas.

## Fora do escopo deste plano

- Dropar tabelas legadas.
- Criar migrations.
- Alterar routers, services, schemas ou modelos.
- Alterar gates de monetização ou permissão.
- Unificar fisicamente `fin_despesas` e `fin_receitas`.
- Tratar tabelas de integração externa, como staging fiscal/ERP, como fontes canônicas.
