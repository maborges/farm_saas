# Step 47 - Auditoria de Módulos Existentes para Modelo Unificado

## Objetivo

Auditar o que já existe no repositório antes de propor ou implementar qualquer novo modelo ER cross-módulo. O foco é evitar duplicidade e reaproveitar tabelas, models, schemas, routers e services já implementados.

## Escopo

- Apenas auditoria e recomendação.
- Não implementa código.
- Não altera schema.
- Não altera gates existentes.
- Não substitui migrations.
- Toda recomendação abaixo cita arquivos e tabelas existentes.

## Observação sobre o ER preliminar

O documento `docs/contexts/step47-unified-data-model-context.md` deve ser tratado como rascunho conceitual preliminar. Esta auditoria deve prevalecer antes de qualquer implementação, porque o repositório já possui entidades canônicas ou semi-canônicas para quase todos os domínios da matriz cross-módulo.

## Inventário por Módulo

| Módulo | Models/tabelas principais | Schemas | Routers | Services | Leitura arquitetural |
|---|---|---|---|---|---|
| Core / Tenant / Auth | `services/api/core/models/tenant.py` (`tenants`), `services/api/core/models/auth.py` (`usuarios`, `tenant_usuarios`, `unidade_produtiva_usuarios`, `perfis_acesso`) | `services/api/core/schemas/*.py` | `services/api/core/routers/auth.py`, `team.py`, `unidades_produtivas.py`, `fazendas.py` | `services/api/core/services/auth_service.py`, `fazenda_service.py`, `unidade_produtiva_service.py` | Manter como base comum. |
| Core / Fazenda | `services/api/core/models/unidade_produtiva.py` (`unidades_produtivas`), `services/api/core/models/fazenda.py` alias de compatibilidade | `services/api/core/schemas/unidade_produtiva_*.py`, `fazenda_*.py` | `services/api/core/routers/unidades_produtivas.py`, `fazendas.py` | `services/api/core/services/unidade_produtiva_service.py`, `fazenda_service.py` | `unidades_produtivas` já substitui fazenda. |
| Core / Áreas rurais | `services/api/core/cadastros/propriedades/models.py` (`cadastros_areas_rurais`, matrículas, registros ambientais, infraestruturas, arquivos geo) | `services/api/core/cadastros/propriedades/schemas.py` | `services/api/core/cadastros/propriedades/router.py` | `services/api/core/cadastros/propriedades/service.py` | Fonte mais forte para talhão, piquete, curral e subdivisão espacial. |
| Core / Pessoas | `services/api/core/cadastros/pessoas/models.py` (`cadastros_pessoas`, documentos, contatos, endereços, relacionamentos) | `services/api/core/cadastros/pessoas/schemas.py` | `services/api/core/cadastros/pessoas/router.py` | `services/api/core/cadastros/pessoas/service.py` | Já suporta fornecedor, cliente, funcionário e prestador por papéis. |
| Core / Produtos | `services/api/core/cadastros/produtos/models.py` (`cadastros_produtos`, marca, modelo, categoria, detalhes agrícola/estoque/EPI, `cadastros_culturas`) | `services/api/core/cadastros/produtos/schemas.py` | `services/api/core/cadastros/produtos/router.py` | `services/api/core/cadastros/produtos/service.py` | Fonte canônica recomendada para produto/insumo. |
| Agricultura | `services/api/agricola/safras/models.py`, `cultivos/models.py`, `operacoes/models.py`, `production_units/models.py`, `custos/models.py` | `services/api/agricola/*/schemas.py` | `services/api/agricola/*/router.py` | `services/api/agricola/*/service.py` | Já possui ciclo produtivo maduro. Integrar, não recriar. |
| Pecuária | `services/api/pecuaria/animal/models.py`, `models/piquete.py`, `models/manejo.py`, `producao/models.py` | `services/api/pecuaria/schemas/*.py` | `services/api/pecuaria/routers/*.py` | `services/api/pecuaria/services/*.py` | Possui modelo moderno de animal/lote/evento e modelo legado de piquete separado. |
| Estoque | `services/api/operacional/models/estoque.py` (`estoque_depositos`, `estoque_saldos`, `estoque_lotes`, `estoque_movimentacoes`, `estoque_movimentos`) | `services/api/operacional/schemas/estoque.py` | `services/api/operacional/routers/estoque.py` | `services/api/operacional/services/estoque_service.py`, `estoque_ledger.py`, `estoque_fifo.py` | `estoque_movimentos` é melhor candidato a ledger canônico; `estoque_movimentacoes` é histórico legado/operacional. |
| Financeiro | `services/api/financeiro/models/*.py` (`fin_planos_conta`, `fin_despesas`, `fin_receitas`, `fin_rateios`, `fin_notas_fiscais`, conciliação) | `services/api/financeiro/schemas/*.py` | `services/api/financeiro/routers/*.py` | `services/api/financeiro/services/*.py` | Financeiro existe como receitas/despesas separadas; não há `lancamento_financeiro` único. |
| Frota/Máquinas | `services/api/core/cadastros/equipamentos/models.py` (`cadastros_equipamentos`), `services/api/operacional/models/frota.py`, `abastecimento.py`, `apontamento.py`, `documento_equipamento.py` | `services/api/operacional/schemas/*.py`, `core/cadastros/equipamentos/schemas.py` | `services/api/operacional/routers/*.py`, `core/cadastros/equipamentos/router.py` | `services/api/operacional/services/frota_service.py`, `abastecimento_service.py` | Cadastro mestre já foi movido para Core; operacional referencia equipamento. |
| Compras | `services/api/operacional/models/compras.py` (`compras_*`) | `services/api/operacional/schemas/compras.py` e schemas inline em router | `services/api/operacional/routers/compras.py` | lógica no router e integrações com Estoque | Existe, mas fornecedor duplica Pessoa. |
| Vendas/Comercialização | `services/api/financeiro/comercializacao/models.py` (`financeiro_comercializacoes`), `services/api/agricola/romaneios/models.py`, `agricola/colheita/models.py` | `services/api/financeiro/comercializacao/schemas.py`, `agricola/romaneios/schemas.py` | `services/api/financeiro/comercializacao/router.py`, `agricola/romaneios/router.py` | `financeiro/comercializacao/service.py`, `agricola/romaneios/service.py` | Comercialização está dentro de Financeiro; usa `cadastros_pessoas` para comprador. |
| Fiscal | `services/api/financeiro/models/nota_fiscal.py` (`fin_notas_fiscais`), `integracoes/sankhya/models/__init__.py` (`sankhya_nfe`) | `services/api/financeiro/schemas/nota_fiscal.py`, `integracoes/sankhya/schemas` | `services/api/financeiro/routers/notas_fiscais.py`, `integracoes/sankhya/router.py` | `financeiro/services/nfe_*`, `integracoes/sankhya/services/*` | Fiscal está acoplado ao Financeiro e integrações; precisa clareza de ownership antes de virar módulo próprio. |

