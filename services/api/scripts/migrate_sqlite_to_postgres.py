"""
Script para migrar dados do SQLite para PostgreSQL.
"""
import asyncio
import sys
import os
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, inspect
from core.database import Base
from loguru import logger

# Import todos os models
from core.models import *
from agricola.safras.models import *
from agricola.operacoes.models import *
from agricola.monitoramento.models import *
from agricola.romaneios.models import *
from agricola.previsoes.models import *
from agricola.cadastros.models import *
from pecuaria.models.piquete import *
from pecuaria.models.lote import *
from pecuaria.models.manejo import *
from financeiro.models.plano_conta import *
from financeiro.models.despesa import *
from financeiro.models.rateio import *

# Conexões
SQLITE_URL = "sqlite+aiosqlite:///./agrosaas.db"
POSTGRES_URL = "postgresql+asyncpg://borgus:numsey01@192.168.0.2/farms"

# Ordem correta para migração (respeitando foreign keys)
MIGRATION_ORDER = [
    # Core - Primeiro os independentes
    Usuario,
    AdminUser,
    EmailTemplate,
    ConfiguracaoSaaS,
    Cupom,

    # Depois os que dependem de Usuario
    Tenant,

    # Depois os que dependem de Tenant
    Fazenda,
    PlanoAssinatura,
    AssinaturaTenant,
    PerfilAcesso,
    TenantUsuario,
    ConfiguracaoTenant,

    # Depois os que dependem de Fazenda/Tenant
    FazendaUsuario,
    ConviteAcesso,
    Fatura,
    EmailLog,
    AdminAuditLog,

    # Agrícola - Dependem de Tenant/Fazenda
    Cultura,
    Safra,

    # Operações e demais
    # Adicione aqui conforme necessário, respeitando dependências
]

async def migrate_table(source_session: AsyncSession, dest_session: AsyncSession, model):
    """Migra uma tabela específica."""
    table_name = model.__tablename__

    try:
        # Buscar todos os dados da tabela no SQLite
        result = await source_session.execute(select(model))
        rows = result.scalars().all()

        if not rows:
            logger.info(f"  ⚪ {table_name}: Sem dados para migrar")
            return 0

        # Inserir no PostgreSQL
        count = 0
        for row in rows:
            # Criar nova instância com os mesmos dados
            row_dict = {c.name: getattr(row, c.name) for c in row.__table__.columns}
            new_row = model(**row_dict)
            dest_session.add(new_row)
            count += 1

        await dest_session.commit()
        logger.success(f"  ✅ {table_name}: {count} registros migrados")
        return count

    except Exception as e:
        logger.error(f"  ❌ {table_name}: Erro - {e}")
        await dest_session.rollback()
        return 0

async def migrate_data():
    """Migra todos os dados do SQLite para PostgreSQL."""
    logger.info("🚀 Iniciando migração SQLite → PostgreSQL\n")

    # Engines
    sqlite_engine = create_async_engine(SQLITE_URL)
    postgres_engine = create_async_engine(POSTGRES_URL.replace("%%", "%"))

    # Session makers
    sqlite_session_maker = async_sessionmaker(sqlite_engine, class_=AsyncSession, expire_on_commit=False)
    postgres_session_maker = async_sessionmaker(postgres_engine, class_=AsyncSession, expire_on_commit=False)

    total_migrated = 0

    async with sqlite_session_maker() as source_session, postgres_session_maker() as dest_session:
        for model in MIGRATION_ORDER:
            count = await migrate_table(source_session, dest_session, model)
            total_migrated += count

    await sqlite_engine.dispose()
    await postgres_engine.dispose()

    logger.success(f"\n🎉 Migração concluída! Total: {total_migrated} registros migrados")

if __name__ == "__main__":
    asyncio.run(migrate_data())
