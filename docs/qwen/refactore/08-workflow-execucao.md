# Workflow de Execução — Refatoração Hierárquica

**Data:** 2026-04-06
**Modelo:** Git Feature Branches + PRs + Deploy por Sprint

---

## 1. Visão Geral do Workflow

```
main
 │
 ├── feature/rf01-hierarquia-base          ← RF-01 (backend)
 │    ├── feature/rf01-hierarquia-ui       ← RF-01 (frontend)
 │    └── feature/rf01-custeio-fix         ← CF-01 a CF-04 (crítico)
 │
 ├── feature/rf02-dados-precisao           ← RF-02 (backend)
 │    ├── feature/rf02-dados-precisao-ui   ← RF-02 (frontend)
 │    └── feature/rf02-safra-talhao-null   ← A-01, A-02
 │
 ├── feature/rf03-vra-por-zona             ← RF-03 (backend + frontend)
 │
 └── feature/rf04-indicadores              ← RF-04 (backend + frontend, paralelo)
```

**Regra de ouro:** Cada PR é mergeável independentemente. Nada bloqueia o main.

---

## 2. Pré-requisitos (antes de começar)

### 2.1. Ambiente

```bash
# Garantir que o ambiente local está funcional
cd /opt/lampp/htdocs/farm

# Backend
cd services/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # ou poetry install
alembic current                   # Verificar estado das migrations
pytest --co -q                    # Listar testes existentes

# Frontend
cd apps/web
pnpm install
pnpm typecheck                    # Zero erros
pnpm build                        # Build limpo

# Banco
# Garantir que PostgreSQL está rodando com dados de teste
```

### 2.2. Snapshot de segurança

```bash
# Backup do banco antes de qualquer migration
pg_dump -U pguser -d agrosaas -F c -f /tmp/agrosaas_pre_rf_snapshot.dump

# Tag git no estado atual
git tag -a rf-start-$(date +%Y%m%d) -m "Snapshot antes da refatoração hierárquica"
git push origin --tags
```

### 2.3. Script de diagnóstico

Executar **ANTES** de qualquer mudança para documentar o estado atual:

```sql
-- Salvar em /tmp/diagnostico_pre_rf.sql

-- 1. Contagem de AreaRural por tipo
SELECT tipo, COUNT(*) FROM cadastros_areas_rurais GROUP BY tipo ORDER BY COUNT(*) DESC;

-- 2. Áreas com parent_id (quantos níveis de hierarquia existem?)
SELECT COUNT(*) as total, COUNT(parent_id) as com_pai, COUNT(*) - COUNT(parent_id) as sem_pai
FROM cadastros_areas_rurais WHERE ativo = true;

-- 3. Operações com talhao_id de tipo incomum
SELECT ar.tipo, COUNT(*) FROM operacoes_agricolas oa
JOIN cadastros_areas_rurais ar ON oa.talhao_id = ar.id GROUP BY ar.tipo;

-- 4. Prescrições VRA com tipo de área
SELECT ar.tipo, COUNT(*) FROM prescricoes_vra pv
JOIN cadastros_areas_rurais ar ON pv.talhao_id = ar.id GROUP BY ar.tipo;

-- 5. Safras com talhao_id non-null (quantas usam o campo legado?)
SELECT COUNT(*) as total, COUNT(talhao_id) as com_talhao FROM safras;

-- 6. Despesas de origem OPERACAO_AGRICOLA com e sem rateio
SELECT COUNT(*) as total_despesas,
       (SELECT COUNT(*) FROM fin_rateios r JOIN fin_despesas d ON r.despesa_id = d.id
        WHERE d.origem_tipo = 'OPERACAO_AGRICOLA') as com_rateio
FROM fin_despesas WHERE origem_tipo = 'OPERACAO_AGRICOLA';
```

---

## 3. Workflow por Sprint

### Sprint RF-01: Fundação Territorial

#### Passo 1: Branch backend

```bash
git checkout -b feature/rf01-hierarquia-base
```

#### Passo 2: Modelos + Migration (ordem de execução)

