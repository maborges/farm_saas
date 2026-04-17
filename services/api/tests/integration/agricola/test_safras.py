"""
Testes de Integração — Safras (HTTP)
AGR-SAF-01..05: CRUD e filtros via API REST
"""
import pytest
import uuid
from sqlalchemy import text

# IDs herdados do conftest de integração
from tests.integration.conftest import TENANT_ID, FAZENDA_ID, TALHAO_ID


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _payload_safra(**overrides) -> dict:
    base = {
        "talhao_id": str(TALHAO_ID),
        "ano_safra": f"2{uuid.uuid4().int % 900 + 100}",
        "cultura": "SOJA",
        "cultivar_nome": "TMG 7062 IPRO",
        "sistema_plantio": "PLANTIO_DIRETO",
        "area_plantada_ha": 50.0,
    }
    base.update(overrides)
    return base


async def _garantir_talhao(session):
    """Garante que os registros de suporte (tenant, fazenda, talhao) existem."""
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, 'Tenant Integração', '12345678901', true,  0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO fazendas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, 'Fazenda Integração', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(FAZENDA_ID), "tenant_id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO cadastros_areas_rurais
            (id, tenant_id, unidade_produtiva_id, tipo, nome, area_hectares, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, :unidade_produtiva_id, 'TALHAO', 'Talhão Integração', 100.0, true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TALHAO_ID), "tenant_id": str(TENANT_ID), "unidade_produtiva_id": str(FAZENDA_ID)})

    await session.execute(text("""
        INSERT INTO talhoes
            (id, tenant_id, unidade_produtiva_id, nome, area_ha, ativo, irrigado, historico_culturas, created_at, updated_at)
        VALUES (:id, :tenant_id, :unidade_produtiva_id, 'Talhão Integração', 100.0, true, false, '[]'::json, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TALHAO_ID), "tenant_id": str(TENANT_ID), "unidade_produtiva_id": str(FAZENDA_ID)})

    # Cancela safras existentes para evitar conflito de duplicata entre runs
    await session.execute(text(
        "UPDATE safras SET status = 'CANCELADA' WHERE tenant_id = :tid AND status != 'CANCELADA'"
    ), {"tid": str(TENANT_ID)})

    await session.commit()


# ---------------------------------------------------------------------------
# AGR-SAF-01: Criar safra com dados válidos
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_criar_safra_dados_validos(client, session, headers_agricola):
    """AGR-SAF-01: POST /safras cria safra e retorna 201 com dados corretos"""
    await _garantir_talhao(session)

    response = await client.post(
        "/api/v1/safras/",
        json=_payload_safra(),
        headers=headers_agricola,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["cultura"] == "SOJA"
    assert data["status"] == "PLANEJADA"
    assert "id" in data
    assert "ano_safra" in data


# ---------------------------------------------------------------------------
# AGR-SAF-02: Safra com nome duplicado (mesmo talhão + ano + cultura)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_safra_duplicada_retorna_erro(client, session, headers_agricola):
    """AGR-SAF-02: Criar safra duplicada (mesmo talhao+ano+cultura) retorna 400/409"""
    await _garantir_talhao(session)

    payload = _payload_safra(ano_safra="2024/25", cultura="MILHO")

    # Primeira criação
    r1 = await client.post("/api/v1/safras/", json=payload, headers=headers_agricola)
    assert r1.status_code == 201

    # Segunda criação igual — deve falhar
    r2 = await client.post("/api/v1/safras/", json=payload, headers=headers_agricola)
    assert r2.status_code in (400, 409, 422), f"Esperava erro, recebeu {r2.status_code}: {r2.text}"


# ---------------------------------------------------------------------------
# AGR-SAF-03: Listar safras com filtros
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listar_safras_com_filtros(client, session, headers_agricola):
    """AGR-SAF-03: GET /safras?cultura=SOJA retorna apenas safras de soja"""
    await _garantir_talhao(session)

    # Garante ao menos uma safra de soja
    await client.post(
        "/api/v1/safras/",
        json=_payload_safra(cultura="SOJA"),
        headers=headers_agricola,
    )

    response = await client.get(
        "/api/v1/safras/?cultura=SOJA",
        headers=headers_agricola,
    )

    assert response.status_code == 200
    safras = response.json()
    assert isinstance(safras, list)
    # Todas devem ser SOJA (se filtro funcionar)
    culturas = {s["cultura"] for s in safras}
    assert culturas <= {"SOJA"}, f"Filtro de cultura falhou: {culturas}"


# ---------------------------------------------------------------------------
# AGR-SAF-04: Atualizar safra
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_atualizar_safra(client, session, headers_agricola):
    """AGR-SAF-04: PATCH /safras/{id} atualiza campos da safra"""
    await _garantir_talhao(session)

    # Cria safra
    r = await client.post(
        "/api/v1/safras/",
        json=_payload_safra(),
        headers=headers_agricola,
    )
    assert r.status_code == 201
    safra_id = r.json()["id"]

    # Atualiza
    update_resp = await client.patch(
        f"/api/v1/safras/{safra_id}",
        json={"observacoes": "Atualizado via teste de integração"},
        headers=headers_agricola,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["observacoes"] == "Atualizado via teste de integração"


# ---------------------------------------------------------------------------
# AGR-SAF-05: Avançar fase da safra
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_avancar_fase_safra(client, session, headers_agricola):
    """AGR-SAF-05: POST /safras/{id}/avancar-fase avança para PREPARO_SOLO"""
    await _garantir_talhao(session)

    r = await client.post(
        "/api/v1/safras/",
        json=_payload_safra(),
        headers=headers_agricola,
    )
    assert r.status_code == 201
    safra_id = r.json()["id"]
    assert r.json()["status"] == "PLANEJADA"

    # Avança fase
    fase_resp = await client.post(
        f"/api/v1/safras/{safra_id}/avancar-fase/PREPARO_SOLO",
        json={"observacao": "Iniciando preparo do solo"},
        headers=headers_agricola,
    )
    assert fase_resp.status_code in (200, 201), fase_resp.text

    # Confirma nova fase
    get_resp = await client.get(
        f"/api/v1/safras/{safra_id}",
        headers=headers_agricola,
    )
    if get_resp.status_code == 200:
        assert get_resp.json()["status"] == "PREPARO_SOLO"


# ---------------------------------------------------------------------------
# AGR-SAF: Sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_safras_sem_token_retorna_401(client):
    """Endpoint de safras sem token retorna 401"""
    response = await client.get("/api/v1/safras/")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# AGR-SAF: Token sem módulo A1 retorna 402/403
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_safras_sem_modulo_a1_retorna_erro(client, token_financeiro):
    """Token sem módulo A1 não acessa safras"""
    headers = {"Authorization": f"Bearer {token_financeiro}"}
    response = await client.get("/api/v1/safras/", headers=headers)
    assert response.status_code in (402, 403)