## Classificação por Entidade da Matriz

| Entidade da matriz | Implementação existente | Classificação | Recomendação |
|---|---|---|---|
| Fazenda | `unidades_produtivas` em `services/api/core/models/unidade_produtiva.py`; `Fazenda = UnidadeProdutiva` em `core/models/fazenda.py` | Manter como está | Usar `unidades_produtivas` como fonte canônica. Evitar nova tabela `fazendas`; o alias já sinaliza migração concluída. |
| Unidade produtiva / área produtiva | `cadastros_areas_rurais` em `core/cadastros/propriedades/models.py`; `production_units` em `agricola/production_units/models.py` | Ajustar para fonte canônica por nível | `unidades_produtivas` = propriedade/fazenda; `cadastros_areas_rurais` = talhão/piquete/curral/área; `production_units` = unidade econômica agrícola safra+cultivo+área. |
| Pessoa | `cadastros_pessoas` e relacionamentos em `core/cadastros/pessoas/models.py` | Ajustar para virar fonte canônica | Migrar consumidores que ainda usam cadastros próprios ou texto livre para `cadastros_pessoas` + `cadastros_pessoa_relacionamentos`. |
| Fornecedor | `compras_fornecedores` em `operacional/models/compras.py`; `cadastros_pessoas` com relacionamento FORNECEDOR | Depreciar/substituir | `compras_fornecedores` duplica Pessoa. Deve virar compatibilidade ou ponte para `cadastros_pessoas`. |
| Cliente/comprador | `cadastros_pessoas` em comercialização (`comprador_id`), mas `fin_receitas.cliente` texto livre existe | Integrar com módulo central | Manter `pessoa_id` em `fin_receitas`; reduzir uso de `cliente` texto livre. |
| Produto/insumo | `cadastros_produtos` em `core/cadastros/produtos/models.py`; estoque usa `ProdutoCatalogo` reexportado em `core/cadastros/models.py` | Manter como fonte canônica | Não criar `produto` novo em Estoque, Agricultura ou Pecuária. |
| Cultura/cultivo agrícola | `cadastros_culturas` em Core; tabela antiga `culturas` em `agricola/cadastros/models.py`; `cultivos` em Agricultura | Integrar/depreciar duplicidade | `cadastros_culturas` deve ser catálogo; `cultivos` é entidade produtiva; `culturas` legado deve ser depreciada. |
| Estoque | `estoque_depositos`, `estoque_saldos`, `estoque_lotes`, `estoque_movimentacoes`, `estoque_movimentos` em `operacional/models/estoque.py` | Ajustar para fonte canônica | Padronizar `estoque_movimentos` como ledger append-only e tratar `estoque_movimentacoes` como camada legado/operacional até migração. |
| Centro de custo | Não há `centro_custo` explícito; existe `fin_planos_conta`, `fin_rateios`, `cost_allocations` | Criar novo ou formalizar existente | Gap real. `fin_rateios` rateia despesas para safra/talhão; `cost_allocations` apropria custo agrícola. Falta centro de custo geral para Agricultura, Pecuária e Frota. |
| Financeiro | `fin_despesas`, `fin_receitas`, `fin_rateios`, `fin_planos_conta`, `fin_lancamentos_bancarios` | Manter e ajustar | Não criar `lancamento_financeiro` genérico sem plano de migração; hoje a fonte é dual: despesas/receitas. |
| Safra | `safras`, `safra_talhoes`, `safra_fase_historico` em `agricola/safras/models.py` | Manter como está | Fonte canônica agrícola para período produtivo. |
| Cultivo | `cultivos`, `cultivo_areas` em `agricola/cultivos/models.py` | Manter como está | Fonte canônica da unidade produtiva agrícola de negócio. |
| Operação agrícola | `operacoes_agricolas`, `operacoes_execucoes`, `insumos_operacao` em `agricola/operacoes/models.py` | Manter e integrar | Já integra Estoque, Financeiro e `cost_allocations` em `agricola/operacoes/service.py`. |
| Rebanho/lote | `pec_lotes` em `pecuaria/animal/models.py`; não há tabela explícita `rebanho` | Ajustar/criar novo se necessário | `pec_lotes` é fonte para lote. Falta entidade agregadora `rebanho` se a regra de negócio exigir agrupamento acima do lote. |
| Animal | `pec_animais`, `pec_eventos_animal` em `pecuaria/animal/models.py` | Manter como está | Modelo moderno; não duplicar em produto/estoque. |
| Piquete | `pec_piquetes` em `pecuaria/models/piquete.py`; `cadastros_areas_rurais` suporta `PIQUETE` | Depreciar/substituir | `pec_piquetes` duplica área rural. Preferir `cadastros_areas_rurais` tipo `PIQUETE`; manter `pec_piquetes` apenas compatibilidade até migração. |
| Manejo pecuário | `pec_manejos_lote` em `pecuaria/models/manejo.py`; `pec_eventos_animal` em `pecuaria/animal/models.py` | Integrar | Coletivo em `pec_manejos_lote`, individual em `pec_eventos_animal`. Falta integração com Estoque para vacina/medicação. |
| Máquina/veículo | `cadastros_equipamentos` em Core; Frota referencia `cadastros_equipamentos.id` | Manter como fonte canônica | Não recriar `maquina_veiculo`. Resolver inconsistências de nomes em serviços. |
| Compras | `compras_pedidos`, `compras_itens_pedido`, `compras_recebimentos`, `compras_cotacoes` | Manter e integrar | Compras já integra produtos e recebimento/estoque, mas fornecedor deve migrar para Pessoa. |
| Vendas | `financeiro_comercializacoes`, `romaneios_colheita`, `agricola_produtos_colhidos` | Integrar com módulo central | Há ciclo venda agrícola; falta generalizar para Pecuária sem duplicar Financeiro. |
| Fiscal | `fin_notas_fiscais`, `sankhya_nfe`, campos NF em receitas/despesas/comercializações | Integrar com módulo central | Fiscal é real, mas disperso. Antes de novo módulo fiscal, definir se `fin_notas_fiscais` será fonte canônica. |

