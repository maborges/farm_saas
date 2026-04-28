# Aplicação do Índice Único Parcial em `compras_fornecedores`

Data/hora: 2026-04-27T22:59:30-03:00

## Objetivo

Aplicar a proteção contra nova duplicidade lógica em `compras_fornecedores` por:

- `tenant_id + pessoa_id`

Sem aplicar `NOT NULL` em `pessoa_id`.

## Checks prévios executados no ambiente alvo

Resultados antes da aplicação:

- `sem_pessoa = 0`
- `pessoa_orfa = 0`
- `duplicidade_tenant_pessoa = 0`
- `referencias_orfas_cotacoes = 0`
- `referencias_orfas_devolucoes = 0`
- `pessoas_fornecedor_sem_relacao = 0`

Conclusão:

- ambiente apto para aplicação do índice único parcial.

## Migration aplicada

Migration:

- `b2c4d6e8f001_add_unique_partial_index_compras_fornecedores_tenant_pessoa.py`

Revision final:

- `b2c4d6e8f001 (head)`

## Estrutura aplicada

Índice único parcial:

```sql
CREATE UNIQUE INDEX uq_compras_fornecedores_tenant_pessoa
ON farms.compras_fornecedores (tenant_id, pessoa_id)
WHERE pessoa_id IS NOT NULL;
```

Observação:

- `pessoa_id` continua nullable nesta etapa.

## Auditoria pós-aplicação

Resultados após a migration:

- `sem_pessoa = 0`
- `pessoa_orfa = 0`
- `duplicidade_tenant_pessoa = 0`
- `referencias_orfas_cotacoes = 0`
- `referencias_orfas_devolucoes = 0`
- `pessoas_fornecedor_sem_relacao = 0`
- `indice_existe = 1`

## Conclusão

O índice único parcial por `tenant_id + pessoa_id` foi aplicado com sucesso no ambiente alvo.

Estado final:

- nenhum fornecedor sem `pessoa_id` no ambiente auditado;
- nenhuma duplicidade por `tenant_id + pessoa_id`;
- nenhuma referência órfã conhecida;
- nenhuma constraint `NOT NULL` aplicada ainda.

## Próximo passo sugerido

- observar o comportamento do fluxo de Compras com o índice em vigor;
- só depois considerar a etapa futura de `ALTER COLUMN pessoa_id SET NOT NULL`.
