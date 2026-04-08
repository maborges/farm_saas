# Backlog Completo — 3 Frentes de Refatoração

**Data:** 2026-04-06

---

## Frente C: Propriedade + Exploração Rural (Fundação)

### Backend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| C-01 | Criar modelos `Propriedade`, `ExploracaoRural`, `DocumentoExploracao` | `core/cadastros/propriedades/propriedade_models.py` | 2h |
| C-02 | Criar enums `NaturezaVinculo`, `TipoDocumentoExploracao` | mesmo arquivo | 15min |
| C-03 | Criar schemas Pydantic (PropriedadeCreate/Update, ExploracaoCreate/Update, DocumentoCreate/Response) | `core/cadastros/propriedades/propriedade_schemas.py` | 1h |
| C-04 | Criar service `ExploracaoRuralService` com validações (sobreposição, área) | `core/cadastros/propriedades/propriedade_service.py` | 2h |
| C-05 | Criar router com CRUD Propriedade + Exploracao + Documentos | `core/cadastros/propriedades/propriedade_router.py` | 2h |
| C-06 | Criar migration (3 tabelas novas + migração de dados GrupoFazendas→Propriedade) | `migrations/versions/` | 3h |
| C-07 | Registrar router no `main.py` | `main.py` | 15min |
| C-08 | Testes unitários: sobreposição de vigência | `tests/unit/` | 1h |
| C-09 | Testes unitários: área explorada > área total | `tests/unit/` | 30min |
| C-10 | Testes de integração: CRUD completo | `tests/integration/` | 2h |

**Total Backend Frente C:** ~15h

### Frontend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| CF-C1 | Criar Zod schemas (`propriedade-schemas.ts`) | `packages/zod-schemas/src/` | 1h |
| CF-C2 | Página Lista de Propriedades | `app/(dashboard)/cadastros/propriedades-econ/page.tsx` | 4h |
| CF-C3 | Página Detalhe da Propriedade (abas) | `app/(dashboard)/cadastros/propriedades-econ/[id]/page.tsx` | 6h |
| CF-C4 | Dialog criação de Exploração (natureza, vigência) | `components/core/propriedades/ExploracaoDialog.tsx` | 3h |
| CF-C5 | Upload de documentos de exploração | `components/core/propriedades/DocumentoUpload.tsx` | 3h |
| CF-C6 | Página de Fazenda exibe vínculo de exploração | `app/(dashboard)/cadastros/propriedades/[id]/page.tsx` | 2h |

**Total Frontend Frente C:** ~19h

**Subtotal Frente C:** 34h

---

## Frente A: Hierarquia + Agricultura de Precisão

### Backend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| A-01 | Adicionar `SUBTALHAO` + `ZONA_DE_MANEJO` ao enum `TipoArea` | `core/cadastros/propriedades/models.py` | 15min |
| A-02 | Adicionar 11 colunas de precisão ao `AreaRural` | mesmo arquivo | 1h |
| A-03 | Criar modelo `HistoricoUsoTalhao` | mesmo arquivo | 1h |
| A-04 | Criar modelo `AmostraSolo` | mesmo arquivo | 1h |
| A-05 | Criar migration (tipos + colunas + 2 tabelas novas) | `migrations/versions/` | 2h |
| A-06 | Script popular `nivel_profundidade` existente | script SQL | 1h |
| A-07 | `validar_hierarquia()` no `AreaRuralService` | `core/cadastros/propriedades/service.py` | 2h |
| A-08 | `calcular_soma_areas()` no Service | mesmo arquivo | 30min |
| A-09 | `obter_arvore()` no Service | mesmo arquivo | 1h |
| A-10 | Aplicar validação no POST do router | `core/cadastros/propriedades/router.py` | 30min |
| A-11 | Endpoints `/arvore`, `/soma-areas` | mesmo arquivo | 30min |
| A-12 | Endpoints `GET/POST /{area_id}/historico-uso` | mesmo arquivo | 1h |
| A-13 | Endpoints `GET/POST /{area_id}/amostras-solo` | mesmo arquivo | 1h |
| A-14 | Expandir schemas `AreaRuralCreate/Update` com campos de precisão | `core/cadastros/propriedades/schemas.py` | 30min |
| A-15 | Criar schemas `HistoricoUsoCreate/Response`, `AmostraSoloCreate/Response` | mesmo arquivo | 1h |
| A-16 | Validar RN-CP-004 (soma ≤ 105%) no backend | `service.py` | 2h |
| A-17 | Testes unitários: validação hierárquica | `tests/unit/` | 2h |
| A-18 | Testes unitários: soma de áreas + RN-CP-004 | `tests/unit/` | 1h |
| A-19 | Testes integração: histórico + amostras | `tests/integration/` | 2h |
| A-20 | `Safra.talhao_id` → nullable | `agricola/safras/models.py` + migration | 2h |
| A-21 | Restringir `OperacaoAgricola.talhao_id` a tipos válidos | `agricola/operacoes/service.py` | 1h |

**Total Backend Frente A:** ~26h

