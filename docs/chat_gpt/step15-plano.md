# Step 15 — Plano de Execução

**Arquivo da migration:** `services/api/migrations/versions/step15_production_units.py`
**Revision ID:** `step15_pu`
**Down revision:** `step14_uom`
**Data:** 2026-04-24
**Pré-requisito:** Step 14 deployado (staging verde) — tabelas `unidades_medida*` disponíveis.

---

## 1. Justificativa das decisões

> **Nota:** decisões conceituais foram aprovadas em `step15-desenho-conceitual.md`. Esta seção explica as decisões de **implementação** do DDL.

### 1.1 Função PL/pgSQL em vez de SQL puro nas triggers

- Lógica envolve condicional de `TG_OP` e cálculo de status derivado com 4 ramos.
- PL/pgSQL permite `RAISE EXCEPTION` com mensagem contextual e `USING ERRCODE` para clientes detectarem violação.
- SQL puro forçaria split em múltiplas funções; PL/pgSQL é canônico para triggers de negócio.

### 1.2 Por que trigger de validação usa `NEW.tenant_id/safra_id/area_id`

- Para `CONSTRAINT TRIGGER DEFERRED`, o trigger dispara uma vez por linha afetada, ao COMMIT.
- Na hora do disparo, a tabela já contém o estado final — `SELECT SUM(...)` vê todas as linhas, inclusive NEW.
- Por isso a função filtra por `(tenant_id, safra_id, area_id)` de NEW e soma a tabela inteira. Não precisa excluir NEW.

### 1.3 Por que trigger de refresh é **não** deferred

- Refresh do read model deve ser visível imediatamente para a query subsequente na mesma transação (ex: service que cria PU e depois consulta `status_consorcio_area` no mesmo endpoint).
- DEFERRED atrasaria o refresh até o COMMIT — poderia devolver status stale.
- Validação é DEFERRED porque só importa no fim; refresh é imediato porque consulta imediata é comum.

### 1.4 Por que refresh do read model re-visita OLD em UPDATE que muda chaves

- Se `(tenant, safra, area)` de uma PU mudar (não deveria, mas é possível), a área antiga fica "fantasma" com status stale.
- Função defensivamente recomputa OLD se distinto de NEW.
- CHECK declarativo em PG não consegue capturar "campos imutáveis" sem trigger BEFORE. Optamos por tolerar a mudança e apenas recomputar ambos lados.

### 1.5 Por que `ON CONFLICT ... DO NOTHING` usa cláusula `WHERE`

- Partial unique exige que `ON CONFLICT (cols) WHERE <pred>` case com o predicado do índice.
- No backfill, toda linha inserida tem `status='ATIVA'` → satisfaz `WHERE status <> 'CANCELADA'`.
- Re-execução da migration não duplica: conflito detectado → ignora.

### 1.6 Por que DISABLE TRIGGER durante backfill

- Backfill insere N linhas; sem DISABLE, cada INSERT dispara:
  - Validação de soma (leitura) — custo agregado O(N²) no pior caso.
  - Refresh do read model — N UPSERTs no `status_consorcio_area`.
- Ordem: DISABLE → bulk INSERT → rebuild manual de `status_consorcio_area` → ENABLE.
- Rebuild manual ao final é idempotente e equivalente ao trigger rodando linha a linha.

### 1.7 Por que janela `SUM(area_ha) OVER (PARTITION BY safra_id, area_id)`

- Para consórcio, precisamos distribuir percentual entre cultivos que compartilham `(safra, area)`.
- Window function no `SELECT` entrega o denominador por grupo sem self-join.
- `ROUND(..., 2)` garante que percentuais caibam em `NUMERIC(5,2)`. Pequenos arredondamentos são absorvidos pela tolerância ±0,01 do status.

### 1.8 Por que `downgrade()` levanta `NotImplementedError`

- Steps 16–19 adicionarão FKs `production_unit_id` em tabelas legadas.
- Rollback isolado do step15 deixaria FKs apontando para tabela removida.
- Reversão real = restore de backup. Mesma política do step14.
- Procedimento cirúrgico (sem steps posteriores aplicados) documentado em §5.2.

### 1.9 Por que `percentual_participacao > 0` (estrito) e não `>= 0`

- PU com participação zero não faz sentido operacional — se cultivo não está na área, não cria a PU.
- Cancelamento = `status='CANCELADA'`, não `percentual=0`.
- Evita ambiguidade (linha fantasma com percentual 0 contando para `qtd_unidades`).

