
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from agricola.cenarios.service import CenariosService
from agricola.cenarios.schemas import CenarioCreate

async def test():
    # Database URL from .env.local
    db_url = "postgresql+asyncpg://borgus:numsey01@192.168.0.2/farms"
    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Use a real tenant_id and safra_id if possible, or just mock
        tenant_id = uuid.UUID("592b906e-0329-44df-8c58-80ca744ae243")
        safra_id = uuid.UUID("e122e7f7-f0a2-4f4b-a4df-ead9c05e9966")
        service = CenariosService(session, tenant_id)
        
        data = CenarioCreate(
            nome="Teste Automatizado",
            tipo="CUSTOM",
            produtividade_default=55.0,
            preco_default=130.0,
            custo_ha_default=4500.0,
            fator_custo_pct=1.0
        )
        
        print(f"Tentando criar cenário para safra {safra_id}...")
        try:
            cenario = await service.create_cenario(safra_id, data)
            print(f"✅ Cenário criado: {cenario.id}")
            await session.commit()
        except Exception as e:
            print(f"❌ Erro ao criar cenário: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
