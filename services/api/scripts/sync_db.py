import asyncio
from core.database import engine, Base
import core.models # Garante que todos os models foram importados para o metadata

async def sync():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Banco sincronizado.")

if __name__ == "__main__":
    asyncio.run(sync())
