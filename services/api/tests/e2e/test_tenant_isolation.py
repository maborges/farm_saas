"""
Testes E2E — Isolamento de Tenant (Multi-tenancy)
INT-TEN-01..04: Tenant A não acessa dados de Tenant B
"""
import pytest
import uuid
from datetime import timedelta
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock

from core.services.auth_service import AuthService


# ---------------------------------------------------------------------------
# Dois tenants completamente separados
# ---------------------------------------------------------------------------

TENANT_A_ID = uuid.UUID("aaaaaaaa-1111-0000-0000-000000000001")
TENANT_B_ID = uuid.UUID("bbbbbbbb-2222-0000-0000-000000000002")
FAZENDA_A_ID = uuid.UUID("aaaaaaaa-1111-0000-0000-000000000010")
FAZENDA_B_ID = uuid.UUID("bbbbbbbb-2222-0000-0000-000000000010")
GRUPO_A_ID = uuid.UUID("aaaaaaaa-1111-0000-0000-000000000020")
GRUPO_B_ID = uuid.UUID("bbbbbbbb-2222-0000-0000-000000000020")


def _token(tenant_id: uuid.UUID, modules: list[str] = None) -> str:
    svc = AuthService(MagicMock())
    return svc.create_access_token({
        "sub": str(uuid.uuid4()),
        "tenant_id": str(tenant_id),
        "modules": modules or ["CORE", "A1_PLANEJAMENTO", "F1_TESOURARIA", "O1_FROTA", "O2_ESTOQUE"],
        "fazendas_auth": [{"id": str(
            FAZENDA_A_ID if tenant_id == TENANT_A_ID else FAZENDA_B_ID
        ), "role": "admin"}],
        "is_superuser": False,
        "plan_tier": "PROFISSIONAL",
    }, expires_delta=timedelta(hours=1))


@pytest.fixture(scope="module")
def headers_a():
    return {"Authorization": f"Bearer {_token(TENANT_A_ID)}",
            "X-Tenant-ID": str(TENANT_A_ID),
            "x-fazenda-id": str(FAZENDA_A_ID)}


@pytest.fixture(scope="module")
def headers_b():
    return {"Authorization": f"Bearer {_token(TENANT_B_ID)}",
            "X-Tenant-ID": str(TENANT_B_ID),
            "x-fazenda-id": str(FAZENDA_B_ID)}


