# Proposta de Constraint Futura para Fornecedores Canônicos

Data: 2026-04-27

## Objetivo

Preparar a aplicação futura de garantias mais fortes sobre `compras_fornecedores`, agora que:

- novos writes já resolvem `Pessoa` canônica;
- `pessoa_id` já foi preenchido via backfill;
- duplicidades legadas por `tenant_id + pessoa_id` já foram consolidadas no ambiente local/dev.

Esta etapa **não aplica constraint**. Ela apenas documenta:

- a proposta técnica;
- as validações obrigatórias antes da migration;
- o plano de rollout;
- o plano de rollback.

## Estado atual

Hoje `compras_fornecedores` continua sendo uma tabela de compatibilidade.

Situação desejada para fase futura:

1. todo fornecedor legado deve apontar para uma `Pessoa` canônica;
2. um mesmo par `tenant_id + pessoa_id` não deve existir duas vezes;
3. novos cadastros via Compras não devem criar fornecedor sem `pessoa_id`.

## Constraints candidatas

### 1. Unicidade por `tenant_id + pessoa_id`

Objetivo:

- impedir duplicidade lógica do mesmo fornecedor canônico no legado.

Proposta:

```sql
CREATE UNIQUE INDEX CONCURRENTLY uq_compras_fornecedores_tenant_pessoa
ON farms.compras_fornecedores (tenant_id, pessoa_id)
WHERE pessoa_id IS NOT NULL;
```

Observações:

- índice parcial evita bloquear registros antigos eventualmente ainda sem `pessoa_id`;
- a proposta é compatível com a decisão atual de manter `pessoa_id` nullable durante a transição.

### 2. `pessoa_id` obrigatório em fase posterior

Objetivo:

- bloquear definitivamente fornecedor legado sem vínculo canônico.

Isso **não deve ser feito agora**.

Pré-condição mínima:

- `SELECT COUNT(*) FROM compras_fornecedores WHERE pessoa_id IS NULL = 0`

Proposta futura:

```sql
ALTER TABLE farms.compras_fornecedores
ALTER COLUMN pessoa_id SET NOT NULL;
```

### 3. FK já existente deve permanecer

O vínculo para `cadastros_pessoas.id` já existe e deve ser preservado:

- `compras_fornecedores.pessoa_id -> cadastros_pessoas.id`

Não há ação adicional necessária aqui, apenas validação de integridade antes do rollout.

## Validações prévias obrigatórias

Antes de qualquer migration com constraint, executar e arquivar auditoria com os checks abaixo.

### A. Fornecedores sem pessoa

```sql
SELECT COUNT(*)
FROM farms.compras_fornecedores
WHERE pessoa_id IS NULL;
```

Critério:

- resultado deve ser `0` para avançar rumo a `NOT NULL`;
- para aplicar apenas a unicidade parcial, ainda é aceitável haver `NULL`, desde que isso seja uma decisão consciente.

### B. Pessoa órfã

```sql
SELECT COUNT(*)
FROM farms.compras_fornecedores f
WHERE f.pessoa_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1
    FROM farms.cadastros_pessoas p
    WHERE p.id = f.pessoa_id
  );
```

Critério:

- resultado deve ser `0`.

### C. Duplicidade por `tenant_id + pessoa_id`

```sql
SELECT tenant_id, pessoa_id, COUNT(*) AS total
FROM farms.compras_fornecedores
WHERE pessoa_id IS NOT NULL
GROUP BY tenant_id, pessoa_id
HAVING COUNT(*) > 1;
```

Critério:

- nenhuma linha retornada.

### D. Referências órfãs para `compras_fornecedores`

Atualmente as referências reais conhecidas são:

- `compras_cotacoes.fornecedor_id`
- `compras_devolucoes.fornecedor_id`

Checks:

```sql
SELECT COUNT(*)
FROM farms.compras_cotacoes c
WHERE NOT EXISTS (
  SELECT 1
  FROM farms.compras_fornecedores f
  WHERE f.id = c.fornecedor_id
);
```

