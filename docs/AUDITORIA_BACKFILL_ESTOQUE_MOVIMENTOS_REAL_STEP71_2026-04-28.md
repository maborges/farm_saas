# Step 71 - Auditoria do backfill real `estoque_movimentacoes` -> `estoque_movimentos`

## Contexto

Esta etapa executa o backfill real de `estoque_movimentacoes` para `estoque_movimentos`, depois do saneamento do Alembic e da liberação de `LEGADO` na constraint do ledger.

Pré-condições já atendidas antes da execução:

- estado do Alembic consistente;
- constraint `ck_estoque_movimentos_origem` aceitando `LEGADO`;
- dry-run validado sem erro;
- política de elegibilidade consolidada:
  - `IGNORAR`
  - `MIGRAR`
  - `MARCAR_COMO_LEGADO`
  - `REVISAR_MANUALMENTE`

## Comando executado

Diretório:

```bash
/opt/lampp/htdocs/farm/apps/web/services/api
```

Comando:

```bash
.venv/bin/python scripts/backfill_estoque_movimentacoes.py
```

## Resumo da execução real

Resultado do script:

- `total_processado`: `9`
- `ja_backfillados`: `0`
- `ignorados`: `4`
- `migrados`: `0`
- `marcados_como_legado`: `4`
- `revisao_manual`: `1`
- `erros`: `0`

Leitura prática:

- não houve caso determinístico adicional para `MIGRAR`;
- o backfill real inseriu apenas os `4` casos classificados como `LEGADO`;
- os `4` casos de `PEDIDO_COMPRA` permaneceram corretamente fora da carga;
- o `1` caso de `OPERACAO_AGRICOLA` continuou em revisão manual.

## Detalhamento por categoria

### `IGNORAR`

Total: `4`

Origem:

- `PEDIDO_COMPRA`: `4`

Motivo:

- já cobertos no ledger canônico;
- não migrados para evitar dupla contagem.

### `MIGRAR`

Total: `0`

Origem:

- nenhuma no snapshot atual.

### `MARCAR_COMO_LEGADO`

Total persistido: `4`

Origem:

- `origem_tipo = NULL`: `4`

Movimentos criados no ledger:

- `2` saídas `LEGADO`
- `2` entradas `LEGADO`

### `REVISAR_MANUALMENTE`

Total pendente: `1`

Origem:

- `OPERACAO_AGRICOLA`: `1`

Motivo:

- sem vínculo determinístico único para `OPERACAO_EXECUCAO`.

## Validação pós-execução

### Contagem de ledger

Resultado observado:

- `estoque_movimentos` antes do backfill real: `30` no snapshot auditado do Step 65;
- `estoque_movimentos` após o backfill real: `34`.

Impacto líquido:

- `+4` linhas no ledger;
- exatamente o volume esperado de `LEGADO`.

### Duplicidade por `legacy_movimentacao_id`

Resultado:

- grupos duplicados: `0`
- linhas excedentes: `0`

Leitura:

- não houve duplicação de marcador legado;
- a idempotência por `legacy_movimentacao_id` foi preservada.

### Integridade referencial

Checagens executadas:

- `operacao_execucao_id` inválido em `estoque_movimentos`: `0`
- `produto_id` inválido em `estoque_movimentos`: `0`
- `deposito_id` inválido em `estoque_movimentos`: `0`

Leitura:

- nenhuma quebra de constraint ou FK foi observada na carga persistida.

### Backfill persistido no ledger

Total de movimentos com marcador de backfill:

- `4`

Origem dos movimentos persistidos:

- `LEGADO`: `4`

## Prova de idempotência

Após a execução real, foi rodada uma nova simulação:

```bash
.venv/bin/python scripts/backfill_estoque_movimentacoes.py --dry-run
```

Resumo do dry-run pós-backfill:

- `total_processado`: `9`
- `ja_backfillados`: `4`
- `ignorados`: `4`
- `migrados`: `0`
- `marcados_como_legado`: `0`
- `revisao_manual`: `1`
- `erros`: `0`

Leitura:

- os `4` movimentos persistidos já foram reconhecidos como backfillados;
- não houve nova tentativa de inserção para esses casos;
- a idempotência operacional do script ficou demonstrada.

## Comparação com o dry-run do Step 70

Dry-run válido do Step 70:

- `ignorados`: `4`
- `migrados`: `0`
- `marcados_como_legado`: `4`
- `revisao_manual`: `1`
- `erros`: `0`

Execução real do Step 71:

- `ignorados`: `4`
- `migrados`: `0`
- `marcados_como_legado`: `4`
- `revisao_manual`: `1`
- `erros`: `0`

Conclusão da comparação:

- a execução real reproduziu exatamente a expectativa do dry-run válido;
- não houve desvio de classificação;
- não apareceu impacto colateral inesperado.

## Impacto colateral

Resultado observado:

- nenhuma quebra de constraint;
- nenhuma inconsistência de FK;
- nenhum indício de duplicidade no ledger;
- nenhum processamento adicional sobre o caso ambíguo de `OPERACAO_AGRICOLA`.

Observação:

- o script foi desenhado para acrescentar apenas movimentos em `estoque_movimentos`;
- ele não atualiza `estoque_saldos`, e nesta execução não houve sinal de efeito colateral fora do ledger.

## Conclusão

O backfill real foi executado com sucesso e sem erro.

Resultado final:

- `4` movimentos históricos foram persistidos no ledger como `LEGADO`;
- `4` movimentos de compra permaneceram corretamente ignorados;
- `1` movimento agrícola segue pendente de revisão manual;
- a idempotência foi validada por reexecução em `dry-run`.

Estado após o Step 71:

- backfill real concluído para os casos elegíveis do snapshot atual;
- nenhum impacto colateral observado;
- nenhum caso ambíguo foi promovido automaticamente.
