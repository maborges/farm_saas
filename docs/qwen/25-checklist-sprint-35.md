# ✅ Checklist - Início da Sprint 35

**Data de Início:** 2026-07-01
**Sprint:** 35
**Fase:** 4 - Polimento e Lançamento

---

## 📋 CHECKLIST DE INÍCIO DE SPRINT

### Pré-Sprint (2026-03-31)

#### Documentação
- [x] Status da Fase 4 criado (`20-status-fase-4.md`)
- [x] Sprint 35 Kickoff criado (`21-sprint-35-kickoff.md`)
- [x] Guia de Performance criado (`22-guia-performance-profiling.md`)
- [x] Template de Relatório criado (`23-template-relatorio-performance.md`)
- [x] Script de Baseline criado (`scripts/performance_baseline.py`)
- [ ] Índice mestre atualizado

#### Setup Técnico
- [ ] PostgreSQL configurado com pg_stat_statements
- [ ] Query logging habilitado (>500ms)
- [ ] Redis instalado e configurado em staging
- [ ] Scripts de baseline testados

#### Time
- [ ] Sprint 35 apresentada ao time
- [ ] Responsabilidades definidas
- [ ] Capacidade da sprint confirmada (62 pontos)

---

## 🗓️ CHECKLIST DIÁRIO - SEMANA 1

### Dia 1 (2026-07-01) - Setup e Baseline

#### Manhã
- [ ] Configurar pg_stat_statements no banco de dados
```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
ALTER SYSTEM SET log_min_duration_statement = 500;
SELECT pg_reload_conf();
```

- [ ] Verificar se query logging está ativo
```sql
SHOW log_min_duration_statement;
-- Deve retornar: 500
```

- [ ] Testar script de baseline
```bash
cd services/api
python scripts/performance_baseline.py
```

#### Tarde
- [ ] Executar baseline de performance
- [ ] Coletar top 20 queries mais lentas
- [ ] Salvar relatório JSON e texto
- [ ] Documentar tempos atuais (baseline)

#### Fim do Dia
- [ ] Daily standup realizada
- [ ] Progresso atualizado no quadro
- [ ] Impedimentos reportados

**Status do Dia:** ⬜ Não iniciado | 🟡 Em andamento | ✅ Concluído

---

### Dia 2 (2026-07-02) - Análise de Queries Lentas

#### Manhã
- [ ] Abrir relatório de baseline
- [ ] Selecionar top 10 queries para analisar
- [ ] Executar EXPLAIN ANALYZE em cada query

#### Tarde
- [ ] Identificar tipo de scan (Seq vs Index)
- [ ] Identificar gargalos (joins, sorts, aggregations)
- [ ] Listar índices candidatos
- [ ] Priorizar otimizações por impacto

#### Fim do Dia
- [ ] Lista de otimizações priorizada
- [ ] Plano de ação para Dia 3-4 definido

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 3 (2026-07-03) - Otimização Financeiro (Parte 1)

#### Manhã
- [ ] Analisar query do dashboard financeiro
- [ ] Criar índice para tenant_id + data
- [ ] Testar melhoria com EXPLAIN ANALYZE

#### Tarde
- [ ] Analisar query de lançamentos por categoria
- [ ] Criar índice para categoria_id
- [ ] Otimizar join se necessário

#### Fim do Dia
- [ ] Medir melhoria de performance
- [ ] Documentar otimizações

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 4 (2026-07-04) - Otimização Financeiro (Parte 2)

#### Manhã
- [ ] Otimizar query de fluxo de caixa
- [ ] Otimizar query de conciliação bancária
- [ ] Criar índices restantes

#### Tarde
- [ ] Validar todas queries financeiras < 200ms
- [ ] Documentar otimizações do financeiro
- [ ] Preparar migration de índices

#### Fim do Dia
- [ ] Módulo financeiro otimizado
- [ ] Índices documentados

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 5 (2026-07-05) - Otimização Agrícola (Parte 1)

#### Manhã
- [ ] Analisar query de safras por cultura
- [ ] Criar índice para tenant_id + ano_safra
- [ ] Testar melhoria

#### Tarde
- [ ] Analisar query de operações agrícolas
- [ ] Criar índice para safra_id
- [ ] Otimizar query de agregação de custo

#### Fim do Dia
- [ ] Medir melhoria de performance
- [ ] Documentar otimizações

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 6 (2026-07-06) - Otimização Agrícola (Parte 2)

#### Manhã
- [ ] Otimizar query de romaneios de colheita
- [ ] Otimizar query de produtividade
- [ ] Criar índices restantes

#### Tarde
- [ ] Validar todas queries agrícolas < 200ms
- [ ] Documentar otimizações do agrícola
- [ ] Atualizar migration de índices

#### Fim do Dia
- [ ] Módulo agrícola otimizado
- [ ] Índices documentados

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 7 (2026-07-07) - Review Semana 1

#### Manhã
- [ ] Revisar otimizações implementadas
- [ ] Comparar baseline antes/depois
- [ ] Identificar ajustes necessários

#### Tarde
- [ ] Planejar otimizações da pecuária (Semana 2)
- [ ] Planejar implementação do Redis (Semana 2)
- [ ] Atualizar status da sprint

#### Fim do Dia
- [ ] Review da Semana 1 realizada
- [ ] Plano da Semana 2 definido
- [ ] Status atualizado no `20-status-fase-4.md`

**Status do Dia:** ⬜ | 🟡 | ✅

---

