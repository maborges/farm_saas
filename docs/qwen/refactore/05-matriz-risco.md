# Matriz de Risco — Refatoração Hierárquica

**Data:** 2026-04-06

---

## 1. Riscos Técnicos

| # | Risco | Probabilidade | Impacto | Severidade | Mitigação |
|---|-------|:-------------:|:-------:|:----------:|-----------|
| R-01 | Migration de colunas novas em tabela com muitos registros (>100K) | Média | Alto | 🔴 | Executar em janela de manutenção; usar `ALTER TABLE ... ADD COLUMN` (PostgreSQL 11+ é instantâneo para colunas nullable) |
| R-02 | `Safra.talhao_id` nullable quebra queries existentes que fazem JOIN | Baixa | Médio | 🟡 | Migration inclui `UPDATE safras SET talhao_id = NULL WHERE ...` não necessário — apenas tornar nullable; queries existentes com JOIN continuam funcionando |
| R-03 | Validação hierárquica bloqueia criações legítimas de dados existentes | Média | Alto | 🔴 | Validar apenas no POST (criação nova); dados existentes não são afetados; validar com query de diagnóstico antes de deploy |
| R-04 | `dados_extras` JSON existente tem schema diferente das novas colunas | Baixa | Baixo | 🟢 | Colunas novas são independentes do JSON; migração de dados pode ser feita por script posterior |
| R-05 | Query N+1 em `obter_arvore()` com muitos níveis | Alta | Médio | 🟡 | Usar `selectinload` recursivo ou CTE recursiva no PostgreSQL |
| R-06 | Frontend renderiza árvore muito profunda (>1000 nós) com lentidão | Média | Médio | 🟡 | Virtualização com `react-window`; lazy loading de nós expandidos |
| R-07 | Enum `TipoArea` com valor novo quebra enum CHECK constraint no PostgreSQL | Baixa | Alto | 🟡 | Usar `String(30)` ao invés de PostgreSQL ENUM type (já é o caso atual) |
| R-08 | `AmostraSolo` com FK `area_rural_id` nullable permite amostra "órfã" | Média | Baixo | 🟢 | Aceitável — amostra pode existir sem área vinculada (georreferenciada mas não atribuída) |

---

## 2. Riscos de Negócio

| # | Risco | Probabilidade | Impacto | Severidade | Mitigação |
|---|-------|:-------------:|:-------:|:----------:|-----------|
| R-09 | Usuário cria hierarquia incorreta antes da validação ser deployada | Baixa | Médio | 🟡 | Deploy da RF-01 é prioritário; janela entre merge e deploy é mínima |
| R-10 | Prescrição VRA por zona gera dose incorreta se soma de áreas ≠ 100% | Média | Alto | 🔴 | Validação bloqueante no backend (V-03); alerta visual no frontend |
| R-11 | Histórico de uso conflita com cultura atual do talhão | Baixa | Baixo | 🟢 | `HistoricoUsoTalhao.data_fim = NULL` define o uso atual; `cultura_atual` é denormalização para performance — reconciliar via trigger |
| R-12 | Amostra de solo desatualizada gera zona de manejo imprecisa | Média | Médio | 🟡 | Campo `data_coleta` permite filtrar por recência; alertar se > 2 anos |

---

## 3. Riscos de Regressão

| # | Módulo | O que pode quebrar | Teste de regressão |
|---|--------|-------------------|-------------------|
| R-13 | Safra | Criar safra com `talhao_id` NULL não testado | Teste: criar safra sem talhão primário, associar via SafraTalhao |
| R-14 | Operações | Operação vinculada a GLEBA era aceita, agora rejeitada | Teste: tentar criar operação com `talhao_id` = GLEBA → espera 422 |
| R-15 | Cadastro | Criar talhão sem parent_id era aceito, agora rejeitado | Teste: POST `/cadastros/areas-rurais` com `parent_id=null, tipo=TALHAO` → espera 422 |
| R-16 | Prescrição VRA | Prescrição existente com `talhao_id` de tipo inválido | Query de diagnóstico: `SELECT COUNT(*) FROM prescricoes_vra pv JOIN cadastros_areas_rurais ar ON pv.talhao_id = ar.id WHERE ar.tipo NOT IN ('TALHAO', 'PASTAGEM', 'SUBTALHAO', 'ZONA_DE_MANEJO', 'PIQUETE')` |
| R-17 | Frontend | `AreaRuralDialog` não envia campos de precisão | Teste: criar subtalhão via UI → verificar `tipo_solo`, `ph_solo` no banco |
| R-18 | Sidebar | Menu de propriedades não exibe nova aba | Teste manual: navegar para `/cadastros/propriedades/{id}` → verificar abas |