### 1.10 Por que `status_consorcio_area` tem PK `id` separada da chave natural

- `(tenant_id, safra_id, area_id)` é unique (chave natural), mas PK UUID mantém coerência com demais tabelas do projeto.
- `ON CONFLICT (tenant_id, safra_id, area_id) DO UPDATE` funciona via UNIQUE — não precisa de PK composta.
- Facilita referências futuras (debug, logs), embora nenhuma FK aponte para esta tabela.

---

## 2. Riscos da migration

| # | Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|---|
| R1 | Backfill gera soma > 100 por arredondamento em consórcio | Média | Médio | Tolerância ±0,01 no trigger; status `INCONSISTENTE` emerge naturalmente se drift > 0,01 |
| R2 | `cultivo_areas` com `area_ha = 0` ou NULL (dados inconsistentes) | Baixa | Médio | CHECK `area_ha > 0` em production_units bloqueia; migration falha explicitamente se encontrar — identificar em staging |
| R3 | Cultivos órfãos (cultivo_id sem safra válida) | Zero | Alto | FK já existe em `cultivos.safra_id`; JOIN no backfill não traz órfãos |
| R4 | Performance do backfill em tenant grande (>10k cultivo_areas) | Baixa | Médio | DISABLE TRIGGER garante O(N) inserts + 1 rebuild O(N log N) |
| R5 | `CONSTRAINT TRIGGER DEFERRED` não disponível (PG < 9.0) | Zero | — | Prod é PG 14+ |
| R6 | Advisory lock colide com outra função do sistema | Zero | — | Hash `'pu_area:...'` é prefixado; colisão estatística desprezível |
| R7 | Trigger de refresh gera deadlock sob alta concorrência | Baixa | Médio | Advisory lock serializa por `(safra, area)` antes do INSERT — refresh roda em sessão já exclusiva |
| R8 | Backfill re-executado após novas PUs criadas manualmente | Baixa | Alto | `ON CONFLICT DO NOTHING` protege. Partial unique garante: se PU ativa/encerrada existe, nova não é criada |
| R9 | DISABLE TRIGGER + crash da migration deixa triggers off | Baixa | Alto | Migration é transacional em PG — rollback automático reabilita. Verificar `pg_trigger.tgenabled` pós-upgrade |
| R10 | `gen_random_uuid()` conflita (colisão astronômica) | Zero | — | UUID v4 |
| R11 | `cultivos.consorciado` column não existe ainda | Zero | — | Migration `step5_add_consorciado_to_cultivos.py` já aplicada |
| R12 | Bug Alembic+asyncpg com ROLLBACK silencioso | Baixa | Alto | Migration usa apenas `op.create_table`/`op.execute` sem `run_sync` — não dispara o bug. Validar `SELECT COUNT(*) FROM production_units` pós-upgrade |

**Principais mitigações pré-deploy:**
- `alembic upgrade step15_pu --sql > step15_review.sql` para review manual.
- Staging: verificar count `production_units` = count esperado de `cultivo_areas`.
- Staging: verificar ausência de linhas em `status_consorcio_area` com status `INCONSISTENTE` após backfill (salvo se dados legados realmente inconsistentes — investigar caso a caso).
- Validar triggers ativos: `SELECT tgname, tgenabled FROM pg_trigger WHERE tgrelid = 'production_units'::regclass` — todos devem ter `tgenabled = 'O'` (enabled).

---

## 3. Plano de testes

### 3.1 Testes automatizados obrigatórios

**Arquivo:** `services/api/tests/migrations/test_step15_production_units.py`

**Bloco A — Estrutura**
| # | Teste | Valida |
|---|---|---|
| T1 | `test_tabelas_criadas` | `production_units` e `status_consorcio_area` existem |
| T2 | `test_partial_unique_ativa` | INSERT duplicado com `status='ATIVA'` falha; INSERT após `status='CANCELADA'` do anterior passa |
| T3 | `test_fks_cascade_e_set_null` | DELETE tenant/safra/cultivo/area → PU removida; DELETE cultivo_area → `cultivo_area_id=NULL` |
| T4 | `test_checks_basicos` | `percentual=0`, `percentual=101`, `area_ha=0`, `status='X'`, `data_fim<data_inicio` todos falham |

