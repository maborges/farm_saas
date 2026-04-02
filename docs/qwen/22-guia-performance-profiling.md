# 🔍 Guia de Performance Profiling - PostgreSQL

**Versão:** 1.0
**Data:** 2026-03-31
**Status:** ✅ Pronto para uso

---

## 📋 VISÃO GERAL

Este guia fornece instruções passo-a-passo para identificar, analisar e otimizar queries lentas no PostgreSQL.

---

## 🛠️ SETUP INICIAL

### 1. Habilitar pg_stat_statements

```sql
-- Conectar ao banco como superuser
psql -U postgres -d agrosaas

-- Criar extensão pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verificar se foi instalado
SELECT * FROM pg_stat_statements LIMIT 1;
```

### 2. Configurar Query Logging

```sql
-- Habilitar logging de queries lentas (>500ms)
ALTER SYSTEM SET log_min_duration_statement = 500;

-- Recarregar configuração
SELECT pg_reload_conf();

-- Verificar configuração
SHOW log_min_duration_statement;
```

### 3. Configurar PostgreSQL para Performance

```sql
-- Ajustar shared_buffers (25% da RAM)
ALTER SYSTEM SET shared_buffers = '2GB';

-- Ajustar work_mem (para sorting e hash joins)
ALTER SYSTEM SET work_mem = '64MB';

-- Ajustar effective_cache_size (50-75% da RAM)
ALTER SYSTEM SET effective_cache_size = '6GB';

-- Habilitar auto-explain para queries lentas
LOAD 'auto_explain';
SET auto_explain.log_min_duration = '500ms';
SET auto_explain.log_analyze = 'on';
SET auto_explain.log_buffers = 'on';
```

---

## 📊 IDENTIFICANDO QUERIES LENTAS

### Top 20 Queries Mais Lentas (Tempo Médio)

```sql
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### Top 20 Queries Mais Lentas (Tempo Total)

```sql
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

### Queries Mais Executadas

```sql
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;
```

### Queries com Maior Impacto (calls × mean_time)

```sql
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time,
    (calls * mean_exec_time) as impact_score
FROM pg_stat_statements
ORDER BY impact_score DESC
LIMIT 20;
```

---

## 🔍 ANALISANDO QUERIES COM EXPLAIN ANALYZE

### Sintaxe Básica

```sql
EXPLAIN ANALYZE
SELECT * FROM tabela WHERE condicao;
```

### Exemplo Prático - Query Financeira

```sql
EXPLAIN ANALYZE
SELECT 
    f.id,
    f.descricao,
    f.valor,
    f.data_vencimento,
    c.nome as categoria
FROM financeiro_lancamentos f
JOIN financeiro_categorias c ON f.categoria_id = c.id
WHERE f.tenant_id = 'uuid-do-tenant'
  AND f.data_vencimento >= '2026-01-01'
  AND f.data_vencimento <= '2026-12-31'
ORDER BY f.data_vencimento DESC;
```

### Exemplo Prático - Query Agrícola

```sql
EXPLAIN ANALYZE
SELECT 
    s.id,
    s.nome,
    s.cultura,
    s.ano_safra,
    SUM(o.custo) as custo_total
FROM agricola_safras s
LEFT JOIN agricola_operacoes o ON o.safra_id = s.id
WHERE s.tenant_id = 'uuid-do-tenant'
  AND s.ano_safra = '2025/26'
GROUP BY s.id, s.nome, s.cultura, s.ano_safra;
```

### Exemplo Prático - Query Pecuária

```sql
EXPLAIN ANALYZE
SELECT 
    p.categoria,
    COUNT(*) as total_animais,
    AVG(p.peso) as peso_medio,
    SUM(p.peso) as peso_total
FROM pecuaria_animais p
WHERE p.tenant_id = 'uuid-do-tenant'
  AND p.status = 'ATIVO'
GROUP BY p.categoria;
```

---

## 📖 LENDO O PLANO DE EXECUÇÃO

### Elementos do Explain Analyze

```
Seq Scan on tabela  (cost=0.00..100.00 rows=1000 width=100) (actual time=0.5..10.5 ms rows=1000 loops=1)
  Filter: (condicao = 'valor')
  Rows Removed by Filter: 5000
```

