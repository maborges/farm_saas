# Validacao Cross-Modulo Step 92

Data: 2026-04-30

## Objetivo

Validar que as migracoes recentes nao quebraram os fluxos principais entre Estoque, Compras, Agricultura, Pecuaria e Financeiro, sem alterar schema, migrations ou regra de negocio alem de correcoes bloqueantes encontradas durante a validacao.

## Escopo executado

- Testes focados dos modulos impactados
- `py_compile` nos modulos operacionais
- Guardrail de legado de estoque
- Guardrail de ownership cross-modulo
- Varredura estatica para reintroducao de `estoque_movimentacoes`
- Varredura estatica para reintroducao de `insumo_id`

## Validacoes estaticas

- Nenhum uso ativo de `MovimentacaoEstoque` ou `estoque_movimentacoes` em codigo Python ativo sob `services/api/**/*.py`
- Nenhum uso ativo de `insumo_id` em codigo Python ativo sob `services/api/**/*.py`
- O guardrail opcional do espelho `apps/web/services/api/**/*.py` segue compativel com o estado atual

## Comandos executados

### Guardrails

```bash
services/api/.venv/bin/pytest \
  services/api/tests/unit/operacional/test_estoque_legacy_guardrail.py \
  services/api/tests/unit/test_cross_module_ownership_guardrails.py -q
```

Resultado:

```text
3 passed in 0.58s
```

### Compilacao Python

```bash
find services/api/operacional services/api/agricola services/api/pecuaria services/api/financeiro \
  -name '*.py' -print0 | xargs -0 .venv/bin/python -m py_compile
```

Resultado: sem erros.

### Suite focada cross-modulo

```bash
services/api/.venv/bin/pytest \
  services/api/tests/integration/operacional/test_compras.py \
  services/api/tests/integration/operacional/test_estoque.py \
  services/api/tests/test_fifo_estoque.py \
  services/api/tests/test_compras_lote_integration.py \
  services/api/tests/integration/agricola/test_safras.py \
  services/api/tests/integration/test_pecuaria.py \
  services/api/tests/integration/financeiro/test_receitas.py \
  services/api/tests/integration/financeiro/test_despesas.py \
  services/api/tests/unit/pecuaria/test_manejo_produto_canonico.py \
  services/api/tests/unit/agricola/test_insumo_campos_canonicos.py -q
```

Resultado final:

```text
76 passed, 2 xfailed, 44 warnings in 92.42s
```

### Validacao complementar no espelho `apps/web`

```bash
apps/web/services/api/.venv/bin/pytest \
  apps/web/services/api/tests/unit/financeiro/test_origem_financeira.py -q
```

Resultado:

```text
6 passed in 0.36s
```

```bash
apps/web/services/api/.venv/bin/pytest \
  apps/web/services/api/tests/integration/agricola/test_safra_estoque_ledger.py -q
```

Resultado:

```text
1 passed in 2.44s
```

### Integridade de diff

```bash
git diff --check
```

Resultado: sem erros.

## Problemas bloqueantes encontrados e corrigidos

### 1. Avanco de fase de safra exigia corpo obrigatorio indevido

Sintoma:

- `POST /api/v1/safras/{id}/avancar-fase/{nova_fase}` retornava `422` quando o teste usava apenas a fase na URL

Impacto:

- Quebrava o fluxo agricola validado por integracao

Correcao aplicada:

- `SafraAvancarFase.novo_status` passou a ser opcional
- A rota continua usando a fase da URL como fonte canonica
- Foi adicionada validacao defensiva para rejeitar divergencia entre URL e corpo quando ambos forem enviados

Arquivos:

- `services/api/agricola/safras/schemas.py`
- `services/api/agricola/safras/router.py`
- `apps/web/services/api/agricola/safras/schemas.py`
- `apps/web/services/api/agricola/safras/router.py`

### 2. Leitura de historico de ledger da safra expunha quantidade com sinal invertido para consumo

Sintoma:

- O endpoint de leitura por safra retornava `quantidade = -12.0` para um movimento cujo `tipo` ja indicava saida

Impacto:

- Quebrava a interpretacao canonica do payload e o teste de integracao do espelho `apps/web`

Correcao aplicada:

- A leitura por safra passou a normalizar `quantidade` com `abs(...)`
- A direcao do movimento permanece representada pelo campo `tipo`

Arquivos:

- `services/api/agricola/safras/service.py`
- `apps/web/services/api/agricola/safras/service.py`

### 3. Teste de integracao em `apps/web` nao registrava metadata necessaria para FK

Sintoma:

- `NoReferencedTableError` para `unidade_medida_id` ao montar metadata do teste

Impacto:

- Bloqueava a validacao complementar do fluxo agricola espelhado

Correcao aplicada:

- Registro explicito do modelo `UnidadeMedida` na fixture/import do teste

Arquivo:

- `apps/web/services/api/tests/integration/agricola/test_safra_estoque_ledger.py`

## Cobertura funcional validada

- Compras: criacao/recebimento e integracao com estoque e financeiro cobertos pela suite operacional focada
- Estoque: entrada, saida, ajuste, transferencia, FIFO e saldo coerente cobertos pelas suites operacional e FIFO
- Agricultura: operacao com `produto_id`, consumo de lote, ledger e leitura por safra cobertos pelas suites de safra
- Pecuaria: manejo com `produto_id` e origem financeira cobertos por testes de integracao e unidade
- Financeiro: uso de `MANUAL` para lancamentos manuais e origem real para fluxos operacionais cobertos pelas suites de receitas, despesas e origem financeira

## Conclusao

- Os testes focados passaram no estado atual
- Nao ha uso ativo de `estoque_movimentacoes` no codigo Python validado
- Nao ha uso ativo de `insumo_id` no codigo Python validado
- Os problemas encontrados foram bloqueantes, localizados e corrigidos sem alterar schema ou migrations
- Os fluxos principais seguem operacionais dentro do escopo validado
