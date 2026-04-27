# Step 48 - Ownership Canônico das Entidades Cross-Módulo

## Objetivo

Congelar a decisão arquitetural de ownership das entidades compartilhadas do SaaS agro antes de qualquer nova implementação. Este documento define quais tabelas/models existentes são a fonte da verdade atual para Core, Agricultura, Pecuária e módulos integradores.

## Base

- `docs/contexts/step46-cross-module-integration-monetization-context.md`
- `docs/contexts/step47-existing-modules-inventory-context.md`

## Escopo

- Não implementa código.
- Não altera migrations.
- Não altera gates existentes.
- Não renomeia tabelas.
- Não cria novo ER.
- Apenas documenta decisões de ownership, consumo e pendências de migração.

## Regra Geral

Novas funcionalidades devem consumir as fontes canônicas listadas aqui. Quando uma entidade já existe como fonte canônica, não criar outra tabela paralela em módulo produtivo, financeiro, estoque, frota, compras, vendas ou fiscal.

## Ownership Canônico

| Entidade | Fonte canônica atual | Arquivos/tabelas | Módulo dono | Consumidores | Não criar novamente | Pendências de migração/depreciação |
|---|---|---|---|---|---|---|
| Tenant | `Tenant` | `services/api/core/models/tenant.py` (`tenants`) | Core | Todos os módulos, billing, backoffice, integrações | `tenant`, `empresa`, `conta_cliente` por módulo | Nenhuma pendência estrutural identificada para cross-módulo. |
| Usuário/permissão | `Usuario`, `TenantUsuario`, `UnidadeProdutivaUsuario`, `PerfilAcesso` | `services/api/core/models/auth.py` (`usuarios`, `tenant_usuarios`, `unidade_produtiva_usuarios`, `perfis_acesso`) | Core / Auth | Todos os módulos, RBAC, convites, equipe, auditoria | `usuario_agricola`, `usuario_pecuaria`, permissões locais por módulo | Módulos devem só consumir RBAC central; evitar permissões hardcoded fora de gates/roles existentes. |
| Unidade produtiva/fazenda | `UnidadeProdutiva`; alias `Fazenda` para compatibilidade | `services/api/core/models/unidade_produtiva.py` (`unidades_produtivas`), `services/api/core/models/fazenda.py` | Core | Agricultura, Pecuária, Estoque, Financeiro, Frota, Imóveis, Fiscal, Relatórios | Nova tabela `fazendas` ou `propriedades_operacionais` | Manter compatibilidade com nomes legados `fazenda`; novas referências devem usar `unidade_produtiva_id`. |
| Área rural/talhão/piquete/curral | `AreaRural` | `services/api/core/cadastros/propriedades/models.py` (`cadastros_areas_rurais`) | Core / Cadastros de Propriedades | Agricultura, Pecuária, Imóveis, Ambiental, Relatórios, NDVI, Operações | `talhoes`, `pec_piquetes`, `currais` como cadastros espaciais separados | Depreciar gradualmente `services/api/pecuaria/models/piquete.py` (`pec_piquetes`) em favor de `cadastros_areas_rurais` tipo `PIQUETE`. Manter `production_units` apenas como unidade econômica agrícola, não como área física. |
| Pessoa/fornecedor/cliente/prestador | `Pessoa` + documentos/contatos/endereços/relacionamentos | `services/api/core/cadastros/pessoas/models.py` (`cadastros_pessoas`, `cadastros_pessoa_relacionamentos`, tabelas auxiliares) | Core / Pessoas | Compras, Vendas, Financeiro, Fiscal, Pecuária, Frota, RH, Integrações | `fornecedores`, `clientes`, `prestadores` isolados por módulo | Substituir `compras_fornecedores` em `services/api/operacional/models/compras.py`. Reduzir uso de `fin_despesas.fornecedor` e `fin_receitas.cliente` como texto livre; preferir `pessoa_id`. Tratar `sankhya_pessoas` como staging de integração. |
| Produto/insumo | `Produto` e detalhes por tipo | `services/api/core/cadastros/produtos/models.py` (`cadastros_produtos`, `cadastros_produtos_agricola`, `cadastros_produtos_estoque`, `cadastros_produtos_epi`, marcas/modelos/categorias) | Core / Cadastros de Produtos, consumido por Estoque | Estoque, Agricultura, Pecuária, Frota, Compras, Fiscal, Financeiro | `produto_estoque`, `insumo_agricola`, `insumo_pecuario`, `peca_frota` em tabelas separadas | Manter `core/cadastros/models.py` apenas como reexport/compatibilidade. Tratar `sankhya_produtos` como staging. Não usar Produto para animal vivo ou commodity colhida. |
| Cultura agrícola | `ProdutoCultura` | `services/api/core/cadastros/produtos/models.py` (`cadastros_culturas`, `solo_parametros_cultura`) | Core / Cadastros de Produtos | Agricultura, solo, cultivos, recomendações, templates | Nova tabela `culturas` em Agricultura | Depreciar `services/api/agricola/cadastros/models.py` (`culturas`). `cultivos` continua sendo entidade produtiva, não catálogo. |
| Equipamento/máquina/veículo | `Equipamento` | `services/api/core/cadastros/equipamentos/models.py` (`cadastros_equipamentos`) | Core / Cadastros de Equipamentos | Frota, Máquinas, Agricultura, Pecuária, Estoque, Financeiro | `maquina_veiculo`, `frota_maquinarios`, cadastro local de máquinas em Agricultura/Pecuária | Padronizar services/schemas para `equipamento_id`; corrigir referências legadas como `maquinario_id` em `services/api/operacional/services/frota_service.py` em etapa própria. |
| Estoque ledger | `EstoqueMovimento` | `services/api/operacional/models/estoque.py` (`estoque_movimentos`), `services/api/operacional/services/estoque_ledger.py` | Estoque / Operacional | Agricultura, Pecuária, Frota, Compras, Vendas, Fiscal, Financeiro, Rastreabilidade | `movimentacao_estoque` nova por módulo, ledger agrícola ou ledger pecuário paralelo | Consolidar consumidores em `estoque_movimentos`. `estoque_movimentacoes` existe e deve ser tratado como histórico operacional/legado até migração. |
| Estoque saldo | `SaldoEstoque` | `services/api/operacional/models/estoque.py` (`estoque_saldos`) | Estoque / Operacional | Estoque UI, Agricultura, Pecuária, Compras, Frota, dashboards | Saldo por módulo, saldo por safra, saldo pecuário separado | Garantir que saldos sejam derivados/atualizados por movimentos. Não usar saldos de Produto como fonte única de quantidade. |
| Estoque lote | `LoteEstoque` | `services/api/operacional/models/estoque.py` (`estoque_lotes`) | Estoque / Operacional | Estoque, Agricultura, Pecuária, Compras, Fiscal, Rastreabilidade | Lote de insumo agrícola/pecuário separado | Integrar consumo pecuário com lotes de estoque. Avaliar vínculo de `agricola_produtos_colhidos` com estoque sem transformar lote colhido em duplicidade de `estoque_lotes` sem regra clara. |
| Depósito/almoxarifado | `Deposito` | `services/api/operacional/models/estoque.py` (`estoque_depositos`) | Estoque / Operacional | Estoque, Compras, Frota, Agricultura, Pecuária | `estoque_local`, `almoxarifado_agricola`, `deposito_pecuaria` novos | Pode referenciar `unidade_produtiva_id`; se precisar área física detalhada, usar `cadastros_areas_rurais`/infraestrutura como contexto, não nova árvore. |
| Financeiro receitas/despesas | `Despesa` e `Receita` | `services/api/financeiro/models/despesa.py` (`fin_despesas`), `services/api/financeiro/models/receita.py` (`fin_receitas`) | Financeiro | Agricultura, Pecuária, Frota, Compras, Vendas, Fiscal, Contabilidade, Dashboards | `lancamento_financeiro` físico novo sem plano de migração, financeiro agrícola/pecuário paralelo | Se for necessário lançamento unificado, iniciar por facade/read model sobre `fin_despesas` e `fin_receitas`. Padronizar `origem_tipo/origem_id` em integrações. |
| Plano de contas | `PlanoConta` | `services/api/financeiro/models/plano_conta.py` (`fin_planos_conta`) | Financeiro | Financeiro, Agricultura, Pecuária, Frota, Compras, Fiscal, Contabilidade | Categorias financeiras locais por módulo | Manter como classificação contábil/financeira. Não confundir com centro de custo gerencial. |
| Rateio financeiro | `Rateio` | `services/api/financeiro/models/rateio.py` (`fin_rateios`) | Financeiro | Agricultura, relatórios, custo de produção | Rateios por módulo sem vínculo financeiro | Hoje atende safra/talhão. Pendente decisão sobre centro de custo geral cross-módulo. |
| Apropriação de custo agrícola | `CostAllocation` | `services/api/agricola/custos/models.py` (`cost_allocations`), `services/api/agricola/custos/allocation_service.py` | Agricultura com origem Financeiro/Estoque | Agricultura, dashboards agrícolas, custo por `production_unit` | Nova tabela de custo agrícola paralela | Manter como projeção gerencial agrícola. Antes de generalizar para Pecuária/Frota, decidir se vira apropriação cross-módulo ou se haverá entidade equivalente. |
| Safra | `Safra` | `services/api/agricola/safras/models.py` (`safras`, `safra_talhoes`, `safra_fase_historico`) | Agricultura | Agricultura, Financeiro, Estoque, Vendas, Rastreabilidade, Relatórios | `safra` duplicada em Financeiro/Estoque/Vendas | Novas integrações devem referenciar `safras.id`. Campo `cultura` em `safras` é legado/contexto; cultura operacional deve estar em `cultivos`. |
| Cultivo | `Cultivo`, `CultivoArea` | `services/api/agricola/cultivos/models.py` (`cultivos`, `cultivo_areas`) | Agricultura | Operações, custos, estoque, romaneios, produção, relatórios | `cultivo` paralelo por talhão ou por operação | Manter como unidade produtiva agrícola de negócio. |
| Unidade econômica agrícola | `ProductionUnit` | `services/api/agricola/production_units/models.py` (`production_units`, `status_consorcio_area`) | Agricultura | Cost allocations, estoque ledger, operações, dashboards | Usar `production_units` como área física ou fazenda | Não substituir `unidades_produtivas` nem `cadastros_areas_rurais`; é recorte safra+cultivo+área. |
| Operação agrícola | `OperacaoAgricola`, `OperacaoExecucao`, `InsumoOperacao` | `services/api/agricola/operacoes/models.py` (`operacoes_agricolas`, `operacoes_execucoes`, `insumos_operacao`) | Agricultura | Estoque, Financeiro, Frota, Caderno, Rastreabilidade, Relatórios | `atividade_agricola`, `consumo_agricola` paralelo | Já integra Estoque e Financeiro em `services/api/agricola/operacoes/service.py`. Futuras mudanças devem preservar esses vínculos. |
| Animal | `Animal`, `EventoAnimal` | `services/api/pecuaria/animal/models.py` (`pec_animais`, `pec_eventos_animal`) | Pecuária | Pecuária, Financeiro, Vendas, Fiscal, Rastreabilidade | Animal como `produto`, animal em estoque, evento animal em financeiro | Manter animal como ativo biológico, não produto/insumo. Eventos individuais devem usar `pec_eventos_animal`. |
| Lote pecuário | `LoteAnimal` | `services/api/pecuaria/animal/models.py` (`pec_lotes`) | Pecuária | Manejos, produção de leite, vendas, financeiro, relatórios | `lote_bovino`, `rebanho_lote` novo | Manter `pec_lotes` como fonte atual. Avaliar criação de `rebanho` apenas se houver necessidade de agrupamento acima do lote. |
| Manejo pecuário coletivo | `ManejoLote` | `services/api/pecuaria/models/manejo.py` (`pec_manejos_lote`) | Pecuária | Financeiro, Estoque, Rastreabilidade, Relatórios | Manejo financeiro ou manejo estoque em tabelas paralelas | Integrar com Estoque para vacinação/medicação e padronizar `origem_tipo/origem_id` nas receitas/despesas geradas. |
| Produção pecuária | `ProducaoLeite` | `services/api/pecuaria/producao/models.py` (`pec_producao_leite`) | Pecuária | Comercialização, Financeiro, Estoque/commodities, Relatórios | Produto leiteiro paralelo fora da Pecuária sem integração | Definir integração de leite com estoque/comercialização antes de expandir vendas pecuárias. |
| Comercialização/vendas agrícolas | `ComercializacaoCommodity`, `RomaneioColheita`, `ProdutoColhido` | `services/api/financeiro/comercializacao/models.py` (`financeiro_comercializacoes`), `services/api/agricola/romaneios/models.py` (`romaneios_colheita`), `services/api/agricola/colheita/models.py` (`agricola_produtos_colhidos`) | Comercialização hoje dentro de Financeiro + Agricultura | Financeiro, Fiscal, Estoque, Agricultura, Dashboards | Nova venda agrícola isolada, cliente em vendas separado | Manter `comprador_id` apontando para `cadastros_pessoas`. Definir se Comercialização sai de Financeiro para módulo próprio sem quebrar tabela atual. |
| Comercialização/vendas pecuárias | `Receita` gerada por `ManejoLote`; eventos animal têm campos de venda | `services/api/pecuaria/services/manejo_service.py`, `services/api/pecuaria/models/manejo.py`, `services/api/pecuaria/animal/models.py`, `services/api/financeiro/models/receita.py` | Pecuária + Financeiro | Financeiro, Fiscal, Relatórios, Rastreabilidade | Tabela de venda pecuária nova sem integrar com `cadastros_pessoas` e `fin_receitas` | Gap real: falta entidade comercial pecuária equivalente a `financeiro_comercializacoes`. Criar só após desenho de integração com Pessoa, Receita e Fiscal. |
| Compras | `PedidoCompra`, `ItemPedidoCompra`, `RecebimentoParcial`, `ItemRecebimento`, `CotacaoFornecedor`, `DevolucaoFornecedor` | `services/api/operacional/models/compras.py` (`compras_pedidos`, `compras_itens_pedido`, `compras_recebimentos`, `compras_recebimentos_itens`, `compras_cotacoes`, `compras_devolucoes`) | Compras / Operacional | Estoque, Financeiro, Fiscal, Pessoas, Produtos | Pedido/recebimento por módulo produtivo | Manter pedidos e recebimentos. Depreciar apenas `compras_fornecedores` como cadastro duplicado; trocar por Pessoa com papel FORNECEDOR. |
| Fiscal/notas | `NotaFiscal` | `services/api/financeiro/models/nota_fiscal.py` (`fin_notas_fiscais`), `services/api/financeiro/routers/notas_fiscais.py`, `services/api/financeiro/services/nfe_*` | Fiscal atualmente em Financeiro | Financeiro, Vendas, Compras, Estoque, Contabilidade, Integrações | `nota_fiscal_agricola`, `nota_fiscal_pecuaria`, NF local por módulo | Até existir módulo Fiscal separado, `fin_notas_fiscais` é fonte operacional. Campos de NF em receitas/despesas/comercializações são referências auxiliares. |
| Integração fiscal/ERP | Tabelas Sankhya | `services/api/integracoes/sankhya/models/__init__.py` (`sankhya_pessoas`, `sankhya_produtos`, `sankhya_nfe`, `sankhya_lancamentos_financeiros`) | Integrações | Core, Produtos, Pessoas, Financeiro, Fiscal | Tratar staging externo como fonte interna de verdade | Tabelas Sankhya são espelhos/staging. Devem sincronizar para fontes canônicas, não substituí-las. |

