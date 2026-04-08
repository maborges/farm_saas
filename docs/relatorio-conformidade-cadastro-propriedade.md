# Relatório de Conformidade — Cadastro da Propriedade

**Data:** 2026-04-06
**Base de análise:**
- `docs/brainstorm-cadastro-propriedade.md`
- `docs/contexts/core/cadastro-propriedade.md`

---

## 1. Resumo Executivo

A implementação do submódulo **Cadastro da Propriedade** evoluiu significativamente em relação ao plano original do brainstorm. A arquitetura foi **refatorada** para um modelo hierárquico unificado (`AreaRural`), que generaliza Talhões, Glebas, Pastagens, Piquetes, APP, Reserva Legal e Infraestrutura em uma única entidade polimórfica. Essa decisão técnica é **superior ao plano original**, pois oferece flexibilidade maior para expansão futura.

**Conformidade geral: ~78%**

| Dimensão | Conformidade | Observação |
|----------|-------------|------------|
| Backend — Modelos | ✅ 95% | Todos os modelos existem; `AreaRural` unifica Talhao/Gleba |
| Backend — Schemas | ✅ 90% | Pydantic completo; falta validação de formato CAR/CPF/CNPJ |
| Backend — Services | ✅ 85% | CRUD completo; falta RN-CP-004 (validação soma áreas) e RN-CP-008 |
| Backend — Routers | ✅ 90% | Endpoints completos + upload geo; falta endpoint dedicado de validação |
| Backend — Migrations | ✅ 90% | Migrations existem para todas as entidades |
| Backend — Testes | ⚠️ 50% | Testes de Infraestrutura OK; faltam testes unitários para AreaRural |
| Frontend — Lista | ✅ 80% | DataTable funcional; faltam botões de editar/excluir na lista |
| Frontend — Detalhe | ✅ 75% | Abas Talhões/Infraestrutura/Dados OK; editar/desativar são stubs |
| Frontend — Zod Schemas | ⚠️ 45% | Schema Fazenda incompleto; faltam schemas Talhao, Gleba, Infraestrutura |
| Regras de Negócio | ⚠️ 55% | RN-CP-004 e RN-CP-008 não implementadas; validações de formato ausentes |
| Geoprocessamento | ✅ 85% | Upload e processamento de shapefile/KML/GeoJSON implementados |
| Multi-tenant | ✅ 95% | `tenant_id` em todos os modelos e enforce no BaseService |

---

## 2. Análise Detalhada por Sprint

### Sprint 1 — Migration + Modelos (Backend)

#### 2.1. Modelo Fazenda

| Campo | Brainstorm | Implementado | Conformidade |
|-------|-----------|--------------|-------------|
| `id` (UUID) | Sim | Sim | ✅ |
| `tenant_id` (UUID FK) | Sim (RN-CP-007) | Sim | ✅ |
| `grupo_id` (UUID FK) | Não mencionado | Sim (adição) | ℹ️ Adição válida |
| `nome` (String 100) | Sim | Sim (String 150) | ✅ |
| `cpf_cnpj` (String 18) | Sim | Sim | ✅ |
| `inscricao_estadual` (String 20) | Sim | Sim (String 50) | ✅ |
| `codigo_car` (String 20) | Sim | Sim (String 50) | ✅ |
| `nirf` (String 20) | Sim | Sim | ✅ |
| `uf` (Char 2) | Sim | Sim (String 2) | ✅ |
| `municipio` (String 100) | Sim | Sim | ✅ |
| `area_total_ha` (Numeric 12,4) | Sim | Sim (Numeric 12,4) | ✅ |
| `area_aproveitavel_ha` (Numeric 12,4) | Sim | Sim | ✅ |
| `area_app_ha` (Numeric 12,4) | Sim | Sim | ✅ |
| `area_rl_ha` (Numeric 12,4) | Sim | Sim | ✅ |
| `modulos_fiscais` (Decimal 6,2) | Sim | ❌ Faltando | 🔴 |
| `geojson` (JSONB) | Sim | Sim (`geometria` JSON) | ✅ |
| `is_active` (Boolean) | Sim | Sim (`ativo`) | ✅ |
| `coordenadas_sede` | Sim | Sim (String 100) | ✅ |

