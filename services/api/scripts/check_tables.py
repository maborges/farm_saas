"""Verifica quais tabelas de abastecimento/apontamento existem no banco."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from core.database import engine


async def check_tables():
    async with engine.begin() as conn:
        # Lista todas as tabelas com 'abastecimento' ou 'apontamento' no nome
        result = await conn.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname='farms'
              AND (tablename LIKE '%abastecimento%' OR tablename LIKE '%apontamento%')
            ORDER BY tablename
        """))

        tables = result.fetchall()

        print("Tabelas encontradas:")
        for table in tables:
            print(f"  - {table[0]}")


asyncio.run(check_tables())
