# Step 73 - Estratégia final de desativação do legado `estoque_movimentacoes`

## Objetivo

Definir a política arquitetural final para encerrar o uso de `estoque_movimentacoes` com segurança, mantendo apenas o mínimo necessário para histórico e compatibilidade temporária.

Base considerada:

- Step 61: novos writes já foram travados em `estoque_movimentos`
- Step 63: leituras funcionais principais já foram adaptadas para priorizar o ledger canônico
- Step 71: backfill real executado para os casos elegíveis
- Step 72: exceção remanescente de `OPERACAO_AGRICOLA` revisada manualmente

Fora de escopo desta etapa:

- remover a tabela;
- alterar código;
- quebrar APIs atuais;
- mudar comportamento em produção imediatamente.

## Estado atual consolidado

### O que já está resolvido

- novos writes operacionais usam `estoque_movimentos`;
- leituras principais de Safra e Relatórios já priorizam o ledger canônico;
- o passivo elegível do legado já foi tratado:
  - `4` casos persistidos como `LEGADO`;
  - `4` casos de `PEDIDO_COMPRA` ignorados por já estarem cobertos;
  - `1` caso de `OPERACAO_AGRICOLA` ficou deliberadamente fora da automação.

### O que ainda existe no legado

- tabela física `estoque_movimentacoes`;
- model ORM `MovimentacaoEstoque`;
- leituras de fallback controlado em Safra e Relatórios;
- testes que:
  - verificam fallback histórico;
  - verificam ausência de novos writes no legado;
- migrations históricas e metadata de Alembic.

## 1. Classificação dos usos restantes

## Leitura necessária

1. [agricola/safras/service.py](/opt/lampp/htdocs/farm/apps/web/services/api/agricola/safras/service.py:611)

Uso atual:

- fallback legado para movimentos/lotes de safra ainda não cobertos pelo ledger canônico.

Classificação:

- `LEITURA_HISTORICA_TEMPORARIA`

2. [operacional/services/relatorio_service.py](/opt/lampp/htdocs/farm/apps/web/services/api/operacional/services/relatorio_service.py:200)

Uso atual:

- fallback legado para agregados históricos fora da cobertura canônica.

Classificação:

- `LEITURA_HISTORICA_TEMPORARIA`

## Fallback controlado

1. Leituras híbridas de Safra
2. Leituras híbridas de Relatórios

Política:

- permitido apenas enquanto existir dado histórico relevante não representado de forma suficiente em `estoque_movimentos`;
- proibido ampliar esse padrão para novos módulos.

Classificação:

- `FALLBACK_TEMPORARIO`

## Testes

1. [tests/integration/operacional/test_estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/integration/operacional/test_estoque.py:81)

Uso atual:

- garante que novos writes não entram em `estoque_movimentacoes`.

Classificação:

- `TESTE_GUARDA_OBRIGATORIO`

2. [tests/integration/agricola/test_safra_estoque_ledger.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/integration/agricola/test_safra_estoque_ledger.py:151)
3. [tests/integration/operacional/test_relatorio_estoque_ledger.py](/opt/lampp/htdocs/farm/apps/web/services/api/tests/integration/operacional/test_relatorio_estoque_ledger.py:1)

Uso atual:

- exercitam cenário híbrido com dados legados e canônicos.

Classificação:

- `TESTE_COMPATIBILIDADE_TEMPORARIA`

## Código morto ou apenas histórico estrutural

1. [operacional/models/estoque.py](/opt/lampp/htdocs/farm/apps/web/services/api/operacional/models/estoque.py:110)

Uso atual:

- model ORM ainda necessário enquanto existir leitura/fallback/migration.

Classificação:

- `ESTRUTURA_LEGADA_CONTROLADA`

2. [migrations/env.py](/opt/lampp/htdocs/farm/apps/web/services/api/migrations/env.py:85)
3. migrations históricas que referenciam `estoque_movimentacoes`

Classificação:

- `HISTORICO_E_METADATA`

4. [scripts/backfill_estoque_movimentacoes.py](/opt/lampp/htdocs/farm/apps/web/services/api/scripts/backfill_estoque_movimentacoes.py:1)

Uso atual:

- utilitário de migração pontual já executado.

Classificação:

- `FERRAMENTA_DE_MIGRACAO_CONGELADA`

## 2. Política oficial

### Leituras históricas

Política oficial:

- leitura histórica de `estoque_movimentacoes` ainda é permitida apenas como compatibilidade temporária para dados antigos já conhecidos;
- essa leitura deve ser sempre subordinada ao ledger canônico;
- nenhum novo endpoint deve usar `estoque_movimentacoes` como fonte primária.