**Bloco B — CONSTRAINT TRIGGER DEFERRED**
| # | Teste | Valida |
|---|---|---|
| T5 | `test_deferred_permite_intermediario_invalido` | INSERT 60 + INSERT 50 + UPDATE 50→40 numa transação → COMMIT sucesso (soma final 100) |
| T6 | `test_deferred_rejeita_no_commit` | INSERT 60 + INSERT 50 sem correção → COMMIT falha com `check_violation`, transação inteira aborta |
| T7 | `test_deferred_separa_areas` | Transação com inserts em 2 áreas distintas; erro numa não afeta validação da outra (mas aborta tudo — teste observa mensagem correta) |
| T8 | `test_cancelada_nao_conta_na_soma` | PU 70 + PU 50 com `status='CANCELADA'` → soma válida = 70 |

**Bloco C — Trigger de refresh (read model)**
| # | Teste | Valida |
|---|---|---|
| T9 | `test_refresh_cria_linha_no_primeiro_insert` | Antes: nenhuma linha em `status_consorcio_area`; após INSERT em PU → 1 linha com `soma_participacao`, `qtd_unidades=1`, `status` correto |
| T10 | `test_refresh_atualiza_em_update` | UPDATE de `percentual_participacao` → `status_consorcio_area` refletido imediatamente |
| T11 | `test_refresh_em_delete_atualiza_soma` | DELETE de PU → soma recalculada, `qtd_unidades` decrementada |
| T12 | `test_status_vazio_incompleto_valido_inconsistente` | Cenários: 0 PUs → VAZIO; soma 50 → INCOMPLETO; soma 100 → VALIDO; forçar soma 110 (via DISABLE + INSERT) → INCONSISTENTE |
| T13 | `test_refresh_tolerancia_99_99_100_01` | Soma 99,99 → VALIDO; 100,01 → VALIDO; 99,98 → INCOMPLETO; 100,02 → INCONSISTENTE |
| T14 | `test_refresh_handles_old_area_on_key_change` | UPDATE que muda `area_id` de PU → status antigo e novo recomputados |

**Bloco D — Backfill**
| # | Teste | Valida |
|---|---|---|
| T15 | `test_backfill_cultivo_solo` | Fixture com 1 `cultivo_areas` não-consorciado → PU com `percentual=100`, `area_ha` igual |
| T16 | `test_backfill_consorcio_dois_cultivos` | 2 `cultivo_areas` consorciados em mesma `(safra, area)` com areas 5 e 5 → 2 PUs com `percentual=50` cada |
| T17 | `test_backfill_consorcio_proporcional` | 2 cultivos com areas 7 e 3 → percentuais 70 e 30 |
| T18 | `test_backfill_idempotente` | Rodar migration 2x → count de PUs igual ao inicial |
| T19 | `test_backfill_rebuilda_status_consorcio_area` | Após backfill, existe linha em `status_consorcio_area` por `(tenant, safra, area)` presente |
| T20 | `test_backfill_cultivo_area_id_preenchido` | PUs geradas têm `cultivo_area_id` apontando para linha correta de `cultivo_areas` |

**Bloco E — Gate seletivo (integração com service)**
| # | Teste | Valida |
|---|---|---|
| T21 | `test_service_rejeita_mutacao_em_area_inconsistente` | Forçar `status='INCONSISTENTE'` via DISABLE; service `criar()` em mesma (safra, area) → `BusinessRuleError` |
| T22 | `test_service_avancar_fase_encerrada_exige_valido` | Safra com área `INCOMPLETO`; `SafraService.avancar_fase(ENCERRADA)` → rejeitado com lista de áreas |
| T23 | `test_service_avancar_fase_encerrada_aceita_todas_valido` | Todas áreas VALIDO → avanço permitido |

**Bloco F — Concorrência (advisory lock)**
| # | Teste | Valida |
|---|---|---|
| T24 | `test_advisory_lock_serializa_mesma_area` | 2 sessões async tentando criar PU em mesma (safra, area) com soma que no total > 100 — só 1 sucede |
| T25 | `test_advisory_lock_nao_bloqueia_areas_distintas` | 2 sessões em áreas diferentes commitam em paralelo |

### 3.2 Checks manuais em staging