```
1. Editar models.py (cadastros/propriedades/)
   ├── Adicionar SUBTALHAO, ZONA_DE_MANEJO ao enum TipoArea
   ├── Adicionar 11 colunas de precisão ao AreaRural
   └── Adicionar nivel_profundidade

2. Criar migration
   alembic revision -m "add_hierarquia_precisao_tipos_e_colunas"
   # Editar upgrade/downgrade com ALTER TABLE ADD COLUMN

3. Testar migration local
   alembic upgrade head
   alembic downgrade -1
   alembic upgrade head  # Re-aplicar
```

**Commit:** `feat(cadastros): adicionar SUBTALHAO, ZONA_DE_MANEJO e colunas de precisão`

#### Passo 3: Service + Validação

```
4. Editar service.py (cadastros/propriedades/)
   ├── Adicionar HIERARQUIA_VALIDA dict
   ├── Adicionar NIVEL_PROFUNDO dict
   ├── Implementar validar_hierarquia()
   ├── Implementar calcular_soma_areas()
   └── Implementar obter_arvore()

5. Editar router.py
   ├── Aplicar validar_hierarquia() no POST
   ├── Adicionar GET /{area_id}/arvore
   └── Adicionar GET /{area_id}/soma-areas
```

**Commit:** `feat(cadastros): validação hierárquica e endpoints de árvore`

#### Passo 4: Schemas + Validação RN-CP-004

```
6. Editar schemas.py
   ├── Expandir AreaRuralCreate com campos de precisão
   ├── Expandir AreaRuralUpdate com campos de precisão
   └── Criar HistoricoUsoCreate/Response (preparação RF-02)

7. Implementar RN-CP-004 no service
   └── Bloquear soma > 105% no criar_area()
```

**Commit:** `feat(cadastros): schemas de precisão e validação RN-CP-004`

#### Passo 5: Testes

```
8. Criar testes unitários
   ├── test_validar_hierarquia_cenario_valido
   ├── test_validar_hierarquia_cenario_invalido
   ├── test_calcular_soma_areas
   └── test_rn_cp_004_bloqueio

9. Criar teste de integração
   └── test_criar_area_com_validacao_hierarquica

10. Rodar suite completa
    pytest services/api/tests/ -v --tb=short
    # Todos devem passar
```

**Commit:** `test(cadastros): testes de validação hierárquica e RN-CP-004`

#### Passo 6: Branch frontend

```bash
git checkout -b feature/rf01-hierarquia-ui
```

#### Passo 7: Zod schemas + UI

```
11. Atualizar Zod schemas
    └── packages/zod-schemas/src/fazenda-schemas.ts

12. Criar componentes
    ├── components/core/areas/AreaTree.tsx
    └── components/core/areas/AreaTreeItem.tsx

13. Integrar na página de detalhe
    └── Nova aba "Hierarquia" em cadastros/propriedades/[id]/page.tsx

14. Integrar RN-CP-004 visual bloqueante
    └── Progress bar vermelha quando > 105%
```

**Commits:**
- `feat(ui): Zod schemas atualizados com campos de precisão`
- `feat(ui): componente AreaTree com hierarquia expansível`
- `feat(ui): aba Hierarquia na página de detalhe`
- `feat(ui): RN-CP-004 bloqueante no frontend`

#### Passo 8: PR + Review + Merge

```bash
# Push das branches
git push origin feature/rf01-hierarquia-base
git push origin feature/rf01-hierarquia-ui

# Criar PRs no GitHub/GitLab
# PR 1: Backend (feature/rf01-hierarquia-base → main)
# PR 2: Frontend (feature/rf01-hierarquia-ui → main)

# Após aprovação, merge em ordem:
# 1. Backend primeiro (migrações)
# 2. Frontend depois (depende de novos endpoints)
```

#### Passo 9: Deploy RF-01

