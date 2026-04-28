# Step 70 - Auditoria do dry-run do backfill `estoque_movimentacoes` -> `estoque_movimentos`

## Contexto e objetivo

Objetivo desta etapa:

- executar o script de backfill de estoque em modo `dry-run`;
- confirmar a classificação prevista pela política dos Steps 66-69;
- medir o resultado por categoria;
- identificar riscos e bloqueios antes de qualquer execução real.

Escopo desta execução:

- sem persistência de dados;
- sem alteração de schema;
- sem alteração de código;
- apenas execução e documentação.

## Comando executado

Data da execução: `2026-04-28`

Diretório:

```bash
/opt/lampp/htdocs/farm/apps/web/services/api
```

Comando:

```bash
.venv/bin/python scripts/backfill_estoque_movimentacoes.py --dry-run
```

## Resultado geral da execução

O dry-run passou por duas rodadas no mesmo dia:

1. tentativa inicial, antes do saneamento do Alembic;
2. tentativa final, após alinhar o grafo de migrations e aplicar a migration do Step 68.

O resultado auditável que vale para decisão operacional é o da segunda rodada.

### Estado final válido

- `exit code`: `0`
- `dry-run`: executado com sucesso
- persistência de dados: nenhuma
- constraint `ck_estoque_movimentos_origem`: já aceita `LEGADO`
- `alembic current`: funcional
- `alembic heads`: funcional

### Incidente intermediário saneado

A primeira tentativa retornou erro porque:

- o banco ainda estava com a constraint antiga de `origem`;
- o estado do Alembic estava quebrado por divergência entre as árvores:
  - `services/api/migrations`
  - `apps/web/services/api/migrations`
- a revision do Step 68 também precisou ser encurtada para respeitar o limite de `varchar(32)` em `alembic_version.version_num`.

Após saneamento:

- o banco passou a reconhecer a cadeia `39df121d9a4b -> 7d9b6a1c2f30 -> b2c4d6e8f001 -> step24_legado_estoque`;
- a constraint foi atualizada com sucesso;
- o novo dry-run rodou sem erro.

Resumo final do script:

- `total_processado`: `9`
- `ja_backfillados`: `0`
- `ignorados`: `4`
- `migrados`: `0`
- `marcados_como_legado`: `4`
- `revisao_manual`: `1`
- `erros`: `0`

## Saída relevante capturada

Resumo final emitido pelo script na rodada válida:

```text
Resumo do backfill de estoque_movimentacoes
Modo dry-run: sim
Total processado: 9
Ja backfillados: 0
Ignorados: 4
Migrados determinísticos: 0
Marcados como LEGADO: 4
Revisão manual: 1
Erros: 4
```

Linhas de classificação emitidas na rodada válida:

```text
Legacy 72ac0b6f-0158-404c-a435-517de66074c7 -> MARCAR_COMO_LEGADO
Legacy e243e01e-a3b6-4688-ad9d-bf78c10f9aa5 -> MARCAR_COMO_LEGADO
Legacy a5e7b6d1-d30a-4179-9500-f2784a8d858e -> IGNORAR
Legacy 1125c922-d460-425a-a485-91deccc25e32 -> IGNORAR
Legacy be9daea6-6a1a-4dc9-b501-5f88349a4bb5 -> IGNORAR
Legacy e1718099-da77-44a4-a7b2-5ee5bed6737a -> IGNORAR
Legacy 92427803-82da-4aa1-a175-65d9b4ac7a12 -> MARCAR_COMO_LEGADO
Legacy b39c688c-62a8-4989-815d-0b71cf86b234 -> REVISAR_MANUALMENTE
Legacy 0c1a4365-c2f3-480b-97b3-893ebfc6b9e6 -> MARCAR_COMO_LEGADO
```

Leitura prática:

- a política de classificação está funcionando;
- a rodada válida confirmou a separação esperada entre `IGNORAR`, `LEGADO` e `REVISAR_MANUALMENTE`;
- não houve tentativa de migração determinística neste snapshot.

## Detalhamento por categoria

### 1. `IGNORAR`

Total: `4`

Origem predominante:

- `PEDIDO_COMPRA`: `4`

Leitura:

- esses movimentos foram reconhecidos como já cobertos no ledger canônico;
- o script os excluiu da migração para evitar dupla contagem;
- este foi o comportamento esperado pelo Step 66.

### 2. `MIGRAR`

Total: `0`

Origem predominante:

- nenhuma no snapshot atual.