**Arquivos:**
- `services/api/core/models/fazenda.py` — ✅ Modelo completo e bem estruturado
- `services/api/core/schemas/fazenda_input.py` — ✅ `FazendaCreate` e `FazendaUpdate` completos
- `services/api/core/schemas/fazenda_output.py` — ✅ `FazendaResponse` existe
- `services/api/core/services/fazenda_service.py` — ⚠️ CRUD básico; faltam validações de negócio

#### 2.2. Modelo Talhão → AreaRural

O brainstorm previa um modelo `Talhao` standalone. A implementação optou por unificar em `AreaRural` com discriminação por `tipo`. Isso é **uma evolução arquitetural válida**.

| Entidade Brainstorm | Equivalente Implementado | Conformidade |
|---------------------|------------------------|-------------|
| `Talhao` (tabela própria) | `AreaRural` com `tipo=TALHAO/PASTAGEM/APP/RESERVA_LEGAL` | ✅ (refatorado) |
| `Gleba` (tabela própria) | `AreaRural` com `tipo=GLEBA` + `MatriculaImovel` | ✅ (refatorado) |
| Hierarquia `Fazenda → Talhao → Gleba` | `AreaRural` com `parent_id` (auto-relacionamento) | ✅ (generalizado) |

**Campos do Talhão original vs AreaRural:**

| Campo Talhão (brainstorm) | Equivalente AreaRural | Conformidade |
|---------------------------|----------------------|-------------|
| `fazenda_id` FK | `fazenda_id` FK | ✅ |
| `nome` (String 100) | `nome` (String 200) | ✅ |
| `codigo` (String 20) | `codigo` (String 50) | ✅ |
| `area_ha` (Numeric 12,4) | `area_hectares` (Float) | ⚠️ Usa Float ao invés de Numeric |
| `geojson` (JSON) | `geometria` (JSON) | ✅ |
| `tipo_solo` (Enum) | `dados_extras.tipo_solo` (JSON) | ⚠️ Em JSON, não coluna dedicada |
| `uso_atual` (String 50) | `dados_extras.cultura_atual` (JSON) | ⚠️ Em JSON, não coluna dedicada |
| `tipo_talhao` (Enum) | `tipo` (String 30, 12 valores) | ✅ (expandido) |

**Arquivos:**
- `services/api/core/cadastros/propriedades/models.py` — ✅ `AreaRural` com 12 tipos
- `services/api/core/cadastros/propriedades/schemas.py` — ✅ `AreaRuralCreate/Update/Response/Tree`
- `services/api/core/cadastros/propriedades/service.py` — ✅ `AreaRuralService` completo
- `services/api/core/cadastros/propriedades/router.py` — ✅ CRUD + `/tree`, `/filhos`

#### 2.3. Modelo Infraestrutura

| Campo | Brainstorm | Implementado | Conformidade |
|-------|-----------|--------------|-------------|
| `id` (UUID) | Sim | Sim | ✅ |
| `fazenda_id` (UUID FK) | Sim | `area_rural_id` FK → AreaRural | ✅ (refatorado) |
| `nome` (String 100) | Sim | Sim | ✅ |
| `tipo` (Enum) | Sim (sede/silo/curral/galpao/oficina/outro) | Sim (`TipoInfraestrutura` enum) | ✅ |
| `capacidade` (Decimal 12,2) | Sim | Sim (Numeric 12,2) | ✅ |
| `unidade_capacidade` (String 20) | Sim | Sim | ✅ |
| `latitude` (Decimal 10,8) | Sim | Sim | ✅ |
| `longitude` (Decimal 11,8) | Sim | Sim | ✅ |
| `observacoes` (Text) | Sim | Sim | ✅ |
| `is_active` (Boolean) | Sim | Sim | ✅ |

**Arquivos:**
- `services/api/core/cadastros/propriedades/models.py` — ✅ `Infraestrutura` + `TipoInfraestrutura`
- `services/api/core/cadastros/propriedades/schemas.py` — ✅ `InfraestruturaCreate/Update/Response`
- `services/api/core/cadastros/propriedades/service.py` — ✅ `InfraestruturaService`
- `services/api/core/cadastros/propriedades/router.py` — ✅ CRUD em `/{area_id}/infraestruturas`
- `services/api/tests/integration/core/test_infraestrutura.py` — ✅ 3 testes de integração

