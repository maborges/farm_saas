# Step 46 - Matriz de Integração e Monetização Cross-Módulos

## Objetivo

Mapear como os módulos Agricultura, Pecuária, Financeiro, Estoque, Frota, Máquinas, Compras, Vendas, Fiscal e Core se integram dentro da mesma arquitetura SaaS agro, definindo entidades compartilhadas, dependências operacionais, regras de monetização e riscos de duplicidade.

## Escopo

- Documento de arquitetura e monetização.
- Não altera gates existentes.
- Não implementa código.
- Não cria novos planos nem muda nomes canônicos de tiers.
- Usa `Core` como base comum e `A1_PLANEJAMENTO`, `PROFISSIONAL` e `ENTERPRISE` como níveis de monetização.

## Princípio Arquitetural

O SaaS deve operar como uma plataforma única com módulos especializados. Agricultura e Pecuária são módulos produtivos, mas não devem criar cadastros, estoque, financeiro, frota ou dashboards paralelos. A integração correta é feita por entidades compartilhadas do Core e por módulos integradores.

```
Core
  ├── Agricultura
  ├── Pecuária
  ├── Financeiro
  ├── Estoque
  ├── Frota / Máquinas
  ├── Compras
  ├── Vendas / Comercialização
  └── Fiscal / Contabilidade
```

## Classificação dos Módulos

| Módulo | Papel arquitetural | Classificação | Função principal |
|---|---|---|---|
| Core | Fundação comum | Core | Tenant, fazendas, usuários, permissões, planos, configurações globais e cadastros comuns |
| Agricultura | Produção vegetal | Operacional | Safras, talhões, operações de campo, insumos agrícolas, rastreabilidade agrícola |
| Pecuária | Produção animal | Operacional | Rebanho, lotes, piquetes, manejos, sanidade, nutrição e rastreabilidade animal |
| Financeiro | Consolidador econômico | Integrador | Receitas, despesas, fluxo de caixa, centros de custo, contas a pagar/receber e custo de produção |
| Estoque | Consolidador físico de insumos/produtos | Integrador | Produtos, saldos, movimentações, lotes, validade, almoxarifados e valoração |
| Frota | Operação de veículos/equipamentos | Integrador | Veículos, abastecimento, manutenção, custo hora e documentação |
| Máquinas | Operação de implementos/máquinas | Integrador operacional | Máquinas agrícolas, implementos, horas trabalhadas, disponibilidade e apropriação de custo |
| Compras | Entrada comercial | Integrador comercial | Requisições, cotações, pedidos, fornecedores e entrada de insumos/serviços |
| Vendas / Comercialização | Saída comercial | Integrador comercial | Clientes, contratos, romaneios, vendas de produção vegetal ou animal |
| Fiscal / Contabilidade | Compliance e escrituração | Premium / Integrador regulatório | NF-e, documentos fiscais, LCDPR, integração contábil, auditoria e obrigações legais |

## Entidades Compartilhadas

| Entidade | Dono canônico | Consumidores | Regra de integração |
|---|---|---|---|
| Fazenda | Core | Todos os módulos | Toda entidade operacional deve referenciar fazenda ou tenant. Não duplicar fazenda em módulos produtivos. |
| Unidade produtiva | Core com especialização operacional | Agricultura, Pecuária, Financeiro, Estoque, Relatórios | Talhão, piquete, curral, galpão ou área devem usar uma base comum de unidade produtiva quando possível. |
| Pessoa | Core / Pessoas | Compras, Vendas, Financeiro, Fiscal, Pecuária | Cadastro único para pessoa física/jurídica, com papéis adicionais. |
| Fornecedor | Pessoa com papel fornecedor | Compras, Estoque, Financeiro, Fiscal | Não deve existir cadastro de fornecedor separado em Compras, Estoque ou Financeiro. |
| Cliente | Pessoa com papel cliente | Vendas, Financeiro, Fiscal | Cliente de grãos, animais, leite ou serviços deve ser papel do cadastro de Pessoa. |
| Produto/Insumo | Estoque | Agricultura, Pecuária, Compras, Fiscal, Financeiro | Sementes, defensivos, fertilizantes, vacinas, ração, sal, peças e combustível usam cadastro único com categoria. |
| Estoque | Estoque | Agricultura, Pecuária, Frota, Compras, Fiscal | Baixas operacionais devem gerar movimentação centralizada de estoque, não saldos por módulo. |
| Centro de custo | Financeiro | Agricultura, Pecuária, Frota, Máquinas, Compras | Talhão, safra, lote, rebanho, máquina e atividade devem poder receber rateio econômico. |
| Safra / Lote / Rebanho | Agricultura e Pecuária | Financeiro, Estoque, Vendas, Rastreabilidade | Safra é referência produtiva agrícola; lote/rebanho é referência produtiva pecuária. Ambos alimentam custo, estoque e venda. |
| Máquina / Veículo | Frota / Máquinas | Agricultura, Pecuária, Financeiro, Estoque | Uso operacional deve apropriar horas, combustível, manutenção e custo para atividades produtivas. |
| Usuário / Permissão | Core | Todos os módulos | RBAC e escopo de acesso devem ser centralizados. Módulos só consomem permissões. |