## Duplicidades Identificadas

### Produto duplicado por módulo

- `cadastros_produtos` em `services/api/core/cadastros/produtos/models.py` é o catálogo unificado de insumos.
- `core/cadastros/models.py` reexporta `ProdutoCatalogo` para compatibilidade.
- `agricola/cadastros/models.py` mantém `culturas`, mas Core já tem `cadastros_culturas` em `core/cadastros/produtos/models.py`.
- `sankhya_produtos` em `services/api/integracoes/sankhya/models/__init__.py` é tabela de staging/sincronização externa, não deve virar fonte canônica.

Recomendação: manter `cadastros_produtos` e `cadastros_culturas` como fontes canônicas. Depreciar `agricola/cadastros/models.py` (`culturas`) e tratar `sankhya_produtos` como espelho de integração.

### Pessoa/fornecedor/cliente duplicado

- `cadastros_pessoas` e `cadastros_pessoa_relacionamentos` em `core/cadastros/pessoas/models.py` já modelam papéis.
- `compras_fornecedores` em `operacional/models/compras.py` duplica fornecedor com `nome_fantasia`, `cnpj_cpf`, `email`, `telefone`.
- `fin_despesas` ainda possui `fornecedor` texto livre, embora já tenha `pessoa_id`.
- `fin_receitas` ainda possui `cliente` texto livre, embora já tenha `pessoa_id`.
- `sankhya_pessoas` é staging de integração, não fonte canônica.