### Componentes

| Elemento | Significado |
|----------|-------------|
| **Seq Scan** | Scan sequencial (ruim para tabelas grandes) |
| **Index Scan** | Scan usando índice (bom) |
| **Index Only Scan** | Scan apenas no índice (ótimo) |
| **Bitmap Heap Scan** | Scan usando bitmap de índices |
| **Nested Loop** | Join com loop aninhado (bom para poucas rows) |
| **Hash Join** | Join usando hash table (bom para médias) |
| **Merge Join** | Join usando merge sort (bom para grandes) |
| **cost=0.00..100.00** | Custo estimado (inicial..final) |
| **actual time=0.5..10.5** | Tempo real (startup..total) |
| **rows=1000** | Linhas retornadas |
| **loops=1** | Quantas vezes executado |

### O Que Procurar

🔴 **Problemas Críticos:**
- `Seq Scan` em tabelas grandes (>10k rows)
- `actual time` alto (>100ms)
- `Rows Removed by Filter` alto (muitas rows descartadas)
- `Buffers: hit=1000 read=500` (muitas leituras de disco)

🟡 **Atenção:**
- `Nested Loop` com muitas iterações
- `Sort` sem índice (usando disk)
- `Hash Join` com hash grande

🟢 **Bom:**
- `Index Scan` ou `Index Only Scan`
- `actual time` baixo (<50ms)
- Poucas rows removidas pelo filter
- `Buffers: hit=100 read=0` (tudo em cache)

---

## 🎯 OTIMIZANDO QUERIES

### 1. Criar Índices Estratégicos

```sql
-- Índice simples para filtro comum
CREATE INDEX idx_financeiro_tenant ON financeiro_lancamentos(tenant_id);

-- Índice composto para filtro + ordenação
CREATE INDEX idx_financeiro_tenant_data 
ON financeiro_lancamentos(tenant_id, data_vencimento DESC);

-- Índice para join
CREATE INDEX idx_financeiro_categoria ON financeiro_lancamentos(categoria_id);

-- Índice parcial (apenas rows ativas)
CREATE INDEX idx_animais_ativos ON pecuaria_animais(tenant_id) 
WHERE status = 'ATIVO';

-- Índice para agregação
CREATE INDEX idx_safras_ano ON agricola_safras(tenant_id, ano_safra);
```

### 2. Reescrever Queries

#### Antes (Lento)
```sql
SELECT * FROM financeiro_lancamentos
WHERE DATE(data_vencimento) >= '2026-01-01'
  AND DATE(data_vencimento) <= '2026-12-31';
```

#### Depois (Rápido)
```sql
SELECT * FROM financeiro_lancamentos
WHERE data_vencimento >= '2026-01-01'
  AND data_vencimento <= '2026-12-31';
```

#### Antes (Subquery correlacionada)
```sql
SELECT 
    f.*,
    (SELECT SUM(valor) FROM financeiro_parcelas WHERE lancamento_id = f.id) as total_parcelas
FROM financeiro_lancamentos f;
```

#### Depois (JOIN)
```sql
SELECT 
    f.*,
    SUM(p.valor) as total_parcelas
FROM financeiro_lancamentos f
LEFT JOIN financeiro_parcelas p ON p.lancamento_id = f.id
GROUP BY f.id;
```

### 3. Usar CTEs para Queries Complexas

```sql
WITH safras_ativas AS (
    SELECT id, nome, cultura
    FROM agricola_safras
    WHERE tenant_id = 'uuid' AND status = 'ATIVA'
),
operacoes_por_safra AS (
    SELECT 
        safra_id,
        SUM(custo) as custo_total,
        COUNT(*) as total_operacoes
    FROM agricola_operacoes
    WHERE tenant_id = 'uuid'
    GROUP BY safra_id
)
SELECT 
    s.id,
    s.nome,
    s.cultura,
    COALESCE(o.custo_total, 0) as custo_total,
    COALESCE(o.total_operacoes, 0) as total_operacoes
FROM safras_ativas s
LEFT JOIN operacoes_por_safra o ON o.safra_id = s.id;
```

---