## Matriz de Dependências entre Módulos

| Módulo consumidor | Depende de Core | Financeiro | Estoque | Frota / Máquinas | Compras | Vendas | Fiscal |
|---|---|---|---|---|---|---|---|
| Agricultura | Obrigatório | Custos, centro de custo, orçamento, fluxo de caixa | Insumos, sementes, defensivos, fertilizantes, produção colhida | Operações mecanizadas, combustível, custo hora | Requisição e compra de insumos | Romaneio e venda de produção | NF-e, receituário, rastreabilidade e auditoria |
| Pecuária | Obrigatório | Custo por lote/animal, receitas, despesas | Vacinas, medicamentos, ração, sal mineral | Manejos, trato, transporte, abastecimento | Compra de animais, insumos e serviços | Venda de animais, leite ou subprodutos | GTA, NF-e, SISBOV e obrigações |
| Financeiro | Obrigatório | Base própria | Valoração e consumo | Custo hora, manutenção e combustível | Contas a pagar | Contas a receber | Escrituração e documentos |
| Estoque | Obrigatório | Valoração, contas a pagar e custos | Base própria | Combustível, peças e lubrificantes | Entrada por pedido/nota | Baixa por venda/expedição | XML, NF-e, inventário fiscal |
| Frota / Máquinas | Obrigatório | Custo hora, manutenção e depreciação | Combustível, peças e lubrificantes | Base própria | Compra de peças/serviços | Eventual prestação de serviço | Documentação e notas |
| Compras | Obrigatório | Títulos a pagar e orçamento | Entrada de produtos | Serviços de manutenção, peças | Base própria | Não obrigatório | NF-e de entrada |
| Vendas | Obrigatório | Títulos a receber e receita | Baixa/expedição de produto | Transporte próprio | Não obrigatório | Base própria | NF-e de saída |
| Fiscal / Contabilidade | Obrigatório | Lançamentos e contas | Notas, inventário e custo | Documentos e despesas | NF-e entrada | NF-e saída | Base própria |

## Integração Agricultura e Pecuária

Agricultura e Pecuária devem coexistir como módulos produtivos equivalentes, compartilhando cadastros, recursos operacionais e consolidação econômica.

| Ponto de integração | Agricultura | Pecuária | Módulo integrador | Regra |
|---|---|---|---|---|
| Estoque de insumos | Sementes, defensivos, fertilizantes, corretivos | Vacinas, medicamentos, ração, sal mineral | Estoque | Toda aplicação/consumo deve baixar o estoque central quando Estoque estiver contratado. |
| Custos | Custo por safra, talhão, operação | Custo por lote, animal, arroba, manejo | Financeiro | Custos devem ser rateados por centro de custo e origem produtiva. |
| Financeiro | Despesas de safra e receitas de venda agrícola | Compra/venda de animais, despesas sanitárias e nutrição | Financeiro | Receitas e despesas não devem ficar isoladas em módulos produtivos. |
| Máquinas/Frota | Plantio, pulverização, colheita, preparo de solo | Trato, transporte, manejo, distribuição de ração | Frota / Máquinas | Horas, combustível e manutenção devem apropriar custo para atividade produtiva. |
| Atividades operacionais | Operação de campo, caderno, apontamentos | Manejo, pesagem, vacinação, movimentação | Core + módulos produtivos | Atividades usam calendário, responsáveis, fazenda e unidade produtiva comuns. |
| Rastreabilidade | Lote de produção, aplicação, colheita, beneficiamento | Animal/lote, manejo sanitário, movimentação, SISBOV | Rastreabilidade / Fiscal | Histórico operacional deve existir no módulo produtivo; auditoria avançada, exportações regulatórias e SISBOV ficam em `ENTERPRISE`. |
| Relatórios executivos | Margem por safra/talhão/cultura | Margem por lote/rebanho/arroba | Financeiro + Dashboards | Dashboards devem consolidar produção vegetal e animal sem duplicar indicadores. |

## Regras de Monetização Cross-Módulo

### Duas Camadas de Monetização

A monetização deve separar contratação de domínio funcional e profundidade de uso:

- **Módulo contratado:** libera o domínio funcional. Exemplo: contratar Estoque libera produto, saldo e movimentação; contratar Financeiro libera lançamentos, caixa e títulos; contratar Frota/Máquinas libera equipamentos, abastecimentos e manutenções.
- **Tier contratado:** define a profundidade disponível dentro do domínio contratado: `A1_PLANEJAMENTO`, `PROFISSIONAL` ou `ENTERPRISE`.

Exemplo: Agricultura contratada em `A1_PLANEJAMENTO` permite registrar safra e operações básicas. Agricultura em `PROFISSIONAL` adiciona planejamento, custos e dashboards gerenciais. Agricultura em `ENTERPRISE` adiciona automação avançada, rastreabilidade auditável e integrações complexas. A mesma lógica vale para Pecuária, preservando equivalência entre os dois módulos produtivos.

### A1_PLANEJAMENTO / A1 Planejamento

`A1_PLANEJAMENTO` é o plano base comercial e deve incluir a fundação operacional mínima para uso real do SaaS:

- Core: tenant, fazenda, usuários, permissões básicas, configurações globais e planos.
- Cadastros compartilhados básicos: pessoa, fazenda, unidade produtiva, produto/insumo básico.
- Agricultura A1: safras, operações de campo e caderno de campo básico.
- Pecuária A1: cadastro de rebanho, piquetes/pastagens e manejos básicos.
- Estoque A1: cadastro de produtos, saldos e movimentações simples.
- Financeiro A1: lançamentos básicos, categorias e fluxo de caixa.

### Exige Módulo Contratado

Uma funcionalidade exige módulo contratado quando o valor principal pertence a outro domínio funcional. O módulo libera o domínio; o tier contratado define a profundidade:

| Funcionalidade usada dentro de outro módulo | Módulo exigido | Profundidade por tier |
|---|---|---|
| Baixa automática de insumo agrícola ou pecuário | Estoque | A1 para movimentação simples; `PROFISSIONAL` para lote, validade e custeio; `ENTERPRISE` para inventário automatizado e fiscal avançado |
| Controle de saldo por almoxarifado | Estoque | A1 para saldo simples; `PROFISSIONAL` para múltiplos almoxarifados, FIFO e estoque mínimo |
| Geração de lançamentos a partir de compra/venda | Financeiro | A1 para lançamento simples; `PROFISSIONAL` para contas a pagar/receber, centro de custo e conciliação manual |
| Rateio econômico por centro de custo | Financeiro | `PROFISSIONAL` para rateio operacional; `ENTERPRISE` para custeio completo, auditoria e integrações |
| Uso de máquinas, horas, combustível ou manutenção em operação produtiva | Frota / Máquinas | A1 para cadastro e apontamento básico; `PROFISSIONAL` para custo hora e manutenção preventiva; `ENTERPRISE` para telemetria e oficina interna |
| Requisição, cotação e pedido de compra | Compras | A1 para solicitação simples; `PROFISSIONAL` para cotação/pedido; `ENTERPRISE` para workflow integrado e automações |
| Contrato, romaneio e venda comercial | Vendas / Comercialização | A1 para registro simples; `PROFISSIONAL` para contratos e acompanhamento; `ENTERPRISE` para hedge, exportação e integrações |
| Emissão/importação de NF-e, XML, GTA ou obrigações regulatórias | Fiscal / Contabilidade | `PROFISSIONAL` para emissão/controle operacional quando aplicável; `ENTERPRISE` para auditoria, multiempresa, automações e compliance avançado |

### Exige PROFISSIONAL

Funcionalidades que ampliam gestão, análise e automação operacional devem ficar no tier `PROFISSIONAL`:

- Planejamento de safra, orçamento e custos de produção.
- Centro de custo e rateio por talhão, safra, lote, animal, rebanho ou máquina.
- Contas a pagar/receber e conciliação manual.
- Estoque mínimo, FIFO/custo médio, lote e validade.
- Custo hora de máquina, manutenção preventiva e documentação operacional.
- Nutrição, sanidade e reprodução pecuária avançadas.
- Confinamento operacional quando a fazenda precisa controlar trato, lotes, ganho de peso e custo de diária sem exigência de automação avançada.
- Emissão e controle fiscal operacional quando o valor está no uso recorrente do módulo contratado, não em auditoria ou integração complexa.
- Dashboards gerenciais comparativos entre fazendas, safras, lotes e centros de custo.

### Exige ENTERPRISE

`ENTERPRISE` deve ser reservado para escala, compliance, automação avançada, auditoria e integrações complexas. Operações importantes para o dia a dia não devem subir para `ENTERPRISE` apenas por serem valiosas; elas devem ficar em `A1_PLANEJAMENTO` ou `PROFISSIONAL` conforme a profundidade.