```bash
# 1. Deploy backend
git checkout main && git pull
cd services/api
alembic upgrade head

# 2. Verificar migration
alembic current
# Deve mostrar a migration nova

# 3. Smoke test
curl http://localhost:8000/api/v1/cadastros/areas-rurais/?apenas_raizes=true
# Deve retornar 200

# 4. Smoke test: criar subtalhão
curl -X POST http://localhost:8000/api/v1/cadastros/areas-rurais/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste Subtalhão","tipo":"SUBTALHAO","fazenda_id":"...","parent_id":"UUID_DO_TALHAO"}'
# Deve retornar 201

# 5. Smoke test: hierarquia inválida
curl -X POST http://localhost:8000/api/v1/cadastros/areas-rurais/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste","tipo":"TALHAO","fazenda_id":"...","parent_id":null}'
# Deve retornar 422 com BusinessRuleError

# 6. Deploy frontend
cd apps/web
pnpm build && pnpm start

# 7. Teste visual
# Abrir /cadastros/propriedades/[id] → aba Hierarquia
# Deve mostrar árvore expansível
```

---

### Sprint RF-02: Dados de Precisão + Histórico

Mesmo workflow, branches paralelas:

```
feature/rf02-dados-precisao           ← Modelos, migration, schemas
feature/rf02-dados-precisao-ui        ← Componentes UI
feature/rf02-safra-talhao-null        ← A-01, A-02 (independente)
```

**Ordem de merge:**
1. `rf02-safra-talhao-null` (migração isolada, sem conflito)
2. `rf02-dados-precisao` (backend)
3. `rf02-dados-precisao-ui` (frontend)

**Verificação crítica pós-merge RF-02:**
```sql
-- Confirmar que tabelas novas existem
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('cadastros_areas_historico_uso', 'cadastros_amostras_solo');

-- Confirmar que Safra.talhao_id é nullable
SELECT is_nullable FROM information_schema.columns
WHERE table_name = 'safras' AND column_name = 'talhao_id';
-- Deve retornar 'YES'
```

---

### Sprint RF-03: VRA por Zona + Polimento

Branch única (frontend e backend são acoplados):

```
feature/rf03-vra-por-zona
├── Backend: validação VRA, campo nivel_area, endpoint /por-zona
└── Frontend: ZonaManejoDialog, mapa de prescrição, polimento UI
```

---

### Sprint RF-04: Indicadores + Polimento

Pode rodar **em paralelo** com RF-02 e RF-03:

```
feature/rf04-indicadores
├── Backend: margem, ROI, comparativo inter-safras
└── Frontend: UI de indicadores, comparativo
```

---

## 4. Fluxo de Commit (Conventional Commits)

| Prefixo | Quando usar | Exemplo |
|---------|------------|---------|
| `feat(cadastros)` | Nova funcionalidade no cadastro | `feat(cadastros): adicionar SUBTALHAO e ZONA_DE_MANEJO` |
| `feat(ui)` | Nova funcionalidade no frontend | `feat(ui): componente AreaTree com hierarquia` |
| `fix(cadastros)` | Bug fix no backend | `fix(cadastros): corrigir soma de áreas no obter_arvore` |
| `fix(ui)` | Bug fix no frontend | `fix(ui): corrigir renderização de nós folha na árvore` |
| `test(cadastros)` | Testes novos | `test(cadastros): validação hierárquica com 10 cenários` |
| `refactor(cadastros)` | Refatoração sem mudança funcional | `refactor(cadastros): extrair HIERARQUIA_VALIDA para módulo separado` |
| `perf(cadastros)` | Otimização | `perf(cadastros): evitar N+1 em obter_arvore com selectinload` |
| `docs` | Documentação | `docs: adicionar workflow de execução da refatoração` |
| `chore` | Infra/tooling | `chore: adicionar script de diagnóstico pré-deploy` |

---

## 5. Pipeline de CI/CD (por PR)

Cada PR deve passar por:

```
PR aberto
   │
   ├── ✅ Lint (ruff check + ruff format)
   ├── ✅ Type check (mypy services/api/)
   ├── ✅ Type check (tsc apps/web/)
   ├── ✅ Build (pnpm build)
   ├── ✅ Testes unitários (pytest --cov=80%)
   ├── ✅ Testes de integração (pytest tests/integration/)
   ├── ✅ Migration check (alembic check — conflitos)
   │
   ├── 👀 Code review (mínimo 1 approver)
   │
   └── ✅ Merge → main
         │
         ├── Deploy staging
         │    ├── Smoke tests automáticos
         │    └── Health check
         │
         └── Deploy production (após staging OK)
              ├── alembic upgrade head
              ├── Smoke tests
              └── Monitorar logs por 24h
```

