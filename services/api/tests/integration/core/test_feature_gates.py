"""
Testes de integração — Feature Gates por Módulo
FG-01..14: Garante que require_module() retorna 402 para módulos não contratados
            e 200 para módulos contratados, por domínio.

Estratégia:
- TENANT_FULL: assinatura com todos os módulos (status=ATIVA)
- TENANT_CORE: assinatura apenas com CORE (sem módulos pagos)
"""
import pytest
import uuid
from sqlalchemy import text

pytestmark = pytest.mark.asyncio

# ── IDs de teste ─────────────────────────────────────────────────────────────
TENANT_FULL_ID  = uuid.UUID("f0000001-0000-0000-0000-000000000001")
TENANT_CORE_ID  = uuid.UUID("c0000001-0000-0000-0000-000000000001")
FAZENDA_FULL_ID = uuid.UUID("f0000002-0000-0000-0000-000000000002")
FAZENDA_CORE_ID = uuid.UUID("c0000002-0000-0000-0000-000000000002")
USER_ID         = uuid.UUID("eeeeeeee-0000-0000-0000-000000000005")

MODULES_FULL = [
    "CORE",
    "A1_PLANEJAMENTO", "A2_CAMPO", "A3_DEFENSIVOS", "A4_PRECISAO", "A5_COLHEITA",
    "F1_TESOURARIA", "F2_CUSTOS_ABC", "F3_FISCAL",
    "O1_FROTA", "O2_ESTOQUE", "O3_COMPRAS",
    "P1_REBANHO",
    "RH1_REMUNERACAO",
]
MODULES_CORE = ["CORE"]


# ── Helpers de token ─────────────────────────────────────────────────────────

def _make_token(tenant_id: uuid.UUID, unidade_produtiva_id: uuid.UUID, modules: list[str]) -> str:
    from datetime import timedelta
    from unittest.mock import MagicMock
    from core.services.auth_service import AuthService
    svc = AuthService(MagicMock())
    return svc.create_access_token(
        {
            "sub": str(USER_ID),
            "tenant_id": str(tenant_id),
            "modules": modules,
            "fazendas_auth": [{"id": str(unidade_produtiva_id), "role": "admin"}],
            "is_superuser": False,
            "plan_tier": "PROFISSIONAL",
        },
        expires_delta=timedelta(hours=1),
    )


def _headers(tenant_id: uuid.UUID, unidade_produtiva_id: uuid.UUID, modules: list[str]) -> dict:
    return {
        "Authorization": f"Bearer {_make_token(tenant_id, unidade_produtiva_id, modules)}",
        "X-Fazenda-ID": str(unidade_produtiva_id),
    }


# ── DB Fixtures ───────────────────────────────────────────────────────────────

