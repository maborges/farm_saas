# Step 62 - Auditoria de Leituras e Testes Legados de `MovimentacaoEstoque`

Data: 2026-04-27

## Objetivo

Listar onde `MovimentacaoEstoque` e `estoque_movimentacoes` ainda são usados após o Step 61 e classificar cada caso como:

- `MANTER COMPATIBILIDADE`
- `ADAPTAR LEITURA`
- `DEPRECIAR`

Escopo desta auditoria:

- código de aplicação
- testes
- documentação operacional claramente desatualizada

Fora de escopo:

- migrations históricas que apenas preservam o legado no banco
- metadados de import em `env.py` e `core/models/__init__.py` quando não representam consumo funcional

## Resumo executivo

Estado atual encontrado:

- novos writes já foram travados no ledger canônico `estoque_movimentos`;
- ainda existem leituras funcionais importantes apontando para `MovimentacaoEstoque`;
- a maior dependência funcional restante está em consultas agrícolas por safra e em relatórios operacionais;
- a maior dependência de testes está em cenários FIFO/E2E que ainda descrevem rastreabilidade via `MovimentacaoEstoque`, embora hoje o consumo FIFO em si não grave mais nessa tabela.

Recomendação de prioridade:

1. adaptar leituras funcionais de Safra e Relatórios para `estoque_movimentos`;
2. manter apenas compatibilidade temporária nos endpoints já expostos que ainda falem em “movimentações”;
3. depreciar testes/documentos que assumem criação nova em `estoque_movimentacoes`.

## Inventário classificado

### 1. Leituras funcionais que devem migrar

#### `ADAPTAR LEITURA`

1. [apps/web/services/api/agricola/safras/service.py](/opt/lampp/htdocs/farm/apps/web/services/api/agricola/safras/service.py:524)

Uso atual:
- `get_movimentacoes_safra` consulta `MovimentacaoEstoque`;
- vincula movimento à safra via `origem_id = OperacaoAgricola.id` e `origem_tipo = 'OPERACAO_AGRICOLA'`;
- filtra por tipo, depósito, período e lote;
- pagina e retorna histórico de estoque no detalhe da safra.

Diagnóstico:
- leitura funcional ativa;
- após Step 61, novos consumos agrícolas relevantes passam a ficar no ledger canônico;
- manter essa query no legado vai ocultar movimentos novos ou gerar visão parcial.

Classificação:
- `ADAPTAR LEITURA`

Direção sugerida:
- migrar para `EstoqueMovimento`;
- mapear `origem = 'OPERACAO_EXECUCAO'` com `operacao_execucao_id`;
- projetar saída no mesmo shape atual para não quebrar o frontend.

2. [apps/web/services/api/agricola/safras/service.py](/opt/lampp/htdocs/farm/apps/web/services/api/agricola/safras/service.py:648)

Uso atual:
- `get_lotes_safra` encontra lotes consumidos cruzando `LoteEstoque` com `MovimentacaoEstoque`;
- também depende de `origem_tipo = 'OPERACAO_AGRICOLA'`.

Diagnóstico:
- mesma limitação estrutural do item anterior;
- lote consumido por movimento novo no ledger pode não aparecer.

Classificação:
- `ADAPTAR LEITURA`

Direção sugerida:
- cruzar `LoteEstoque` com `EstoqueMovimento`;
- usar `operacao_execucao_id` ou `origem/ origem_id` canônicos em vez do legado.

3. [apps/web/services/api/operacional/services/relatorio_service.py](/opt/lampp/htdocs/farm/apps/web/services/api/operacional/services/relatorio_service.py:149)

Uso atual:
- `movimentacoes_por_periodo` agrega quantidade e custo por produto/tipo usando `MovimentacaoEstoque`.

Diagnóstico:
- relatório operacional ativo;
- como novos writes já não entram no legado, o relatório tende a ficar incompleto com o tempo.

Classificação:
- `ADAPTAR LEITURA`

