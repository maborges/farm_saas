# Contexto — Step 24: Production Units UI

**Data:** 2026-04-26  
**Status:** CONCLUÍDO  
**Commits:** `404ebef3` (backend) · `dc64beaf` (submodule nav)

---

## Resumo executivo

Step 24 fechou a lacuna principal: o usuário agora acessa e gerencia Production Units pelo painel da safra antes de trabalhar com cenários econômicos.

Diagnóstico confirmado: `production_units/` tinha apenas `models.py` — sem service, router ou schemas. O `cenarios/service.py` lia `ProductionUnit` internamente, mas não havia endpoint público, impossibilitando criação pela UI.

---

## Validação final (4 pontos)

| # | Ponto | Status | Observação |
|---|-------|--------|------------|
| 1 | Rota `/safras/{id}/production-units` funcional | ✅ | Registrada em `main.py` linhas 303 + 380 |
| 2 | Card respeita permissões do módulo agrícola | ✅ | `get_tenant_id` + `get_session_with_tenant` garantem isolamento multi-tenant; endpoints protegidos com `require_module("A1_PLANEJAMENTO")` |
| 3 | Cenários refletem PUs criadas | ✅ | `cenarios/service._fetch_production_units()` filtra `status == "ATIVA"` automaticamente |
| 4 | Sem backend ou tabela duplicada | ✅ | Única definição `__tablename__ = "production_units"` no codebase; reaproveitada migration step15 |

---

## O que foi criado

### Backend

**`services/api/agricola/production_units/schemas.py`**
- `ProductionUnitCreate` — `cultivo_id`, `area_id`, `cultivo_area_id?`, `percentual_participacao`, `area_ha`, `data_inicio?`, `data_fim?`
- `ProductionUnitUpdate` — todos opcionais
- `ProductionUnitResponse` — inclui `cultivo_nome` e `area_nome` (enriquecidos pelo service via join)
- `StatusConsorcioResponse`

**`services/api/agricola/production_units/service.py`**
- `ProductionUnitService(BaseService[ProductionUnit])`
- Métodos: `listar_por_safra`, `criar`, `obter`, `atualizar`, `encerrar`, `status_consorcio`, `_enrich`
- Join com `Cultivo.cultura` e `AreaRural.nome` para enriquecer respostas
- `encerrar()` faz PATCH `status=ENCERRADA` com validação de estado duplo

**`services/api/agricola/production_units/router.py`**
- Prefix: `/safras/{safra_id}/production-units`
- Tag: `Production Units — Step 24`
- Endpoints:
  - `GET /` — listar por safra
  - `POST /` — criar (commit + flush)
  - `GET /status-consorcio` — read model agregado por área
  - `GET /{pu_id}` — detalhe
  - `PATCH /{pu_id}` — atualizar
  - `POST /{pu_id}/encerrar` — encerrar
- Todos usam `get_session_with_tenant` ✅ R1 OK
- Nenhum `select()` no router ✅ R2 OK
- Gate comercial aplicado com `require_module("A1_PLANEJAMENTO")`, seguindo o padrão de `cenarios/router.py`

**`services/api/main.py`**
- Import na linha 303: `from agricola.production_units.router import router as router_production_units`
- Include na linha 380: `app.include_router(router_production_units, prefix="/api/v1")`

### Frontend

**`apps/web/src/app/(dashboard)/agricola/safras/[id]/production-units/page.tsx`**
- DataTable com colunas: Cultivo, Área, Área (ha), Participação (%), Status (badge)
- Ações por linha: editar (Pencil), encerrar (Power), link para cenários (BarChart2)
- KPIs: total de unidades, ativas, área total (ha)
- Estado vazio: card com CTA para criar
- `CreateDialog`: seleciona cultivo → carrega áreas via `/safras/{id}/cultivos/{cultivo_id}/areas` → preenche area_ha, percentual, datas
- `EditDialog`: edita percentual, area_ha, datas
- `AlertDialog` para confirmar encerramento (padrão CLAUDE.md)

**`apps/web/src/app/(dashboard)/agricola/safras/[id]/page.tsx`**
- Import `Layers` adicionado
- Card de navegação inserido antes de "Cenários":
```ts
{ href: `/agricola/safras/${id}/production-units`, icon: Layers, label: "Unidades de Produção", desc: "Cultivo × área × participação", color: "text-cyan-600 bg-cyan-50" }
```

---

## Modelos validados

| Modelo | Tabela | Campo principal |
|--------|--------|-----------------|
| `ProductionUnit` | `production_units` | `safra_id`, `cultivo_id`, `area_id`, `percentual_participacao`, `area_ha`, `status` |
| `Cultivo` | `cultivos` | `cultura` (**não** `nome`) |
| `AreaRural` | `cadastros_areas_rurais` | `nome`, `tipo`, `area_hectares` |
| `StatusConsorcioArea` | `status_consorcio_area` | read model — `soma_participacao`, `qtd_unidades`, `status` |

---

## Lint final

| Regra | Status |
|-------|--------|
| R1 — `get_session` em router tenant-scoped | ✅ 0 violações |
| R2 — `select()` em router | ✅ 0 violações |
| R3 — `StorageService.save()` sem track | ✅ 0 violações |
| R4 — `session.add()` sem flush (financeiro) | ⚠️ dívida técnica Step 23 — não bloqueante |

---

## Pendência de segurança/comercialização

Fechada após Step 24:
- `production_units/router.py` importa `require_module`
- define `MODULE = "A1_PLANEJAMENTO"`
- todos os endpoints públicos incluem `_: None = Depends(require_module(MODULE))`
- tenant sem `A1_PLANEJAMENTO` recebe `402` com header `X-Module-Required: A1_PLANEJAMENTO`

---

## O que NÃO foi feito (evolução futura)

- Dashboard visual de consorciamento (barra de % por área)
- Alertas quando `soma_participacao > 100`
- Filtro por status (ATIVA / ENCERRADA) na listagem
- Paginação (volume esperado pequeno por safra)

---

## Candidatos para Step 25

| Candidato | Esforço | Valor |
|-----------|---------|-------|
| **Step 20b — IR/Depreciação** — `depreciacao_ha` já existe em `safra_cenarios_unidades`; service de cálculo pendente | Médio | Completar cenários econômicos |
| **Irrigação UI** — backend `ndvi_avancado/routers/irrigacao.py` existe; falta página frontend | Médio | Fechar lacuna UI similar ao step24 |
| **Pecuária backend** — frontend `/dashboard/pecuaria/` existe; backend `pecuaria/` parcialmente implementado | Alto | Novo módulo com valor comercial |

---

## Como retomar

Na próxima sessão, referenciar este arquivo e escolher um candidato:

```
Retomar após Step 24 (Production Units UI — concluído).
Contexto: docs/contexts/step24-production-units-context.md
Próximo: [escolher candidato da tabela acima]
```