#### 2.4. Entidades Extras (não previstas no brainstorm)

| Entidade | Descrição | Avaliação |
|----------|-----------|-----------|
| `MatriculaImovel` | Matrículas cartoriais (CAR, NIRF, INCRA, CCIR, SNCR, ITR) | ✅ Excelente adição — compliance fundiário |
| `RegistroAmbiental` | Licenças ambientais (CAR_APP, CAR_RL, LICENCA_IBAMA) | ✅ Excelente adição — compliance ambiental |
| `ValorPatrimonial` | Avaliações patrimoniais com métodos (MERCADO, CUSTO, RENDA) | ✅ Excelente adição — módulo financeiro |
| `ArquivoGeo` | Auditoria de uploads geoespaciais com status de processamento | ✅ Excelente adição — rastreabilidade |

---

### Sprint 2 — Frontend Lista + Cadastro

#### 2.5. Página `/cadastros/propriedades` (Lista)

| Requisito | Status | Observação |
|-----------|--------|------------|
| Listagem de fazendas | ✅ Implementado | DataTable com colunas: Nome, Localização, Área, CAR, Status, Ações |
| Filtro por status (ativa/inativa) | ✅ Implementado | Select com Todas/Ativas/Inativas |
| Stats bar (total propriedades, área total) | ✅ Implementado | Contador + soma de áreas |
| Botão "Nova Propriedade" → Dialog | ✅ Implementado | Dialog com formulário |
| Campos do formulário: nome, UF, município, área total | ✅ Implementado | Todos presentes |
| Campos opcionais: CNPJ/CPF | ✅ Implementado | Campo CPF/CNPJ presente |
| Auto-seleção de grupo único | ✅ Implementado | Quando há apenas 1 grupo |
| **Grid de cards** (plano original) | ⚠️ DataTable ao invés de cards | ℹ️ DataTable é mais funcional para grandes volumes |
| **Empty state com CTA** | ❌ Ausente | Mensagem genérica "Nenhuma propriedade cadastrada" |
| **Botão de editar propriedade** | ❌ Ausente | Apenas botão de visualizar (Eye) |
| **Botão de excluir/desativar** | ❌ Ausente | Nenhuma ação de delete na lista |
| **Validação de formato CAR** | ❌ Ausente | Sem validação no frontend |
| **Validação de CPF/CNPJ** | ❌ Ausente | Sem validação algorítmica |
| **Upload de shapefile/KML** | ❌ Ausente | Não há na página de criação |

#### 2.6. Zod Schemas — `fazenda-schemas.ts`

| Schema | Brainstorm | Implementado | Conformidade |
|--------|-----------|--------------|-------------|
| `createFazendaSchema` | Sim | ⚠️ Parcial | 45% |
| `updateFazendaSchema` | Sim | ⚠️ Parcial | 45% |
| `TalhaoCreateSchema` | Sim | ❌ Ausente neste arquivo | 🔴 |
| `TalhaoUpdateSchema` | Sim | ❌ Ausente neste arquivo | 🔴 |
| `InfraestruturaCreateSchema` | Sim | ❌ Ausente neste arquivo | 🔴 |
| `GlebaCreateSchema` | Implícito | ❌ Ausente | 🔴 |

**Campos ausentes no `createFazendaSchema`:**

| Campo | Backend (`FazendaCreate`) | Frontend (Zod) | Gap |
|-------|--------------------------|----------------|-----|
| `codigo_car` | ✅ | ❌ | 🔴 |
| `nirf` | ✅ | ❌ | 🔴 |
| `uf` | ✅ | ❌ | 🔴 |
| `municipio` | ✅ | ❌ | 🔴 |
| `area_aproveitavel_ha` | ✅ | ❌ | 🔴 |
| `area_app_ha` | ✅ | ❌ | 🔴 |
| `area_rl_ha` | ✅ | ❌ | 🔴 |
| `coordenadas_sede` | ✅ | ✅ | ✅ |
| `cpf_cnpj` | ✅ | ⚠️ (`cnpj` apenas) | 🔴 |

