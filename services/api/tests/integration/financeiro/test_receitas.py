"""
Testes de Integração — Receitas Financeiras (HTTP)
FIN-REC-01..08: CRUD, parcelamento, baixa e estorno via API REST
"""
import pytest
import uuid
from datetime import date, timedelta
from sqlalchemy import text

from tests.integration.conftest import TENANT_ID, FAZENDA_ID


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _garantir_plano_conta(session) -> uuid.UUID:
    """Garante que existe um plano de contas para usar nas receitas."""
    plano_id = uuid.UUID("dddddddd-0000-0000-0000-000000000010")
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, modulos_ativos, max_usuarios_simultaneos, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, 'Tenant Financeiro', '98765432100', true, '["CORE","F1"]', 10, 0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO fazendas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, 'Fazenda Financeiro', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(FAZENDA_ID), "tenant_id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO fin_planos_conta
            (id, tenant_id, codigo, nome, tipo, natureza, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, '4.1.01', 'Venda de Grãos', 'RECEITA', 'CREDITO', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(plano_id), "tenant_id": str(TENANT_ID)})

    await session.commit()
    return plano_id


def _payload_receita(plano_conta_id: uuid.UUID, **overrides) -> dict:
    base = {
        "fazenda_id": str(FAZENDA_ID),
        "plano_conta_id": str(plano_conta_id),
        "descricao": "Venda de soja safra 2025",
        "valor_total": 15000.0,
        "data_emissao": str(date.today()),
        "data_vencimento": str(date.today() + timedelta(days=30)),
        "status": "A_RECEBER",
        "total_parcelas": 1,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# FIN-REC-01: Criar receita
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_criar_receita(client, session, headers_financeiro):
    """FIN-REC-01: POST /receitas cria receita e retorna 201"""
    plano_id = await _garantir_plano_conta(session)

    response = await client.post(
        "/api/v1/financeiro/receitas/",
        json=_payload_receita(plano_id),
        headers=headers_financeiro,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert isinstance(data, list)  # retorna lista (suporte a parcelamento)
    assert len(data) == 1
    receita = data[0]
    assert receita["valor_total"] == 15000.0
    assert receita["status"] == "A_RECEBER"
    assert "id" in receita


# ---------------------------------------------------------------------------
# FIN-REC-03: Parcelar receita
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parcelar_receita(client, session, headers_financeiro):
    """FIN-REC-03: Receita com 3 parcelas cria 3 registros"""
    plano_id = await _garantir_plano_conta(session)

    response = await client.post(
        "/api/v1/financeiro/receitas/",
        json=_payload_receita(plano_id, total_parcelas=3, valor_total=9000.0),
        headers=headers_financeiro,
    )

    assert response.status_code == 201, response.text
    parcelas = response.json()
    assert len(parcelas) == 3

    # Cada parcela deve ser 1/3 do total
    for p in parcelas:
        assert abs(p["valor_total"] - 3000.0) < 0.01
        assert p["total_parcelas"] == 3


# ---------------------------------------------------------------------------
# FIN-REC-04: Receitas vencendo
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_receitas_vencendo(client, session, headers_financeiro):
    """FIN-REC-04: GET /receitas/vencendo retorna receitas a vencer em N dias"""
    plano_id = await _garantir_plano_conta(session)

    # Cria receita vencendo em 3 dias
    vencimento = date.today() + timedelta(days=3)
    await client.post(
        "/api/v1/financeiro/receitas/",
        json=_payload_receita(plano_id, data_vencimento=str(vencimento),
                              descricao="Receita vencendo logo"),
        headers=headers_financeiro,
    )

    response = await client.get(
        "/api/v1/financeiro/receitas/vencendo?dias=7",
        headers=headers_financeiro,
    )

    assert response.status_code == 200
    receitas = response.json()
    assert isinstance(receitas, list)
    # Deve conter ao menos a que criamos
    assert len(receitas) >= 1


# ---------------------------------------------------------------------------
# FIN-REC-05: Atualizar receita
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_atualizar_receita(client, session, headers_financeiro):
    """FIN-REC-05: PATCH /receitas/{id} atualiza observações"""
    plano_id = await _garantir_plano_conta(session)

    r = await client.post(
        "/api/v1/financeiro/receitas/",
        json=_payload_receita(plano_id, descricao="Receita para atualizar"),
        headers=headers_financeiro,
    )
    assert r.status_code == 201
    receita_id = r.json()[0]["id"]

    update = await client.patch(
        f"/api/v1/financeiro/receitas/{receita_id}",
        json={"observacoes": "Atualizado via teste"},
        headers=headers_financeiro,
    )
    assert update.status_code == 200
    assert update.json()["observacoes"] == "Atualizado via teste"


# ---------------------------------------------------------------------------
# FIN-REC-06: Baixar receita (marcar como recebida)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_baixar_receita(client, session, headers_financeiro):
    """FIN-REC-06: POST /receitas/{id}/baixar marca receita como RECEBIDO"""
    plano_id = await _garantir_plano_conta(session)

    r = await client.post(
        "/api/v1/financeiro/receitas/",
        json=_payload_receita(plano_id, descricao="Receita para baixar"),
        headers=headers_financeiro,
    )
    assert r.status_code == 201
    receita_id = r.json()[0]["id"]

    baixa = await client.post(
        f"/api/v1/financeiro/receitas/{receita_id}/baixar",
        json={
            "data_recebimento": str(date.today()),
            "valor_recebido": 15000.0,
            "forma_recebimento": "PIX",
        },
        headers=headers_financeiro,
    )
    assert baixa.status_code in (200, 201), baixa.text
    assert baixa.json()["status"] == "RECEBIDO"


# ---------------------------------------------------------------------------
# FIN-REC-08: Listar receitas por status
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listar_receitas_por_status(client, session, headers_financeiro):
    """FIN-REC-08: GET /receitas?status=A_RECEBER retorna apenas pendentes"""
    plano_id = await _garantir_plano_conta(session)

    # Garante ao menos uma receita A_RECEBER
    await client.post(
        "/api/v1/financeiro/receitas/",
        json=_payload_receita(plano_id, descricao="Receita pendente filtro"),
        headers=headers_financeiro,
    )

    response = await client.get(
        "/api/v1/financeiro/receitas/?status=A_RECEBER",
        headers=headers_financeiro,
    )

    assert response.status_code == 200
    receitas = response.json()
    assert isinstance(receitas, list)
    status_set = {r["status"] for r in receitas}
    assert status_set <= {"A_RECEBER"}, f"Filtro de status falhou: {status_set}"


# ---------------------------------------------------------------------------
# FIN-REC: Sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_receitas_sem_token_retorna_401(client):
    """Endpoint financeiro sem token retorna 401"""
    response = await client.get("/api/v1/financeiro/receitas/")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# FIN-REC: Sem módulo F1 retorna 402/403
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_receitas_sem_modulo_f1(client, token_agricola):
    """Token sem módulo F1 não acessa receitas"""
    headers = {"Authorization": f"Bearer {token_agricola}"}
    response = await client.get("/api/v1/financeiro/receitas/", headers=headers)
    assert response.status_code in (402, 403)
