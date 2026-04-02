#!/usr/bin/env python3
"""
Setup de Performance - PostgreSQL
Configura pg_stat_statements e query logging no banco de dados
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '192.168.0.2'),
    'database': os.getenv('DB_NAME', 'farms'),
    'user': os.getenv('DB_USER', 'borgus'),
    'password': os.getenv('DB_PASSWORD', 'numsey01')
}


async def setup_performance():
    """Configurar performance monitoring no PostgreSQL"""
    
    print("=" * 60)
    print("🚀 Setup de Performance - PostgreSQL")
    print("=" * 60)
    print()
    
    try:
        # 1. Conectar ao banco
        print("1️⃣  Conectando ao banco de dados...")
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Conexão estabelecida com sucesso!")
        print()
        
        # 2. Criar pg_stat_statements
        print("2️⃣  Configurando pg_stat_statements...")
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
            print("✅ pg_stat_statements configurado!")
        except Exception as e:
            print(f"⚠️  pg_stat_statements: {str(e)}")
            print("   Pode já existir ou requerer superuser")
        print()
        
        # 3. Habilitar query logging
        print("3️⃣  Habilitando query logging (>500ms)...")
        try:
            await conn.execute("ALTER SYSTEM SET log_min_duration_statement = 500;")
            print("✅ Query logging habilitado!")
        except Exception as e:
            print(f"⚠️  Query logging: {str(e)}")
            print("   Pode requerer privilégios de superuser")
        print()
        
        # 4. Recarregar configuração
        print("4️⃣  Recarregando configuração...")
        try:
            await conn.execute("SELECT pg_reload_conf();")
            print("✅ Configuração recarregada!")
        except Exception as e:
            print(f"⚠️  Recarregar config: {str(e)}")
        print()
        
        # 5. Verificar configurações
        print("5️⃣  Verificando configurações...")
        result = await conn.fetchval("SHOW log_min_duration_statement;")
        print(f"   log_min_duration_statement = {result}ms")
        print()
        
        # 6. Verificar pg_stat_statements
        print("6️⃣  Verificando pg_stat_statements...")
        try:
            result = await conn.fetchval("SELECT COUNT(*) FROM pg_stat_statements;")
            print(f"   Total de queries monitoradas: {result}")
            print("✅ pg_stat_statements está ativo!")
        except Exception as e:
            print(f"⚠️  pg_stat_statements não disponível: {str(e)}")
        print()
        
        # 7. Coletar baseline inicial
        print("7️⃣  Coletando baseline inicial...")
        baseline = await conn.fetch("""
            SELECT 
                query,
                calls,
                mean_exec_time,
                max_exec_time
            FROM pg_stat_statements
            ORDER BY mean_exec_time DESC
            LIMIT 10;
        """)
        
        print("\n📊 Top 5 Queries Mais Lentas:")
        print("-" * 60)
        for i, row in enumerate(baseline[:5], 1):
            print(f"{i}. Tempo Médio: {row['mean_exec_time']:.2f}ms | Calls: {row['calls']}")
            print(f"   Query: {row['query'][:80]}...")
            print()
        
        await conn.close()
        
        print("=" * 60)
        print("✅ Setup de performance concluído com sucesso!")
        print("=" * 60)
        print()
        print("Próximos passos:")
        print("1. Executar: python3 scripts/performance_baseline.py")
        print("2. Analisar relatório em: reports/performance_baseline_*.json")
        print("3. Identificar queries para otimização")
        print()
        
    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ Erro de PostgreSQL: {e}")
        print()
        print("Verifique:")
        print("- Conexão com o banco de dados")
        print("- Credenciais no arquivo .env")
        print("- Permissões de superuser para ALTER SYSTEM")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(setup_performance())