Recomendação: ajustar Compras para consumir `cadastros_pessoas` com papel FORNECEDOR. Manter campos texto livre em Financeiro apenas como legado/fallback.

### Estoque paralelo

- `estoque_movimentacoes` em `operacional/models/estoque.py` é histórico de entrada/saída usado pelo serviço.
- `estoque_movimentos` no mesmo arquivo é ledger append-only com `tenant_id`, unidade de medida, origem e vínculos agrícolas.
- `agricola/colheita/models.py` cria `agricola_produtos_colhidos`, que representa lote colhido e não saldo genérico.
- `financeiro/comercializacao/models.py` referencia `produto_colhido_id`, mas não usa `estoque_movimentos`.

Recomendação: escolher `estoque_movimentos` como ledger canônico de movimentação. Manter `estoque_saldos` como estado atual. Integrar `agricola_produtos_colhidos` ao Estoque por regra clara de entrada/baixa, sem criar outro saldo agrícola.

### Financeiro paralelo

- `fin_despesas` e `fin_receitas` são fontes atuais para contas a pagar/receber.
- `agricola/custos/models.py` (`cost_allocations`) apropria custo por `production_unit`.
- `fin_rateios` rateia despesas para safra/talhão.
- `operacoes_agricolas` mantém `custo_total` e `custo_por_ha`.
- `romaneios_colheita` mantém `receita_total`.
- `pec_manejos_lote` mantém `custo_total` e `valor_venda`.

Recomendação: manter valores operacionais nos módulos produtivos como contexto/resultado local, mas Financeiro deve continuar fonte canônica de receitas/despesas. Formalizar `cost_allocations` como projeção gerencial, não lançamento financeiro primário.

### Unidade produtiva duplicada

- `unidades_produtivas` é a fazenda/propriedade operacional.
- `cadastros_areas_rurais` é a hierarquia espacial dentro da unidade produtiva.
- `production_units` é uma unidade econômica agrícola (`safra + cultivo + área`).
- `pec_piquetes` duplica área espacial que já cabe em `cadastros_areas_rurais` tipo `PIQUETE`.
- `imoveis_rurais` e `cadastros_propriedades` modelam dimensão jurídica/documental e podem sobrepor dados de propriedade.

Recomendação: não criar nova tabela `unidade_produtiva`. Usar `unidades_produtivas`, `cadastros_areas_rurais` e `production_units` com papéis distintos. Planejar convergência de `pec_piquetes` para `cadastros_areas_rurais`.

### Máquina/frota duplicada

- `cadastros_equipamentos` em Core é mestre e o próprio comentário diz que substitui `frota_maquinarios`.
- `operacional/models/frota.py`, `abastecimento.py`, `apontamento.py` e `documento_equipamento.py` referenciam `cadastros_equipamentos.id`.
- Há inconsistências de nomenclatura nos serviços: `FrotaService` usa `maquinario_id` em alguns pontos, enquanto os models têm `equipamento_id`.

Recomendação: manter `cadastros_equipamentos` como fonte canônica. Ajustar futuramente services/schemas para padronizar `equipamento_id`, sem criar tabela nova.

## Integrações Já Implementadas

