# Step 14 — Plano de Execução

**Arquivo da migration:** `services/api/migrations/versions/step14_unidades_medida.py`
**Revision ID:** `step14_uom`
**Down revision:** `0808ec16ef17` (head atual)
**Data:** 2026-04-24

---

## 1. Justificativa das decisões

> **Nota sobre `casas_decimais`:** representa **precisão de apresentação** (UI/máscaras) e **não substitui a precisão de cálculo** (NUMERIC). Toda operação aritmética (conversão, rateio, soma de saldos) preserva `NUMERIC(18,9)` do `fator_canonico` e `NUMERIC(precision,scale)` das colunas de quantidade/custo. `casas_decimais` orienta exclusivamente formatação de entrada e exibição no frontend.

### 1.1 Por que este step precisa existir primeiro

O doc mestre exige um **Measurement Engine** antes de `estoque_movimentos` e `operacoes_execucoes`. Sem UOM canônica:
- Saldos de estoque ficam sem unidade (kg? saca? litro?).
- Execuções de operação não conseguem comparar `qtd_prevista` vs `qtd_executada` em unidades diferentes.
- Conversão saca↔kg por cultura (café 50kg vs soja 60kg) fica espalhada em código.

Step 14 é **bloqueante** para steps 17 e 18 — FKs `unidade_medida_id NOT NULL` dependem desta tabela.

### 1.2 Por que seed dentro da migration (não runbook)

- As 14 unidades de sistema (`KG`, `TON`, `SC60`, `HA`, `HR_MAQ`, etc.) são **universais** — não variam por tenant.
- Step 17/18 têm FK `NOT NULL` para `unidades_medida.id`; se o seed não existir, migrations subsequentes falham em ambientes frescos.
- Idempotente via `ON CONFLICT DO NOTHING` no partial unique `WHERE tenant_id IS NULL`.

### 1.3 Por que `tenant_id` nullable

- Unidades de sistema (tenant_id NULL) são globais — evita duplicação por tenant.
- Tenants podem adicionar unidades customizadas (tenant_id preenchido) sem colidir com globais.
- Partial unique index separa os dois escopos limpamente em PG nativo.

### 1.4 Por que dimensões em pt-BR

Consistência com padrão do projeto: `aprovado_em`, `cancelado_por`, `ativo`. Dimensões entram no mesmo nível de campos de negócio (pt-BR). Termos técnicos ORM (`created_at`) permanecem em inglês.

### 1.5 Por que `HR_MAQ` e `HR_HOMEM` são dimensões separadas

Hora de máquina e hora humana **não são intercambiáveis** (1 h de trator ≠ 1 h de operário). Usar dimensão única `tempo` permitiria conversão errada. Separar em `hora_maquina` e `hora_homem` bloqueia via CHECK de dimensão.

### 1.6 Por que `SC50` e `SC60` como unidades distintas (não conversão)

Sacas de 50 kg (café) e 60 kg (soja/milho) são **unidades fixas**, não conversões condicionais. Modelar como unidades separadas com `fator_canonico` próprio é mais simples que gerenciar conversão por cultura.

`unidades_medida_conversoes` fica reservada para casos realmente variáveis (densidade de grão granel, m³→ton por umidade).

### 1.7 Por que unique index via `op.execute` e não `UniqueConstraint`

- **Partial unique** (`WHERE tenant_id IS NULL/NOT NULL`) não é suportado pelo construtor `UniqueConstraint` do SQLAlchemy.
- **Expression index** (`COALESCE(...)`) também não. Exige DDL direto.
- PG nativo suporta ambos — solução limpa.

### 1.8 Por que `downgrade()` levanta `NotImplementedError`

- Step 14 cria seed referenciado por steps 17/18 (via FK `NOT NULL`).
- Rollback isolado deixaria ambientes intermediários com FKs órfãs.
- Reversão real = restore de backup (regra do projeto para steps destrutivos-por-cascata).

### 1.9 Por que incluir `casas_decimais`

- **Fonte única de verdade** para precisão de apresentação. Sem isso, cada tela do frontend hardcoda formatação — gera drift (SC60 com 2 casas numa tela, 3 noutra).
- Alinha com regra do `CLAUDE.md`: *"Formatação de Campos sempre usar máscaras"*.
- Separação clara: cálculo usa `NUMERIC(18,9)`, apresentação usa `casas_decimais` (0–9).
- CHECK `BETWEEN 0 AND 9` evita valores absurdos.

