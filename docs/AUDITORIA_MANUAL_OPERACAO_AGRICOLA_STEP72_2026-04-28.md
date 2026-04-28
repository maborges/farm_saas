# Step 72 - Revisão manual do caso remanescente `OPERACAO_AGRICOLA`

## Objetivo

Decidir manualmente o destino do único caso legado de `estoque_movimentacoes` que permaneceu fora do backfill automático:

- virar movimento canônico com vínculo real;
- ficar como `LEGADO`;
- ou ser ignorado por já estar coberto.

## Registro auditado

Movimentação legada:

- `estoque_movimentacoes.id = b39c688c-62a8-4989-815d-0b71cf86b234`
- `tenant_id = aaaaaaaa-0000-0000-0000-000000000010`
- `tipo = SAIDA`
- `quantidade = 5.0`
- `custo_unitario = 9.0`
- `custo_total = 45.0`
- `data_movimentacao = 2026-04-28 05:38:15`
- `origem_tipo = OPERACAO_AGRICOLA`
- `origem_id = 3e1a163d-8945-40b7-914d-584b6a246d1c`
- `produto_id = ed3f6d92-b581-41f3-a515-27f128d719e2`
- `deposito_id = 865e34f2-ced2-4cc7-a888-81c53fa9cffd`
- `lote_id = 7593376c-985d-44bd-97c8-4e3909c40b68`
- `motivo = Consumo legado`

## Evidências levantadas

### 1. A operação agrícola legada existe

`operacoes_agricolas.id = 3e1a163d-8945-40b7-914d-584b6a246d1c`

Dados principais:

- `tipo = ADUBACAO`
- `descricao = Operação legada`
- `data_realizada = 2026-04-05`
- `talhao_id = 2d476920-e869-48c7-b6ea-ee8b28d00d37`
- `safra_id = 8932e2c1-c2b7-4e6c-890e-ea40602e3e67`

### 2. Não existe `operacao_execucao` vinculada a essa operação

Consulta em `operacoes_execucoes` por `operacao_id = 3e1a163d-8945-40b7-914d-584b6a246d1c`:

- resultado: `0` linhas

Leitura:

- não há vínculo canônico real disponível para converter este movimento automaticamente para `origem = OPERACAO_EXECUCAO`.

### 3. Existe um movimento canônico no mesmo contexto de produto/deposito/data, mas ele não cobre este caso

Movimento canônico encontrado:

- `estoque_movimentos.id = b13e975b-0ffb-4a5d-a687-3691baa937ab`
- `origem = OPERACAO_EXECUCAO`
- `operacao_execucao_id = a87731ad-7729-423d-a343-4eb797ab733e`
- `tipo_movimento = SAIDA`
- `quantidade = -12.000000`
- `lote_id = 5e258d57-f76b-4bd3-b9d3-7836b031b793`
- `observacoes = Consumo no ledger`

Esse movimento canônico aponta para:

- `operacoes_execucoes.id = a87731ad-7729-423d-a343-4eb797ab733e`
- `operacao_id = 4ac7d757-19c9-46d8-958a-08a9421de42b`

E a operação correspondente é:

- `tipo = PULVERIZACAO`
- `descricao = Operação com ledger`
- `data_realizada = 2026-04-10`
- mesmo `talhao_id = 2d476920-e869-48c7-b6ea-ee8b28d00d37`
- mesma `safra_id = 8932e2c1-c2b7-4e6c-890e-ea40602e3e67`

### 4. Diferenças materiais entre o legado e o canônico existente

Operação legada:

- `ADUBACAO`
- `data_realizada = 2026-04-05`
- quantidade legada consumida: `5.0`
- lote legado: `LEGADO-001`

Operação canônica encontrada:

- `PULVERIZACAO`
- `data_realizada = 2026-04-10`
- quantidade canônica consumida: `12.0`
- lote canônico: `LEDGER-001`

Leitura:

- isso não é o mesmo evento operacional;
- portanto, não há base para concluir cobertura e ignorar o legado.

### 5. O registro ainda não foi backfillado

Checagem por marcador em `observacoes` do ledger:

- `legacy_movimentacao_id=b39c688c-62a8-4989-815d-0b71cf86b234`
- resultado: `0` linhas

## Decisão manual

### Conclusão

Este caso **não deve ser ignorado** e **não pode virar movimento canônico com vínculo real nesta etapa**.

Decisão recomendada:

- classificar este remanescente como **`LEGADO` manualmente**, se a equipe optar por preservar o histórico no ledger;
- manter fora da automação como `REVISAR_MANUALMENTE` até essa inserção manual controlada acontecer.

## Justificativa da decisão

### Por que não ignorar

- não existe cobertura canônica do mesmo evento;
- o movimento encontrado no ledger pertence a outra operação, com outro tipo, outra data, outra quantidade e outro lote.

### Por que não migrar com vínculo real

- não existe `operacao_execucao` para a operação agrícola legada;
- qualquer vínculo novo para `OPERACAO_EXECUCAO` seria inventado, não rastreado.

### Por que `LEGADO` é o destino mais seguro

- a origem operacional histórica é conhecida no legado, mas não existe equivalente canônico executável para ligação formal;
- preservar como `LEGADO` mantém o consumo auditável no ledger sem fabricar uma execução agrícola que não existe;
- isso respeita a política do Step 67: `LEGADO` para histórico sem vínculo canônico confiável.

## Recomendação operacional

Estado do caso após a revisão manual:

- decisão de negócio/técnica: **preservar como `LEGADO`**
- decisão de execução: **não inserir automaticamente nesta etapa**

Próximo passo seguro, se desejado:

1. inserir manualmente um `estoque_movimentos` com `origem = LEGADO`;
2. registrar em `observacoes`:
   - `legacy_movimentacao_id=b39c688c-62a8-4989-815d-0b71cf86b234`
   - `origem_tipo_legacy=OPERACAO_AGRICOLA`
   - `origem_id_legacy=3e1a163d-8945-40b7-914d-584b6a246d1c`
   - referência textual de que não existe `operacao_execucao` correspondente;
3. manter o backfill automático inalterado.

## Decisão final do Step 72

- `IGNORAR`: **não**
- `MIGRAR com vínculo real`: **não**
- `LEGADO`: **sim, por inserção manual controlada quando houver aceite**