---

## 4. Matriz de rollback

| Sprint | Ponto de rollback | Como reverter | Impacto do rollback |
|--------|------------------|---------------|-------------------|
| RF-01 | Migration de enum + colunas | `alembic downgrade -1` | Nenhum dado perdido (colunas novas são nullable) |
| RF-02 | Tabelas `HistoricoUsoTalhao` + `AmostraSolo` | `alembic downgrade -1` | Dados de histórico e amostras são perdidos (tabelas novas) |
| RF-03 | Campo `nivel_area` em `PrescricaoVRA` | `alembic downgrade -1` | Nenhum dado perdido |
| RF-04 | Campo `objetivo_economico` em `Safra` | `alembic downgrade -1` | Nenhum dado perdido |

---

## 5. Script de Diagnóstico Pré-Deploy

Executar ANTES de cada deploy para detectar dados inconsistentes:

```sql
-- 1. Áreas com hierarquia inválida
SELECT ar.id, ar.nome, ar.tipo, ar.parent_id, pai.tipo as tipo_pai
FROM cadastros_areas_rurais ar
LEFT JOIN cadastros_areas_rurais pai ON ar.parent_id = pai.id
WHERE pai.tipo IS NOT NULL
  AND ar.tipo NOT IN (
    CASE pai.tipo
      WHEN 'PROPRIEDADE' THEN ANY(ARRAY['GLEBA','TALHAO','PASTAGEM','APP','RESERVA_LEGAL','UNIDADE_PRODUTIVA','SEDE','ARMAZEM','INFRAESTRUTURA','AREA'])
      WHEN 'GLEBA' THEN ANY(ARRAY['TALHAO','PASTAGEM','APP','RESERVA_LEGAL','AREA'])
      WHEN 'TALHAO' THEN ANY(ARRAY['SUBTALHAO','PIQUETE'])
      -- ... etc
    END
  );

-- 2. Operações com talhao_id de tipo inválido
SELECT oa.id, oa.safra_id, oa.talhao_id, ar.tipo
FROM operacoes_agricolas oa
JOIN cadastros_areas_rurais ar ON oa.talhao_id = ar.id
WHERE ar.tipo NOT IN ('TALHAO', 'PASTAGEM', 'PIQUETE');

-- 3. Prescrições VRA com area de tipo inválido
SELECT pv.id, pv.talhao_id, ar.tipo
FROM prescricoes_vra pv
JOIN cadastros_areas_rurais ar ON pv.talhao_id = ar.id
WHERE ar.tipo NOT IN ('TALHAO', 'PASTAGEM', 'PIQUETE', 'SUBTALHAO', 'ZONA_DE_MANEJO');

-- 4. Safras com talhao_id pointing to non-talhao types
SELECT s.id, s.talhao_id, ar.tipo
FROM safras s
JOIN cadastros_areas_rurais ar ON s.talhao_id = ar.id
WHERE ar.tipo NOT IN ('TALHAO', 'PASTAGEM', 'PIQUETE');
```

---

## 6. Check-list de Deploy

### Pré-deploy
- [ ] Script de diagnóstico executado — zero resultados inesperados
- [ ] Migration testada em staging com dados de produção (clone anonimizado)
- [ ] Rollback testado em staging
- [ ] Todos os testes unitários passando (>90% coverage)
- [ ] Lint/typecheck sem erros
- [ ] Review de código aprovado por 2 devs

### Durante deploy
- [ ] Migration aplicada (`alembic upgrade head`)
- [ ] Backend deployado
- [ ] Health check passa (`GET /health`)
- [ ] Smoke test: criar subtalhão via API
- [ ] Frontend deployado
- [ ] Smoke test: abrir página de hierarquia

### Pós-deploy (24h)
- [ ] Monitorar logs por `BusinessRuleError` de hierarquia (deve ser >0 se usuários criam áreas)
- [ ] Monitorar taxa de erro 422 em `/cadastros/areas-rurais` (pico esperado)
- [ ] Verificar métricas de performance (p95 < 500ms para `/arvore`)
- [ ] Suporte preparado para tickets sobre "não consigo criar X dentro de Y"