## Decisões de Não Recriação

- Não criar nova tabela `fazendas`; usar `unidades_produtivas`.
- Não criar novo cadastro de fornecedor/cliente/prestador; usar `cadastros_pessoas` com papéis.
- Não criar novo catálogo de insumos por módulo; usar `cadastros_produtos`.
- Não criar novo catálogo de culturas em Agricultura; usar `cadastros_culturas`.
- Não criar novo cadastro de máquinas/veículos; usar `cadastros_equipamentos`.
- Não criar estoque agrícola, pecuário ou frota separado; usar Estoque central.
- Não criar financeiro agrícola ou pecuário separado; usar `fin_despesas` e `fin_receitas` com origem rastreável.
- Não usar tabelas de integração externa como fonte canônica interna.

## Pendências Priorizadas

| Prioridade | Pendência | Motivo |
|---|---|---|
| Alta | Migrar Compras de `compras_fornecedores` para `cadastros_pessoas` | Remove duplicidade crítica de fornecedor e melhora integração fiscal/financeira. |
| Alta | Definir `estoque_movimentos` como ledger único em novos fluxos | Evita estoque paralelo e melhora auditoria. |
| Alta | Padronizar origem financeira (`origem_tipo/origem_id`) em Pecuária, Frota, Compras e Vendas | Permite dashboards e rastreabilidade financeira cross-módulo. |
| Média | Depreciar `pec_piquetes` em favor de `cadastros_areas_rurais` tipo `PIQUETE` | Unifica área rural/talhão/piquete/curral. |
| Média | Depreciar `agricola/cadastros/models.py` (`culturas`) em favor de `cadastros_culturas` | Remove duplicidade de cultura. |
| Média | Corrigir nomenclatura `maquinario_id` vs `equipamento_id` em Frota | Reduz risco de bug e consolida `cadastros_equipamentos`. |
| Média | Definir estratégia de centro de custo geral | Hoje há rateio e cost allocation, mas não centro de custo cross-módulo. |
| Baixa | Separar módulo Fiscal conceitual de Financeiro sem quebrar `fin_notas_fiscais` | Fiscal já existe operacionalmente, mas ownership ainda está acoplado ao Financeiro. |

## Regra de Manutenção

Ao criar nova funcionalidade, verificar esta ordem:

1. Existe fonte canônica neste documento?
2. A entidade nova é realmente uma especialização ou apenas duplicidade?
3. O módulo consumidor pode referenciar a fonte canônica por FK ou origem rastreável?
4. Há campo legado que deve ser mantido apenas como compatibilidade?
5. A mudança exige plano de migração/depreciação antes de criar tabela nova?

Se a resposta indicar duplicidade, não criar nova tabela. Atualizar ou integrar com a fonte canônica existente.

## Critérios de Aceite

- Ownership canônico definido para todas as entidades solicitadas.
- Cada entidade possui fonte atual, arquivos/tabelas, módulo dono, consumidores, bloqueios contra recriação e pendências.
- Decisão alinhada com a matriz cross-módulo e com a auditoria de módulos existentes.
- Nenhum código, migration ou gate alterado.
