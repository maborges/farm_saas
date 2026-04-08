# Brainstorming — Cadastro da Propriedade

**Data:** 2026-04-04  
**Status:** Plano aprovado, implementação iniciando

## Diagnóstico

### Estado Atual do Backend
- `Fazenda` model existe mas incompleto: falta `codigo_car`, `nirf`, `uf`, `municipio`, `area_aproveitavel_ha`, `area_app_ha`, `area_rl_ha`, `cpf_cnpj` (só tem `cnpj`). `area_total_ha` usa `Float` (deve ser `Numeric`).
- Router CRUD completo + upload shapefile/KML + validação geometria.
- `Talhao`, `Gleba`, `Infraestrutura` — inexistentes.

### Estado Atual do Frontend
- `/cadastros/propriedades/page.tsx` — stub vazio
- `/cadastros/propriedades/[id]/page.tsx` — stub vazio

## Plano de Implementação

### Sprint 1 — Migration + Modelos (Backend)

**Tarefas:**
1. Migration Alembic:
   - Alterar `fazendas`: adicionar `codigo_car`, `nirf`, `uf` (Char 2), `municipio`, `cpf_cnpj`, `area_aproveitavel_ha`, `area_app_ha`, `area_rl_ha` (Numeric 12,4); converter `area_total_ha` Float → Numeric
   - Criar tabela `talhoes`: id, fazenda_id FK, nome, codigo, area_ha (Numeric), geojson (JSON), tipo_solo (Enum), uso_atual, tipo_talhao (Enum: producao/app/rl/outro), created_at
   - Criar tabela `glebas`: id, talhao_id FK, nome, area_ha (Numeric), geojson (JSON), observacao
   - Criar tabela `infraestruturas`: id, fazenda_id FK, nome, tipo (Enum: sede/silo/curral/galpao/oficina/outro), capacidade (Numeric), unidade_capacidade, latitude, longitude, observacoes

2. Atualizar `Fazenda` model + schemas (FazendaCreate, FazendaUpdate, FazendaResponse)

3. `Talhao` model + `TalhaoService(BaseService[Talhao])` + router em `/fazendas/{fazenda_id}/talhoes`
   - CRUD completo
   - Validação RN-CP-004: soma áreas ≤ 105% da área total da fazenda

4. `Gleba` model + `GlebaService` + router em `/talhoes/{talhao_id}/glebas`

5. `Infraestrutura` model + `InfraestruturaService` + router em `/fazendas/{fazenda_id}/infraestrutura`

### Sprint 2 — Frontend Lista + Cadastro

**Tarefas:**
6. Página `/cadastros/propriedades` (Server Component):
   - Grid de cards: nome, área total, nº talhões, status (ativo/inativo)
   - Botão "Nova Propriedade" → Drawer com formulário
   - Empty state com CTA

7. Formulário "Nova Propriedade" (Client Component, Drawer):
   - Campos obrigatórios: nome, UF, município, área total
   - Campos opcionais: CNPJ/CPF, IE, CAR, NIRF, coordenadas sede
   - Validação Zod

8. Zod schemas em `packages/zod-schemas/src/fazenda-schemas.ts`:
   - `FazendaCreateSchema`, `FazendaUpdateSchema`, `TalhaoCreateSchema`, `InfraestruturaCreateSchema`

### Sprint 3 — Frontend Detalhe (abas)

**Tarefas:**
9. Página `/cadastros/propriedades/[id]` com Tabs: **Dados Gerais | Talhões | Infraestrutura**

10. Aba Talhões:
    - Lista com: nome, código, área, tipo, uso atual
    - Indicador visual: soma total de áreas vs área fazenda (progress bar)
    - Drawer "Novo Talhão" com validação em tempo real

11. Aba Infraestrutura:
    - Lista com: nome, tipo (badge), capacidade, coordenadas
    - Drawer "Nova Infraestrutura"

### Sprint 4 — Validações de Negócio

**Tarefas:**
12. RN-CP-004: `TalhaoService.validar_soma_areas()` — erro 422 se soma > 105%
13. RN-CP-008: `FazendaService.delete()` — bloquear se safras/operações vinculadas

## Regras de Negócio Críticas

- **RN-CP-003:** `Fazenda → Talhao → Gleba` — hierarquia fixa
- **RN-CP-004:** Soma talhões ≤ 105% área total (tolerância para arredondamento/APP)
- **RN-CP-007:** Fazenda sempre vinculada a `tenant_id` (isolamento multi-tenant)
- **RN-CP-008:** Exclusão bloqueada se há safras/lotes/operações vinculadas

## Arquivos a Criar/Modificar

### Backend
- `services/api/core/models/fazenda.py` — atualizar
- `services/api/core/models/talhao.py` — criar
- `services/api/core/models/gleba.py` — criar
- `services/api/core/models/infraestrutura.py` — criar
- `services/api/core/schemas/fazenda_input.py` — atualizar
- `services/api/core/schemas/fazenda_output.py` — atualizar
- `services/api/core/schemas/talhao_schemas.py` — criar
- `services/api/core/schemas/gleba_schemas.py` — criar
- `services/api/core/schemas/infraestrutura_schemas.py` — criar
- `services/api/core/services/talhao_service.py` — criar
- `services/api/core/services/gleba_service.py` — criar
- `services/api/core/services/infraestrutura_service.py` — criar
- `services/api/core/routers/talhoes.py` — criar
- `services/api/core/routers/glebas.py` — criar
- `services/api/core/routers/infraestrutura.py` — criar
- `services/api/main.py` — registrar novos routers
- `services/api/alembic/versions/XXXX_cadastro_propriedade_completo.py` — migration

### Frontend
- `apps/web/src/app/(dashboard)/cadastros/propriedades/page.tsx` — implementar
- `apps/web/src/app/(dashboard)/cadastros/propriedades/[id]/page.tsx` — implementar
- `apps/web/src/components/core/propriedades/PropriedadeCard.tsx` — criar
- `apps/web/src/components/core/propriedades/PropriedadeForm.tsx` — criar
- `apps/web/src/components/core/talhoes/TalhaoList.tsx` — criar
- `apps/web/src/components/core/talhoes/TalhaoForm.tsx` — criar
- `apps/web/src/components/core/infraestrutura/InfraestruturaList.tsx` — criar
- `apps/web/src/components/core/infraestrutura/InfraestruturaForm.tsx` — criar
- `packages/zod-schemas/src/fazenda-schemas.ts` — atualizar/criar