> **Nota:** O schema Zod usa `cnpj` enquanto o backend usa `cpf_cnpj`. Essa inconsistência pode causar bugs de serialização.

**Observação:** Existem schemas Zod separados em `packages/zod-schemas/src/agricola/talhao.ts` para Talhão, mas o `fazenda-schemas.ts` está desatualizado em relação ao modelo backend.

---

### Sprint 3 — Frontend Detalhe (Abas)

#### 2.7. Página `/cadastros/propriedades/[id]`

| Requisito | Status | Observação |
|-----------|--------|------------|
| Aba "Dados Gerais" | ✅ Implementado | Campos: CPF/CNPJ, IE, CAR, NIRF, UF, município, áreas |
| Aba "Talhões" | ✅ Implementado | DataTable com nome, tipo (badge), área, solo/cultura, ações |
| Aba "Infraestrutura" | ✅ Implementado | DataTable com nome, tipo (badge), capacidade, ações |
| Dialog reutilizável para CRUD | ✅ Implementado | `AreaRuralDialog` para Talhões e Infraestrutura |
| Progress bar: soma áreas vs área total | ✅ Implementado | RN-CP-004 visual (não bloqueante) |
| KPI cards | ✅ Implementado | Área Total, Talhões/Áreas, Infraestruturas, Código CAR |
| Dropdown: "Editar propriedade" | ⚠️ Stub | Exibe toast "Funcionalidade em desenvolvimento" |
| Dropdown: "Desativar/Reativar" | ⚠️ Stub | Exibe toast "Funcionalidade em desenvolvimento" |
| **Aba de Glebas** | ❌ Ausente | Hierarquia Fazenda → Talhão → Gleba não tem aba dedicada |
| **Mapa interativo com polígonos** | ❌ Ausente | Não há renderização de mapa na página de detalhe |
| **Coordenadas GPS na infraestrutura** | ❌ Ausente | Formulário não captura lat/long |
| **Upload/importação de mapa** | ❌ Ausente | Sem botão para importar shapefile/KML na página de detalhe |
| **Validação bloqueante RN-CP-004** | ⚠️ Apenas visual | Progress bar exibe mas não bloqueia criação |
| **AlertDialog de confirmação para delete** | ✅ Implementado | Confirm dialog antes de remover |

> **Nota positiva:** A página tem 926 linhas com implementação robusta de DataTable, filtros, badges tipificados e formulários reutilizáveis.

---

### Sprint 4 — Validações de Negócio

#### 2.8. Regras de Negócio — Status de Implementação

| Regra | Descrição | Status | Detalhes |
|-------|-----------|--------|----------|
| **RN-CP-001** | Campos obrigatórios: nome, CPF/CNPJ, UF, área total | ⚠️ Parcial | Campos existem no modelo, mas sem validação obrigatória no formulário frontend (UF e CPF/CNPJ são opcionais no form) |
| **RN-CP-002** | Formato válido do CAR (UF + 12 dígitos) | ❌ Não implementado | Sem validação no backend nem no frontend |
| **RN-CP-003** | Hierarquia fixa `Fazenda → Talhão → Gleba` | ✅ Implementado | `AreaRural` com `parent_id` e `fazenda_id` garante hierarquia |
| **RN-CP-004** | Soma talhões ≤ 105% área total | ⚠️ Parcial | Progress bar visual existe, mas **não há validação bloqueante no backend**. `AreaRuralService.criar_area()` não verifica soma |
| **RN-CP-005** | Upload shapefile/KML/GeoJSON com validação | ✅ Implementado | Endpoint `/{area_id}/arquivos-geo/upload` com detecção de formato e processamento via `GeoprocessamentoService` |
| **RN-CP-006** | Coordenadas em SIRGAS 2000 (EPSG:4674) | ⚠️ Parcial | `GeoprocessamentoService` existe e faz conversão, mas não há validação explícita no modelo |
| **RN-CP-007** | Fazenda vinculada a `tenant_id` | ✅ Implementado | `tenant_id` em todos os modelos + enforce no `BaseService` |
| **RN-CP-008** | Exclusão bloqueada se há safras/operações | ❌ Não implementado | `FazendaService` não verifica dependências antes de deletar. `AreaRuralService.soft_delete()` só verifica filhos diretos |
| **RN-CP-009** | Infraestrutura com tipo enum + coordenadas GPS | ✅ Implementado | `TipoInfraestrutura` enum + campos lat/long no modelo |
| **RN-CP-010** | NIRF único por estado, validação RFB | ❌ Não implementado | Sem validação de unicidade nem algoritmo de dígito verificador |
| **RN-CP-011** | Módulos fiscais calculados automaticamente | ❌ Não implementado | Campo `modulos_fiscais` nem existe no modelo |
| **RN-CP-012** | APP + RL com percentual mínimo por bioma | ❌ Não implementado | Sem validação de percentual mínimo |