```sql
-- 1. Contagem pós-backfill
SELECT
  (SELECT COUNT(*) FROM cultivo_areas) AS cultivo_areas_count,
  (SELECT COUNT(*) FROM production_units) AS pu_count,
  (SELECT COUNT(*) FROM status_consorcio_area) AS scs_count;
-- Esperado: pu_count = cultivo_areas_count
--           scs_count = COUNT(DISTINCT (safra_id, area_id)) de cultivo_areas

-- 2. Status distribution
SELECT status, COUNT(*) FROM status_consorcio_area GROUP BY status ORDER BY status;
-- Esperado: majoritariamente VALIDO; INCONSISTENTE = 0

-- 3. Consórcios detectados
SELECT tenant_id, safra_id, area_id, qtd_unidades, soma_participacao, status
  FROM status_consorcio_area
 WHERE qtd_unidades > 1
 ORDER BY qtd_unidades DESC
 LIMIT 20;
-- Revisar casos manualmente

-- 4. Triggers ativos
SELECT tgname, tgenabled, tgdeferrable, tginitdeferred
  FROM pg_trigger
 WHERE tgrelid = 'production_units'::regclass
   AND NOT tgisinternal;
-- Esperado: tg_production_units_valida_soma (O, true, true)
--           tg_production_units_refresh_status (O, false, false)

-- 5. PUs com cultivo_area_id NULL (não deveria haver após backfill)
SELECT COUNT(*) FROM production_units WHERE cultivo_area_id IS NULL;
-- Esperado: 0 no backfill; depois pode aumentar (criação manual via API)

-- 6. Divergência area_ha vs AreaRural (read-only — informativo)
SELECT pu.id, pu.area_ha AS pu_area, ar.area_ha AS ar_area,
       ABS(pu.area_ha - ar.area_ha * pu.percentual_participacao / 100) AS divergencia
  FROM production_units pu
  JOIN cadastros_areas_rurais ar ON ar.id = pu.area_id
 WHERE ABS(pu.area_ha - ar.area_ha * pu.percentual_participacao / 100) > 0.1
 LIMIT 20;
-- Esperado: 0 linhas logo após backfill; pode aumentar se AreaRural for corrigida depois
```

### 3.3 Smoke test pós-deploy (produção)

Script `services/api/scripts/smoke_step15.py`:
1. Assert `COUNT(production_units) = COUNT(cultivo_areas)`.
2. Assert ausência de `status='INCONSISTENTE'` em `status_consorcio_area`.
3. Assert 2 triggers ativos em `production_units`.
4. Assert function `fn_production_units_valida_soma` e `fn_production_units_refresh_status` existem e são owned pela role da app.

---

## 4. Plano de rollout

### 4.1 Ambientes e janelas

| Ambiente | Janela | Responsável | Validação |
|---|---|---|---|
| Dev local | Imediato | Dev | `alembic upgrade head` + `pytest tests/migrations/test_step15_production_units.py` |
| Staging | D+1 após merge | DevOps | Smoke test + checks §3.2 + teste de carga backfill (importar snapshot de prod) |
| Produção | D+7 após staging verde | DevOps | Smoke test + monitoramento 48h |

### 4.2 Procedimento de deploy

1. **Pré-deploy:**
   - `pg_dump --schema-only > backup_pre_step15.sql`
   - `pg_dump --table=cultivo_areas --table=cultivos --data-only > backup_fontes_step15.sql` (dados que backfill consome — facilita análise forense se houver problema).
   - `alembic current` → confirmar `step14_uom`.
   - `alembic upgrade step15_pu --sql > step15_review.sql` → review.
2. **Deploy:**
   - `alembic upgrade step15_pu`
   - Monitorar tempo de execução (esperado < 30s para tenant típico).
3. **Pós-deploy:**
   - Rodar §3.2 (todos os 6 checks).
   - Rodar smoke test §3.3.
   - Monitorar logs por 30 min.
   - Verificar `alembic current = step15_pu`.
4. **Gate:** **NÃO avançar para step16** sem aprovação explícita.

### 4.3 Comunicação

- Slack #ops — pré-deploy e pós-deploy.
- Changelog interno: "Step 15 — ProductionUnit + status_consorcio_area (centro de custo canônico agrícola)".

---

## 5. Plano de rollback

### 5.1 Triggers de rollback

Rollback imediato se:
- Backfill produz linhas com `status='INCONSISTENTE'` não explicáveis por dados legados conhecidos.
- Count de `production_units` ≠ `cultivo_areas`.
- Triggers não ativos pós-upgrade (um ficou `DISABLE`).
- Qualquer teste §3.1 falhar.
- Aplicação começa a falhar ao acessar safras existentes.

### 5.2 Procedimento cirúrgico (sem step16+ aplicado)

