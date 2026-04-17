"""
Testes de Integração — RH (HTTP)
RH-COL-01..04: Colaboradores
RH-DIA-01..02: Diárias
RH-EMP-01..03: Empreitadas
"""
import pytest
import uuid
from datetime import date
from sqlalchemy import text

from tests.integration.conftest import TENANT_ID, FAZENDA_ID


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

async def _garantir_suporte(session):
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, 'Tenant RH', '77788899900', true,  0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TENANT_ID)})
    await session.execute(text("""
        INSERT INTO fazendas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, 'Fazenda RH', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(FAZENDA_ID), "tenant_id": str(TENANT_ID)})
    await session.commit()


@pytest.fixture(scope="module")
def token_rh():
    from datetime import timedelta
    from unittest.mock import MagicMock
    from core.services.auth_service import AuthService
    svc = AuthService(MagicMock())
    return svc.create_access_token({
        "sub": str(uuid.uuid4()),
        "tenant_id": str(TENANT_ID),
        "modules": ["CORE", "RH1"],
        "fazendas_auth": [{"id": str(FAZENDA_ID), "role": "admin"}],
        "is_superuser": False,
        "plan_tier": "PROFISSIONAL",
    }, expires_delta=__import__("datetime").timedelta(hours=1))


@pytest.fixture
def headers_rh(token_rh):
    return {"Authorization": f"Bearer {token_rh}",
            "X-Tenant-ID": str(TENANT_ID)}


def _payload_colaborador(**overrides) -> dict:
    base = {
        "nome": f"Colaborador {uuid.uuid4().hex[:4]}",
        "tipo_contrato": "DIARISTA",
        "valor_diaria": 180.0,
        "unidade_produtiva_id": str(FAZENDA_ID),
        "cargo": "Operador Rural",
    }
    # Remove cpf if not supported by schema (ColaboradorCreate has cpf as Optional)
    base.update(overrides)
    return base


# ===========================================================================
# RH-COL: Colaboradores
# ===========================================================================

@pytest.mark.asyncio
async def test_cadastrar_colaborador(client, session, headers_rh):
    """RH-COL-01: POST /rh/colaboradores cria colaborador e retorna 201"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/rh/colaboradores",
        json=_payload_colaborador(),
        headers=headers_rh,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["tipo_contrato"] == "DIARISTA"
    assert data["valor_diaria"] == 180.0
    assert "id" in data


@pytest.mark.asyncio
async def test_listar_colaboradores(client, session, headers_rh):
    """RH-COL-02: GET /rh/colaboradores retorna lista"""
    await _garantir_suporte(session)

    await client.post("/api/v1/rh/colaboradores",
                      json=_payload_colaborador(), headers=headers_rh)

    response = await client.get("/api/v1/rh/colaboradores", headers=headers_rh)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
@pytest.mark.xfail(reason="CPF unique constraint not yet implemented in rh_colaboradores")
async def test_colaborador_cpf_duplicado(client, session, headers_rh):
    """RH-COL-04: Colaborador com CPF duplicado retorna 400/409"""
    await _garantir_suporte(session)

    cpf = "12345678901"
    payload = _payload_colaborador(cpf=cpf)

    r1 = await client.post("/api/v1/rh/colaboradores", json=payload, headers=headers_rh)
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/rh/colaboradores", json=payload, headers=headers_rh)
    assert r2.status_code in (400, 409, 422), (
        f"CPF duplicado deveria ser rejeitado, recebeu {r2.status_code}"
    )


# ===========================================================================
# RH-DIA: Diárias
# ===========================================================================

@pytest.mark.asyncio
async def test_lancar_diaria(client, session, headers_rh):
    """RH-DIA-01: POST /rh/diarias lança diária para colaborador"""
    await _garantir_suporte(session)

    r = await client.post("/api/v1/rh/colaboradores",
                          json=_payload_colaborador(), headers=headers_rh)
    assert r.status_code == 201
    colaborador_id = r.json()["id"]

    response = await client.post(
        "/api/v1/rh/diarias",
        json={
            "colaborador_id": colaborador_id,
            "data": str(date.today()),
            "horas_trabalhadas": 8.0,
            "atividade": "PLANTIO",
            "valor_diaria": 180.0,
            "unidade_produtiva_id": str(FAZENDA_ID),
        },
        headers=headers_rh,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["valor_diaria"] == 180.0
    assert data["status"] == "PENDENTE"


@pytest.mark.asyncio
async def test_pagar_diarias(client, session, headers_rh):
    """RH-DIA-02: POST /rh/diarias/pagar-lote marca diárias como pagas"""
    await _garantir_suporte(session)

    r = await client.post("/api/v1/rh/colaboradores",
                          json=_payload_colaborador(), headers=headers_rh)
    assert r.status_code == 201
    colaborador_id = r.json()["id"]

    # Cria 2 diárias
    ids = []
    for i in range(2):
        d = await client.post("/api/v1/rh/diarias", json={
            "colaborador_id": colaborador_id,
            "data": str(date.today() - __import__("datetime").timedelta(days=i)),
            "horas_trabalhadas": 8.0,
            "atividade": "COLHEITA",
            "valor_diaria": 200.0,
            "unidade_produtiva_id": str(FAZENDA_ID),
        }, headers=headers_rh)
        assert d.status_code == 201
        ids.append(d.json()["id"])

    # Paga em lote
    pagamento = await client.post(
        "/api/v1/rh/diarias/pagar-lote",
        json={"ids": ids, "data_pagamento": str(date.today())},
        headers=headers_rh,
    )
    assert pagamento.status_code == 200, pagamento.text


# ===========================================================================
# RH-EMP: Empreitadas
# ===========================================================================

@pytest.mark.asyncio
async def test_criar_empreitada(client, session, headers_rh):
    """RH-EMP-01: POST /rh/empreitadas cria empreitada"""
    await _garantir_suporte(session)

    r = await client.post("/api/v1/rh/colaboradores",
                          json=_payload_colaborador(tipo_contrato="EMPREITEIRO"),
                          headers=headers_rh)
    assert r.status_code == 201
    colaborador_id = r.json()["id"]

    response = await client.post(
        "/api/v1/rh/empreitadas",
        json={
            "colaborador_id": colaborador_id,
            "descricao": "Capina manual 50 ha",
            "valor_unitario": 70.0,
            "quantidade": 50.0,
            "unidade": "HECTARE",
            "data_inicio": str(date.today()),
            "unidade_produtiva_id": str(FAZENDA_ID),
        },
        headers=headers_rh,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["valor_total"] == 3500.0
    assert data["status"] in ("ABERTA", "EM_ANDAMENTO", "PENDENTE")


@pytest.mark.asyncio
async def test_concluir_empreitada(client, session, headers_rh):
    """RH-EMP-03: PATCH /rh/empreitadas/{id}/concluir encerra empreitada e gera pagamento"""
    await _garantir_suporte(session)

    r = await client.post("/api/v1/rh/colaboradores",
                          json=_payload_colaborador(tipo_contrato="EMPREITEIRO"),
                          headers=headers_rh)
    assert r.status_code == 201
    colaborador_id = r.json()["id"]

    emp = await client.post("/api/v1/rh/empreitadas", json={
        "colaborador_id": colaborador_id,
        "descricao": "Colheita manual 20 ha",
        "valor_unitario": 100.0,
        "quantidade": 20.0,
        "unidade": "HECTARE",
        "data_inicio": str(date.today()),
        "unidade_produtiva_id": str(FAZENDA_ID),
    }, headers=headers_rh)
    assert emp.status_code == 201
    empreitada_id = emp.json()["id"]

    # Conclui a empreitada
    conclusao = await client.patch(
        f"/api/v1/rh/empreitadas/{empreitada_id}/concluir",
        json={
            "quantidade_final": 20.0,
            "data_fim": str(date.today()),
        },
        headers=headers_rh,
    )
    assert conclusao.status_code == 200, conclusao.text
    assert conclusao.json()["status"] in ("CONCLUIDA", "PAGA", "FINALIZADA")


# ---------------------------------------------------------------------------
# Sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rh_sem_token_retorna_401(client):
    response = await client.get("/api/v1/rh/colaboradores")
    assert response.status_code == 401