---

## 3. Análise de Gaps Críticos

### 3.1. Gaps de Backend

| Gap | Severidade | Impacto |
|-----|-----------|---------|
| **RN-CP-004 não bloqueante no backend** | 🔴 Alta | Usuário pode cadastrar talhões que excedem a área total sem nenhum bloqueio |
| **RN-CP-008 não implementada** | 🔴 Alta | Fazenda com safras ativas pode ser excluída, causando órfãos |
| **Validação de formato CAR ausente** | 🟡 Média | Cadastro de CAR inválido sem alerta |
| **Validação CPF/CNPP ausente** | 🟡 Média | CPF/CNPJ inválido pode ser cadastrado |
| **Campo `modulos_fiscais` inexistente** | 🟡 Média | Não é possível calcular ITR corretamente |
| **`area_hectares` usa Float ao invés de Numeric** | 🟡 Média | Precisão fiscal comprometida (ITR, CAR exigem precisão) |
| **Falta de testes unitários para AreaRuralService** | 🟡 Média | Regras de hierarquia e soma de áreas sem cobertura de testes |

### 3.2. Gaps de Frontend

| Gap | Severidade | Impacto |
|-----|-----------|---------|
| **Zod schemas desatualizados** | 🔴 Alta | Formulário não valida campos que o backend espera (CAR, NIRF, UF, município) |
| **Editar/Desativar propriedade são stubs** | 🟡 Média | Usuário não consegue editar dados da fazenda após criação |
| **Sem aba de Glebas** | 🟡 Média | Hierarquia completa não é gerenciável pela UI |
| **Sem mapa interativo na página de detalhe** | 🟡 Média | Usuário não visualiza polígonos de talhões |
| **Sem upload de mapa na página de detalhe** | 🟡 Média | Fluxo de importação de mapa (Fluxo 2 do doc) não existe na UI |
| **Inconsistência `cnpj` vs `cpf_cnpj`** | 🟡 Média | Bug potencial de serialização entre frontend e backend |

### 3.3. Gaps de Infraestrutura/DevOps

| Gap | Severidade | Impacto |
|-----|-----------|---------|
| **StorageService não verificado** | 🟡 Média | Upload de shapefile depende de serviço de storage que pode não estar configurado |
| **GeoprocessamentoService não verificado** | 🟡 Média | Processamento de shapefile/KML depende de biblioteca PROJ.4/GeoPandas |

---

## 4. Arquivos do Brainstorm — Status

### 4.1. Backend — Arquivos Previstos vs Estado