Direção sugerida:
- migrar agregação para `EstoqueMovimento`;
- normalizar `tipo` compatível a partir de `tipo_movimento` e sinal da quantidade.

### 2. Compatibilidade temporária de contrato/API

#### `MANTER COMPATIBILIDADE`

1. [apps/web/services/api/agricola/safras/router.py](/opt/lampp/htdocs/farm/apps/web/services/api/agricola/safras/router.py:262)

Uso atual:
- endpoint `/safras/{id}/estoque/movimentacoes` expõe histórico para frontend.

Diagnóstico:
- o problema real não está no router, mas na service subjacente;
- o nome do endpoint pode permanecer por compatibilidade, desde que a fonte passe a ser o ledger.

Classificação:
- `MANTER COMPATIBILIDADE`

Direção sugerida:
- manter rota e payload;
- trocar apenas a leitura interna da service.

2. [apps/web/services/api/operacional/models/estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/operacional/models/estoque.py:110)

Uso atual:
- definição ORM de `MovimentacaoEstoque`.

Diagnóstico:
- ainda necessária enquanto houver leitura compatível, migrations históricas e dados legados;
- não é ponto de negócio, mas é suporte de compatibilidade.

Classificação:
- `MANTER COMPATIBILIDADE`

3. [apps/web/services/api/migrations/env.py](/opt/lampp/htdocs/farm/apps/web/services/api/migrations/env.py:85)

Uso atual:
- importa `MovimentacaoEstoque` para registrar metadata do Alembic.

Diagnóstico:
- não é dependência de leitura/escrita funcional;
- deve permanecer até remoção física futura da tabela.

Classificação:
- `MANTER COMPATIBILIDADE`

4. [apps/web/services/api/core/models/__init__.py](/opt/lampp/htdocs/farm/apps/web/services/api/core/models/__init__.py:59)

Uso atual:
- reexporta `MovimentacaoEstoque`.

Diagnóstico:
- suporte de import legado;
- não força uso funcional por si só.

Classificação:
- `MANTER COMPATIBILIDADE`

### 3. Testes que precisam sair do legado

#### `DEPRECIAR`

1. [apps/web/services/api/tests/test_fifo_estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/test_fifo_estoque.py:18)

Uso atual:
- importa `MovimentacaoEstoque`, mas os cenários abertos nesta auditoria testam consumo FIFO e custo histórico, não criação de movimento legado.

Diagnóstico:
- dependência principalmente semântica/documental;
- o import indica acoplamento residual desnecessário.

Classificação:
- `DEPRECIAR`

Direção sugerida:
- remover referência/import legado;
- se for necessário validar rastreabilidade, trocar a asserção para `EstoqueMovimento`.

2. [apps/web/services/api/tests/test_compras_lote_integration.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/test_compras_lote_integration.py:17)

Uso atual:
- importa `MovimentacaoEstoque`, mas o fluxo testado é recebimento, criação de lote e consumo FIFO.

Diagnóstico:
- mesmo padrão: o contrato relevante já é lote, saldo e FIFO;
- não deveria ancorar o cenário em tabela legada.

Classificação:
- `DEPRECIAR`

Direção sugerida:
- remover import legado;
- se houver extensão do teste para rastreabilidade, validar ledger canônico.

3. [apps/web/services/api/tests/test_e2e_colheita_completa.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/test_e2e_colheita_completa.py:16)

Uso atual:
- importa `MovimentacaoEstoque`;
- a docstring ainda diz “validar rastreabilidade via MovimentacaoEstoque”.

Diagnóstico:
- esse teste está semanticamente desatualizado frente ao Step 61;
- é candidato claro a migração de expectativa.

Classificação:
- `DEPRECIAR`

Direção sugerida:
- reescrever expectativa para ledger canônico;
- eventualmente renomear o teste para refletir `EstoqueMovimento`.

4. [apps/web/services/api/tests/integration/operacional/test_estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/integration/operacional/test_estoque.py:81)