- Rastreabilidade auditável agrícola e pecuária com exportação, cadeia de custódia, certificações e SISBOV.
- Prescrições VRT, agricultura de precisão com integração de máquinas, mapas e automações avançadas.
- Beneficiamento avançado quando envolve rastreabilidade por lote, integração fiscal/comercial e controle multiunidade.
- Confinamento avançado com automação, integração de balanças, indicadores preditivos ou operação multiunidade.
- Genética/melhoramento com genealogia, DEPs, auditoria e análises avançadas.
- Conciliação automática, crédito rural complexo e custo completo de produção com trilha auditável.
- Compras integradas com workflow de aprovação, inventário automatizado e integração fiscal avançada.
- Telemetria, oficina interna, indicadores avançados de frota e integração com sensores ou fornecedores externos.
- Auditoria, exportação, integrações externas, multiempresa e obrigações fiscais/contábeis avançadas.

## Regras de Gate e Dependência

- Core é obrigatório para todos os módulos.
- Um módulo produtivo pode registrar dados manuais mesmo sem módulo integrador contratado, desde que não simule funcionalidade premium.
- Quando o módulo integrador não estiver contratado, o sistema pode exibir campos informativos manuais ou CTA de upgrade.
- Quando o módulo integrador estiver contratado, a fonte canônica deve ser o módulo integrador.
- A contratação do módulo responde "qual domínio está habilitado"; o tier responde "qual profundidade daquele domínio está habilitada".
- Agricultura e Pecuária devem seguir a mesma lógica de profundidade: A1 para registro operacional básico, `PROFISSIONAL` para gestão e análise, `ENTERPRISE` para escala, auditoria, automação avançada e integrações.
- Feature gates existentes continuam sendo a fonte técnica de verdade.
- Este documento orienta novas decisões, mas não altera nenhum gate implementado.

## Riscos de Duplicidade

| Risco | Impacto | Mitigação arquitetural |
|---|---|---|
| Cadastros duplicados de pessoa, fornecedor ou cliente | Duplicidade fiscal, financeiro inconsistente e dificuldade de conciliação | Pessoa única no Core/Pessoas com papéis por contexto. |
| Estoque separado por módulo | Saldos divergentes, compra emergencial indevida e perda de rastreabilidade | Estoque central como dono de produto, saldo, lote e movimentação. |
| Financeiro isolado em Agricultura ou Pecuária | Margem incorreta e fluxo de caixa incompleto | Financeiro central como dono de lançamentos, centros de custo e títulos. |
| Frota duplicada entre máquinas agrícolas e veículos | Custo hora inconsistente e manutenção fragmentada | Cadastro unificado de equipamento com tipo: veículo, máquina ou implemento. |
| Dashboards inconsistentes | Gestão executiva perde confiança nos números | Dashboards devem consumir indicadores consolidados e fontes canônicas. |
| Unidades produtivas sem padrão | Talhão, piquete e área não comparáveis | Base comum de unidade produtiva com especializações por domínio. |
| Rastreabilidade parcial | Auditoria frágil e impossibilidade de comprovar origem | Eventos produtivos imutáveis e integrados com estoque, fiscal e comercialização. |
| Compras fora do estoque/financeiro | Entrada sem saldo ou título a pagar | Pedido aprovado deve gerar entrada prevista de estoque e obrigação financeira quando módulos existirem. |
| Vendas fora do estoque/financeiro | Receita sem baixa de produto ou sem conta a receber | Venda confirmada deve gerar baixa/expedição e título a receber quando módulos existirem. |

## Diretrizes para Novas Funcionalidades

- Antes de criar entidade em Agricultura ou Pecuária, verificar se ela já pertence ao Core, Estoque, Financeiro, Frota, Compras, Vendas ou Fiscal.
- Entidades compartilhadas devem ter identificador único por tenant e referências claras para fazenda/unidade produtiva.
- Dados produtivos podem ser específicos do módulo, mas cadastros e movimentos econômicos/físicos devem ser centralizados.
- Relatórios executivos devem consolidar por fazenda, unidade produtiva, safra/lote/rebanho, centro de custo e período.
- CTAs de upgrade devem explicar o módulo exigido e o ganho operacional, não apenas bloquear a tela.

## Critérios de Aceite

- Matriz de dependências entre módulos definida.
- Agricultura e Pecuária posicionadas como módulos produtivos dentro da mesma arquitetura.
- Core definido como base comum e pré-requisito universal.
- Financeiro, Estoque e Frota/Máquinas tratados como módulos integradores.
- Regras de monetização cross-módulo documentadas por `A1_PLANEJAMENTO`, módulo contratado, tier contratado, `PROFISSIONAL` e `ENTERPRISE`.
- Riscos de duplicidade e mitigação arquitetural documentados.
- Nenhuma alteração de código ou gate realizada.
