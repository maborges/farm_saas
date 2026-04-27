# Contexto — Step 30: Validação e Priorização dos Gaps de Monetização Agrícola

**Data:** 2026-04-27  
**Status:** DOCUMENTADO  

---

## Objetivo

Validar os gaps identificados na matriz global de monetização agrícola do Step 29 e priorizar a implementação futura dos gates faltantes.

Este step não altera código. O foco é separar:

- gaps confirmados;
- gaps dependentes de decisão comercial/técnica;
- itens que devem permanecer em `A1_PLANEJAMENTO`;
- ordem recomendada de implementação dos gates.

---

## Validação Executada

Arquivos e áreas revisados:

- `services/api/main.py`
- `services/api/agricola/**/router.py`
- `services/api/core/routers/reports.py`
- `apps/web/src/app/(dashboard)/agricola/**`
- `apps/web/src/app/(dashboard)/dashboard/agricola/**`
- `apps/web/src/components/agricola/**`
- `apps/web/src/hooks/use-has-tier.ts`

Ponto importante: vários routers avançados são incluídos diretamente em `main.py` sem dependência no `include_router`, então a ausência de gate no router é gap real, não apenas dúvida documental.

---

## Decisões Mantidas

### A1_PLANEJAMENTO continua operacional

Não priorizar gates adicionais para:

- listar, criar, visualizar e editar safras;
- cultivos e áreas;
- talhões/contexto;
- checklist operacional;
- tarefas operacionais;
- fenologia operacional;
- caderno básico;
- orçamento operacional;
- custos básicos;
- Production Units operacionais;
- listagem e visualização de cenários econômicos;
- recalcular cenário `BASE`.

### PROFISSIONAL concentra inteligência

Priorizar `require_tier(PlanTier.PROFISSIONAL)` para:

- simulações;
- previsões;
- recomendações;
- geração automática de tarefas;
- alertas executivos;
- relatórios analíticos;
- dashboards avançados.

### ENTERPRISE está padronizado

O código usa `PlanTier.ENTERPRISE` como nome canônico do topo da oferta.
`PlanTier.PREMIUM` permanece apenas como alias legado para compatibilidade
com dados já persistidos e integrações antigas.

Enquanto o alias existir, novas gates, UI e documentação devem preferir
`ENTERPRISE` e tratar `PREMIUM` apenas como formato histórico.

---

## Gaps Confirmados

### P0 — Exposição sem gate de módulo/tier

Esses endpoints têm maior risco porque estão incluídos em `main.py` e os routers observados não aplicam `require_module` nem `require_tier`.

| Área | Endpoint base | Arquivo | Gate atual | Tier alvo | Prioridade |
|---|---|---|---|---|---:|
| Templates agrícolas | `/templates/*` | `agricola/templates/router.py` | Autenticação/tenant, sem módulo/tier | PROFISSIONAL para aplicar; ENTERPRISE para governança global | P0 |
| Amostragem de solo | `/amostragem-solo/amostras/*` | `agricola/amostragem_solo/routers/amostras.py` | Tenant, sem módulo/tier | ENTERPRISE | P0 |
| Mapas de fertilidade | `/amostragem-solo/mapas_fertilidade/*` | `agricola/amostragem_solo/routers/mapas_fertilidade.py` | Tenant, sem módulo/tier | ENTERPRISE | P0 |
| Prescrições VRA avançadas | `/amostragem-solo/prescricoes_vra/*` | `agricola/amostragem_solo/routers/prescricoes_vra.py` | Tenant, sem módulo/tier | ENTERPRISE | P0 |
| Agricultura de precisão avançada | `/agricultura-precisao/ndvi/*` | `agricola/ndvi_avancado/routers/ndvi.py` | Tenant, sem módulo/tier | ENTERPRISE | P0 |
| Irrigação avançada | `/agricultura-precisao/irrigacao/*` | `agricola/ndvi_avancado/routers/irrigacao.py` | Tenant, sem módulo/tier | ENTERPRISE | P0 |
| Meteorologia avançada | `/agricultura-precisao/meteorologia/*` | `agricola/ndvi_avancado/routers/meteorologia.py` | Tenant, sem módulo/tier | ENTERPRISE | P0 |

