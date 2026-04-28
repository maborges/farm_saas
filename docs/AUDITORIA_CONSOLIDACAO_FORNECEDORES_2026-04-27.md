# Auditoria da Consolidação de Duplicidade em `compras_fornecedores`

Data/hora: 2026-04-27T22:51:31-03:00

## Escopo consolidado

Grupo consolidado:

- tenant_id: `592b906e-0329-44df-8c58-80ca744ae243`
- pessoa_id: `2389e124-0c77-40c1-8626-00decbdfbcdf`

Registros originais:

1. fornecedor A: `ae34de87-5c8f-4987-a946-f6bdbcf72d42`
2. fornecedor B: `fc8bd619-b1b2-4344-9572-8a53e7c0425f`

## Mapeamento de referências para `compras_fornecedores`

Referências com FK real encontradas no código:

- `compras_cotacoes.fornecedor_id`
- `compras_devolucoes.fornecedor_id`

Validação do grupo consolidado:

- referências em `compras_cotacoes` para A: `0`
- referências em `compras_cotacoes` para B: `0`
- referências em `compras_devolucoes` para A: `0`
- referências em `compras_devolucoes` para B: `0`

## Critério do registro canônico

O script de consolidação usa regra determinística:

1. maior número de referências
2. maior preenchimento de campos relevantes
3. presença de documento
4. desempate estável por `id`

Para este grupo, o canônico escolhido foi:

- `fc8bd619-b1b2-4344-9572-8a53e7c0425f`

Registro removido:

- `ae34de87-5c8f-4987-a946-f6bdbcf72d42`

## Decisão sobre inativação/depreciação

`compras_fornecedores` não possui campo adequado de inativação/depreciação.

Decisão aplicada:

- reapontar referências primeiro
- mesclar dados faltantes no registro canônico quando necessário
- remover o duplicado apenas após a consolidação

Neste caso específico, não havia referências para reapontar.

## Execução realizada

Dry-run:

```bash
cd /opt/lampp/htdocs/farm/services/api
.venv/bin/python scripts/consolidar_fornecedores_duplicados.py \
  --tenant-id 592b906e-0329-44df-8c58-80ca744ae243 \
  --pessoa-id 2389e124-0c77-40c1-8626-00decbdfbcdf \
  --dry-run
```

Execução real:

```bash
cd /opt/lampp/htdocs/farm/services/api
.venv/bin/python scripts/consolidar_fornecedores_duplicados.py \
  --tenant-id 592b906e-0329-44df-8c58-80ca744ae243 \
  --pessoa-id 2389e124-0c77-40c1-8626-00decbdfbcdf
```

## Auditoria pós-consolidação

Resultados finais:

- `total_fornecedores = 3`
- `sem_pessoa = 0`
- `pessoa_orfa = 0`
- `duplicidade_tenant_pessoa = 0`
- `duplicidade_tenant_doc_normalizado = 0`
- `referencias_orfas_cotacoes = 0`
- `referencias_orfas_devolucoes = 0`

## Validação de idempotência

Nova execução do mesmo comando após consolidar:

- `grupos = 0`
- `removidos = 0`
- `refs = 0`
- `erros = 0`

## Conclusão

A duplicidade legada por `tenant_id + pessoa_id` foi eliminada sem deixar referências órfãs.

O ambiente local/dev ficou pronto para a próxima etapa de avaliação de constraint, mas nenhuma constraint foi criada nesta fase.