## 📈 SCRIPT DE BASELINE AUTOMATIZADO

### Script Python

```python
#!/usr/bin/env python3
"""
Performance Baseline Script
Coleta métricas de performance do banco de dados
"""

import psycopg2
import json
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'database': 'agrosaas',
    'user': 'postgres',
    'password': 'senha'
}

def get_slow_queries(conn, limit=20):
    """Top queries lentas por tempo médio"""
    query = """
    SELECT 
        query,
        calls,
        total_exec_time,
        mean_exec_time,
        max_exec_time,
        rows
    FROM pg_stat_statements
    ORDER BY mean_exec_time DESC
    LIMIT %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (limit,))
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def get_table_stats(conn):
    """Estatísticas das tabelas"""
    query = """
    SELECT 
        relname as table_name,
        n_live_tup as rows,
        pg_size_pretty(pg_total_relation_size(relid)) as total_size
    FROM pg_stat_user_tables
    ORDER BY n_live_tup DESC;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def get_index_usage(conn):
    """Uso de índices"""
    query = """
    SELECT 
        schemaname,
        tablename,
        indexname,
        idx_scan as index_scans
    FROM pg_stat_user_indexes
    ORDER BY idx_scan DESC;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def generate_report():
    """Gerar relatório de baseline"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'slow_queries': get_slow_queries(conn),
        'table_stats': get_table_stats(conn),
        'index_usage': get_index_usage(conn)
    }
    
    conn.close()
    
    # Salvar relatório
    filename = f"performance_baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Relatório salvo: {filename}")
    return report

if __name__ == '__main__':
    generate_report()
```

### Executar Script

```bash
cd services/api
python scripts/performance_baseline.py
```

---

## 📊 MONITORAMENTO CONTÍNUO

### Dashboard de Performance (SQL)

```sql
-- Queries lentas nas últimas 24h
SELECT 
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 500
ORDER BY mean_exec_time DESC;

-- Tabelas com mais scans sequenciais
SELECT 
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;

-- Índices não utilizados
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%pkey%';
```

### Alertas de Performance

```sql
-- Criar view para monitoramento
CREATE VIEW performance_alerts AS
SELECT 
    query,
    mean_exec_time,
    CASE 
        WHEN mean_exec_time > 1000 THEN 'CRITICO'
        WHEN mean_exec_time > 500 THEN 'ATENCAO'
        ELSE 'OK'
    END as status
FROM pg_stat_statements
WHERE mean_exec_time > 500;

-- Verificar alertas
SELECT * FROM performance_alerts WHERE status != 'OK';
```

---

## 🎯 CHECKLIST DE OTIMIZAÇÃO

### Para Cada Query Lenta

- [ ] Executar EXPLAIN ANALYZE
- [ ] Identificar tipo de scan (Seq vs Index)
- [ ] Verificar filtros (WHERE)
- [ ] Verificar joins (tipo e condições)
- [ ] Verificar ordenação (ORDER BY)
- [ ] Verificar agregação (GROUP BY)
- [ ] Identificar índices faltantes
- [ ] Testar índice candidato
- [ ] Medir melhoria
- [ ] Documentar otimização

### Critérios de Aceite

- [ ] Query < 200ms (meta Fase 4)
- [ ] Usando Index Scan ou Index Only Scan
- [ ] Buffers hit > 90%
- [ ] Rows removidas pelo filter < 50%
- [ ] Sem sorts em disco

---

## 🔗 RECURSOS ADICIONAIS

### Documentação Oficial
- [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [pg_stat_statements](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [PostgreSQL Performance](https://wiki.postgresql.org/wiki/Performance_Optimization)

### Ferramentas
- [pgHero](https://github.com/ankane/pghero) - Dashboard de performance
- [pgAdmin](https://www.pgadmin.org/) - GUI com explain visual
- [EXPLAIN Visualizer](https://explain.dalibo.com/) - Visualizador online

### Livros
- "PostgreSQL 14 Internals" - E. Rogov
- "Mastering PostgreSQL 14" - Hans-Jürgen Schönig

---

**Autor:** Backend Team
**Data:** 2026-03-31
**Próxima Revisão:** 2026-07-01 (Sprint 35)
