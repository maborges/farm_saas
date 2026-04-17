"""
Testes de Integração — Despesas Financeiras (HTTP)
FIN-DES-01..10: CRUD, parcelamento, rateio, baixa e estorno via API REST
"""
import pytest
import uuid
from datetime import date, timedelta
from sqlalchemy import text

from tests.integration.conftest import TENANT_ID, FAZENDA_ID, TALHAO_ID


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PLANO_DESPESA_ID = uuid.UUID("eeeeeeee-0000-0000-0000-000000000020")


async def _garantir_suporte(session):
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, 'Tenant Despesas', '11122233344', true,  0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO fazendas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, 'Fazenda Despesas', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(FAZENDA_ID), "tenant_id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO fin_planos_conta
            (id, tenant_id, codigo, nome, tipo, natureza, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, '5.1.01', 'Insumos Agrícolas', 'DESPESA', 'DEBITO', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(PLANO_DESPESA_ID), "tenant_id": str(TENANT_ID)})

    await session.commit()


def _payload_despesa(**overrides) -> dict:
    base = {
        "unidade_produtiva_id": str(FAZENDA_ID),
        "plano_conta_id": str(PLANO_DESPESA_ID),
        "descricao": "Compra de herbicida",
        "valor_total": 5000.0,
        "data_emissao": str(date.today()),
        "data_vencimento": str(date.today() + timedelta(days=30)),
        "status": "A_PAGAR",
        "total_parcelas": 1,
        "rateios": [],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# FIN-DES-01: Criar despesa
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_criar_despesa(client, session, headers_financeiro):
    """FIN-DES-01: POST /despesas cria despesa e retorna 201"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/financeiro/despesas/",
        json=_payload_despesa(),
        headers=headers_financeiro,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert isinstance(data, list)
    despesa = data[0]
    assert despesa["valor_total"] == 5000.0
    assert despesa["status"] == "A_PAGAR"
    assert "id" in despesa


# ---------------------------------------------------------------------------
# FIN-DES-03: Despesa sem custo (valor <= 0) não cria
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_despesa_valor_zero_retorna_422(client, session, headers_financeiro):
    """FIN-DES-03: Despesa com valor_total=0 retorna 422 (validação Pydantic)"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/financeiro/despesas/",
        json=_payload_despesa(valor_total=0),
        headers=headers_financeiro,
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# FIN-DES-04: Parcelar despesa
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parcelar_despesa(client, session, headers_financeiro):
    """FIN-DES-04: Despesa com 4 parcelas cria 4 registros de igual valor"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/financeiro/despesas/",
        json=_payload_despesa(total_parcelas=4, valor_total=8000.0,
                              descricao="Parcelamento de defensivo"),
        headers=headers_financeiro,
    )

    assert response.status_code == 201, response.text
    parcelas = response.json()
    assert len(parcelas) == 4
    for p in parcelas:
        assert abs(p["valor_total"] - 2000.0) < 0.01


# ---------------------------------------------------------------------------
# FIN-DES-05: Despesas vencendo
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_despesas_vencendo(client, session, headers_financeiro):
    """FIN-DES-05: GET /despesas/vencendo retorna despesas a vencer em N dias"""
    await _garantir_suporte(session)

    vencimento = date.today() + timedelta(days=2)
    await client.post(
        "/api/v1/financeiro/despesas/",
        json=_payload_despesa(data_vencimento=str(vencimento),
                              descricao="Despesa urgente"),
        headers=headers_financeiro,
    )

    response = await client.get(
        "/api/v1/financeiro/despesas/vencendo?dias=7",
        headers=headers_financeiro,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


# ---------------------------------------------------------------------------
# FIN-DES-06: Atualizar despesa
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_atualizar_despesa(client, session, headers_financeiro):
    """FIN-DES-06: PATCH /despesas/{id} atualiza descrição"""
    await _garantir_suporte(session)

    r = await client.post(
        "/api/v1/financeiro/despesas/",
        json=_payload_despesa(descricao="Despesa para atualizar"),
        headers=headers_financeiro,
    )
    assert r.status_code == 201
    despesa_id = r.json()[0]["id"]

    update = await client.patch(
        f"/api/v1/financeiro/despesas/{despesa_id}",
        json={"observacoes": "Atualizado via teste de integração"},
        headers=headers_financeiro,
    )
    assert update.status_code == 200
    assert update.json()["observacoes"] == "Atualizado via teste de integração"


# ---------------------------------------------------------------------------
# FIN-DES-07: Baixar despesa (marcar como paga)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_baixar_despesa(client, session, headers_financeiro):
    """FIN-DES-07: POST /despesas/{id}/baixar marca como PAGO"""
    await _garantir_suporte(session)

    r = await client.post(
        "/api/v1/financeiro/despesas/",
        json=_payload_despesa(descricao="Despesa para baixar"),
        headers=headers_financeiro,
    )
    assert r.status_code == 201
    despesa_id = r.json()[0]["id"]

    baixa = await client.post(
        f"/api/v1/financeiro/despesas/{despesa_id}/baixar",
        json={
            "data_pagamento": str(date.today()),
            "valor_pago": 5000.0,
            "forma_pagamento": "PIX",
        },
        headers=headers_financeiro,
    )
    assert baixa.status_code in (200, 201), baixa.text
    assert baixa.json()["status"] == "PAGO"


# ---------------------------------------------------------------------------
# FIN-DES-09: Despesa com rateios múltiplos (100%)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_despesa_com_rateio_100_porcento(client, session, headers_financeiro):
    """FIN-DES-09: Despesa com rateios somando 100% é aceita"""
    await _garantir_suporte(session)

    safra_a = uuid.uuid4()
    safra_b = uuid.uuid4()

    rateios = [
        {"percentual": 60.0, "valor_rateado": 3000.0},
        {"percentual": 40.0, "valor_rateado": 2000.0},
    ]

    response = await client.post(
        "/api/v1/financeiro/despesas/",
        json=_payload_despesa(rateios=rateios, descricao="Despesa rateada 60/40"),
        headers=headers_financeiro,
    )
    assert response.status_code == 201, response.text


# ---------------------------------------------------------------------------
# FIN-DES-10: Rateio com percentual != 100% é rejeitado
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_despesa_rateio_soma_incorreta_rejeitado(client, session, headers_financeiro):
    """FIN-DES-10: Rateios somando ≠ 100% retornam 422"""
    await _garantir_suporte(session)

    rateios = [
        {"percentual": 60.0, "valor_rateado": 3000.0},
        {"percentual": 30.0, "valor_rateado": 1500.0},
        # Total = 90% — inválido
    ]

    response = await client.post(
        "/api/v1/financeiro/despesas/",
        json=_payload_despesa(rateios=rateios, descricao="Rateio inválido"),
        headers=headers_financeiro,
    )
    assert response.status_code == 422, response.text


# ---------------------------------------------------------------------------
# FIN-DES: Sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_despesas_sem_token_retorna_401(client):
    """Endpoint de despesas sem token retorna 401"""
    response = await client.get("/api/v1/financeiro/despesas/")
    assert response.status_code == 401
