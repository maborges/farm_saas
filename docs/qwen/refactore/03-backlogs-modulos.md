# Backlogs por Módulo/Submódulo

**Data:** 2026-04-06

---

## MÓDULO: CORE → Submódulo: Cadastro da Propriedade

**Responsável:** Backend + Frontend
**Prioridade:** 🔴 Crítica — base para agricultura de precisão

### Backend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| C-01 | Adicionar `SUBTALHAO` e `ZONA_DE_MANEJO` ao enum `TipoArea` | `models.py` | 15min |
| C-02 | Adicionar colunas de precisão ao `AreaRural` | `models.py` | 1h |
| C-03 | Criar modelo `HistoricoUsoTalhao` | `models.py` | 1h |
| C-04 | Criar modelo `AmostraSolo` | `models.py` | 1h |
| C-05 | Adicionar relationships `historico_uso` e `amostras_solo` | `models.py` | 15min |
| C-06 | Criar migration completa (tipos + colunas + tabelas novas) | `migrations/versions/` | 2h |
| C-07 | Script para popular `nivel_profundidade` em dados existentes | script SQL | 1h |
| C-08 | `validar_hierarquia()` no `AreaRuralService` | `service.py` | 2h |
| C-09 | `calcular_soma_areas()` no `AreaRuralService` | `service.py` | 30min |
| C-10 | `obter_arvore()` no `AreaRuralService` | `service.py` | 1h |
| C-11 | Aplicar validação hierárquica no POST do router | `router.py` | 30min |
| C-12 | Endpoint `GET /{area_id}/arvore` | `router.py` | 30min |
| C-13 | Endpoint `GET /{area_id}/soma-areas` | `router.py` | 30min |
| C-14 | Endpoints `GET/POST /{area_id}/historico-uso` | `router.py` | 1h |
| C-15 | Endpoints `GET/POST /{area_id}/amostras-solo` | `router.py` | 1h |
| C-16 | Expandir schemas `AreaRuralCreate/Update` com campos de precisão | `schemas.py` | 30min |
| C-17 | Criar schemas `HistoricoUsoCreate/Response` | `schemas.py` | 30min |
| C-18 | Criar schemas `AmostraSoloCreate/Response` | `schemas.py` | 30min |
| C-19 | Validar RN-CP-004 (soma talhões ≤ 105%) no backend | `service.py` | 2h |
| C-20 | Testes unitários: validação hierárquica | `tests/unit/` | 2h |
| C-21 | Testes unitários: soma de áreas | `tests/unit/` | 1h |
| C-22 | Testes de integração: histórico de uso | `tests/integration/` | 1h |
| C-23 | Testes de integração: amostras de solo | `tests/integration/` | 1h |

**Total Backend:** ~18h

### Frontend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| CF-01 | Atualizar Zod schemas `fazenda-schemas.ts` | `packages/zod-schemas/src/` | 1h |
| CF-02 | Criar Zod schemas para `AreaRural`, `HistoricoUso`, `AmostraSolo` | `packages/zod-schemas/src/` | 2h |
| CF-03 | Componente `AreaTree.tsx` (árvore hierárquica) | `components/core/areas/` | 6h |
| CF-04 | Componente `ZonaManejoDialog.tsx` | `components/core/areas/` | 4h |
| CF-05 | Componente `HistoricoUsoTimeline.tsx` | `components/core/areas/` | 3h |
| CF-06 | Componente `AmostrasSoloMap.tsx` | `components/core/areas/` | 6h |
| CF-07 | Nova aba "Hierarquia" na página de detalhe | `cadastros/propriedades/[id]/` | 4h |
| CF-08 | Nova aba "Amostras de Solo" na página de detalhe | `cadastros/propriedades/[id]/` | 4h |
| CF-09 | Integrar validação RN-CP-004 no UI (progress bar bloqueante) | `cadastros/propriedades/[id]/` | 2h |
| CF-10 | Botão "Editar propriedade" (hoje stub) | `cadastros/propriedades/[id]/` | 2h |
| CF-11 | Botão "Desativar/Reativar propriedade" (hoje stub) | `cadastros/propriedades/[id]/` | 2h |
| CF-12 | Botão de editar/excluir na lista de propriedades | `cadastros/propriedades/page.tsx` | 2h |
| CF-13 | Empty state com CTA na lista de propriedades | `cadastros/propriedades/page.tsx` | 1h |
| CF-14 | Campos opcionais no form de criação (CAR, NIRF, IE) | `cadastros/propriedades/page.tsx` | 2h |
| CF-15 | Validação de formato CAR no frontend | `packages/zod-schemas/src/` | 1h |

**Total Frontend:** ~42h

---

## MÓDULO: AGRÍCOLA → Safra (A1_PLANEJAMENTO)

**Responsável:** Backend
**Prioridade:** 🟡 Alta — inconsistência conceitual

### Backend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| A-01 | Tornar `Safra.talhao_id` nullable | `models.py` + migration | 2h |
| A-02 | Restringir `OperacaoAgricola.talhao_id` a tipos válidos (TALHAO, SUBTALHAO, ZONA_DE_MANEJO, PASTAGEM, PIQUETE) | `operacoes/service.py` | 1h |
| A-03 | Adicionar campo `nivel_area` a `PrescricaoVRA` | `prescricoes/models.py` + migration | 1h |
| A-04 | Adicionar campo `objetivo_economico` a `Safra` | `safras/models.py` + migration | 1h |
| A-05 | Calcular margem líquida no `resumo_planejado_realizado` | `safras/service.py` | 1h |
| A-06 | Testes: operação com subtalhão/zona | `tests/` | 1h |

**Total Backend:** ~7h

---

## MÓDULO: FINANCEIRO → Custos (F2_CUSTOS_ABC)

**Responsável:** Backend
**Prioridade:** 🟢 Média — indicador avançado

### Backend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| F-01 | Calcular margem líquida por safra | `custos/service.py` | 2h |
| F-02 | Calcular ROI por safra | `custos/service.py` | 2h |
| F-03 | Endpoint comparativo inter-safras | `custos/router.py` | 3h |
| F-04 | Adapter de custos que lê agrícola + pecuária | `custos/service.py` | 4h |

**Total Backend:** ~11h

---

## MÓDULO: AGRÍCOLA → Prescrição VRA (A4_PRECISAO)

**Responsável:** Backend + Frontend
**Prioridade:** 🟡 Alta — habilita taxa variável por zona

### Backend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| V-01 | Validar que `talhao_id` da prescrição pode ser SUBTALHAO ou ZONA_DE_MANEJO | `prescricoes/service.py` | 1h |
| V-02 | Endpoint `GET /prescricoes/safra/{safra_id}/por-zona` | `prescricoes/router.py` | 2h |
| V-03 | Validar coerência: soma de áreas das zonas = área do subtalhão | `prescricoes/service.py` | 2h |

**Total Backend:** ~5h

### Frontend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| VF-01 | UI de prescrição por zona (mapa colorido) | `agricola/prescricoes/` | 8h |
| VF-02 | Upload de grade de prescrição (GeoJSON) | `agricola/prescricoes/` | 4h |

**Total Frontend:** ~12h

---

## Resumo Geral

| Módulo | Backend | Frontend | Total |
|--------|---------|----------|-------|
| **CORE → Cadastro** | 18h | 42h | 60h |
| **AGRÍCOLA → Safra** | 7h | — | 7h |
| **FINANCEIRO → Custos** | 11h | — | 11h |
| **AGRÍCOLA → VRA** | 5h | 12h | 17h |
| **TOTAL** | **41h** | **54h** | **95h** |