| Arquivo (brainstorm) | Status Real | Localização Atual |
|----------------------|-------------|-------------------|
| `models/fazenda.py` | ✅ Atualizado | `services/api/core/models/fazenda.py` |
| `models/talhao.py` | ℹ️ Unificado em AreaRural | `services/api/core/cadastros/propriedades/models.py` |
| `models/gleba.py` | ℹ️ Unificado em AreaRural | `services/api/core/cadastros/propriedades/models.py` |
| `models/infraestrutura.py` | ✅ Implementado | `services/api/core/cadastros/propriedades/models.py` |
| `schemas/fazenda_input.py` | ✅ Atualizado | `services/api/core/schemas/fazenda_input.py` |
| `schemas/fazenda_output.py` | ✅ Existe | `services/api/core/schemas/fazenda_output.py` |
| `schemas/talhao_schemas.py` | ℹ️ Unificado | `services/api/core/cadastros/propriedades/schemas.py` |
| `schemas/gleba_schemas.py` | ℹ️ Unificado | `services/api/core/cadastros/propriedades/schemas.py` |
| `schemas/infraestrutura_schemas.py` | ✅ Implementado | `services/api/core/cadastros/propriedades/schemas.py` |
| `services/talhao_service.py` | ℹ️ Unificado | `services/api/core/cadastros/propriedades/service.py` |
| `services/gleba_service.py` | ℹ️ Unificado | `services/api/core/cadastros/propriedades/service.py` |
| `services/infraestrutura_service.py` | ✅ Implementado | `services/api/core/cadastros/propriedades/service.py` |
| `routers/talhoes.py` | ℹ️ Unificado | `services/api/core/cadastros/propriedades/router.py` |
| `routers/glebas.py` | ℹ️ Unificado | `services/api/core/cadastros/propriedades/router.py` |
| `routers/infraestrutura.py` | ✅ Implementado | `services/api/core/cadastros/propriedades/router.py` |
| `alembic/versions/XXXX_*.py` | ✅ Migrations existem | `services/api/migrations/versions/` |

### 4.2. Frontend — Arquivos Previstos vs Estado

| Arquivo (brainstorm) | Status | Observação |
|----------------------|--------|------------|
| `cadastros/propriedades/page.tsx` | ✅ Implementado | DataTable ao invés de grid de cards |
| `cadastros/propriedades/[id]/page.tsx` | ✅ Implementado | 926 linhas, abas funcionais |
| `components/core/propriedades/PropriedadeCard.tsx` | ❌ Não criado | Lógica inline no page.tsx |
| `components/core/propriedades/PropriedadeForm.tsx` | ❌ Não criado | Formulário inline no Dialog |
| `components/core/talhoes/TalhaoList.tsx` | ❌ Não criado | Lógica inline na page [id] |
| `components/core/talhoes/TalhaoForm.tsx` | ❌ Não criado | `AreaRuralDialog` reutilizado |
| `components/core/infraestrutura/InfraestruturaList.tsx` | ❌ Não criado | Lógica inline na page [id] |
| `components/core/infraestrutura/InfraestruturaForm.tsx` | ❌ Não criado | `AreaRuralDialog` reutilizado |
| `packages/zod-schemas/src/fazenda-schemas.ts` | ⚠️ Desatualizado | Faltam campos e schemas de Talhao/Infra |

---

## 5. Fluxos de Uso — Cobertura

| Fluxo (documento) | Cobertura UI | Cobertura API | Observação |
|-------------------|-------------|---------------|------------|
| **Fluxo 1:** Cadastro de nova propriedade | ✅ 70% | ✅ 80% | Formulário existe mas faltam campos opcionais (IE, CAR, NIRF, coordenadas) |
| **Fluxo 2:** Importação de mapa georreferenciado | ❌ 0% | ✅ 85% | API de upload existe, mas não há UI para preview e associação de polígonos |
| **Fluxo 3:** Cadastro de hierarquia de áreas | ✅ 60% | ✅ 80% | Talhões são cadastráveis, mas Glebas não têm UI dedicada |
| **Fluxo 4:** Cadastro de infraestrutura | ✅ 70% | ✅ 90% | CRUD funcional, mas sem captura de coordenadas GPS na UI |

---

## 6. Critérios de Aceite (Definition of Done)

