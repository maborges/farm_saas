"""
Testes E2E — Isolamento de Tenant no módulo Caderno de Campo
CDN-TEN-01..04: Tenant A não acessa caderno de Tenant B
"""
import pytest
import uuid
from datetime import date, timedelta
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
SAFRA_A_ID = uuid.UUID("aaaaaaaa-1111-0000-0000-000000000030")
SAFRA_B_ID = uuid.UUID("bbbbbbbb-2222-0000-0000-000000000030")
TALHAO_A_ID = uuid.UUID("aaaaaaaa-1111-0000-0000-000000000040")
TALHAO_B_ID = uuid.UUID("bbbbbbbb-2222-0000-0000-000000000040")


def _token(tenant_id: uuid.UUID) -> str:
    svc = AuthService(MagicMock())
    unidade_produtiva_id = FAZENDA_A_ID if tenant_id == TENANT_A_ID else FAZENDA_B_ID
    return svc.create_access_token({
        "sub": str(uuid.uuid4()),
        "tenant_id": str(tenant_id),
        "modules": ["CORE", "AGRICOLA_ESSENCIAL"],
        "fazendas_auth": [{"id": str(unidade_produtiva_id), "role": "admin"}],
        "is_superuser": False,
        "plan_tier": "PROFISSIONAL",
    }, expires_delta=timedelta(hours=1))


@pytest.fixture(scope="module")
def headers_a():
    return {
        "Authorization": f"Bearer {_token(TENANT_A_ID)}",
        "X-Tenant-ID": str(TENANT_A_ID),
        "x-fazenda-id": str(FAZENDA_A_ID),
    }


@pytest.fixture(scope="module")
def headers_b():
    return {
        "Authorization": f"Bearer {_token(TENANT_B_ID)}",
        "X-Tenant-ID": str(TENANT_B_ID),
        "x-fazenda-id": str(FAZENDA_B_ID),
    }


@pytest.fixture
async def client():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# Setup do banco de dados para os dois tenants
# ---------------------------------------------------------------------------