```sql
SELECT COUNT(*)
FROM farms.compras_devolucoes d
WHERE NOT EXISTS (
  SELECT 1
  FROM farms.compras_fornecedores f
  WHERE f.id = d.fornecedor_id
);
```

Critério:

- ambos devem retornar `0`.

### E. Papel `FORNECEDOR` ausente na pessoa vinculada

```sql
SELECT COUNT(*)
FROM (
  SELECT DISTINCT f.tenant_id, f.pessoa_id
  FROM farms.compras_fornecedores f
  WHERE f.pessoa_id IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM farms.cadastros_pessoa_relacionamentos pr
      JOIN farms.cadastros_tipos_relacionamento tr
        ON tr.id = pr.tipo_id
      WHERE pr.pessoa_id = f.pessoa_id
        AND tr.codigo = 'FORNECEDOR'
        AND tr.ativo = true
        AND (tr.tenant_id = f.tenant_id OR tr.tenant_id IS NULL)
    )
) x;
```

Critério:

- resultado deve ser `0`.

## Plano de rollout

### Fase 1. Auditoria congelada

1. rodar todos os checks acima em staging e produção;
2. salvar o relatório com data/hora;
3. bloquear rollout se qualquer check falhar.

### Fase 2. Aplicar unicidade parcial primeiro

Aplicar primeiro apenas:

```sql
CREATE UNIQUE INDEX CONCURRENTLY uq_compras_fornecedores_tenant_pessoa
ON farms.compras_fornecedores (tenant_id, pessoa_id)
WHERE pessoa_id IS NOT NULL;
```

Razão:

- protege contra nova duplicidade lógica;
- menor risco que `SET NOT NULL`;
- compatível com rollout gradual.

### Fase 3. Observar comportamento

Após criar o índice:

1. monitorar erros de escrita no fluxo de Compras;
2. monitorar logs do create/update de fornecedor;
3. verificar se alguma integração externa ainda tenta criar duplicata legada.

Janela recomendada:

- pelo menos um ciclo operacional real antes de considerar `NOT NULL`.

### Fase 4. Avaliar `NOT NULL`

Só depois de estabilidade comprovada:

```sql
ALTER TABLE farms.compras_fornecedores
ALTER COLUMN pessoa_id SET NOT NULL;
```

## Plano de rollback

### Rollback do índice único

Se houver regressão:

```sql
DROP INDEX CONCURRENTLY IF EXISTS farms.uq_compras_fornecedores_tenant_pessoa;
```

Quando usar:

- erros inesperados no create/update de fornecedor;
- integrações antigas ainda escrevendo duplicado;
- necessidade operacional de liberar writes antes de corrigir origem do problema.

### Rollback de `NOT NULL`

Se em fase futura o `NOT NULL` gerar regressão:

```sql
ALTER TABLE farms.compras_fornecedores
ALTER COLUMN pessoa_id DROP NOT NULL;
```

Quando usar:

- fluxo legado ainda não totalmente saneado;
- jobs ou integrações antigas criando registros incompletos;
- inconsistência descoberta após a mudança.

## Riscos conhecidos

1. Integração fora do router:
   writes diretos no banco ou scripts antigos podem não respeitar a lógica canônica.

2. Duplicidade sem documento:
   embora o fluxo atual tenha sido consolidado, dados futuros de baixa qualidade podem pressionar o fallback por nome.

3. Ambiente divergente:
   local/dev já foi saneado, mas staging e produção precisam da mesma auditoria antes de qualquer migration.

## Recomendação objetiva

Próxima etapa segura:

1. repetir auditoria em staging/produção;
2. se tudo estiver limpo, aplicar **apenas** o índice único parcial por `tenant_id + pessoa_id`;
3. postergar `SET NOT NULL` para uma etapa seguinte, depois de observação operacional.

## Fora de escopo desta etapa

- criar migration;
- aplicar índice;
- aplicar `NOT NULL`;
- alterar contratos de API;
- remover `compras_fornecedores`.