async def _setup_tenant(session, tenant_id: uuid.UUID, unidade_produtiva_id: uuid.UUID, modules: list[str]):
    """Insere tenant, fazenda, plano e assinatura via SQL raw (evita mapper lazy-init)."""
    import json
    from sqlalchemy import text

    doc = str(tenant_id.int)[:11]
    plano_id = str(uuid.uuid4())

    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, :nome, :doc, true, 0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(tenant_id), "nome": f"Tenant Gate {str(tenant_id)[:8]}", "doc": doc})

    await session.execute(text("""
        INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, :nome, true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(unidade_produtiva_id), "tenant_id": str(tenant_id), "nome": "Fazenda Gate Test"})

    await session.execute(text("""
        INSERT INTO planos_assinatura (id, nome, modulos_inclusos, max_fazendas, limite_usuarios_minimo,
            limite_usuarios_maximo, preco_mensal, preco_anual, plan_tier, ativo, tem_trial, dias_trial,
            is_free, destaque, disponivel_site, disponivel_crm, ordem, created_at)
        VALUES (:id, :nome, CAST(:modulos AS json), -1, 1, 9999, 0, 0, 'PROFISSIONAL', true,
                false, 0, true, false, false, false, 0, NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": plano_id, "nome": f"Plano Gate {str(tenant_id)[:8]}", "modulos": json.dumps(modules)})

    await session.execute(text("""
        INSERT INTO assinaturas_tenant (id, tenant_id, plano_id, status, tipo_assinatura, ciclo_pagamento, data_inicio, created_at, updated_at)
        VALUES (:id, :tenant_id, :plano_id, 'ATIVA', 'TENANT', 'MENSAL', NOW(), NOW(), NOW())
        ON CONFLICT (tenant_id, tipo_assinatura) DO UPDATE SET plano_id = EXCLUDED.plano_id, status = 'ATIVA'
    """), {"id": str(uuid.uuid4()), "tenant_id": str(tenant_id), "plano_id": plano_id})

    await session.commit()


@pytest.fixture(scope="module")
async def gate_db():
    """Garante que os dois tenants de teste têm assinaturas configuradas no banco."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from tests.conftest import _get_db_url
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy.pool import NullPool

    engine = create_async_engine(_get_db_url(), echo=False, poolclass=NullPool,
                                  connect_args={"server_settings": {"search_path": "farms"}})
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as sess:
        await _setup_tenant(sess, TENANT_FULL_ID, FAZENDA_FULL_ID, MODULES_FULL)
        await _setup_tenant(sess, TENANT_CORE_ID, FAZENDA_CORE_ID, MODULES_CORE)
    await engine.dispose()
    yield


# ── Cabeçalhos de teste ───────────────────────────────────────────────────────

@pytest.fixture
def h_full():
    return _headers(TENANT_FULL_ID, FAZENDA_FULL_ID, MODULES_FULL)


@pytest.fixture
def h_core():
    return _headers(TENANT_CORE_ID, FAZENDA_CORE_ID, MODULES_CORE)


# ── FG-01..06: Módulo não contratado retorna 402 ─────────────────────────────

async def test_fg01_agricola_sem_modulo_retorna_402(client, gate_db, h_core):
    """FG-01: GET /safras sem A1_PLANEJAMENTO retorna 402."""
    resp = await client.get("/api/v1/safras/", headers=h_core)
    assert resp.status_code == 402, f"Esperado 402, recebeu {resp.status_code}: {resp.text}"
    assert resp.headers.get("X-Module-Required") == "A1_PLANEJAMENTO"


async def test_fg02_operacoes_sem_a2_retorna_402(client, gate_db, h_core):
    """FG-02: GET /operacoes sem A2_CAMPO retorna 402."""
    resp = await client.get("/api/v1/operacoes/", headers=h_core)
    assert resp.status_code == 402
    assert resp.headers.get("X-Module-Required") == "A2_CAMPO"


async def test_fg03_financeiro_sem_modulo_retorna_402(client, gate_db, h_core):
    """FG-03: GET /financeiro/receitas sem F1_TESOURARIA retorna 402."""
    resp = await client.get("/api/v1/financeiro/receitas/", headers=h_core)
    assert resp.status_code == 402


async def test_fg04_estoque_sem_modulo_retorna_402(client, gate_db, h_core):
    """FG-04: GET /estoque/depositos sem O2_ESTOQUE retorna 402."""
    resp = await client.get("/api/v1/estoque/depositos", headers=h_core)
    assert resp.status_code == 402


async def test_fg05_rh_colaboradores_sem_modulo_retorna_402(client, gate_db, h_core):
    """FG-05: GET /rh/colaboradores sem RH1_REMUNERACAO retorna 402."""
    resp = await client.get("/api/v1/rh/colaboradores", headers=h_core)
    assert resp.status_code == 402
    assert resp.headers.get("X-Module-Required") == "RH1_REMUNERACAO"


async def test_fg06_rh_dashboard_sem_modulo_retorna_402(client, gate_db, h_core):
    """FG-06: GET /rh/dashboard sem RH1_REMUNERACAO retorna 402."""
    resp = await client.get("/api/v1/rh/dashboard", headers=h_core)
    assert resp.status_code == 402


# ── FG-07..09: Módulo contratado permite acesso ───────────────────────────────

async def test_fg07_agricola_com_modulo_permite_acesso(client, gate_db, h_full):
    """FG-07: GET /safras com A1_PLANEJAMENTO retorna 200."""
    resp = await client.get("/api/v1/safras/", headers=h_full)
    assert resp.status_code == 200


async def test_fg08_operacoes_com_a2_permite_acesso(client, gate_db, h_full):
    """FG-08: GET /operacoes com A2_CAMPO retorna 200."""
    resp = await client.get("/api/v1/operacoes/", headers=h_full)
    assert resp.status_code == 200


async def test_fg09_rh_com_modulo_permite_acesso(client, gate_db, h_full):
    """FG-09: GET /rh/colaboradores com RH1_REMUNERACAO retorna 200."""
    resp = await client.get("/api/v1/rh/colaboradores", headers=h_full)
    assert resp.status_code == 200


# ── FG-10..11: Módulo errado não dá acesso a outro domínio ───────────────────

async def test_fg10_modulo_agricola_nao_acessa_financeiro(client, gate_db, h_core):
    """FG-10: CORE-only tenant não acessa F1_TESOURARIA."""
    resp = await client.get("/api/v1/financeiro/receitas/", headers=h_core)
    assert resp.status_code == 402


async def test_fg11_rh_modulo_agricola_nao_acessa_rh(client, gate_db, h_core):
    """FG-11: Token só com CORE não acessa endpoints de RH."""
    resp = await client.get("/api/v1/rh/diarias", headers=h_core)
    assert resp.status_code == 402


# ── FG-12: Admin com todos os módulos acessa tudo ────────────────────────────

async def test_fg12_admin_acessa_todos_modulos(client, gate_db, h_full):
    """FG-12: Tenant com todos os módulos retorna 200 em todos os domínios."""
    endpoints = [
        "/api/v1/safras/",
        "/api/v1/operacoes/",
        "/api/v1/financeiro/receitas/",
        "/api/v1/estoque/depositos",
        "/api/v1/rh/colaboradores",
    ]
    for endpoint in endpoints:
        resp = await client.get(endpoint, headers=h_full)
        assert resp.status_code == 200, (
            f"Tenant full deveria acessar {endpoint}, recebeu {resp.status_code}: {resp.text}"
        )


# ── FG-13: Sem token retorna 401 (não 402) ───────────────────────────────────

async def test_fg13_sem_token_retorna_401_nao_402(client):
    """FG-13: Sem Authorization, retorna 401 — não cai no gate de módulo."""
    resp = await client.get("/api/v1/rh/colaboradores")
    assert resp.status_code == 401


# ── FG-14: Mensagem 402 inclui detalhe legível ───────────────────────────────

async def test_fg14_mensagem_402_inclui_nome_modulo(client, gate_db, h_core):
    """FG-14: 402 retorna mensagem com nome legível do módulo."""
    resp = await client.get("/api/v1/safras/", headers=h_core)
    assert resp.status_code == 402
    body = resp.json()
    assert "detail" in body
    detail = body["detail"].lower()
    assert "módulo" in detail or "planejamento" in detail or "module" in detail