### 1.10 Por que incluir `eh_canonica` explícita

- **Queries legíveis:** `WHERE eh_canonica = true` vs `WHERE codigo = codigo_canonico AND fator_canonico = 1`.
- **Constraint de unicidade:** sem a flag, não há como garantir no banco que existe apenas 1 canônica por dimensão. Partial unique `WHERE eh_canonica = true` resolve.
- **CHECK de coerência:** `(eh_canonica = false) OR (codigo = codigo_canonico AND fator_canonico = 1)` força que a flag só seja `true` quando os dados são de fato canônicos — elimina o risco de drift entre flag e valores.
- **Seed determinístico:** 7 canônicas (`KG, L, HA, HR_MAQ, HR_HOMEM, UN, BRL`) marcadas explicitamente; nunca mais dependemos de inspeção dos dados.

---

## 2. Riscos da migration

| # | Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|---|
| R1 | Collision de nome `unidades_medida` com tabela existente | Baixa (verificado; não existe) | Alto | Grep pré-deploy |
| R2 | `gen_random_uuid()` indisponível em PG < 13 | Baixa (prod é PG 14+) | Médio | Smoke test `SELECT gen_random_uuid()` antes |
| R3 | Seed duplicado ao rodar migration 2x | Zero | — | `ON CONFLICT DO NOTHING` idempotente |
| R4 | `uuid_nil()` não existe nativamente em PG | **Médio** | Médio | Substituído por literal `'00000000-0000-0000-0000-000000000000'::uuid` no DDL (já feito) |
| R5 | Migration silenciosa por bug Alembic+asyncpg (conhecido) | Baixa (sem `run_sync` custom) | Alto | Usar fluxo padrão `op.*`; validar pós-upgrade com `SELECT COUNT(*) FROM unidades_medida WHERE sistema=true` = 14 |
| R6 | `cadastros_commodities` não existir (FK destino) | Zero (verificado; existe) | Alto | Se faltar, migration falha explicitamente |
| R7 | Tenant multi-schema não aplicado | N/A | — | Projeto usa single-schema com `tenant_id` coluna; não afeta |
| R8 | Concorrência: migration rodando + app inserindo | Baixa | Baixo | DDL em PG é transacional; inserts após COMMIT veem o schema |
| R9 | Tamanho dos dados seed afeta tempo | Zero | — | 14 linhas; <10ms |
| R10 | FK `commodity_id` quebra em tenant sem commodities cadastradas | Zero | — | FK é nullable; SET NULL em cascade |

**Principais mitigações pré-deploy:**
- Rodar `pg_dump --schema-only` antes para baseline.
- `alembic upgrade step14_uom --sql > step14.sql` para review manual do DDL gerado.
- Aplicar em staging + validar seed count antes de produção.

---

## 3. Plano de testes

### 3.1 Testes automatizados obrigatórios

**Arquivo:** `services/api/tests/migrations/test_step14_unidades_medida.py`

| # | Teste | Valida |
|---|---|---|
| T1 | `test_tabela_unidades_medida_existe` | Tabela criada |
| T2 | `test_tabela_unidades_medida_conversoes_existe` | Tabela criada |
| T3 | `test_seed_sistema_14_unidades` | `SELECT COUNT(*) FROM unidades_medida WHERE sistema=true AND tenant_id IS NULL` = 14 |
| T4 | `test_seed_codigos_canonicos` | KG, L, HA, BRL, HR_MAQ, HR_HOMEM, UN presentes como canônicos |
| T5 | `test_partial_unique_codigo_global` | INSERT duplicado de (NULL, 'KG') falha com IntegrityError |
| T6 | `test_partial_unique_codigo_tenant` | INSERT duplicado de (tenant_A, 'CUSTOM') falha; INSERT (tenant_A, 'CUSTOM') + (tenant_B, 'CUSTOM') passam |
| T7 | `test_tenant_pode_redefinir_codigo_global` | Tenant pode criar `KG` próprio (tenant_id preenchido) sem colidir com global |
| T8 | `test_check_fator_canonico_positivo` | INSERT com `fator_canonico = 0` ou negativo falha |
| T9 | `test_check_dimensao_valida` | INSERT com `dimensao = 'inválido'` falha |
| T10 | `test_check_conversao_unidades_distintas` | INSERT com `unidade_origem_id = unidade_destino_id` falha |
| T11 | `test_unique_conversao_escopo_com_nulls` | Duas conversões iguais (mesmo tenant=NULL, mesma origem/destino, cultura=NULL) segunda falha |
| T12 | `test_fk_tenant_cascade` | DELETE tenant → unidades do tenant removidas; globais intactas |
| T13 | `test_fk_origem_destino_restrict` | DELETE de `unidades_medida` com conversão existente falha |
| T14 | `test_seed_idempotente` | Rodar migration 2x consecutivas não duplica linhas |
| T15 | `test_partial_unique_canonica_global` | INSERT de 2ª unidade `eh_canonica=true` na mesma dimensão (tenant_id=NULL) falha com IntegrityError; por tenant idem |
| T16 | `test_check_canonica_coerencia` | INSERT com `eh_canonica=true` mas `codigo<>codigo_canonico` ou `fator_canonico<>1` falha CHECK; UPDATE que quebre a coerência idem |
| T17 | `test_check_casas_decimais_range` | INSERT com `casas_decimais=10` ou `-1` falha |
| T18 | `test_seed_canonicas_presentes` | Todas as 7 canônicas (`KG, L, HA, HR_MAQ, HR_HOMEM, UN, BRL`) têm `eh_canonica=true` e exatamente 1 por dimensão |

