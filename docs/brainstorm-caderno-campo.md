# Caderno de Campo — Plano de Continuação

**Data:** 2026-04-06  
**Status:** Implementação parcial concluída — aguardando continuação

---

## O que foi implementado

### Backend (`services/api/agricola/caderno/`)
- `models.py` — 5 tabelas: `caderno_campo_entradas`, `caderno_campo_fotos`, `visitas_tecnicas`, `epi_entregas`, `caderno_exportacoes`
- `schemas.py` — Pydantic v2 para todas as entidades + `TimelineItem` agregado
- `service.py` — 4 services: `CadernoCampoService`, `VisitaTecnicaService`, `EPIEntregaService`, `CadernoExportacaoService`
- `router.py` — 12 endpoints sob `/api/v1/caderno/*`
- Migration `8c2e891d6ba9_caderno_campo` — **aplicada em banco**
- Registrado em `main.py`

### Frontend (`apps/web/`)
- `apps/web/src/app/(dashboard)/agricola/safras/[id]/caderno/page.tsx` — página principal
- `apps/web/src/components/agricola/caderno/CadernoTimeline.tsx` — timeline agrupada por data
- `apps/web/src/components/agricola/caderno/EntradaDrawer.tsx` — sheet lateral de detalhe
- `apps/web/src/components/agricola/caderno/NovaEntradaForm.tsx` — modal de novo registro
- Link "Caderno" adicionado na página de detalhe da safra (`safras/[id]/page.tsx`)

---

## O que falta — por prioridade

### P0 — Bloqueante para uso real

| # | Item | Detalhe | Estimativa |
|---|------|---------|-----------|
| P0.1 | **Seletor de talhão no form** | `NovaEntradaForm.tsx` tem `talhao_id` vazio/hardcoded — buscar talhões da safra via `GET /safras/{id}/talhoes` e renderizar Select | 30min |
| P0.2 | **Upload de fotos com geolocalização** | Criar `FotoUpload.tsx` que usa `navigator.geolocation` + `FormData` para `POST /caderno/entradas/{id}/fotos` (endpoint a criar). Compressão client-side opcional | 2h |
| P0.3 | **Trigger automático de operações** | Em `agricola/operacoes/service.py`, quando operação muda para status `REALIZADA`, criar entrada automática em `caderno_campo_entradas` com `tipo=OPERACAO_AUTO` e `operacao_id` vinculado | 1h |
| P0.4 | **Geração de PDF real** | `CadernoExportacaoService.gerar()` hoje retorna URL placeholder. Implementar com `reportlab` ou `weasyprint`: cabeçalho fazenda/safra/talhão + entradas cronológicas + fotos em miniatura + campo de assinatura | 3h |
| P0.5 | **Assinatura digital do RT** | Endpoint `POST /caderno/exportacoes/{id}/assinar` que registra `assinado_por + crea_rt` na exportação. Frontend: modal com campos nome + CREA, botão "Assinar" na página | 1h |

### P1 — Funcionalidade importante

| # | Item | Detalhe | Estimativa |
|---|------|---------|-----------|
| P1.1 | **Form de Visita Técnica** | Criar `VisitaTecnicaForm.tsx` com campos: nome RT, CREA, data, observações, constatações (lista dinâmica). Botão "Registrar Visita" na página do caderno | 1.5h |
| P1.2 | **Form de Entrega de EPI** | Criar `EPIEntregaForm.tsx` com campos: trabalhador, tipo EPI, quantidade, validade, campo de assinatura (upload de foto da assinatura) | 1h |
| P1.3 | **Fotos exibidas no Drawer** | `EntradaDrawer.tsx` hoje mostra apenas contagem. Buscar fotos via `GET /caderno/entradas/{id}` e renderizar galeria responsiva | 1h |
| P1.4 | **Modal de exclusão com motivo** | Hoje motivo está hardcoded em `page.tsx`. Criar `DeleteEntradaDialog.tsx` com campo `motivo_exclusao` (mínimo 10 chars, validado) | 30min |

### P2 — Qualidade e compliance

| # | Item | Detalhe |
|---|------|---------|
| P2.1 | **Teste de tenant isolation** | `tests/unit/test_caderno_tenant_isolation.py` — verificar que tenant A não acessa dados do tenant B |
| P2.2 | **Modelos de exportação para certificações** | PDF com layout específico para GlobalG.A.P., Orgânico (USDA/IBD) e MAPA — campos obrigatórios diferentes por modelo |
| P2.3 | **Alerta CREA vencido** | Antes de assinar, verificar data de validade do CREA e alertar se vencido |
| P2.4 | **Página global `/agricola/caderno`** | Visão cross-safras para agrônomo/auditor com seletor de safra/talhão e histórico de exportações |
| P2.5 | **Endpoint de fotos** | `POST /caderno/entradas/{id}/fotos` ainda não existe no router — apenas o service tem `adicionar_foto()`. Adicionar endpoint com `UploadFile` |
| P2.6 | **GET /caderno/entradas/{id}** | Endpoint de detalhe individual de entrada (com fotos) não existe no router — necessário para o Drawer exibir fotos |
| P2.7 | **Tabs na página** | Separar seções: Timeline / Visitas Técnicas / Entregas EPI / Exportações — hoje tudo numa tela plana |
| P2.8 | **Caderno no sidebar global** | Adicionar link no sidebar principal de agrícola para acesso direto sem passar pela safra |
| P2.9 | **Alerta caderno desatualizado** | Badge/notificação quando safra ativa está sem registros há mais de X dias (configurável) |

---

## Decisões de arquitetura já tomadas

- **Abordagem B** — módulo próprio com tabelas dedicadas (não estende monitoramento)
- Ponto de entrada principal: aba dentro da safra (`/safras/[id]/caderno`) — página global na fase 2
- Soft delete com `excluida + motivo_exclusao` — sem hard delete para auditabilidade
- Janela de edição livre: 72h (constante `JANELA_EDICAO_HORAS` em `service.py`)
- Timeline agrega entradas manuais + operações automáticas (sem duplicar dados)
- Permissões: `require_module("AGRICOLA_ESSENCIAL")`

---

## Contexto do módulo

- **Docs de referência:** `docs/contexts/agricola/essencial/caderno-campo.md`
- **Legislação:** IN 02/2008 MAPA, Lei 7.802/89, GlobalG.A.P., EU Due Diligence 2023/1115
- **Personas:** Agrônomo/RT (principal), Operador de Campo (mobile/offline), Produtor (consulta), Auditor (exportação)
- **Dependências:** `agricola/operacoes`, `agricola/safras`, `agricola/monitoramento`, `core/auth`

---

## Próxima sessão — ordem sugerida

1. P0.1 → seletor de talhão (desbloqueador imediato — sem isso nada salva)
1a. P2.6 → endpoint GET /entradas/{id} (necessário para drawer funcionar)
2. P0.3 → trigger automático (fecha loop entre operações e caderno)
3. P1.4 → modal de exclusão com motivo (qualidade básica)
4. P0.2 → upload de fotos
5. P0.4 + P0.5 → PDF + assinatura RT
6. P1.1 + P1.2 → forms de visita técnica e EPI