| Integração | Evidência | Status |
|---|---|---|
| Operação agrícola baixa estoque por FIFO | `services/api/agricola/operacoes/service.py` usa `consumir_lotes_fifo`, cria `MovimentacaoEstoque` e chama `registrar_ledger_estoque` | Implementada, mas com dois históricos (`estoque_movimentacoes` e `estoque_movimentos`). |
| Operação agrícola gera despesa | `agricola/operacoes/service.py` cria `Despesa` com `origem_tipo="OPERACAO_AGRICOLA"` | Implementada. |
| Operação agrícola gera apropriação de custo | `agricola/operacoes/service.py` chama `registrar_cost_allocation`; model em `agricola/custos/models.py` | Implementada para Agricultura. |
| Rateio financeiro projeta custo agrícola | `agricola/custos/allocation_service.py` lê `fin_rateios` e insere `cost_allocations` | Implementada. |
| Romaneio gera produto colhido | `agricola/romaneios/service.py` cria `ProdutoColhido` | Implementada. |
| Romaneio gera receita | `agricola/romaneios/service.py` cria `Receita` com `origem_tipo="ROMANEIO_COLHEITA"` | Implementada. |
| Manejo pecuário gera receita/despesa | `pecuaria/services/manejo_service.py` cria `Despesa` para VACINACAO/MEDICACAO e `Receita` para VENDA/ABATE | Parcial; não usa `origem_id/origem_tipo` nem Estoque. |
| Abastecimento baixa estoque ou gera despesa | `operacional/services/abastecimento_service.py` baixa por nome do combustível para abastecimento interno e cria `Despesa` para externo | Implementada, mas frágil por busca textual de produto. |
| OS de frota baixa estoque e gera despesa | `operacional/services/frota_service.py` usa `EstoqueService.registrar_saida_insumo` e cria `Despesa` | Implementada, mas há risco por inconsistência `maquinario_id`/`equipamento_id`. |
| Compras recebe produto no estoque | `operacional/routers/compras.py` importa `EstoqueService`, `registrar_ledger_estoque`, `LoteEstoque`, `SaldoEstoque` | Implementada no router; precisa service dedicado e fornecedor canônico. |
| Comercialização usa comprador canônico | `financeiro/comercializacao/models.py` usa `comprador_id -> cadastros_pessoas.id` | Boa base para Vendas. |

## Gaps Reais Antes de Implementar Novo ER

| Gap | Evidência | Recomendação |
|---|---|---|
| Centro de custo geral não existe | Não há tabela `centro_custo`; existem `fin_rateios` e `cost_allocations` | Criar apenas após decidir como convive com `fin_rateios` e `production_units`; não substituir sem migração. |
| Lançamento financeiro único não existe | Financeiro usa `fin_despesas` e `fin_receitas` separados | Não criar `lancamento_financeiro` novo sem plano de compatibilidade. Uma view ou facade pode ser primeiro passo. |
| Estoque tem dois modelos de movimentação | `estoque_movimentacoes` e `estoque_movimentos` coexistem | Definir `estoque_movimentos` como ledger e migrar consumidores gradualmente. |
| Fornecedor duplicado | `compras_fornecedores` duplica `cadastros_pessoas` | Integrar Compras com Pessoa antes de expandir compras. |
| Piquete duplicado | `pec_piquetes` duplica `cadastros_areas_rurais` tipo `PIQUETE` | Migrar pecuária para `cadastros_areas_rurais.area_id`. |
| Pecuária sem consumo de estoque em manejo | `pec_manejos_lote` não referencia produto/lote de estoque; `EventoAnimal` tem `produto_id`, mas service de manejo não baixa estoque | Integrar vacinação/medicação com `cadastros_produtos` + `estoque_movimentos`. |
| Pecuária sem apropriação gerencial equivalente à Agricultura | `cost_allocations` é agrícola e aponta `production_units` | Criar projeção gerencial pecuária ou generalizar apropriação antes de dashboards unificados. |
| Frota usa produto por nome no abastecimento | `abastecimento_service.py` chama `registrar_saida_insumo_por_nome` | Adicionar vínculo explícito de combustível/produto futuramente; não criar novo produto. |
| Inconsistência de nomenclatura Frota | `operacional/models/frota.py` usa `equipamento_id`; `frota_service.py` usa `maquinario_id` em consultas/criação de histórico | Corrigir em etapa própria antes de expandir integrações. |
| Fiscal disperso | `fin_notas_fiscais`, campos NF em `fin_*`, `financeiro_comercializacoes`, `sankhya_nfe` | Definir ownership fiscal antes de novo módulo Fiscal. |
| Imóveis/propriedades sobrepõem Core | `unidades_produtivas`, `cadastros_propriedades`, `imoveis_rurais`, `cadastros_areas_rurais` coexistem | Documentar papéis: operacional, jurídico/documental e espacial. Evitar nova entidade de fazenda. |