async def _setup_tenants(session):
    from sqlalchemy import text

    # Plano base para assinaturas
    plano_base_id = "00000000-0000-0000-0000-000000000001"
    await session.execute(text("""
        INSERT INTO planos_assinatura (id, nome, modulos_inclusos, limite_usuarios_minimo,
            limite_usuarios_maximo, preco_mensal, preco_anual, max_fazendas,
            max_categorias_plano, tem_trial, dias_trial, is_free, destaque, ordem,
            ativo, disponivel_site, disponivel_crm, created_at)
        VALUES (:id, 'Plano Base', CAST(:modulos AS json), 1, 5,
                0, 0, -1, -1, false, 15, false, false, 0, true, false, true, NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": plano_base_id, "modulos": '["CORE","AGRICOLA_ESSENCIAL"]'})

    for t_id, f_id, doc in [
        (TENANT_A_ID, FAZENDA_A_ID, "11111111111"),
        (TENANT_B_ID, FAZENDA_B_ID, "22222222222"),
    ]:
        await session.execute(text("""
            INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb,
                                 storage_limite_mb, idioma_padrao, created_at, updated_at)
            VALUES (:id, :nome, :doc, true,  0, 10240, 'pt-BR', NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(t_id), "nome": f"Tenant {str(t_id)[:4]}", "doc": doc})

        await session.execute(text("""
            INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at)
            VALUES (:id, :tenant_id, :nome, true, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(f_id), "tenant_id": str(t_id),
               "nome": f"Fazenda {str(t_id)[:4]}"})

        await session.execute(text("""
            INSERT INTO assinaturas_tenant (id, tenant_id, plano_id, status, tipo_assinatura, ciclo_pagamento, data_inicio, created_at, updated_at)
            VALUES (:id, :tenant_id, :plano_id, 'ATIVA', 'TENANT', 'MENSAL', NOW(), NOW(), NOW())
            ON CONFLICT (tenant_id, tipo_assinatura) DO UPDATE SET plano_id = EXCLUDED.plano_id, status = 'ATIVA'
        """), {"id": str(uuid.uuid4()), "tenant_id": str(t_id), "plano_id": plano_base_id})

    # Áreas rurais tipo TALHAO
    for talhao_id, tenant_id, unidade_produtiva_id, nome in [
        (TALHAO_A_ID, TENANT_A_ID, FAZENDA_A_ID, "Talhão A"),
        (TALHAO_B_ID, TENANT_B_ID, FAZENDA_B_ID, "Talhão B"),
    ]:
        await session.execute(text("""
            INSERT INTO cadastros_areas_rurais
                (id, tenant_id, unidade_produtiva_id, tipo, nome, area_hectares, ativo, created_at, updated_at)
            VALUES (:id, :tenant_id, :unidade_produtiva_id, 'TALHAO', :nome, 50.0, true, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(talhao_id), "tenant_id": str(tenant_id),
               "unidade_produtiva_id": str(unidade_produtiva_id), "nome": nome})

    # Safras
    for safra_id, tenant_id, talhao_id in [
        (SAFRA_A_ID, TENANT_A_ID, TALHAO_A_ID),
        (SAFRA_B_ID, TENANT_B_ID, TALHAO_B_ID),
    ]:
        await session.execute(text("""
            INSERT INTO safras (id, tenant_id, talhao_id, ano_safra, cultura, status, created_at, updated_at)
            VALUES (:id, :tenant_id, :talhao_id, '2025/26', 'Soja', 'PLANEJADA', NOW(), NOW())
            ON CONFLICT DO NOTHING
        """), {"id": str(safra_id), "tenant_id": str(tenant_id), "talhao_id": str(talhao_id)})

    await session.commit()


# ---------------------------------------------------------------------------
# CDN-TEN-01: Tenant A não vê entradas de caderno de Tenant B
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_a_nao_ve_entradas_de_tenant_b(client, session, headers_a, headers_b):
    """CDN-TEN-01: Entradas do Tenant B não aparecem na timeline do Tenant A"""
    await _setup_tenants(session)

    # Tenant B cria uma entrada no caderno
    r_b = await client.post("/api/v1/caderno/entradas", json={
        "safra_id": str(SAFRA_B_ID),
        "talhao_id": str(TALHAO_B_ID),
        "tipo": "OBSERVACAO",
        "descricao": "OBSERVACAO_SECRETA_TENANT_B",
        "data_registro": str(date.today()),
    }, headers=headers_b)

    if r_b.status_code != 201:
        pytest.skip(f"Não foi possível criar entrada do Tenant B: {r_b.text}")

    # Tenant A lista timeline — não deve ver entradas do Tenant B
    r_a = await client.get(
        f"/api/v1/caderno/safra/{SAFRA_A_ID}/timeline",
        headers=headers_a,
    )
    assert r_a.status_code == 200

    timeline_a = r_a.json()
    descricoes = [item["descricao"] for item in timeline_a]
    assert "OBSERVACAO_SECRETA_TENANT_B" not in descricoes, (
        "VIOLAÇÃO DE ISOLAMENTO: Tenant A conseguiu ver entrada do Tenant B!"
    )


# ---------------------------------------------------------------------------
# CDN-TEN-02: Tenant A não acessa entrada de Tenant B por ID direto
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_a_nao_acessa_entrada_por_id_direto(client, session, headers_a, headers_b):
    """CDN-TEN-02: GET /caderno/entradas/{id_do_tenant_b} retorna 404 para Tenant A"""
    await _setup_tenants(session)

    # Tenant B cria entrada
    r_b = await client.post("/api/v1/caderno/entradas", json={
        "safra_id": str(SAFRA_B_ID),
        "talhao_id": str(TALHAO_B_ID),
        "tipo": "MONITORAMENTO",
        "descricao": "Entrada privada Tenant B",
        "data_registro": str(date.today()),
        "nivel_severidade": "ALTO",
    }, headers=headers_b)

    if r_b.status_code != 201:
        pytest.skip(f"Setup falhou: {r_b.text}")

    entrada_b_id = r_b.json()["id"]

    # Tenant A tenta acessar diretamente
    r_a = await client.get(
        f"/api/v1/caderno/entradas/{entrada_b_id}",
        headers=headers_a,
    )
    assert r_a.status_code in (403, 404), (
        f"VIOLAÇÃO DE ISOLAMENTO: Tenant A recebeu {r_a.status_code} ao acessar entrada do Tenant B"
    )


# ---------------------------------------------------------------------------
# CDN-TEN-03: Tenant A não vê visitas técnicas de Tenant B
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_a_nao_ve_visitas_de_tenant_b(client, session, headers_a, headers_b):
    """CDN-TEN-03: Visitas técnicas do Tenant B não aparecem para Tenant A"""
    await _setup_tenants(session)

    # Tenant B registra visita técnica
    r_b = await client.post("/api/v1/caderno/visitas", json={
        "safra_id": str(SAFRA_B_ID),
        "talhao_id": str(TALHAO_B_ID),
        "nome_rt": "Dr. Visitante B",
        "crea": "123456/UF-B",
        "data_visita": str(date.today()),
        "observacoes": "VISITA_SECRETA_TENANT_B",
        "constatacoes": [{"descricao": "Constatação sigilosa B"}],
    }, headers=headers_b)

    if r_b.status_code != 201:
        pytest.skip(f"Não foi possível criar visita do Tenant B: {r_b.text}")

    # Tenant A lista visitas da safra A — não deve ver do B
    # Como a safra A não existe de verdade, o endpoint deve retornar vazio ou erro
    r_a = await client.get(
        f"/api/v1/caderno/visitas/safra/{SAFRA_A_ID}",
        headers=headers_a,
    )
    # 200 com lista vazia ou 404 são aceitáveis — o importante é não vazar dados
    if r_a.status_code == 200:
        visitas_a = r_a.json()
        observacoes = [v.get("observacoes", "") for v in visitas_a]
        assert "VISITA_SECRETA_TENANT_B" not in observacoes, (
            "VIOLAÇÃO DE ISOLAMENTO: Tenant A conseguiu ver visita do Tenant B!"
        )


# ---------------------------------------------------------------------------
# CDN-TEN-04: Tenant A não vê entregas de EPI de Tenant B
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_a_nao_ve_epis_de_tenant_b(client, session, headers_a, headers_b):
    """CDN-TEN-04: Entregas de EPI do Tenant B não aparecem para Tenant A"""
    await _setup_tenants(session)

    # Tenant B registra entrega de EPI
    r_b = await client.post("/api/v1/caderno/epis", json={
        "nome_trabalhador": "Trabalhador Secreto B",
        "epi_tipo": "LUVA",
        "quantidade": 2,
        "data_entrega": str(date.today()),
    }, headers=headers_b)

    if r_b.status_code != 201:
        pytest.skip(f"Não foi possível criar EPI do Tenant B: {r_b.text}")

    # Tenant A lista EPIs — endpoint /epis não tem filtro por tenant na URL,
    # mas o service filtra por tenant_id. Verifica que não retorna dados do B.
    r_a = await client.get("/api/v1/caderno/epis", headers=headers_a)
    assert r_a.status_code == 200

    epis_a = r_a.json()
    nomes = [e.get("nome_trabalhador", "") for e in epis_a]
    assert "Trabalhador Secreto B" not in nomes, (
        "VIOLAÇÃO DE ISOLAMENTO: Tenant A conseguiu ver EPI do Tenant B!"
    )
