# Brainstorm — Evolução do Módulo Análise de Solo

**Data:** 2026-04-19  
**Status:** Aprovado para implementação

---

## Problema

O módulo de análise de solo atual mistura as 3 camadas definidas no `context-analise-solo.md`:
- Seletor de cultura hardcoded `["SOJA", "MILHO", "TRIGO"]`
- Faixas de interpretação (P, K, pH) únicas e hardcoded no service
- Nitrogênio só diferencia SOJA vs "outros"
- Sem variação regional
- Sem customização por tenant

---

## Solução Definitiva

### Camada 1 — dados brutos (já existe, não muda)
Tabela `analises_solo` com todos os parâmetros laboratoriais. Cálculo automático de CTC e V% no `criar()`.

### Camada 2 — parâmetros de interpretação (nova tabela)
**`solo_parametros_cultura`** — faixas por cultura/região/tenant:

| Campo | Tipo | Descrição |
|---|---|---|
| id | UUID PK | |
| cultura_id | FK cadastros_culturas | |
| tenant_id | UUID nullable | NULL = sistema |
| regiao | String nullable | CERRADO, SUL, NORDESTE, etc. |
| parametro | String | FOSFORO, POTASSIO, PH, NITROGENIO, CALAGEM |
| faixa_min | Numeric(8,2) | |
| faixa_max | Numeric(8,2) | nullable = sem limite superior |
| classificacao | String | MUITO_BAIXO, BAIXO, MEDIO, ALTO |
| rec_dose_kg_ha | Numeric(8,2) | dose recomendada para esta faixa |
| obs | Text | texto técnico agronômico |

### Camada 3 — recomendação (service refatorado)
`gerar_recomendacoes()` faz lookup hierárquico:
1. tenant_id=X + cultura_id + regiao
2. tenant_id=X + cultura_id
3. tenant_id=NULL + cultura_id + regiao
4. tenant_id=NULL + cultura_id
5. fallback hardcoded Embrapa (nunca quebra)

---

## Impacto

### Backend
- `core/cadastros/produtos/models.py` — adicionar `v_meta_pct_padrao` em `ProdutoCultura`
- Nova tabela `solo_parametros_cultura` + model + service + router
- `analises_solo/service.py` — refatorar `gerar_recomendacoes()` para lookup dinâmico
- `analises_solo/router.py` — endpoint `GET /analises-solo/culturas-disponiveis`
- `scripts/seed_parametros_solo.py` — seed das faixas Embrapa para culturas do sistema
- Migration Alembic

### Frontend
- `analises-client.tsx` — seletor dinâmico de culturas via API
- `cadastros/culturas` — aba "Parâmetros de Solo" para gestão das faixas

---

## Regras de negócio
- Culturas com `sistema=True` não são editáveis pelo tenant
- Tenant pode criar seus próprios parâmetros por cultura E região
- Parâmetros do tenant sobrescrevem sistema (nunca deletam)
- `v_meta` exibido no laudo vem da cultura selecionada (`v_meta_pct_padrao`)
