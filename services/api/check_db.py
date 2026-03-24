import asyncio
import uuid
from core.database import async_session_maker
from core.models import Tenant

async def check():
    async with async_session_maker() as session:
        tenant_id = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        tenant = await session.get(Tenant, tenant_id)
        if tenant:
            print(f"Tenant found: {tenant.nome}")
            print(f"Modules: {tenant.modulos_ativos}")
        else:
            print("Tenant NOT found")
            
        from core.models.billing import PlanoAssinatura
        from sqlalchemy import select
        plans = (await session.execute(select(PlanoAssinatura))).scalars().all()
        print(f"\nTotal Plans: {len(plans)}")
        for p in plans:
            print(f"- {p.nome} ({p.preco_mensal}/mo) | Modules: {p.modulos_inclusos}")

if __name__ == "__main__":
    asyncio.run(check())
