import asyncio
import uuid
from core.database import async_session_maker
from core.models import Tenant, Fazenda
from agricola.cadastros.models import Cultura
from core.cadastros.propriedades.models import AreaRural

async def check():
    async with async_session_maker() as session:
        from sqlalchemy import select, func

        tenant_count = await session.scalar(select(func.count()).select_from(Tenant))
        fazenda_count = await session.scalar(select(func.count()).select_from(Fazenda))
        cultura_count = await session.scalar(select(func.count()).select_from(Cultura))
        talhao_count = await session.scalar(
            select(func.count()).select_from(AreaRural).where(AreaRural.tipo == "TALHAO")
        )

        print(f"Tenants: {tenant_count}")
        print(f"Fazendas: {fazenda_count}")
        print(f"Culturas: {cultura_count}")
        print(f"Talhoes: {talhao_count}")
        
        tenant_id = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        tenant = await session.get(Tenant, tenant_id)
        if tenant:
            print(f"Target Tenant found: {tenant.nome}")
            print(f"Modules: {tenant.modulos_ativos}")
        else:
            print("Target Tenant NOT found")

if __name__ == "__main__":
    asyncio.run(check())
