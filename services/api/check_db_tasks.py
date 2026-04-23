import asyncio
import os
import sys

# Adicionar o diretório atual ao sys.path para importar core
sys.path.insert(0, os.getcwd())

from core.database import async_session_maker
from sqlalchemy import text

async def check():
    async with async_session_maker() as s:
        try:
            res = await s.execute(text('SELECT * FROM farms.safra_tarefas'))
            print("Tasks Details:")
            for row in res.mappings():
                print(f"  {dict(row)}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
