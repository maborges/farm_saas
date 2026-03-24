import pytest
import asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from core.database import Base
from core.models import Tenant, Fazenda

# Dois Tenants globais para guerra de isolamento nos testes
TENANT_A_ID = uuid.uuid4()
TENANT_B_ID = uuid.uuid4()

@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()

@pytest.fixture
async def engine_memory():
    # Banco de memória isolado, ultrarrápido para TDD
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture
async def session_a(engine_memory) -> AsyncSession:
    """Uma sessão simulando o contexto restrito do Tenant A"""
    async_session = async_sessionmaker(engine_memory, expire_on_commit=False)
    async with async_session() as session:
        session.info["tenant_id"] = TENANT_A_ID
        yield session

@pytest.fixture
async def session_b(engine_memory) -> AsyncSession:
    """Uma sessão simulando o contexto restrito do Tenant B, o invasor"""
    async_session = async_sessionmaker(engine_memory, expire_on_commit=False)
    async with async_session() as session:
        session.info["tenant_id"] = TENANT_B_ID
        yield session