**Apenas se nenhum step posterior foi aplicado e nenhuma escrita direta em production_units ocorreu fora do backfill:**

```sql
BEGIN;

-- 1. Drop triggers
DROP TRIGGER IF EXISTS tg_production_units_refresh_status ON production_units;
DROP TRIGGER IF EXISTS tg_production_units_valida_soma ON production_units;

-- 2. Drop functions
DROP FUNCTION IF EXISTS fn_production_units_refresh_status();
DROP FUNCTION IF EXISTS fn_production_units_valida_soma();

-- 3. Drop status_consorcio_area
DROP INDEX IF EXISTS ix_status_consorcio_area_tenant_status;
DROP TABLE IF EXISTS status_consorcio_area;

-- 4. Drop production_units
DROP INDEX IF EXISTS ix_production_units_cultivo_area;
DROP INDEX IF EXISTS uq_production_units_ativa;
DROP INDEX IF EXISTS ix_production_units_tenant_status;
DROP INDEX IF EXISTS ix_production_units_tenant_area;
DROP INDEX IF EXISTS ix_production_units_tenant_cultivo;
DROP INDEX IF EXISTS ix_production_units_tenant_safra;
DROP TABLE IF EXISTS production_units;

-- 5. Marcar como não-aplicada
DELETE FROM alembic_version WHERE version_num = 'step15_pu';

COMMIT;
```

### 5.3 Procedimento recomendado (produção)

**Restore de backup:**
```bash
systemctl stop api
psql -U ... -d ... < backup_pre_step15.sql
systemctl start api
```

### 5.4 Critérios de sucesso do rollback

- `alembic current = step14_uom`.
- Tabelas `production_units` e `status_consorcio_area` não existem.
- Funções `fn_production_units_*` não existem.
- `cultivo_areas` intacta (backfill não modifica origem — apenas lê).
- Aplicação sobe sem erros.

### 5.5 Pós-rollback

- Incident report.
- Causa-raiz identificada antes de nova tentativa.
- §2 atualizada com novo risco descoberto.

---

## 6. Checklist de aprovação

- [x] DDL gerado com 2 tabelas, 2 functions, 2 triggers, backfill idempotente
- [x] `production_units` mantida em inglês (exceção documentada)
- [x] Partial unique `WHERE status <> 'CANCELADA'`
- [x] `CONSTRAINT TRIGGER DEFERRABLE INITIALLY DEFERRED` para validação de soma
- [x] Trigger AFTER não-deferred para refresh imediato do read model
- [x] Backfill com DISABLE/ENABLE TRIGGER + rebuild manual do read model
- [x] `ON CONFLICT DO NOTHING` com cláusula WHERE casando partial unique
- [x] FKs nomeadas explicitamente
- [x] `downgrade()` não-implementado com justificativa
- [ ] Código revisado por outro dev
- [ ] 25 testes §3.1 implementados e passando em CI
- [ ] Aplicado em staging com §3.2 verde
- [ ] Smoke test §3.3 criado
- [ ] Aprovação para produção
- [ ] **Aprovação para iniciar step16 (FK `production_unit_id` em tabelas legadas)**

---

## 7. Roadmap futuro (não bloqueante)

- **Trigger de imutabilidade de chaves:** hoje o refresh defende contra mudança de `(tenant, safra, area)`; poderíamos adicionar `BEFORE UPDATE` trigger explícito rejeitando mutação dessas colunas. Ganho: mensagem de erro mais clara. Custo: mais uma função trigger.
- **View `v_production_units_divergencia_area`:** listar PUs cujo `area_ha` diverge de `AreaRural.area_ha × percentual/100` acima da tolerância. Ferramenta de reconciliação para quando AreaRural é corrigida pós-safra.
- **Trigger IMMUTABLE de `production_unit.cultivo_area_id`:** hoje é nullable e pode ser desassociado; poderíamos rejeitar mutação após set inicial. Adiar até caso de uso concreto aparecer.

---

## 8. Referências

- Desenho conceitual: `docs/agro/treinamento/step15-desenho-conceitual.md`
- Análise de concorrência: `docs/agro/treinamento/analise-concorrencia-participation-percent.md`
- Schema diff: `docs/agro/treinamento/schema-diff-production-unit.md §STEP 15`
- Nomenclatura: `docs/agro/treinamento/naming-convention-schema-diff.md`
- Step 14 (dependência): `docs/agro/treinamento/step14-plano.md`
