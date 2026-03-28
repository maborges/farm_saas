"""
Script para verificar foreign keys faltantes em tabelas que referenciam equipamentos.

Uso:
    python scripts/check_missing_fks.py
"""
import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from core.database import engine


async def check_foreign_keys():
    """Verifica foreign keys para cadastros_equipamentos."""

    # Tabelas que devem ter FK para cadastros_equipamentos
    expected_fks = {
        'frota_planos_manutencao': 'equipamento_id',
        'frota_ordens_servico': 'equipamento_id',
        'frota_registros_manutencao': 'equipamento_id',
        'frota_checklists_realizados': 'equipamento_id',
        'frota_documentos_equipamentos': 'equipamento_id',
        'frota_abastecimentos': 'equipamento_id',
        'frota_apontamentos_uso': 'equipamento_id',
    }

    async with engine.begin() as conn:
        # Verifica se estamos usando PostgreSQL ou SQLite
        dialect = conn.dialect.name
        print(f"🔍 Banco de dados: {dialect}\n")

        if dialect == 'postgresql':
            # Query para PostgreSQL
            for table_name, column_name in expected_fks.items():
                query = text("""
                    SELECT
                        tc.constraint_name,
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name,
                        rc.delete_rule
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    LEFT JOIN information_schema.referential_constraints AS rc
                      ON rc.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_name = :table_name
                      AND kcu.column_name = :column_name
                """)

                result = await conn.execute(query, {"table_name": table_name, "column_name": column_name})
                rows = result.fetchall()

                if rows:
                    for row in rows:
                        print(f"✅ {table_name}.{column_name}")
                        print(f"   → {row.foreign_table_name}.{row.foreign_column_name}")
                        print(f"   ON DELETE: {row.delete_rule}")
                else:
                    print(f"❌ {table_name}.{column_name} - SEM FOREIGN KEY!")
                print()

        elif dialect == 'sqlite':
            # Query para SQLite
            for table_name, column_name in expected_fks.items():
                # SQLite usa PRAGMA foreign_key_list
                query = text(f"PRAGMA foreign_key_list({table_name})")

                try:
                    result = await conn.execute(query)
                    rows = result.fetchall()

                    # Filtra apenas as FKs para a coluna específica
                    matching_fks = [row for row in rows if row[3] == column_name]

                    if matching_fks:
                        for row in matching_fks:
                            print(f"✅ {table_name}.{column_name}")
                            print(f"   → {row[2]}.{row[4]}")
                            print(f"   ON DELETE: {row[6]}")
                    else:
                        # Verifica se a tabela existe
                        check_table = text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                        table_exists = await conn.execute(check_table)
                        if table_exists.fetchone():
                            print(f"❌ {table_name}.{column_name} - SEM FOREIGN KEY!")
                        else:
                            print(f"⚠️  {table_name} - TABELA NÃO EXISTE")
                    print()
                except Exception as e:
                    print(f"⚠️  {table_name} - ERRO: {e}")
                    print()


async def main():
    print("=" * 70)
    print("🔍 VERIFICAÇÃO DE FOREIGN KEYS PARA EQUIPAMENTOS")
    print("=" * 70)
    print()

    await check_foreign_keys()

    print("=" * 70)
    print("✅ Verificação concluída!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