---

## 6. Rollback (se algo der errado)

### Cenário A: Migration falha

```bash
# Imediatamente após falha
alembic downgrade -1
# Verifica que voltou ao estado anterior
alembic current
```

### Cenário B: Bug crítico após deploy

```bash
# Reverter o merge no git
git revert <commit-hash> --no-edit
git push origin main

# Se foi migration, fazer downgrade
alembic downgrade -1
```

### Cenário C: Bug só no frontend

```bash
# Reverter deploy do frontend
git revert <commit-hash> --no-edit
git push origin main
# Re-deploy frontend
cd apps/web && pnpm build && pnpm start
```

---

## 7. Checklist de Progresso por Sprint

### RF-01

- [ ] Branch backend criada
- [ ] Enum `TipoArea` com SUBTALHAO + ZONA_DE_MANEJO
- [ ] Colunas de precisão adicionadas ao modelo
- [ ] Migration criada e testada (up + down)
- [ ] `validar_hierarquia()` implementada
- [ ] Router com validação no POST
- [ ] Endpoint `/arvore` funcional
- [ ] Endpoint `/soma-areas` funcional
- [ ] RN-CP-004 bloqueante no backend
- [ ] Testes unitários passando (>90% coverage)
- [ ] PR backend aprovado e merged
- [ ] Zod schemas atualizados
- [ ] `AreaTree.tsx` criado e funcional
- [ ] Aba "Hierarquia" na página de detalhe
- [ ] RN-CP-004 visual bloqueante no frontend
- [ ] PR frontend aprovado e merged
- [ ] Deploy staging OK
- [ ] Smoke tests passando
- [ ] Deploy production OK
- [ ] Monitoramento 24h sem erros novos

### RF-02

- [ ] Modelo `HistoricoUsoTalhao` criado
- [ ] Modelo `AmostraSolo` criado
- [ ] Migration criada e testada
- [ ] Endpoints de histórico e amostras
- [ ] `Safra.talhao_id` nullable
- [ ] `OperacaoAgricola.talhao_id` restrito a tipos válidos
- [ ] Componentes UI de timeline e mapa de amostras
- [ ] Editar/Desativar propriedade funcionais
- [ ] Testes passando
- [ ] Deploy OK

### RF-03

- [ ] Prescrição VRA por zona funcional
- [ ] Validação soma de áreas das zonas
- [ ] Mapa de prescrição colorido
- [ ] Upload de grade GeoJSON
- [ ] Polimento UI (editar, excluir, empty state, validação CAR)
- [ ] Testes passando
- [ ] Deploy OK

### RF-04

- [ ] Margem líquida e ROI por safra
- [ ] Comparativo inter-safras
- [ ] Adapter de custos agrícola + pecuária
- [ ] Documentação Swagger atualizada
- [ ] Zero bugs Alta/Crítica abertos
- [ ] UI responsiva em tablet
- [ ] Queries N+1 eliminadas
- [ ] Deploy OK

---

## 8. Rituais Sugeridos

| Ritual | Frequência | Duração | Participantes |
|--------|-----------|---------|--------------|
| Daily | Diária | 15min | Devs |
| Review de PR | Por PR | 30min | Dev + Reviewer |
| Demo de Sprint | Final de sprint | 1h | Time + Stakeholders |
| Retrospectiva | Final de sprint | 45min | Time |
| Planejamento próxima sprint | Final de sprint | 1h | Tech Lead + PO |

---

## 9. Métricas de Sucesso

| Métrica | Meta | Como medir |
|---------|------|-----------|
| Zero regressões | Nenhum bug reportado em funcionalidades existentes | Issue tracker |
| Coverage > 85% | `pytest --cov` | CI pipeline |
| Type check limpo | Zero erros TypeScript + Python | CI pipeline |
| p95 < 500ms | Endpoint `/arvore` < 500ms | Monitoring |
| Deploy sem rollback | Todas as 4 sprints sem rollback | Git history |
| UX responsivo | Funcional em 1024px (tablet) | Teste manual |
