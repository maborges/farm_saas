#!/usr/bin/env python3
"""
Performance Baseline Script - AgroSaaS
Coleta métricas de performance do banco de dados PostgreSQL

Nota: Este script funciona sem privilégios de superuser.
Para métricas completas, solicitar ao DBA:
1. CREATE EXTENSION pg_stat_statements;
2. ALTER SYSTEM SET log_min_duration_statement = 500;

Uso:
    .venv/bin/python scripts/performance_baseline.py
    
Saída:
    - Relatório JSON em services/api/reports/performance_baseline_YYYYMMDD_HHMMSS.json
    - Relatório texto em services/api/reports/performance_baseline_YYYYMMDD_HHMMSS.txt
"""

import asyncio
import asyncpg
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '192.168.0.2'),
    'database': os.getenv('DB_NAME', 'farms'),
    'user': os.getenv('DB_USER', 'borgus'),
    'password': os.getenv('DB_PASSWORD', 'numsey01')
}

REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')


def ensure_reports_dir():
    """Criar diretório de relatórios se não existir"""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)


async def get_table_stats(conn) -> List[Dict]:
    """Estatísticas das tabelas"""
    query = """
    SELECT 
        schemaname,
        relname as table_name,
        n_live_tup as row_count,
        n_dead_tup as dead_rows,
        seq_scan,
        seq_tup_read,
        idx_scan,
        idx_tup_fetch
    FROM pg_stat_user_tables
    ORDER BY n_live_tup DESC
    LIMIT 30;
    """
    rows = await conn.fetch(query)
    return [dict(r) for r in rows]


async def get_index_stats(conn) -> List[Dict]:
    """Uso de índices"""
    query = """
    SELECT 
        schemaname,
        relname as table_name,
        indexrelname as index_name,
        idx_scan as index_scans,
        idx_tup_read as tuples_read,
        idx_tup_fetch as tuples_fetched
    FROM pg_stat_user_indexes
    ORDER BY idx_scan DESC
    LIMIT 30;
    """
    rows = await conn.fetch(query)
    return [dict(r) for r in rows]


async def get_unused_indexes(conn) -> List[Dict]:
    """Índices não utilizados"""
    query = """
    SELECT 
        schemaname,
        relname as table_name,
        indexrelname as index_name,
        pg_size_pretty(pg_relation_size(indexrelid)) as index_size
    FROM pg_stat_user_indexes
    WHERE idx_scan = 0
      AND indexrelname NOT LIKE '%pkey%'
    ORDER BY pg_relation_size(indexrelid) DESC
    LIMIT 20;
    """
    rows = await conn.fetch(query)
    return [dict(r) for r in rows]


async def get_database_size(conn) -> str:
    """Tamanho total do banco de dados"""
    result = await conn.fetchval("SELECT pg_size_pretty(pg_database_size(current_database()));")
    return result


async def get_cache_hit_ratio(conn) -> float:
    """Taxa de acerto do cache"""
    query = """
    SELECT 
        ROUND(100.0 * sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0), 2) as cache_hit_ratio
    FROM pg_statio_user_tables;
    """
    result = await conn.fetchval(query)
    return result if result else 0.0


async def get_long_running_queries(conn) -> List[Dict]:
    """Queries em execução"""
    query = """
    SELECT 
        pid,
        now() - query_start as duration,
        query
    FROM pg_stat_activity
    WHERE state = 'active'
      AND query NOT ILIKE '%pg_stat_activity%'
    ORDER BY duration DESC
    LIMIT 10;
    """
    rows = await conn.fetch(query)
    return [dict(r) for r in rows]


async def get_locks(conn) -> List[Dict]:
    """Locks ativos"""
    query = """
    SELECT 
        pid,
        locktype,
        relation::regclass,
        mode,
        granted
    FROM pg_locks
    WHERE NOT granted
    LIMIT 10;
    """
    try:
        rows = await conn.fetch(query)
        return [dict(r) for r in rows]
    except:
        return []


async def get_slow_query_simulation(conn) -> List[Dict]:
    """Simula identificação de queries lentas via logs"""
    # Nota: Sem pg_stat_statements, usamos estatísticas das tabelas
    query = """
    SELECT 
        schemaname,
        relname as table_name,
        seq_scan,
        seq_tup_read,
        idx_scan,
        CASE 
            WHEN seq_scan > idx_scan THEN 'Seq Scan Dominante'
            ELSE 'Index Scan Dominante'
        END as scan_type
    FROM pg_stat_user_tables
    WHERE seq_scan > 0
    ORDER BY seq_tup_read DESC
    LIMIT 10;
    """
    rows = await conn.fetch(query)
    return [dict(r) for r in rows]