Uso atual:
- consulta `estoque_movimentacoes` para garantir que novos writes não entram no legado.

Diagnóstico:
- este é o único uso de teste legado que ainda faz sentido no curto prazo;
- ele existe justamente para vigiar a depreciação.

Classificação:
- `MANTER COMPATIBILIDADE`

Observação:
- apesar de tocar a tabela legada, o objetivo é verificar ausência de write;
- esse teste deve permanecer até a remoção definitiva da camada de compatibilidade.

### 4. Código paralelo/desatualizado fora do fluxo principal

#### `DEPRECIAR`

1. [apps/web/services/api/agricola/beneficiamento/service.py](/opt/lampp/htdocs/farm/apps/web/services/api/agricola/beneficiamento/service.py:379)

Uso atual:
- comentário e API interna antiga indicam criação de `MovimentacaoEstoque` via `registrar_movimentacao`;
- o módulo referenciado parece ser uma API paralela/antiga (`operacional.estoque.service`), não o serviço padronizado do fluxo principal usado no Step 61.

Diagnóstico:
- alto cheiro de caminho legado ou código órfão;
- merece revisão dedicada antes de qualquer reativação.

Classificação:
- `DEPRECIAR`

Direção sugerida:
- se esse fluxo ainda estiver ativo, migrá-lo diretamente para `EstoqueService`/`registrar_ledger_estoque`;
- se não estiver ativo, marcar explicitamente como legado.

2. [apps/web/services/api/operacional/services/estoque_fifo.py](/opt/lampp/htdocs/farm/apps/web/services/api/operacional/services/estoque_fifo.py:1)

Uso atual:
- comentários ainda dizem “Record MovimentacaoEstoque for each batch consumed”;
- importa `MovimentacaoEstoque`, mas o trecho auditado não mostra uso funcional necessário.

Diagnóstico:
- indício de resíduo pós-refatoração;
- mesmo quando não quebra a execução, confunde manutenção futura.

Classificação:
- `DEPRECIAR`

Direção sugerida:
- limpar imports e comentários para refletir ledger canônico.

## Itens documentais desatualizados

Há várias menções documentais a criação de `MovimentacaoEstoque` em:

- `docs/P0_HARVEST_INTEGRATION_DEPLOYMENT.md`
- `docs/COMPRAS_MODULE_ANALYSIS.md`
- `docs/plano-acao-integracao-colheita.md`
- `docs/agro/treinamento/*`
- `docs/brainstorm-modulo-agricola.md`

Classificação sugerida:
- `DEPRECIAR`

Observação:
- não impactam runtime, mas já não descrevem o comportamento desejado após o Step 61.

## Migrations e metadados históricos

Arquivos de migration e referências de metadata que mencionam `estoque_movimentacoes`:

- permanecem válidos como histórico de schema;
- não devem ser tratados como “consumidores a migrar” nesta etapa.

Classificação operacional:
- `MANTER COMPATIBILIDADE`

## Conclusão

Classificação consolidada:

- `ADAPTAR LEITURA`
  - `agricola/safras/service.py`
  - `operacional/services/relatorio_service.py`

- `MANTER COMPATIBILIDADE`
  - endpoint `/safras/{id}/estoque/movimentacoes`
  - model ORM `MovimentacaoEstoque`
  - metadata/imports de suporte (`migrations/env.py`, `core/models/__init__.py`)
  - teste de guarda negativa em `tests/integration/operacional/test_estoque.py`

- `DEPRECIAR`
  - testes `test_fifo_estoque.py`, `test_compras_lote_integration.py`, `test_e2e_colheita_completa.py`
  - comentários/imports residuais em `estoque_fifo.py`
  - caminho paralelo em `agricola/beneficiamento/service.py`
  - documentação que ainda presume criação nova em `estoque_movimentacoes`

Próximo passo seguro:

- Step 63 pode atacar primeiro as leituras funcionais de Safra e Relatórios, mantendo os endpoints compatíveis, mas mudando a fonte para `estoque_movimentos`.
