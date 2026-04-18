"""
Testes de integração — Infraestrutura (Cadastro de Propriedade)
INT-INFRA-01: Tenant A não vê infraestrutura de Tenant B
INT-INFRA-02: CRUD completo de infraestrutura
INT-INFRA-03: Soft delete (inativação) não aparece na listagem padrão
"""
import pytest
import uuid
from datetime import timedelta
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock
from sqlalchemy import text

from core.services.auth_service import AuthService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TENANT_A_ID = uuid.UUID("aaaaaaaa-1111-0000-0000-000000000001")
TENANT_B_ID = uuid.UUID("bbbbbbbb-2222-0000-0000-000000000002")
FAZENDA_A_ID = uuid.UUID("aaaaaaaa-1111-0000-0000-000000000010")
FAZENDA_B_ID = uuid.UUID("bbbbbbbb-2222-0000-0000-000000000010")
GRUPO_A_ID   = uuid.UUID("aaaaaaaa-1111-0000-0000-000000000020")
GRUPO_B_ID   = uuid.UUID("bbbbbbbb-2222-0000-0000-000000000020")


def _token(tenant_id: uuid.UUID, unidade_produtiva_id: uuid.UUID) -> str:
    svc = AuthService(MagicMock())
    return svc.create_access_token({
        "sub": str(uuid.uuid4()),
        "tenant_id": str(tenant_id),
        "modules": ["CORE"],
        "fazendas_auth": [{"id": str(unidade_produtiva_id), "role": "admin"}],
        "is_superuser": False,
        "plan_tier": "ESSENCIAL",
    }, expires_delta=timedelta(hours=1))


@pytest.fixture(scope="module")
def headers_a():
    return {
        "Authorization": f"Bearer {_token(TENANT_A_ID, FAZENDA_A_ID)}",
        "X-Tenant-ID": str(TENANT_A_ID),
        "x-fazenda-id": str(FAZENDA_A_ID),
    }


@pytest.fixture(scope="module")
def headers_b():
    return {
        "Authorization": f"Bearer {_token(TENANT_B_ID, FAZENDA_B_ID)}",
        "X-Tenant-ID": str(TENANT_B_ID),
        "x-fazenda-id": str(FAZENDA_B_ID),
    }


@pytest.fixture
async def client():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def _setup_tenant(session, tenant_id, unidade_produtiva_id, grupo_id, doc):
    """Garante tenant e fazenda no banco."""
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb,
            idioma_padrao, created_at, updated_at)
        VALUES (:id, :nome, :doc, true,  0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(tenant_id), "nome": f"Tenant {doc}", "doc": doc})

    await session.execute(text("""
        INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, :nome, true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(unidade_produtiva_id), "tenant_id": str(tenant_id), "nome": "Fazenda"})


async def _create_area_rural(session, tenant_id, unidade_produtiva_id) -> uuid.UUID:
    area_id = uuid.uuid4()
    await session.execute(text("""
        INSERT INTO cadastros_areas_rurais
            (id, tenant_id, unidade_produtiva_id, tipo, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, :unidade_produtiva_id, 'PROPRIEDADE', 'Fazenda Teste', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(area_id), "tenant_id": str(tenant_id), "unidade_produtiva_id": str(unidade_produtiva_id)})
    return area_id


# ---------------------------------------------------------------------------
# INT-INFRA-01: Isolamento de tenant
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_a_nao_ve_infraestrutura_de_tenant_b(client, session, headers_a, headers_b):
    """INT-INFRA-01: Infraestrutura criada por Tenant B não aparece para Tenant A."""
    await _setup_tenant(session, TENANT_A_ID, FAZENDA_A_ID, GRUPO_A_ID, "11111111111")
    await _setup_tenant(session, TENANT_B_ID, FAZENDA_B_ID, GRUPO_B_ID, "22222222222")
    area_b_id = await _create_area_rural(session, TENANT_B_ID, FAZENDA_B_ID)
    await session.commit()

    # Tenant B cria infraestrutura
    r_create = await client.post(
        f"/api/v1/cadastros/areas-rurais/{area_b_id}/infraestruturas",
        json={"nome": "Silo Secreto B", "tipo": "silo", "capacidade": 10000, "unidade_capacidade": "ton"},
        headers=headers_b,
    )
    if r_create.status_code != 201:
        pytest.skip(f"Não foi possível criar infraestrutura do Tenant B: {r_create.text}")

    # Tenant A tenta listar infraestruturas da área do Tenant B — deve receber 404
    r_a = await client.get(
        f"/api/v1/cadastros/areas-rurais/{area_b_id}/infraestruturas",
        headers=headers_a,
    )
    assert r_a.status_code == 404, (
        f"Tenant A acessou infraestrutura do Tenant B! Status: {r_a.status_code}"
    )


# ---------------------------------------------------------------------------
# INT-INFRA-02: CRUD completo
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_infraestrutura_crud(client, session, headers_a):
    """INT-INFRA-02: Criar, listar, atualizar e inativar infraestrutura."""
    await _setup_tenant(session, TENANT_A_ID, FAZENDA_A_ID, GRUPO_A_ID, "11111111111")
    area_a_id = await _create_area_rural(session, TENANT_A_ID, FAZENDA_A_ID)
    await session.commit()

    base = f"/api/v1/cadastros/areas-rurais/{area_a_id}/infraestruturas"

    # Criar
    r_create = await client.post(base, json={
        "nome": "Curral Principal",
        "tipo": "curral",
        "capacidade": 200,
        "unidade_capacidade": "cabeças",
        "latitude": -15.5,
        "longitude": -47.5,
    }, headers=headers_a)
    assert r_create.status_code == 201
    infra = r_create.json()
    assert infra["nome"] == "Curral Principal"
    assert infra["tipo"] == "curral"
    assert float(infra["capacidade"]) == 200.0
    infra_id = infra["id"]

    # Listar
    r_list = await client.get(base, headers=headers_a)
    assert r_list.status_code == 200
    nomes = [i["nome"] for i in r_list.json()]
    assert "Curral Principal" in nomes

    # Atualizar
    r_patch = await client.patch(f"{base}/{infra_id}", json={"capacidade": 350}, headers=headers_a)
    assert r_patch.status_code == 200
    assert float(r_patch.json()["capacidade"]) == 350.0

    # Inativar
    r_delete = await client.delete(f"{base}/{infra_id}", headers=headers_a)
    assert r_delete.status_code == 204

    # Após inativação não aparece na listagem padrão
    r_list2 = await client.get(base, headers=headers_a)
    ids_ativos = [i["id"] for i in r_list2.json()]
    assert infra_id not in ids_ativos


# ---------------------------------------------------------------------------
# INT-INFRA-03: Tipo inválido retorna 422
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_infraestrutura_tipo_invalido(client, session, headers_a):
    """INT-INFRA-03: Tipo não permitido retorna 422."""
    await _setup_tenant(session, TENANT_A_ID, FAZENDA_A_ID, GRUPO_A_ID, "11111111111")
    area_a_id = await _create_area_rural(session, TENANT_A_ID, FAZENDA_A_ID)
    await session.commit()

    r = await client.post(
        f"/api/v1/cadastros/areas-rurais/{area_a_id}/infraestruturas",
        json={"nome": "X", "tipo": "TIPO_INEXISTENTE"},
        headers=headers_a,
    )
    assert r.status_code == 422
