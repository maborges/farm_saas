# Contexto de continuidade: desativação do legado `estoque_movimentacoes`

## Objetivo deste arquivo

Registrar o estado atual da conversa e das mudanças já executadas para permitir continuidade em uma próxima sessão sem perda de contexto.

Data de referência:

- `2026-04-28`

## Resumo executivo

O legado `estoque_movimentacoes` já foi funcionalmente aposentado em favor de `estoque_movimentos`.

Status consolidado:

- `0` leituras funcionais dependem de `estoque_movimentacoes`
- `0` novos writes vão para `estoque_movimentacoes`
- o backfill elegível já foi executado
- a tabela física ainda existe
- a remoção física foi planejada, mas ainda não executada

## Linha do tempo resumida

### Step 61

- novos writes de estoque passaram a gravar apenas em `estoque_movimentos`

### Step 63

- leituras funcionais começaram a ser adaptadas para o ledger canônico

### Step 68

- criada migration para permitir `origem_tipo = LEGADO` em `estoque_movimentos`
- arquivo:
  - [step24_estoque_movimentos_origem_legado.py](/opt/lampp/htdocs/farm/apps/web/services/api/migrations/versions/step24_estoque_movimentos_origem_legado.py:1)

### Step 69

- criado script idempotente de backfill:
  - [backfill_estoque_movimentacoes.py](/opt/lampp/htdocs/farm/apps/web/services/api/scripts/backfill_estoque_movimentacoes.py:1)

### Step 70

- dry-run inicial executado
- depois do saneamento do Alembic e da constraint, o dry-run passou sem erro

### Step 71

- backfill real executado

Resultado:

- `9` registros legados processados
- `4` ignorados por já estarem cobertos
- `4` persistidos no ledger como `LEGADO`
- `1` mantido fora da automação para revisão manual
- `0` erros

Relatório:

- [AUDITORIA_BACKFILL_ESTOQUE_MOVIMENTOS_REAL_STEP71_2026-04-28.md](/opt/lampp/htdocs/farm/docs/AUDITORIA_BACKFILL_ESTOQUE_MOVIMENTOS_REAL_STEP71_2026-04-28.md:1)

### Step 72

- o caso remanescente de `OPERACAO_AGRICOLA` foi revisado manualmente
- decisão:
  - não ignorar
  - não migrar com vínculo canônico real
  - tratar como inserção manual `LEGADO` apenas se a equipe quiser preservar esse histórico

Relatório:

- [AUDITORIA_MANUAL_OPERACAO_AGRICOLA_STEP72_2026-04-28.md](/opt/lampp/htdocs/farm/docs/AUDITORIA_MANUAL_OPERACAO_AGRICOLA_STEP72_2026-04-28.md:1)

### Step 73

- definida a estratégia final de desativação do legado

Documento:

- [ESTRATEGIA_DESATIVACAO_ESTOQUE_LEGADO_STEP73.md](/opt/lampp/htdocs/farm/docs/ESTRATEGIA_DESATIVACAO_ESTOQUE_LEGADO_STEP73.md:1)

### Step 74

- `estoque_movimentacoes` foi marcado no código como legado `read-only`
- criado guardrail estático para impedir novos usos

Arquivo:

- [test_estoque_movimentacoes_guardrails.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/unit/operacional/test_estoque_movimentacoes_guardrails.py:1)

### Step 75

- fallback funcional do legado foi removido de:
  - [safras/service.py](/opt/lampp/htdocs/farm/apps/web/services/api/agricola/safras/service.py:1)
  - [relatorio_service.py](/opt/lampp/htdocs/farm/apps/web/services/api/operacional/services/relatorio_service.py:1)

### Step 76

- allowlist do guardrail foi reduzida ao mínimo necessário:
  - model legado
  - script de backfill
  - teste guarda de ausência de novos writes
  - teste unitário do backfill
  - o próprio guardrail

### Step 77

- gerada auditoria final pré-remoção física

Conclusão:

- `0` uso funcional
- `0` writes novos
- sobraram apenas artefatos estruturais e históricos

Documento:

- [AUDITORIA_FINAL_PRE_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP77_2026-04-28.md](/opt/lampp/htdocs/farm/docs/AUDITORIA_FINAL_PRE_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP77_2026-04-28.md:1)

### Step 78

- criada apenas a estratégia/plano de remoção física
- nenhum drop foi executado ainda

Documento:

- [PLANO_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP78.md](/opt/lampp/htdocs/farm/docs/PLANO_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP78.md:1)

## Estado técnico atual

### O que ainda existe

- model legado:
  - [operacional/models/estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/operacional/models/estoque.py:110)
- import estrutural no Alembic:
  - [migrations/env.py](/opt/lampp/htdocs/farm/apps/web/services/api/migrations/env.py:85)
- migrations históricas que mencionam a tabela
- script congelado de backfill:
  - [backfill_estoque_movimentacoes.py](/opt/lampp/htdocs/farm/apps/web/services/api/scripts/backfill_estoque_movimentacoes.py:1)
- testes residuais:
  - [test_estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/integration/operacional/test_estoque.py:81)
  - [test_backfill_estoque_movimentacoes.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/unit/operacional/test_backfill_estoque_movimentacoes.py:1)
  - [test_estoque_movimentacoes_guardrails.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/unit/operacional/test_estoque_movimentacoes_guardrails.py:1)

### O que não existe mais

- leitura funcional do legado em Safra
- leitura funcional do legado em Relatórios
- novos writes de negócio em `estoque_movimentacoes`

## Observações importantes sobre Alembic

Houve saneamento prévio do estado de migrations.

Pontos importantes:

- o banco estava apontando para `b2c4d6e8f001`
- foi necessário alinhar as migrations entre:
  - `/opt/lampp/htdocs/farm/services/api/migrations`
  - `/opt/lampp/htdocs/farm/apps/web/services/api/migrations`
- a revision da migration que libera `LEGADO` foi ajustada para:
  - `step24_legado_estoque`

Depois do saneamento:

- `alembic current` passou a funcionar
- `alembic heads` passou a funcionar
- a constraint de `estoque_movimentos` passou a aceitar `LEGADO`

## Próximo passo recomendado

O próximo passo natural é executar a entrega real de remoção física da tabela.

Sequência recomendada:

1. remover ou isolar `MovimentacaoEstoque` do model legado
2. limpar `migrations/env.py` para não depender mais do model
3. adaptar/remover testes residuais que ainda assumem a existência da tabela
4. ajustar o guardrail para estado pós-drop
5. criar migration dedicada para remover fisicamente `estoque_movimentacoes`
6. validar Alembic e rodar testes focados

## Arquivos de referência principais

- [CONTEXTO_CONTINUIDADE_ESTOQUE_LEGADO_2026-04-28.md](/opt/lampp/htdocs/farm/docs/CONTEXTO_CONTINUIDADE_ESTOQUE_LEGADO_2026-04-28.md:1)
- [AUDITORIA_FINAL_PRE_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP77_2026-04-28.md](/opt/lampp/htdocs/farm/docs/AUDITORIA_FINAL_PRE_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP77_2026-04-28.md:1)
- [PLANO_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP78.md](/opt/lampp/htdocs/farm/docs/PLANO_REMOCAO_FISICA_ESTOQUE_MOVIMENTACOES_STEP78.md:1)
- [ESTRATEGIA_DESATIVACAO_ESTOQUE_LEGADO_STEP73.md](/opt/lampp/htdocs/farm/docs/ESTRATEGIA_DESATIVACAO_ESTOQUE_LEGADO_STEP73.md:1)