### 3.2 Checks manuais em staging

```sql
-- 1. Contar seed
SELECT COUNT(*) FROM unidades_medida WHERE sistema = true;
-- Esperado: 14

-- 2. Listar por dimensão
SELECT dimensao, COUNT(*), array_agg(codigo ORDER BY codigo)
FROM unidades_medida WHERE sistema = true GROUP BY dimensao;

-- 3. Validar canônicos (agora via flag explícita)
SELECT dimensao, codigo, casas_decimais
  FROM unidades_medida
 WHERE sistema = true AND eh_canonica = true
 ORDER BY dimensao;
-- Esperado: 7 linhas, 1 por dimensão (KG, L, HA, HR_MAQ, HR_HOMEM, UN, BRL)

-- 3b. Validar unicidade da canônica
SELECT dimensao, COUNT(*)
  FROM unidades_medida
 WHERE sistema = true AND eh_canonica = true AND tenant_id IS NULL
 GROUP BY dimensao HAVING COUNT(*) > 1;
-- Esperado: 0 linhas

-- 4. Testar partial unique em tenant
-- (Em psql com tenant de teste)
INSERT INTO unidades_medida (id, tenant_id, codigo, nome, dimensao, codigo_canonico, fator_canonico)
VALUES (gen_random_uuid(), :tenant_id, 'KG', 'Kilograma customizado', 'massa', 'KG', 1);
-- Esperado: sucesso (não colide com global)

-- 5. Testar CHECK
INSERT INTO unidades_medida (id, tenant_id, codigo, nome, dimensao, codigo_canonico, fator_canonico)
VALUES (gen_random_uuid(), NULL, 'TEST', 'Teste', 'inexistente', 'KG', 1);
-- Esperado: erro de CHECK
```

### 3.3 Smoke test pós-deploy (produção)

Script em `services/api/scripts/smoke_step14.py` (a criar no próximo ciclo):
1. Contar seed = 14.
2. Verificar que toda dimensão tem pelo menos 1 unidade canônica.
3. Verificar que nenhuma conversão existe (tabela vazia é esperada).

---

## 4. Plano de rollout

### 4.1 Ambientes

| Ambiente | Janela | Responsável | Validação |
|---|---|---|---|
| **Dev local** | Imediato | Dev | `alembic upgrade head` + pytest suite |
| **Staging** | D+1 após merge | DevOps | Smoke test + checks manuais §3.2 |
| **Produção** | D+7 após staging verde | DevOps | Smoke test + monitoramento 24h |

### 4.2 Procedimento de deploy

1. **Pré-deploy (staging e prod):**
   - `pg_dump --schema-only > backup_pre_step14.sql`
   - `alembic current` para confirmar head atual `0808ec16ef17`.
   - `alembic upgrade step14_uom --sql > step14_review.sql` — review do DDL.
2. **Deploy:**
   - `alembic upgrade step14_uom` (ou `alembic upgrade head` se step14 é o head).
3. **Pós-deploy:**
   - Rodar §3.2 (checks manuais).
   - Monitorar logs por 15 min.
   - Verificar `alembic current` = `step14_uom`.
4. **Crítico:** **NÃO avançar para step15** sem revisão e aprovação.

### 4.3 Comunicação

- Slack #ops — aviso pré-deploy e pós-deploy.
- Changelog interno atualizado: "Step 14 — Measurement Engine (14 unidades de sistema)".