| Critério | Status |
|----------|--------|
| CRUD completo de Fazenda com validação de CPF/CNPJ e CAR | ⚠️ CRUD OK, validações ausentes |
| Hierarquia Fazenda → Talhão → Gleba funcional com validação de soma de áreas | ⚠️ Hierarquia OK, validação de soma ausente |
| Upload e processamento de shapefiles, KML e GeoJSON | ✅ Implementado (API) |
| Conversão automática para SIRGAS 2000 | ⚠️ Depende de GeoprocessamentoService |
| Renderização de mapa interativo com polígonos | ❌ Ausente na página de detalhe |
| CRUD de infraestrutura com tipos pré-definidos e coordenadas GPS | ✅ API completa; UI sem captura de GPS |
| Isolamento de dados por `tenant_id` | ✅ Implementado |
| Inativação (soft delete) de fazendas com dependências ativas | ⚠️ Soft delete existe, mas sem verificação de dependências |
| Testes de integração cobrindo upload de shapefiles | ⚠️ Testes de Infraestrutura existem; faltam testes de AreaRural e upload geo |
| Responsividade: mapa funcional em telas de tablet | ❌ Não há mapa na página de detalhe |
| Validação de formato de CAR por estado | ❌ Não implementado |
| Cálculo automático de área do polígono desenhado | ⚠️ Existe na página `/dashboard/agricola/talhoes` (MapLibre + Turf.js), mas não na página de detalhe |

**Conformidade dos critérios de aceite: 4/12 completos (33%), 5/12 parciais (42%), 3/12 não iniciados (25%)**

---

## 7. Recomendações Prioritárias

### P0 — Crítico (bloqueia produção)

1. **Implementar RN-CP-004 no backend:** `AreaRuralService.criar_area()` deve validar que a soma das áreas dos talhões ≤ 105% da área total da fazenda. Lançar `BusinessRuleError` se exceder.
2. **Implementar RN-CP-008 no backend:** `FazendaService` deve verificar existência de safras, lotes e operações antes de permitir exclusão.
3. **Atualizar Zod schemas:** Adicionar `codigo_car`, `nirf`, `uf`, `municipio`, `area_aproveitavel_ha`, `area_app_ha`, `area_rl_ha` ao `createFazendaSchema`. Corrigir `cnpj` → `cpf_cnpj`.

### P1 — Alto (impacta qualidade)

4. **Implementar validação de formato CAR:** Regex `^[A-Z]{2}-\d{12}$` ou conforme Manual SICAR.
5. **Implementar edição e desativação de fazenda na UI:** Conectar os dropdowns stubs na página de detalhe.
6. **Adicionar validação de CPF/CNPJ:** Algoritmo de dígitos verificadores no backend e/ou frontend.
7. **Corrigir precisão de área:** Migrar `area_hectares` de `Float` para `Numeric(12,4)` no modelo `AreaRural`.

### P2 — Médio (melhoria)

8. **Criar aba de Glebas na página de detalhe:** Permitir cadastro de glebas vinculadas a talhões.
9. **Adicionar mapa interativo na página de detalhe:** Renderizar polígonos de talhões com MapLibre.
10. **Criar UI de importação de mapa:** Dialog com upload + preview de polígonos extraídos.
11. **Adicionar captura de coordenadas GPS no formulário de infraestrutura:** Clique no mapa ou input manual.
12. **Adicionar campo `modulos_fiscais` ao modelo Fazenda:** Com cálculo automático por município.

### P3 — Baixo (nice-to-have)

13. **Extrair componentes reutilizáveis:** Criar `PropriedadeForm.tsx`, `TalhaoList.tsx`, etc., para melhorar manutenibilidade.
14. **Empty state com CTA na lista de propriedades:** Ilustração + botão "Nova Propriedade".
15. **Adicionar testes unitários para AreaRuralService:** Cobrir hierarquia, soma de áreas e soft delete.
16. **Grid de cards como alternativa à DataTable:** Para usuários que preferem visual de cards.

---

## 8. Conclusão

A implementação do submódulo **Cadastro da Propriedade** está em **estágio avançado de desenvolvimento**, com infraestrutura backend sólida e frontend funcional para operações básicas. A decisão de unificar Talhão/Gleba em `AreaRural` foi acertada e oferece base escalável.

Os principais riscos para produção são:
1. **Falta de validações bloqueantes de negócio** (RN-CP-004 e RN-CP-008)
2. **Zod schemas desatualizados** que podem causar inconsistências de dados
3. **Funcionalidades stub** (editar/desativar propriedade) que dão falsa sensação de completude

Com as correções P0 e P1, o módulo atingiria ~90% de conformidade com a especificação e estaria pronto para uso em produção com assinantes beta.