## Recomendações por Status

### Manter como está

- `tenants` em `services/api/core/models/tenant.py`.
- `usuarios`, `tenant_usuarios`, `unidade_produtiva_usuarios`, `perfis_acesso` em `services/api/core/models/auth.py`.
- `unidades_produtivas` em `services/api/core/models/unidade_produtiva.py`.
- `safras`, `cultivos`, `cultivo_areas`, `operacoes_agricolas`, `operacoes_execucoes` em `services/api/agricola/*/models.py`.
- `pec_animais`, `pec_eventos_animal`, `pec_lotes` em `services/api/pecuaria/animal/models.py`.
- `cadastros_equipamentos` em `services/api/core/cadastros/equipamentos/models.py`.

### Ajustar para virar fonte canônica

- `cadastros_pessoas` em `services/api/core/cadastros/pessoas/models.py`: fonte para fornecedores, clientes, operadores, prestadores e compradores.
- `cadastros_produtos` em `services/api/core/cadastros/produtos/models.py`: fonte para insumos agrícolas, pecuários, peças, combustível e EPI.
- `cadastros_areas_rurais` em `services/api/core/cadastros/propriedades/models.py`: fonte para talhão, piquete, curral, armazém e áreas ambientais.
- `estoque_movimentos` em `services/api/operacional/models/estoque.py`: fonte canônica de ledger.

### Integrar com módulo central

- `fin_despesas` e `fin_receitas` devem receber origens consistentes de Agricultura, Pecuária, Frota, Compras e Vendas.
- `cost_allocations` deve continuar integrando custos agrícolas, mas precisa estratégia para Pecuária e Frota.
- `financeiro_comercializacoes` deve permanecer ligado a `cadastros_pessoas` e, futuramente, a estoque/produção pecuária.
- `frota_abastecimentos`, `frota_apontamentos_uso` e `frota_ordens_servico` devem integrar custos via Financeiro e consumo via Estoque com produto explícito.

### Depreciar/substituir

- `compras_fornecedores` em `services/api/operacional/models/compras.py`: substituir por `cadastros_pessoas` com papel FORNECEDOR.
- `culturas` em `services/api/agricola/cadastros/models.py`: substituir por `cadastros_culturas`.
- `pec_piquetes` em `services/api/pecuaria/models/piquete.py`: substituir por `cadastros_areas_rurais` tipo `PIQUETE`.
- Campos texto `fin_despesas.fornecedor` e `fin_receitas.cliente`: manter como legado/fallback, preferir `pessoa_id`.

### Criar novo

- Centro de custo unificado, se o produto exigir gestão gerencial cross-módulo além de `fin_rateios`.
- Camada de apropriação de custo generalizada para Pecuária/Frota, se `cost_allocations` não puder ser ampliada sem quebrar Agricultura.
- Facade/read model de lançamento financeiro unificado, se dashboards precisarem consultar receitas e despesas sem duplicar lógica.
- Tabela de vínculo combustível-produto para Frota, evitando busca textual por nome.

## Recomendação de Próxima Etapa

Antes de implementar o ER unificado:

1. Congelar a decisão de ownership: `unidades_produtivas`, `cadastros_areas_rurais`, `cadastros_pessoas`, `cadastros_produtos`, `cadastros_equipamentos`, `estoque_movimentos`, `fin_despesas/fin_receitas`.
2. Definir migrações conceituais para `compras_fornecedores`, `culturas`, `pec_piquetes` e uso de `estoque_movimentacoes`.
3. Só então revisar o documento de ER para refletir tabelas existentes, em vez de criar nomes novos como `fazenda`, `produto`, `estoque_local`, `lancamento_financeiro` ou `maquina_veiculo`.

## Critérios de Aceite

- Models, schemas, routers e services existentes foram mapeados por módulo.
- Entidades da matriz cross-módulo foram classificadas.
- Duplicidades foram identificadas com arquivos/tabelas existentes.
- Gaps reais foram listados antes de qualquer implementação.
- Nenhum código, schema ou gate foi alterado.
