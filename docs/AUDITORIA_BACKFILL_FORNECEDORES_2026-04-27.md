# Auditoria do Backfill de `compras_fornecedores.pessoa_id`

Data/hora: 2026-04-27T22:44:34-03:00

## Execução realizada

Comando executado:

```bash
cd /opt/lampp/htdocs/farm/services/api
.venv/bin/python scripts/backfill_fornecedores_pessoa.py --apenas-sem-pessoa
```

Resumo observado:

- total processado: 3
- já vinculados: 0
- vinculados por documento: 0
- vinculados por nome: 1
- criados novos: 2
- erros: 0

## Validação de idempotência

Segunda execução com o mesmo comando:

- total processado: 0
- erros: 0

Conclusão: o backfill está idempotente para fornecedores ainda sem `pessoa_id`.

## Auditoria pós-backfill

Resultados:

- `total_fornecedores = 4`
- `sem_pessoa = 0`
- `pessoa_orfa = 0`
- `duplicidade_tenant_pessoa = 1`
- `duplicidade_tenant_doc_normalizado = 0`
- `pessoas_fornecedor_sem_relacao = 0`

## Duplicidade remanescente

Existe uma duplicidade legada por `tenant_id + pessoa_id`:

Tenant: `592b906e-0329-44df-8c58-80ca744ae243`

Pessoa: `2389e124-0c77-40c1-8626-00decbdfbcdf`

Registros:

1. `ae34de87-5c8f-4987-a946-f6bdbcf72d42`
   - nome_fantasia: `Agroquimica Brasil Ltda`
   - cnpj_cpf: `10512032000120`
   - email: `marcos.borges@borgus.com.br`
   - telefone: `11984461010`

2. `fc8bd619-b1b2-4344-9572-8a53e7c0425f`
   - nome_fantasia: `Agroquimica Brasil Ltda`
   - cnpj_cpf: `00034631000121`
   - email: `marcos.borges@borgus.com.br`
   - telefone: `11984461010`

## Conclusão

O backfill cumpriu o objetivo de preencher `pessoa_id` sem deixar fornecedores sem vínculo e sem gerar documento duplicado no legado.

Porém, ainda não é seguro pensar em constraint de unicidade baseada em `tenant_id + pessoa_id`, porque já existe duplicidade legada remanescente após o backfill.

Próximo passo recomendado:

- revisar e decidir estratégia de consolidação dos registros legados duplicados antes de qualquer constraint.