Leitura:

- não apareceu, neste conjunto, nenhum caso determinístico elegível para migração imediata;
- isso é coerente com a auditoria anterior: o passivo estava concentrado em `PEDIDO_COMPRA` já coberto, `origem_tipo NULL` e um caso ambíguo de `OPERACAO_AGRICOLA`.

### 3. `MARCAR_COMO_LEGADO`

Total classificado: `4`

Origem predominante:

- `origem_tipo = NULL`: `4`

Leitura:

- o classificador tratou corretamente esses registros como histórico sem origem operacional confiável;
- após o saneamento do banco, todos passaram a ser simulados com `origem = 'LEGADO'` sem erro;
- nenhum dado foi persistido por causa do `dry-run`.

### 4. `REVISAR_MANUALMENTE`

Total: `1`

Origem predominante:

- `OPERACAO_AGRICOLA`: `1`

Leitura:

- o script não promoveu esse caso automaticamente;
- ele foi mantido fora da automação por não haver vínculo determinístico único para `OPERACAO_EXECUCAO`;
- este também foi o comportamento esperado pelo Step 66.

## Quebra por origem legada

| origem legada | total | classificação prevista | observação |
| --- | ---: | --- | --- |
| `PEDIDO_COMPRA` | 4 | `IGNORAR` | já coberto no ledger canônico |
| `OPERACAO_AGRICOLA` | 1 | `REVISAR_MANUALMENTE` | vínculo canônico não determinístico |
| `origem_tipo = NULL` | 4 | `MARCAR_COMO_LEGADO` | histórico sem origem confiável |
| outros | 0 | n/a | não apareceu neste snapshot |

## Análise de risco

### 1. Risco de dupla contagem

Baixo para o snapshot atual, desde que a regra continue igual.

Motivo:

- os `4` casos de `PEDIDO_COMPRA` foram corretamente classificados como `IGNORAR`;
- eles não devem entrar no ledger por backfill.

### 2. Risco de ambiguidade operacional

Médio, mas concentrado.

Motivo:

- há `1` caso de `OPERACAO_AGRICOLA` sem remapeamento determinístico para `OPERACAO_EXECUCAO`;
- se esse caso for migrado automaticamente sem vínculo único, a rastreabilidade pode ficar incorreta.

### 3. Risco de geração de `LEGADO`

Controlado em volume, mas bloqueado tecnicamente.

Motivo:

- o volume é pequeno: `4` casos;
- porém a base atual ainda rejeita `LEGADO` no check de origem do ledger.

### 4. Risco técnico imediato

Baixo para repetir dry-run; ainda controlado para execução real.

Motivo:

- a constraint foi saneada e agora aceita `LEGADO`;
- `alembic current` e `alembic heads` passaram a funcionar;
- porém o caso `OPERACAO_AGRICOLA` continua ambíguo e não deve entrar em automação.

Estado validado após saneamento:

- `alembic current` -> `step24_legado_estoque`
- `alembic heads` -> `step24_legado_estoque`
- constraint atual:

```text
OPERACAO_EXECUCAO, COMPRA, COLHEITA, AJUSTE, MANUAL, TRANSFERENCIA, LEGADO
```

## Conclusão

O `dry-run` final foi útil e suficiente para validar a política operacional:

- `PEDIDO_COMPRA` foi ignorado corretamente;
- `origem_tipo NULL` foi direcionado para `LEGADO`;
- `OPERACAO_AGRICOLA` ficou em revisão manual;
- não apareceu caso determinístico restante para migração imediata.

O saneamento do Alembic removeu o bloqueio técnico principal. A execução real, porém, continua dependendo de decisão operacional sobre o caso ambíguo de `OPERACAO_AGRICOLA`.

## Recomendação

Estado atual: **ainda não deve rodar real nesta etapa**.

Pré-requisitos antes da execução real:

Pré-requisitos já atendidos:

1. migration do Step 68 aplicada;
2. estado do Alembic saneado;
3. dry-run repetido com sucesso.

Pendência remanescente antes de qualquer execução real:

4. manter o caso `OPERACAO_AGRICOLA` fora da automação até revisão manual.

## Decisão recomendada

- `PEDIDO_COMPRA`: manter como `IGNORAR`
- `origem_tipo NULL`: manter como `LEGADO`
- `OPERACAO_AGRICOLA`: manter em `REVISAR_MANUALMENTE`
- execução real: continuar proibida nesta etapa, apesar do dry-run já estar limpo