---

## 5. Plano de rollback

### 5.1 Janela e triggers de rollback

**Rollback imediato** se qualquer cenário abaixo ocorrer:
- Migration falha no meio (transação aborta naturalmente — PG atomicidade).
- Seed count ≠ 14 pós-upgrade.
- CHECK constraints ausentes (verificar via `\d unidades_medida`).
- Queries de dashboard existentes começam a falhar (improvável — nenhuma referência).

### 5.2 Procedimento de rollback

#### Opção A — DDL manual (rollback cirúrgico)

Válido **somente** se nenhum step subsequente (15+) foi aplicado e nenhuma aplicação começou a escrever em `unidades_medida`:

```sql
BEGIN;

DROP INDEX IF EXISTS uq_unidades_medida_conversoes_escopo;
DROP INDEX IF EXISTS ix_unidades_medida_conversoes_cultura;
DROP INDEX IF EXISTS ix_unidades_medida_conversoes_origem_destino;
DROP TABLE IF EXISTS unidades_medida_conversoes;

DROP INDEX IF EXISTS uq_unidades_medida_codigo_tenant;
DROP INDEX IF EXISTS uq_unidades_medida_codigo_global;
DROP INDEX IF EXISTS ix_unidades_medida_tenant_ativo;
DROP INDEX IF EXISTS ix_unidades_medida_dimensao;
DROP TABLE IF EXISTS unidades_medida;

-- Marcar migration como não-aplicada
DELETE FROM alembic_version WHERE version_num = 'step14_uom';

COMMIT;
```

Justificativa de não implementar `downgrade()` Alembic automático: é o mesmo DDL acima, mas ferramenta automática não sabe se steps subsequentes já existem — risco de perda silenciosa.

#### Opção B — Restore de backup (recomendado para produção)

```bash
# Parar aplicação
systemctl stop api
# Restore do dump schema-only
psql -U ... -d ... < backup_pre_step14.sql
# Reiniciar
systemctl start api
```

### 5.3 Critérios de sucesso do rollback

- `alembic current` = `0808ec16ef17` (head anterior).
- Tabelas `unidades_medida` e `unidades_medida_conversoes` não existem.
- Aplicação inicia sem erros.
- Nenhum dado de tenant perdido (estas tabelas só contêm seed de sistema e customizações novas — irrelevantes pré-step14).

### 5.4 Pós-rollback

- Abrir incident report.
- Identificar causa-raiz antes de nova tentativa.
- Atualizar §2 deste documento com o novo risco descoberto.

---

## 6. Checklist de aprovação

- [x] DDL gerado em `step14_unidades_medida.py`
- [x] Down revision aponta para head atual (`0808ec16ef17`)
- [x] Partial unique indexes usando PG nativo
- [x] Seed idempotente com `ON CONFLICT DO NOTHING`
- [x] Check constraints de `fator_canonico > 0`, `dimensao IN (...)`, `unidades distintas`
- [x] FKs nomeadas explicitamente (`fk_*_*`)
- [x] Índices nomeados explicitamente (`ix_*_*`)
- [x] `downgrade()` explicitamente não-implementado com razão
- [ ] Código revisado por outro dev
- [ ] Testes §3.1 implementados e passando em CI
- [ ] Aplicado em staging com §3.2 verde
- [ ] Smoke test §3.3 criado
- [ ] Aprovação para produção
- [ ] **Aprovação para iniciar step15**

---

## 7. Roadmap futuro (não bloqueante)

- **`dimensao` como VARCHAR + CHECK vs enum/catálogo de domínio:** avaliar no futuro se a coluna deve evoluir para uma tabela-catálogo `unidades_medida_dimensoes(codigo, nome, unidade_canonica_id)` ou um `ENUM` nativo PG. Hoje CHECK declarativo é suficiente — revisar quando houver demanda de i18n, metadados adicionais por dimensão (ex: descrição UI, ordenação), ou customização por tenant. Não impacta Step 14 nem steps 15–20. Registrar como débito técnico.

## 8. Referências

- Schema diff: `docs/agro/treinamento/schema-diff-production-unit.md` §STEP 14
- Nomenclatura: `docs/agro/treinamento/naming-convention-schema-diff.md`
- Doc mestre: `docs/agro/treinamento/context-implementacao-evoluiva-operacional.md`
- Bug conhecido Alembic+asyncpg: `memory/feedback_alembic_async.md`
