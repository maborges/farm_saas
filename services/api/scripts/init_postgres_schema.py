"""
Script para inicializar o schema do PostgreSQL a partir dos models.
"""
import asyncio
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, Base
from loguru import logger

# Import todos os models para registrá-los no Base.metadata
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

async def init_db():
    """Cria todas as tabelas no banco de dados."""
    logger.info("Criando todas as tabelas no PostgreSQL...")

    async with engine.begin() as conn:
        # Drop all tables (cuidado em produção!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    logger.success("✅ Todas as tabelas foram criadas com sucesso!")

if __name__ == "__main__":
    asyncio.run(init_db())