Recomendação P0:

1. Adicionar gate de módulo mínimo imediatamente nos routers avançados.
2. Manter `PREMIUM` apenas como alias de leitura até a migração completa do legado.
3. No frontend, impedir queries desses endpoints para tenants sem o tier/módulo.

---

### P1 — Inteligência hoje liberada em A1

Esses endpoints têm gate de módulo, mas não têm gate de tier. Pela matriz comercial, devem exigir `PROFISSIONAL`.

| Área | Endpoint | Gate atual | Tier alvo | Prioridade |
|---|---|---|---|---:|
| Análise de solo | `GET /analises-solo/{id}/recomendacoes` | `A1_PLANEJAMENTO` | PROFISSIONAL | P1 |
| Análise de solo | `GET /analises-solo/{id}/inteligencia` | `A1_PLANEJAMENTO` | PROFISSIONAL | P1 |
| Análise de solo | `POST /analises-solo/{id}/gerar-tarefas` | `A1_PLANEJAMENTO` | PROFISSIONAL | P1 |
| Previsão | `POST /previsoes/gerar` | `A1_PLANEJAMENTO` | PROFISSIONAL | P1 |
| Previsão | `GET /previsoes` | `A1_PLANEJAMENTO` | PROFISSIONAL | P1 |
| Dashboard agrícola | `POST /agricola/dashboard/verificar-alertas` | `A1_PLANEJAMENTO` | PROFISSIONAL | P1 |
| Relatórios agrícolas | `GET /reports/agricola/summary` | auth apenas | PROFISSIONAL | P1 |
| Relatórios agrícolas | `GET /reports/agricola/talhoes` | auth apenas | PROFISSIONAL | P1 |
| Relatórios agrícolas | `GET /reports/agricola/profitability` | auth apenas | PROFISSIONAL | P1 |

Recomendação P1:

1. Aplicar `require_tier(PlanTier.PROFISSIONAL)` no backend.
2. Manter CRUD básico de análise de solo em A1.
3. Ajustar frontend para não chamar recomendações, inteligência, geração de tarefas, previsões e relatórios premium sem `useHasTier("PROFISSIONAL")`.
4. Adicionar testes de 402 com `X-Tier-Required`.

---

### P2 — Recursos por módulo que precisam de tier adicional

Esses endpoints já usam módulos avançados (`A2_CAMPO`, `A4_PRECISAO`, `A5_COLHEITA`), mas módulo contratado não substitui tier.

| Área | Endpoint/funcionalidade | Gate atual | Tier alvo | Prioridade |
|---|---|---|---|---:|
| Agrônomo IA | `/agronomo/chat`, conversas | `A2_CAMPO` | PROFISSIONAL | P2 |
| RAT | `/agronomo/rat*` | `A2_CAMPO` | PROFISSIONAL ou ENTERPRISE se assinatura/auditoria formal | P2 |
| Monitoramento | `/monitoramentos/diagnosticar-avulso` | `A2_CAMPO` | PROFISSIONAL | P2 |
| NDVI básico | `/ndvi/*` | `A4_PRECISAO` | PROFISSIONAL | P2 |
| Prescrições VRA | `/prescricoes/*` | `A4_PRECISAO` | ENTERPRISE | P2 |
| Beneficiamento | KPIs e relatório de rendimento | `A5_COLHEITA` | PROFISSIONAL | P2 |
| Rastreabilidade | Certificações e cadeia auditável | `A5_COLHEITA` | ENTERPRISE | P2 |
| Caderno | Exportações, download, assinatura | `A1_PLANEJAMENTO` | ENTERPRISE | P2 |

Recomendação P2:

1. Preservar operações CRUD dos módulos como estão.
2. Adicionar tier apenas em inteligência, auditoria, certificação, relatórios e integração.
3. Evitar bloquear registro operacional de campo/colheita.

---

## Itens Que Não Devem Ser Priorizados Para Gate Agora

