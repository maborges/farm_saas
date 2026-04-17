from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import event, text
from core.config import settings
from loguru import logger

# Criação da Engine Assíncrona para o PostgreSQL ou SQLite Fallback
DB_URL = str(settings.database_url)
if not DB_URL or "postgresql" not in DB_URL:
    DB_URL = "sqlite+aiosqlite:///./agrosaas.db"
    logger.warning("Usando banco local SQLite devido à falta de PostgreSQL configurado.")
else:
    # Corrige driver se não especificado ou se especificado asyncpg e ele não for achado
    try:
        import asyncpg
    except ImportError:
        DB_URL = "sqlite+aiosqlite:///./agrosaas.db"
        logger.warning("asyncpg driver não encontrado. Usando banco local SQLite Fallback.")

engine = create_async_engine(
    DB_URL,
    echo=False,  # Em produção manter False para não floodar de logs SQL
    future=True,
    # Remove args impeditivos sqlite
    **({} if "sqlite" in DB_URL else {"pool_size": 10, "max_overflow": 20}),
    connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {"server_settings": {"search_path": "farms"}}
)

# Fábrica de Sessoes Assíncronas (compatível com SQLAlchemy 1.4 e 2.0)
try:
    from sqlalchemy.ext.asyncio import async_sessionmaker
    async_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
except ImportError:
    # Fallback para SQLAlchemy 1.4
    async_session_maker = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        future=True
    )

# Base para os Models do ORM
Base = declarative_base()

# Event Listener do SQLAlchemy para RLS (Row Level Security)
# Injetamos o tenant_id no escopo local do postgres toda vez que a sessão abre
@event.listens_for(engine.sync_engine, "connect")
def set_tenant_context(dbapi_connection, connection_record):
    if "postgresql" in DB_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED")
        cursor.close()


# Dependência para injetar sessão do banco de dados (Dependency Injection)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência do FastAPI para injetar sessão do banco de dados.
    
    Usage:
        @router.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    db = async_session_maker()
    try:
        yield db
    finally:
        await db.close()


# Função utilitária para obter sessão única (para scripts e testes)
async def get_db_session() -> AsyncSession:
    """
    Obtém uma sessão única do banco de dados.
    
    Usage:
        db = await get_db_session()
        # ... usar db ...
        await db.close()
    """
    return async_session_maker()