### Fallback

Política oficial:

- fallback para `estoque_movimentacoes` é permitido somente em serviços já adaptados que ainda precisam cobrir histórico incompleto;
- fallback novo em módulos adicionais está proibido;
- fallback deve ser removido assim que os consumidores históricos estiverem validados contra `estoque_movimentos`.

### Novos usos

Política oficial:

- novos usos de `estoque_movimentacoes` estão proibidos;
- novos writes já estão proibidos por design e devem continuar assim;
- novas leituras diretas fora dos pontos já conhecidos devem ser tratadas como regressão arquitetural.

### Escrita

Política oficial:

- `estoque_movimentacoes` não recebe novos writes de negócio;
- qualquer necessidade de correção histórica deve ser tratada via `estoque_movimentos`, preferencialmente com origem explícita e trilha de auditoria.

## 3. Plano de depreciação

### Fase 1: marcar o legado como congelado

Objetivo:

- tornar explícito que `estoque_movimentacoes` é somente legado/histórico.

Ações planejadas:

1. documentar a tabela como `legacy-read-only`;
2. manter o teste guarda que verifica ausência de novos writes;
3. bloquear em revisão técnica qualquer novo uso funcional.

### Fase 2: eliminar fallback funcional

Objetivo:

- remover dependência de leitura híbrida em Safra e Relatórios.

Ações planejadas:

1. medir se ainda existe consulta funcional dependente do fallback legado;
2. validar se o histórico relevante já está suficientemente disponível via ledger canônico;
3. retirar fallback de:
   - `agricola/safras/service.py`
   - `operacional/services/relatorio_service.py`

### Fase 3: atualizar testes

Objetivo:

- deixar os testes ancorados no ledger canônico, mantendo só a guarda negativa do legado enquanto necessário.

Ações planejadas:

1. remover cenários híbridos quando o fallback sair;
2. preservar temporariamente apenas:
   - teste de ausência de novos writes no legado;
   - eventuais testes de migração/auditoria, se ainda fizerem sentido.

### Fase 4: bloquear novos usos automaticamente

Objetivo:

- transformar a política em proteção operacional.

Ações planejadas:

1. adicionar verificação estática ou grep de CI para barrar novos imports/queries de `MovimentacaoEstoque`;
2. permitir exceções apenas em:
   - migrations históricas;
   - metadata do Alembic;
   - scripts de auditoria/migração explicitamente marcados.

### Fase 5: preparar remoção física futura

Objetivo:

- deixar a tabela pronta para ser aposentada sem surpresa.

Ações planejadas:

1. confirmar ausência de leitura funcional em produção;
2. confirmar ausência de testes dependentes;
3. criar migration dedicada para remoção física apenas em etapa posterior.

## 4. Critérios para remoção futura

Remoção física da tabela só deve ser considerada quando todos os critérios abaixo forem verdadeiros:

1. `0` leituras funcionais em produção dependentes de `estoque_movimentacoes`
2. `0` fallbacks ativos em código de aplicação
3. `0` testes de produto dependentes do legado
4. período mínimo de observação sem necessidade de fallback:
   - recomendação: `30 dias`
5. auditoria confirmando que:
   - o ledger canônico cobre o histórico necessário;
   - não há reconciliação pendente relevante;
   - exceções manuais abertas já foram resolvidas ou aceitas como encerradas

## Critério adicional recomendado

Antes da remoção física:

- rodar uma auditoria final comparando:
  - contagem histórica acessível por API;
  - relatórios consolidados;
  - consultas de safra;
  - saldo e rastreabilidade por produto/deposito/lote

## Decisão executável

Decisão final do Step 73:

- `estoque_movimentacoes` passa a ser oficialmente uma tabela de legado histórico, `read-only`, sem novos usos autorizados.
- Leituras históricas e fallback continuam permitidos apenas nos pontos já conhecidos e apenas como transição.
- O próximo passo arquitetural correto não é remover a tabela ainda; é remover os fallbacks remanescentes e reduzir a superfície de leitura a zero.
- Remoção física futura depende de janela mínima de estabilidade e auditoria final.

## Resumo operacional

Pode fazer agora:

- tratar `estoque_movimentacoes` como legado congelado;
- proibir novos usos;
- planejar remoção de fallback.

Não deve fazer agora:

- apagar a tabela;
- remover o model ORM;
- retirar o teste de guarda de novos writes;
- assumir que toda leitura histórica já pode ser desligada sem validação adicional.