Manter como A1 ou módulo operacional:

- `GET /safras`
- `GET /safras/{id}`
- `POST /safras`
- `PATCH /safras/{id}`
- `GET /safras/{id}/talhoes`
- `PUT /safras/{id}/talhoes`
- `GET /safras/{id}/production-units`
- CRUD de Production Units
- `GET /safras/{id}/cenarios`
- `GET /safras/{id}/cenarios/{cenario_id}`
- `POST /safras/{id}/cenarios/base/recalcular`
- orçamento e itens de orçamento
- tarefas manuais
- checklist operacional
- fenologia operacional
- caderno básico e timeline.

Esses itens sustentam a promessa de que A1 mantém operação agrícola básica.

---

## Ordem Recomendada de Implementação

### Fase 1 — Fechar exposição crítica

Escopo:

- `agricola/templates/router.py`
- `agricola/amostragem_solo/routers/*.py`
- `agricola/ndvi_avancado/routers/*.py`

Objetivo:

- adicionar gate mínimo de módulo;
- preparar tier topo quando `ENTERPRISE`/`PREMIUM` for decidido;
- adicionar testes de bloqueio básico.

### Fase 2 — PROFISSIONAL em inteligência já existente

Escopo:

- `agricola/analises_solo/router.py`
- `agricola/previsoes/router.py`
- `agricola/dashboard/router.py`
- `core/routers/reports.py`
- frontend consumidor dessas queries.

Objetivo:

- A1 mantém CRUD/leitura operacional;
- recursos analíticos e automações passam a `PROFISSIONAL`;
- frontend usa `useHasTier("PROFISSIONAL")` antes de disparar queries.

### Fase 3 — Módulos avançados com tier

Escopo:

- `agricola/agronomo/router.py`
- `agricola/monitoramento/router.py`
- `agricola/ndvi/router.py`
- `agricola/prescricoes/router.py`
- `agricola/beneficiamento/router.py`
- `agricola/rastreabilidade/router.py`
- `agricola/caderno/router.py`

Objetivo:

- manter registro operacional onde fizer sentido;
- monetizar IA, diagnóstico, NDVI, VRA, relatórios, certificação e auditoria.

### Fase 4 — Enterprise técnico

Escopo:

- `PlanTier`
- billing;
- seeds/planos;
- testes de headers;
- frontend `useHasTier`.

Objetivo:

- padronizar `ENTERPRISE` como nome canônico;
- manter `PREMIUM` apenas como alias legado;
- evitar decisões ad hoc por endpoint.

---

## Testes Esperados Quando Implementar

Para cada endpoint com novo tier:

- tenant sem módulo: bloqueio de módulo continua funcionando;
- tenant com módulo e `BASICO`: recebe `402`;
- resposta `402` retorna `X-Tier-Required`;
- tenant `PROFISSIONAL` acessa P1;
- tenant topo acessa P0/P2 Enterprise quando definido;
- frontend não dispara query premium sem tier suficiente.

Para garantir que A1 não quebrou:

- listar/visualizar safra;
- CRUD básico de safra;
- orçamento operacional;
- Production Units;
- listagem/visualização de cenários;
- recalcular `BASE`;
- tarefas/checklist/fenologia/caderno básico.

---

## Resumo Executivo

Prioridade de implementação:

1. **P0:** fechar routers avançados sem gate explícito (`templates`, `amostragem_solo`, `ndvi_avancado`).
2. **P1:** aplicar `PROFISSIONAL` em inteligência já exposta dentro de A1 (`analises_solo`, `previsoes`, `alertas`, `reports`).
3. **P2:** combinar módulos avançados com tier (`agronomo`, `monitoramento`, `NDVI`, `VRA`, `beneficiamento`, `rastreabilidade`, `caderno`).
4. **P3:** manter compatibilidade com o alias `PREMIUM` enquanto `ENTERPRISE` segue como nome canônico.

O maior risco atual é exposição de endpoints avançados sem gate explícito. O maior risco comercial é manter automações e inteligência em A1, reduzindo a diferenciação do plano `PROFISSIONAL`.
