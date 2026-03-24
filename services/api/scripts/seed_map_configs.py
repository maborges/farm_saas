import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.models.tenant import Tenant
from core.models.tenant_config import ConfiguracaoTenant
from core.database import DB_URL

async def seed_map_configs():
    engine = create_async_engine(DB_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        # Pega o primeiro tenant para exemplificar
        from sqlalchemy import select
        res = await session.execute(select(Tenant).limit(1))
        tenant = res.scalar_one_or_none()
        
        if not tenant:
            print("Nenhum tenant encontrado. Rode o seed de auth primeiro.")
            return

        configs = [
            {
                "categoria": "mapas",
                "chave": "enable_3d_terrain",
                "valor": {"enabled": True},
                "descricao": "Habilita a visualização de relevo 3D no mapa."
            },
            {
                "categoria": "mapas",
                "chave": "kml_import",
                "valor": {"enabled": True, "max_size_mb": 10},
                "descricao": "Permite importar perímetros via arquivos KML/GeoJSON."
            },
            {
                "categoria": "mapas",
                "chave": "telemetry_trail",
                "valor": {"enabled": True, "history_hours": 12},
                "descricao": "Exibe o rastro de movimentação das máquinas."
            }
        ]

        for c in configs:
            stmt = select(ConfiguracaoTenant).where(
                ConfiguracaoTenant.tenant_id == tenant.id,
                ConfiguracaoTenant.chave == c["chave"]
            )
            existing = (await session.execute(stmt)).scalar_one_or_none()
            
            if not existing:
                config = ConfiguracaoTenant(tenant_id=tenant.id, **c)
                session.add(config)
        
        await session.commit()
        print(f"Configurações de mapa criadas para o tenant {tenant.nome}")

if __name__ == "__main__":
    asyncio.run(seed_map_configs())
