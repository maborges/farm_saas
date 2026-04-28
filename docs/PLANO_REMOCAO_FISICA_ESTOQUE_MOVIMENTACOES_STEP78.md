# Step 78: plano de remoção física de `estoque_movimentacoes`

## Objetivo

Definir a estratégia final para remover fisicamente a tabela legada `estoque_movimentacoes` com segurança, sem executar a remoção nesta etapa.

Base considerada:

- Step 73: estratégia de desativação do legado
- Step 77: auditoria final pré-remoção física

Fora de escopo:

- executar migration de drop agora
- apagar dados imediatamente
- alterar comportamento funcional nesta etapa

## Estado de partida

Situação confirmada no Step 77:

- `0` leituras funcionais de `estoque_movimentacoes`
- `0` novos writes no legado
- referências remanescentes apenas em:
  - model ORM legado
  - `migrations/env.py`
  - migrations históricas
  - script congelado de backfill
  - testes de guarda/backfill

Leitura arquitetural:

- a aplicação já opera funcionalmente sobre `estoque_movimentos`
- a remoção física agora é um trabalho de saneamento estrutural, não de migração de regra de negócio

## Inventário do que ainda depende do legado

### 1. Estrutural obrigatório antes do drop

- [operacional/models/estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/operacional/models/estoque.py:110)
  - contém o model `MovimentacaoEstoque`
- [migrations/env.py](/opt/lampp/htdocs/farm/apps/web/services/api/migrations/env.py:85)
  - importa `MovimentacaoEstoque` para metadata do Alembic

### 2. Histórico congelado

- [backfill_estoque_movimentacoes.py](/opt/lampp/htdocs/farm/apps/web/services/api/scripts/backfill_estoque_movimentacoes.py:1)
  - utilitário de backfill já executado

### 3. Testes residuais

- [test_estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/integration/operacional/test_estoque.py:81)
  - guarda de ausência de novos writes no legado
- [test_backfill_estoque_movimentacoes.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/unit/operacional/test_backfill_estoque_movimentacoes.py:1)
  - valida o script histórico
- [test_estoque_movimentacoes_guardrails.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/unit/operacional/test_estoque_movimentacoes_guardrails.py:1)
  - impede novos usos fora da allowlist

### 4. Migrations históricas

As migrations antigas que mencionam `estoque_movimentacoes` permanecem como histórico e não devem ser reescritas.

## Política oficial para a remoção

### Decisão

A remoção física de `estoque_movimentacoes` fica aprovada como próxima etapa técnica, desde que executada por migration dedicada e acompanhada de limpeza estrutural mínima.

### Princípios

- não reabrir fallback funcional
- não recriar dependência de leitura/escrita no legado
- tratar a remoção como mudança de infraestrutura de schema
- preservar rastreabilidade histórica relevante no ledger canônico e na documentação

## Plano de execução

### Fase 1: preparar o código para o drop

Objetivo:

- eliminar as últimas dependências estruturais diretas da tabela antes da migration

Ações:

1. remover `MovimentacaoEstoque` de [migrations/env.py](/opt/lampp/htdocs/farm/apps/web/services/api/migrations/env.py:85), mantendo apenas models/tabelas ainda existentes;
2. remover ou isolar o model `MovimentacaoEstoque` em [operacional/models/estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/operacional/models/estoque.py:110);
3. ajustar [test_estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/integration/operacional/test_estoque.py:81) para parar de consultar a tabela removida;
4. aposentar [test_backfill_estoque_movimentacoes.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/unit/operacional/test_backfill_estoque_movimentacoes.py:1) ou mover para um conjunto explícito de testes históricos fora da suíte padrão;
5. atualizar [test_estoque_movimentacoes_guardrails.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/unit/operacional/test_estoque_movimentacoes_guardrails.py:1) para trocar a regra de allowlist por proibição total de novos usos do nome legado em código ativo.

### Fase 2: congelar o script histórico

Objetivo:

- decidir o destino oficial do script de backfill após o drop

Opções aceitáveis:

1. mover o script para pasta de arquivo histórico/documental;
2. manter o script no repositório, claramente marcado como incompatível após o drop;
3. remover o script da árvore principal e manter apenas o relatório/documentação do backfill.

Recomendação:

- manter o script apenas como artefato histórico congelado, fora do caminho operacional normal.

### Fase 3: criar migration de remoção física

Objetivo:

- remover a tabela do schema de forma explícita e reversível

Conteúdo esperado da migration:

1. `upgrade`
   - dropar `estoque_movimentacoes`
   - dropar índices/constraints residuais, se existirem
2. `downgrade`
   - recriar a tabela apenas com estrutura mínima compatível
   - sem promessa de restaurar dados removidos

Princípio de downgrade:

- o downgrade deve restaurar o schema, não o conteúdo histórico.

### Fase 4: validação pós-migration

Objetivo:

- provar que a aplicação segue funcional sem a tabela

Validações mínimas:

1. `alembic upgrade head`
2. `alembic current`
3. suíte focada de estoque/relatórios/safra
4. busca estática por `MovimentacaoEstoque|estoque_movimentacoes`
5. inicialização da aplicação sem erro de import/metadata

## Riscos principais

### 1. Metadata/Alembic

Risco:

- `migrations/env.py` ou imports ORM continuarem referenciando `MovimentacaoEstoque` depois do drop

Mitigação:

- limpar imports/model antes da migration ou no mesmo pacote de mudanças

### 2. Testes residuais

Risco:

- testes ainda consultarem a tabela removida e quebrarem a pipeline

Mitigação:

- adaptar/remover testes residuais na mesma entrega da migration

### 3. Script histórico

Risco:

- operador tentar reutilizar o script de backfill após o drop

Mitigação:

- marcar o script como obsoleto/incompatível ou movê-lo para arquivo histórico

### 4. Downgrade conceitual

Risco:

- expectativa incorreta de que downgrade restaure dados

Mitigação:

- documentar claramente que downgrade recompõe apenas a estrutura

## Critérios de pronto para executar o Step de remoção

Antes de rodar a migration real, todos os itens abaixo devem estar verdadeiros:

1. `migrations/env.py` sem dependência de `MovimentacaoEstoque`
2. model legado removido ou isolado sem impacto em runtime
3. teste guarda do legado substituído por validação compatível com a ausência da tabela
4. script histórico explicitamente congelado/arquivado
5. suíte focada passando sem acessar `estoque_movimentacoes`
6. revisão técnica confirmando que não existe mais dependência estrutural oculta

## Sequência recomendada para a execução futura

1. limpar model/imports/testes residuais
2. ajustar o guardrail para estado pós-drop
3. criar migration de remoção física
4. validar localmente com Alembic e testes focados
5. executar em ambiente controlado
6. monitorar erro de import, startup e rotas de estoque/safra/relatórios

## Decisão executável

Decisão do Step 78:

- a remoção física de `estoque_movimentacoes` está tecnicamente autorizada como próxima etapa;
- ela deve acontecer em uma entrega própria, composta por:
  - limpeza estrutural do código
  - atualização dos testes residuais
  - migration dedicada de drop
- nenhuma remoção é executada nesta etapa; este documento define apenas o plano.