## 🗓️ CHECKLIST DIÁRIO - SEMANA 2

### Dia 8 (2026-07-08) - Otimização Pecuária (Parte 1)

#### Manhã
- [ ] Analisar query de rebanho por categoria
- [ ] Criar índice para tenant_id + categoria
- [ ] Testar melhoria

#### Tarde
- [ ] Analisar query de movimentação de animais
- [ ] Criar índice para animal_id
- [ ] Otimizar query de pesagem

#### Fim do Dia
- [ ] Medir melhoria de performance
- [ ] Documentar otimizações

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 9 (2026-07-09) - Otimização Pecuária (Parte 2)

#### Manhã
- [ ] Otimizar query de confinamento
- [ ] Otimizar query de dieta/TMR
- [ ] Otimizar query de curva de lactação

#### Tarde
- [ ] Validar todas queries de pecuária < 200ms
- [ ] Documentar otimizações da pecuária
- [ ] Completar migration de índices

#### Fim do Dia
- [ ] Módulo pecuária otimizado
- [ ] Todos índices documentados

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 10 (2026-07-10) - Cache Redis (Parte 1)

#### Manhã
- [ ] Configurar Redis connection pool
- [ ] Implementar cache para safras (TTL: 5min)
- [ ] Testar cache de safras

#### Tarde
- [ ] Implementar cache para estoque (TTL: 2min)
- [ ] Testar cache de estoque
- [ ] Medir hit rate do cache

#### Fim do Dia
- [ ] Cache de safras e estoque implementado
- [ ] Hit rate > 80%

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 11 (2026-07-11) - Cache Redis (Parte 2)

#### Manhã
- [ ] Implementar cache para financeiro (TTL: 1min)
- [ ] Implementar cache para dashboard
- [ ] Testar cache financeiro

#### Tarde
- [ ] Documentar estrutura de chaves Redis
- [ ] Documentar TTLs configurados
- [ ] Validar consistência de dados

#### Fim do Dia
- [ ] Cache financeiro implementado
- [ ] Documentação completa

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 12 (2026-07-12) - Cache Invalidation

#### Manhã
- [ ] Implementar invalidation on write (safras)
- [ ] Implementar invalidation on write (estoque)
- [ ] Implementar invalidation on write (financeiro)

#### Tarde
- [ ] Testar cenários de inconsistência
- [ ] Ajustar TTLs conforme necessidade
- [ ] Validar consistência de dados

#### Fim do Dia
- [ ] Cache invalidation configurado
- [ ] Testes de inconsistência passing

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 13 (2026-07-13) - Testes de Performance

#### Manhã
- [ ] Executar testes de carga
- [ ] Medir response time de todas queries
- [ ] Identificar queries ainda lentas

#### Tarde
- [ ] Ajustar otimizações pendentes
- [ ] Re-executar testes
- [ ] Validar meta: 90% < 200ms

#### Fim do Dia
- [ ] Testes de carga executados
- [ ] Performance validada

**Status do Dia:** ⬜ | 🟡 | ✅

---

### Dia 14 (2026-07-14) - Sprint Review

#### Manhã
- [ ] Gerar relatório final de performance
- [ ] Documentar melhorias alcançadas
- [ ] Atualizar documentação

#### Tarde
- [ ] Sprint Review
- [ ] Sprint Retrospective
- [ ] Planejamento Sprint 36

#### Fim do Dia
- [ ] Relatório final salvo (`23-template-relatorio-performance.md`)
- [ ] Sprint Review realizada
- [ ] Sprint 35 encerrada

**Status do Dia:** ⬜ | 🟡 | ✅

---

## 📊 STATUS DIÁRIO DA SPRINT

### Template de Daily Standup

```
Data: 2026-07-__

Participantes:
- Backend: ___
- QA: ___
- DevOps: ___

Feito Ontem:
- 

Plano para Hoje:
- 

Impedimentos:
- 

Métricas do Dia:
- Queries otimizadas: __
- Índices criados: __
- Cache implementado: __
```

---

## ✅ CRITÉRIOS DE PRONTO DA SPRINT 35

### Entregáveis
- [ ] Relatório de baseline gerado
- [ ] Top 20 queries lentas identificadas
- [ ] 10+ queries otimizadas
- [ ] 15+ índices criados
- [ ] Cache Redis implementado
- [ ] Cache invalidation configurado
- [ ] Testes de performance passing
- [ ] Relatório final de performance

### Performance
- [ ] 90% das queries < 200ms
- [ ] Queries do financeiro < 200ms
- [ ] Queries do agrícola < 200ms
- [ ] Queries da pecuária < 200ms
- [ ] Cache hit rate > 80%

### Documentação
- [ ] Índices documentados
- [ ] Estrutura de chaves Redis documentada
- [ ] Otimizações documentadas
- [ ] Relatório final salvo

---

## 🔗 LINKS RELACIONADOS

- [Status da Fase 4](20-status-fase-4.md)
- [Sprint 35 Kickoff](21-sprint-35-kickoff.md)
- [Guia de Performance](22-guia-performance-profiling.md)
- [Template de Relatório](23-template-relatorio-performance.md)
- [Script de Baseline](../../services/api/scripts/performance_baseline.py)

---

**Scrum Master:** _______________________
**Data:** 2026-07-01

**Tech Lead:** _______________________
**Data:** 2026-07-01

---

**Próxima Atualização:** Diariamente durante a Sprint 35
**Status Atual:** 🟡 Em Andamento