### Frontend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| AF-A1 | Atualizar Zod `fazenda-schemas.ts` + novos schemas | `packages/zod-schemas/src/` | 2h |
| AF-A2 | Componente `AreaTree.tsx` | `components/core/areas/` | 6h |
| AF-A3 | Componente `ZonaManejoDialog.tsx` | `components/core/areas/` | 4h |
| AF-A4 | Componente `HistoricoUsoTimeline.tsx` | `components/core/areas/` | 3h |
| AF-A5 | Componente `AmostrasSoloMap.tsx` | `components/core/areas/` | 6h |
| AF-A6 | Nova aba "Hierarquia" na página de detalhe | `cadastros/propriedades/[id]/page.tsx` | 4h |
| AF-A7 | Nova aba "Amostras de Solo" na página de detalhe | `cadastros/propriedades/[id]/page.tsx` | 4h |
| AF-A8 | Integrar RN-CP-004 bloqueante no frontend | `cadastros/propriedades/[id]/page.tsx` | 2h |
| AF-A9 | Prescrição VRA por zona (mapa colorido) | `agricola/prescricoes/` | 8h |
| AF-A10 | Upload de grade GeoJSON para prescrição | `agricola/prescricoes/` | 4h |
| AF-A11 | Editar propriedade (hoje stub) | `cadastros/propriedades/[id]/page.tsx` | 2h |
| AF-A12 | Desativar/Reativar propriedade (hoje stub) | `cadastros/propriedades/[id]/page.tsx` | 2h |
| AF-A13 | Editar/excluir na lista de propriedades | `cadastros/propriedades/page.tsx` | 2h |
| AF-A14 | Empty state com CTA | `cadastros/propriedades/page.tsx` | 1h |
| AF-A15 | Campos opcionais no form de criação (CAR, NIRF, IE) | `cadastros/propriedades/page.tsx` | 2h |
| AF-A16 | Validação de formato CAR no frontend | `packages/zod-schemas/src/` | 1h |

**Total Frontend Frente A:** ~49h

**Subtotal Frente A:** 75h

---

## Frente B: Custeio Automático → Financeiro

### Backend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| B-01 | Criar `Rateio` automaticamente ao criar despesa pela operação | `agricola/operacoes/service.py` | 1h |
| B-02 | Mapear tipo de operação → plano de conta específico | lookup table + migration | 2h |
| B-03 | `CustosService.get_resumo_safra()` ler também despesas do financeiro | `agricola/custos/service.py` | 2h |
| B-04 | Suporte a custo de mão de obra na operação | `agricola/operacoes/models.py` + `service.py` | 3h |
| B-05 | Suporte a custo de máquina na operação | `agricola/operacoes/models.py` + `service.py` | 3h |
| B-06 | Testes de integração: operação → despesa → rateio → centro de custos | `tests/` | 2h |
| B-07 | Margem líquida e ROI por safra | `agricola/custos/service.py` | 2h |
| B-08 | Comparativo inter-safras | `agricola/custos/router.py` | 3h |

**Total Backend Frente B:** ~18h

### Frontend

| ID | Tarefa | Arquivo | Esforço |
|----|--------|---------|---------|
| BF-B1 | Dashboard unificado: custo agrícola + financeiro lado a lado | `agricola/safras/` | 4h |
| BF-B2 | Alerta de divergência: custo agrícola ≠ custo financeiro | `components/` | 2h |
| BF-B3 | UI de indicadores econômicos na safra (margem, ROI) | `agricola/safras/` | 4h |
| BF-B4 | UI comparativo inter-safras | `agricola/safras/` | 4h |

**Total Frontend Frente B:** ~14h

**Subtotal Frente B:** 32h

---

## Resumo Consolidado

| Frente | Backend | Frontend | Total | % do total |
|--------|---------|----------|-------|-----------|
| **C: Propriedade** | 15h | 19h | 34h | 24% |
| **A: Hierarquia** | 26h | 49h | 75h | 53% |
| **B: Custeio** | 18h | 14h | 32h | 23% |
| **TOTAL** | **59h** | **82h** | **141h** | **100%** |

---

## Dependências entre Tarefas

```
Frente C (Propriedade)
├── C-01, C-02, C-06 (modelos + migration)  ← CRÍTICO — sem isso nada anda
├── C-03, C-04, C-05, C-07 (service + router)
├── C-08, C-09, C-10 (testes)
└── CF-C1 a CF-C6 (frontend)

Frente A (Hierarquia)
├── A-01, A-02, A-03, A-04, A-05 (modelos + migration)  ← CRÍTICO
├── A-07 a A-16 (service + router + schemas)
├── A-17 a A-19 (testes)
├── A-20, A-21 (Safra + Operacao)
└── AF-A1 a AF-A16 (frontend)

Frente B (Custeio)
├── B-01, B-02, B-03 (rateio + plano conta + custos service)  ← CRÍTICO
├── B-04, B-05 (MO + máquina)
├── B-06 (testes)
├── B-07, B-08 (margem + ROI + comparativo)
└── BF-B1 a BF-B4 (frontend)
```

**Frente C é pré-requisito para:** nada técnico (A e B são independentes), mas é pré-requisito conceitual — sem Propriedade, a Safra não tem unidade econômica correta.

**Recomendação:** Iniciar C e A em paralelo. B pode iniciar quando A-20 (Safra.talhao_id nullable) estiver pronto.