def generate_text_report(data: Dict[str, Any]) -> str:
    """Gerar relatório em formato texto"""
    lines = []
    lines.append("=" * 80)
    lines.append("📊 RELATÓRIO DE PERFORMANCE BASELINE - AGROSAAS")
    lines.append("=" * 80)
    lines.append(f"Timestamp: {data['timestamp']}")
    lines.append(f"Database: {data['database']}")
    lines.append(f"Tamanho do Banco: {data['database_size']}")
    lines.append(f"Cache Hit Ratio: {data['cache_hit_ratio']}%")
    lines.append("")
    
    lines.append("-" * 80)
    lines.append("📊 ESTATÍSTICAS DAS TABELAS PRINCIPAIS")
    lines.append("-" * 80)
    for t in data['table_stats'][:15]:
        lines.append(f"\nTabela: {t['table_name']} | Rows: {t['row_count']:,} | Dead: {t['dead_rows']:,}")
        lines.append(f"  Seq Scans: {t['seq_scan']:,} ({t['seq_tup_read']:,} rows) | Idx Scans: {t['idx_scan']:,} ({t['idx_tup_fetch']:,} rows)")
    
    lines.append("")
    lines.append("-" * 80)
    lines.append("🎯 ÍNDICES MAIS UTILIZADOS")
    lines.append("-" * 80)
    for idx in data['index_stats'][:10]:
        lines.append(f"\n{idx['index_name']} ({idx['table_name']}) | Scans: {idx['index_scans']:,}")
    
    lines.append("")
    lines.append("-" * 80)
    lines.append("⚠️  ÍNDICES NÃO UTILIZADOS (Candidatos a remoção)")
    lines.append("-" * 80)
    for idx in data['unused_indexes'][:10]:
        lines.append(f"\n{idx['index_name']} ({idx['table_name']}) | Size: {idx['index_size']}")
    
    if not data['unused_indexes']:
        lines.append("\nNenhum índice não utilizado encontrado.")
    
    lines.append("")
    lines.append("-" * 80)
    lines.append("🔒 LOCKS PENDENTES")
    lines.append("-" * 80)
    if data['locks']:
        for lock in data['locks']:
            lines.append(f"\nPID: {lock['pid']} | Type: {lock['locktype']} | Mode: {lock['mode']}")
    else:
        lines.append("\nNenhum lock pendente encontrado.")
    
    lines.append("")
    lines.append("-" * 80)
    lines.append("📈 PADRÃO DE SCAN DAS TABELAS")
    lines.append("-" * 80)
    for q in data['slow_query_simulation'][:10]:
        lines.append(f"\n{q['table_name']}: {q['scan_type']}")
        lines.append(f"  Seq Scans: {q['seq_scan']:,} | Rows Lidas: {q['seq_tup_read']:,}")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("RECOMENDAÇÕES")
    lines.append("=" * 80)
    
    # Analisar e gerar recomendações
    recommendations = []
    
    # Cache hit ratio baixo
    if data['cache_hit_ratio'] < 90:
        recommendations.append(f"⚠️  Cache hit ratio baixo ({data['cache_hit_ratio']}%). Aumentar shared_buffers.")
    
    # Muitas seq scans
    high_seq_scans = [t for t in data['table_stats'] if t['seq_scan'] > 1000]
    if high_seq_scans:
        recommendations.append(f"⚠️  {len(high_seq_scans)} tabelas com muitas seq scans. Criar índices.")
    
    # Índices não utilizados
    if data['unused_indexes']:
        recommendations.append(f"ℹ️  {len(data['unused_indexes'])} índices não utilizados. Considerar remoção.")
    
    # Locks pendentes
    if data['locks']:
        recommendations.append(f"🔴 {len(data['locks'])} locks pendentes. Investigar deadlocks.")
    
    if recommendations:
        for rec in recommendations:
            lines.append(f"\n{rec}")
    else:
        lines.append("\n✅ Nenhuma recomendação crítica no momento.")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("FIM DO RELATÓRIO")
    lines.append("=" * 80)
    
    return "\n".join(lines)


async def generate_baseline_report():
    """Gerar relatório completo de baseline"""
    print("\n🚀 Iniciando coleta de baseline de performance...")
    print()
    
    ensure_reports_dir()
    
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print(f"✅ Conectado ao banco de dados: {DB_CONFIG['database']}")
        print()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        print("📊 Coletando métricas...")
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'database': DB_CONFIG['database'],
            'database_size': await get_database_size(conn),
            'cache_hit_ratio': await get_cache_hit_ratio(conn),
            'table_stats': await get_table_stats(conn),
            'index_stats': await get_index_stats(conn),
            'unused_indexes': await get_unused_indexes(conn),
            'long_running_queries': await get_long_running_queries(conn),
            'locks': await get_locks(conn),
            'slow_query_simulation': await get_slow_query_simulation(conn),
            'note': 'pg_stat_statements não disponível. Solicitar ao DBA: CREATE EXTENSION pg_stat_statements;'
        }
        
        await conn.close()
        
        # Salvar relatório JSON
        json_filename = os.path.join(REPORTS_DIR, f'performance_baseline_{timestamp}.json')
        with open(json_filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        print(f"✅ Relatório JSON salvo: {json_filename}")
        
        # Salvar relatório texto
        text_report = generate_text_report(report_data)
        text_filename = os.path.join(REPORTS_DIR, f'performance_baseline_{timestamp}.txt')
        with open(text_filename, 'w') as f:
            f.write(text_report)
        print(f"✅ Relatório texto salvo: {text_filename}")
        
        # Imprimir resumo
        print()
        print("=" * 80)
        print("📊 RESUMO DO BASELINE")
        print("=" * 80)
        print(f"Database: {report_data['database']}")
        print(f"Tamanho: {report_data['database_size']}")
        print(f"Cache Hit Ratio: {report_data['cache_hit_ratio']}%")
        print(f"Tabelas monitoradas: {len(report_data['table_stats'])}")
        print(f"Índices monitorados: {len(report_data['index_stats'])}")
        print(f"Índices não utilizados: {len(report_data['unused_indexes'])}")
        print(f"Locks pendentes: {len(report_data['locks'])}")
        print("=" * 80)
        print()
        print("✅ Baseline de performance coletada com sucesso!")
        print()
        print("Próximos passos:")
        print("1. Analisar relatório em: reports/performance_baseline_*.txt")
        print("2. Identificar tabelas com muitas seq scans")
        print("3. Revisar índices não utilizados")
        print("4. Solicitar pg_stat_statements ao DBA para métricas completas")
        print()
        
        return report_data
        
    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ Erro de PostgreSQL: {e}")
        raise
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    asyncio.run(generate_baseline_report())
