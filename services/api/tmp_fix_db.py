import asyncio
from sqlalchemy import text
import sys
import os

# Add the current directory to sys.path to allow importing from 'core'
sys.path.append(os.getcwd())

async def fix_notifications():
    from core.database import engine
    async with engine.begin() as conn:
        print("Checking/Creating notifications table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS notificacoes (
                id UUID PRIMARY KEY, 
                tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE, 
                tipo VARCHAR(60) NOT NULL, 
                titulo VARCHAR(200) NOT NULL, 
                mensagem VARCHAR(1000) NOT NULL, 
                lida BOOLEAN DEFAULT false NOT NULL, 
                metadata JSON, 
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notificacoes_tenant_id ON notificacoes (tenant_id)"))
        print("Table notifications created or already exists.")

        print("Checking/Creating relatorios_tecnicos table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS relatorios_tecnicos (
                id UUID PRIMARY KEY, 
                tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE, 
                safra_id UUID NOT NULL REFERENCES safras(id) ON DELETE CASCADE, 
                talhao_id UUID NOT NULL REFERENCES talhoes(id) ON DELETE CASCADE, 
                usuario_id UUID NOT NULL, 
                data_visita DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
                estadio_fenologico VARCHAR(50), 
                condicao_climatica JSON, 
                observacoes_gerais VARCHAR(2000), 
                recomendacoes VARCHAR(2000), 
                constatacoes JSON DEFAULT '[]' NOT NULL, 
                status VARCHAR(20) DEFAULT 'RASCUNHO' NOT NULL, 
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_relatorios_tecnicos_tenant_id ON relatorios_tecnicos (tenant_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_relatorios_tecnicos_safra_id ON relatorios_tecnicos (safra_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_relatorios_tecnicos_talhao_id ON relatorios_tecnicos (talhao_id)"))
        print("Table relatorios_tecnicos created or already exists.")

if __name__ == "__main__":
    asyncio.run(fix_notifications())
