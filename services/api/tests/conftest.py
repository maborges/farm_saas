import sys
from pathlib import Path

# Add services/api to Python path for test imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from core.database import Base
from core.models import Tenant
from core.models.billing import PlanoAssinatura
# Garante que Cultivo é importado antes do mapper Safra ser inicializado,
# evitando InvalidRequestError: 'Cultivo' failed to locate a name.
import agricola.cultivos.models  # noqa: F401
import agricola.analises_solo.models  # noqa: F401
import agricola.tarefas.models  # noqa: F401
import agricola.production_units.models  # noqa: F401
from core.config import settings

# UUIDs fixos para garantir consistência entre importações do módulo
TENANT_A_ID = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000010")
TENANT_B_ID = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000020")

def _get_db_url():
    db_url = str(settings.database_url)
    if "postgresql" not in db_url:
        db_url = "postgresql+asyncpg://borgus:numsey01@192.168.0.2/farms"
    return db_url

@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()

@pytest.fixture(scope="session")
def event_loop():
    """Single event loop shared across all tests in the session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def tenant_id() -> uuid.UUID:
    return TENANT_A_ID

@pytest.fixture
def outro_tenant_id() -> uuid.UUID:
    return TENANT_B_ID

@pytest.fixture
async def session():
    """
    Cria uma nova sessão para cada teste com engine fresco (NullPool).
    """
    engine = create_async_engine(
        _get_db_url(),
        echo=False,
        future=True,
        poolclass=NullPool,
        connect_args={'server_settings': {'search_path': 'farms'}}
    )
    
    # Garante que tabelas existem (ignora erros de FK — banco já existe via Alembic)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    except Exception:
        pass
    
    # Cria sessão
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as sess:
        yield sess
        try:
            await sess.rollback()
        except Exception:
            pass
    await engine.dispose()


@pytest.fixture
async def session_a():
    """Sessão para Tenant A nos testes de isolamento multi-tenant."""
    engine = create_async_engine(
        _get_db_url(), echo=False, future=True, poolclass=NullPool,
        connect_args={'server_settings': {'search_path': 'farms'}}
    )
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    except Exception:
        pass
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as setup_sess:
        setup_sess.add(Tenant(id=TENANT_A_ID, nome="Tenant A", documento=str(TENANT_A_ID)[:11], ativo=True))
        try:
            await setup_sess.commit()
        except Exception as e:
            pass  # tenant já existe — ok
            await setup_sess.rollback()
    async with async_session() as sess:
        yield sess
        try:
            await sess.rollback()
        except Exception:
            pass
    await engine.dispose()

@pytest.fixture
async def session_b():
    """Sessão para Tenant B nos testes de isolamento multi-tenant."""
    engine = create_async_engine(
        _get_db_url(), echo=False, future=True, poolclass=NullPool,
        connect_args={'server_settings': {'search_path': 'farms'}}
    )
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    except Exception:
        pass
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as setup_sess:
        setup_sess.add(Tenant(id=TENANT_B_ID, nome="Tenant B", documento=str(TENANT_B_ID)[:11], ativo=True))
        try:
            await setup_sess.commit()
        except Exception:
            await setup_sess.rollback()
    async with async_session() as sess:
        yield sess
        try:
            await sess.rollback()
        except Exception:
            pass
    await engine.dispose()

@pytest.fixture
async def unidade_produtiva_id(session, tenant_id: uuid.UUID) -> uuid.UUID:
    # Cria tenant
    await session.execute(
        text(
            "INSERT INTO tenants (id, nome, documento, ativo, "
            "storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at) "
            "VALUES (:id, :nome, :doc, true, 0, 10240, 'pt-BR', now(), now()) "
            "ON CONFLICT DO NOTHING"
        ),
        {"id": str(tenant_id), "nome": "Tenant Teste", "doc": str(tenant_id)[:11]},
    )

    # Cria plano base se não existir
    plano_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    await session.execute(
        text(
            "INSERT INTO planos_assinatura (id, nome, modulos_inclusos, limite_usuarios_minimo, limite_usuarios_maximo, "
            "preco_mensal, preco_anual, max_fazendas, max_categorias_plano, tem_trial, dias_trial, is_free, "
            "destaque, ordem, ativo, disponivel_site, disponivel_crm, created_at) "
            "VALUES (:id, 'Plano Teste', CAST('[\"CORE\",\"A1_PLANEJAMENTO\"]' AS json), 1, 5, 0, 0, -1, -1, false, 15, false, false, 0, true, false, true, now()) "
            "ON CONFLICT DO NOTHING"
        ),
        {"id": str(plano_id)},
    )

    # Cria assinatura principal de forma idempotente para respeitar uq_assinatura_tenant_tipo.
    await session.execute(
        text(
            "INSERT INTO assinaturas_tenant "
            "(id, tenant_id, plano_id, tipo_assinatura, ciclo_pagamento, usuarios_contratados, "
            "status, grace_period_days, created_at, updated_at) "
            "VALUES (:assinatura_id, :tenant_id, :plano_id, 'TENANT', 'MENSAL', 5, "
            "'ATIVA', 3, now(), now()) "
            "ON CONFLICT (tenant_id, tipo_assinatura) DO UPDATE SET "
            "plano_id = EXCLUDED.plano_id, "
            "ciclo_pagamento = EXCLUDED.ciclo_pagamento, "
            "usuarios_contratados = EXCLUDED.usuarios_contratados, "
            "status = EXCLUDED.status, "
            "updated_at = now()"
        ),
        {
            "assinatura_id": str(uuid.uuid4()),
            "tenant_id": str(tenant_id),
            "plano_id": str(plano_id),
        },
    )

    # Cria unidade produtiva (antiga fazenda)
    fazenda_id = uuid.uuid4()
    await session.execute(text(
        "INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at) "
        "VALUES (:id, :tenant_id, 'Fazenda Teste', true, now(), now()) "
        "ON CONFLICT DO NOTHING"
    ), {"id": str(fazenda_id), "tenant_id": str(tenant_id)})
    await session.commit()
    return fazenda_id

@pytest.fixture
async def talhao_id(session, tenant_id: uuid.UUID, unidade_produtiva_id: uuid.UUID) -> uuid.UUID:
    """
    Cria registro de talhão em cadastros_areas_rurais.
    Safra e OperacaoAgricola usam cadastros_areas_rurais.id como talhao_id.
    """
    from sqlalchemy import text
    
    area_id = uuid.uuid4()
    
    await session.execute(text("""
        INSERT INTO cadastros_areas_rurais (id, tenant_id, unidade_produtiva_id, tipo, nome, area_hectares, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, :unidade_produtiva_id, :tipo, :nome, :area_hectares, :ativo, NOW(), NOW())
    """), {
        "id": str(area_id),
        "tenant_id": str(tenant_id),
        "unidade_produtiva_id": str(unidade_produtiva_id),
        "tipo": "TALHAO",
        "nome": "Talhão Teste",
        "area_hectares": 100.0,
        "ativo": True
    })

    await session.commit()
    return area_id