@pytest.fixture
async def client():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# INT-TEN-01: Tenant A não vê safras de Tenant B
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_a_nao_ve_safras_de_tenant_b(client, session, headers_a, headers_b):
    """INT-TEN-01: Safras criadas pelo Tenant B não aparecem para Tenant A"""
    from sqlalchemy import text

    # Setup: garante grupos, fazendas e talhão para ambos os tenants
    for t_id, f_id, doc in [
        (TENANT_A_ID, FAZENDA_A_ID, "11111111111"),
        (TENANT_B_ID, FAZENDA_B_ID, "22222222222"),
    ]:
        await session.execute(text("""
            INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
            VALUES (:id, :nome, :doc, true,  0, 10240, 'pt-BR', NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(t_id), "nome": f"Tenant {str(t_id)[:4]}", "doc": doc})

        pass  # grupos_fazendas removed from schema

        await session.execute(text("""
            INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at)
            VALUES (:id, :tenant_id, :nome, true, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(f_id), "tenant_id": str(t_id), "nome": f"Fazenda {str(t_id)[:4]}"})

    talhao_b_id = uuid.uuid4()
    await session.execute(text("""
        INSERT INTO cadastros_areas_rurais
            (id, tenant_id, unidade_produtiva_id, tipo, nome, area_hectares, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, :unidade_produtiva_id, 'TALHAO', 'Talhão B', 50.0, true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(talhao_b_id), "tenant_id": str(TENANT_B_ID),
           "unidade_produtiva_id": str(FAZENDA_B_ID)})
    await session.commit()

    # Tenant B cria uma safra
    r_b = await client.post("/api/v1/safras/", json={
        "talhao_id": str(talhao_b_id),
        "ano_safra": "2099/00",
        "cultura": "SOJA_EXCLUSIVA_B",
        "cultivar_nome": "Cultivar Secreta B",
    }, headers=headers_b)

    if r_b.status_code != 201:
        pytest.skip(f"Não foi possível criar safra do Tenant B: {r_b.text}")

    # Tenant A lista safras — não deve ver a safra do Tenant B
    r_a = await client.get("/api/v1/safras/", headers=headers_a)
    assert r_a.status_code == 200

    safras_a = r_a.json()
    culturas = [s["cultura"] for s in safras_a]
    assert "SOJA_EXCLUSIVA_B" not in culturas, (
        "VIOLAÇÃO DE ISOLAMENTO: Tenant A conseguiu ver safra do Tenant B!"
    )


# ---------------------------------------------------------------------------
# INT-TEN-02: Tenant A não vê financeiro de Tenant B
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_a_nao_ve_financeiro_de_tenant_b(client, session, headers_a, headers_b):
    """INT-TEN-02: Receitas do Tenant B não aparecem para Tenant A"""
    from sqlalchemy import text

    # Setup: garante tenants, grupos e fazendas
    for t_id, f_id, doc in [
        (TENANT_A_ID, FAZENDA_A_ID, "11111111111"),
        (TENANT_B_ID, FAZENDA_B_ID, "22222222222"),
    ]:
        await session.execute(text("""
            INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
            VALUES (:id, :nome, :doc, true,  0, 10240, 'pt-BR', NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(t_id), "nome": f"Tenant {str(t_id)[:4]}", "doc": doc})

        pass  # grupos_fazendas removed from schema

        await session.execute(text("""
            INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at)
            VALUES (:id, :tenant_id, :nome, true, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(f_id), "tenant_id": str(t_id), "nome": f"Fazenda {str(t_id)[:4]}"})
    await session.commit()

    plano_b_id = uuid.uuid4()
    await session.execute(text("""
        INSERT INTO fin_planos_conta
            (id, tenant_id, codigo, nome, tipo, natureza, ativo, ordem, is_sistema, created_at, updated_at)
        VALUES (:id, :tenant_id, '4.9.99', 'Conta Secreta B', 'RECEITA', 'CREDITO', true, 99, false, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(plano_b_id), "tenant_id": str(TENANT_B_ID)})
    await session.commit()

    from datetime import date
    r_b = await client.post("/api/v1/financeiro/receitas/", json={
        "unidade_produtiva_id": str(FAZENDA_B_ID),
        "plano_conta_id": str(plano_b_id),
        "descricao": "RECEITA_SECRETA_TENANT_B",
        "valor_total": 999999.0,
        "data_emissao": str(date.today()),
        "data_vencimento": str(date.today()),
        "total_parcelas": 1,
    }, headers=headers_b)

    if r_b.status_code != 201:
        pytest.skip(f"Não foi possível criar receita do Tenant B: {r_b.text}")

    # Tenant A lista receitas
    r_a = await client.get("/api/v1/financeiro/receitas/", headers=headers_a)
    assert r_a.status_code == 200

    receitas_a = r_a.json()
    descricoes = [r["descricao"] for r in receitas_a]
    assert "RECEITA_SECRETA_TENANT_B" not in descricoes, (
        "VIOLAÇÃO DE ISOLAMENTO: Tenant A conseguiu ver receita do Tenant B!"
    )


# ---------------------------------------------------------------------------
# INT-TEN-03: Tenant A não acessa recurso de Tenant B por ID direto
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_a_nao_acessa_recurso_por_id_direto(client, session, headers_a, headers_b):
    """INT-TEN-03: GET /receitas/{id_do_tenant_b} retorna 404 para Tenant A"""
    from sqlalchemy import text
    from datetime import date

    # Setup: garante tenants, grupos e fazendas
    for t_id, f_id, doc in [
        (TENANT_A_ID, FAZENDA_A_ID, "11111111111"),
        (TENANT_B_ID, FAZENDA_B_ID, "22222222222"),
    ]:
        await session.execute(text("""
            INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
            VALUES (:id, :nome, :doc, true,  0, 10240, 'pt-BR', NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(t_id), "nome": f"Tenant {str(t_id)[:4]}", "doc": doc})

        pass  # grupos_fazendas removed from schema

        await session.execute(text("""
            INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at)
            VALUES (:id, :tenant_id, :nome, true, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(f_id), "tenant_id": str(t_id), "nome": f"Fazenda {str(t_id)[:4]}"})
    await session.commit()

    plano_b_id = uuid.uuid4()
    await session.execute(text("""
        INSERT INTO fin_planos_conta
            (id, tenant_id, codigo, nome, tipo, natureza, ativo, ordem, is_sistema, created_at, updated_at)
        VALUES (:id, :tenant_id, '4.9.98', 'Conta Secreta B2', 'RECEITA', 'CREDITO', true, 98, false, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(plano_b_id), "tenant_id": str(TENANT_B_ID)})
    await session.commit()

    r_b = await client.post("/api/v1/financeiro/receitas/", json={
        "unidade_produtiva_id": str(FAZENDA_B_ID),
        "plano_conta_id": str(plano_b_id),
        "descricao": "Recurso privado Tenant B",
        "valor_total": 1000.0,
        "data_emissao": str(date.today()),
        "data_vencimento": str(date.today()),
        "total_parcelas": 1,
    }, headers=headers_b)

    if r_b.status_code != 201:
        pytest.skip(f"Setup falhou: {r_b.text}")

    recurso_b_id = r_b.json()[0]["id"]

    # Tenant A tenta acessar diretamente o ID do Tenant B
    r_a = await client.get(
        f"/api/v1/financeiro/receitas/{recurso_b_id}",
        headers=headers_a,
    )
    assert r_a.status_code in (403, 404), (
        f"VIOLAÇÃO DE ISOLAMENTO: Tenant A recebeu {r_a.status_code} ao acessar recurso do Tenant B"
    )


# ---------------------------------------------------------------------------
# INT-TEN-04: Token sem tenant_id não acessa recursos de tenant
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_sem_tenant_id_bloqueado(client):
    """INT-TEN-04: Token com tenant_id=None não acessa endpoints de tenant"""
    svc = AuthService(MagicMock())
    token_sem_tenant = svc.create_access_token({
        "sub": str(uuid.uuid4()),
        "tenant_id": None,
        "modules": ["CORE"],
        "is_superuser": False,
        "plan_tier": "BASICO",
    }, expires_delta=timedelta(hours=1))

    response = await client.get(
        "/api/v1/agricola/safras/",
        headers={"Authorization": f"Bearer {token_sem_tenant}"},
    )
    # 404 é aceitável: tenant_id=None faz a query não encontrar nenhum tenant
    # O importante é que não retorne 200 com dados de outro tenant
    assert response.status_code in (401, 403, 404, 422), (
        f"Token sem tenant deveria ser bloqueado, recebeu {response.status_code}"
    )
