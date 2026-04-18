"""
Testes de Integração — Estoque (HTTP)
OPR-MOV-01..07: Entradas, saídas, transferências, ajustes via API REST
OPR-LOT-01..03: Lotes e validade
"""
import pytest
import uuid
from datetime import date, timedelta
from sqlalchemy import text

from tests.integration.conftest import TENANT_ID, FAZENDA_ID
from tests.integration.helpers import garantir_assinatura


# ---------------------------------------------------------------------------
# IDs fixos de suporte
# ---------------------------------------------------------------------------

DEPOSITO_A_ID = uuid.UUID("ff000001-0000-0000-0000-000000000001")
DEPOSITO_B_ID = uuid.UUID("ff000002-0000-0000-0000-000000000002")
PRODUTO_ID    = uuid.UUID("ff000003-0000-0000-0000-000000000003")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _garantir_suporte(session):
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, 'Tenant Estoque', '55566677788', true,  0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, 'Fazenda Estoque', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(FAZENDA_ID), "tenant_id": str(TENANT_ID)})

    for dep_id, nome in [(DEPOSITO_A_ID, "Depósito A"), (DEPOSITO_B_ID, "Depósito B")]:
        await session.execute(text("""
            INSERT INTO estoque_depositos (id, tenant_id, unidade_produtiva_id, nome, tipo, ativo)
            VALUES (:id, :tenant_id, :unidade_produtiva_id, :nome, 'ALMOXARIFADO', true)
            ON CONFLICT (id) DO NOTHING
        """), {"id": str(dep_id), "tenant_id": str(TENANT_ID),
               "unidade_produtiva_id": str(FAZENDA_ID), "nome": nome})

    await session.execute(text("""
        INSERT INTO cadastros_produtos
            (id, tenant_id, nome, tipo, unidade_medida, estoque_minimo, preco_medio, ativo)
        VALUES (:id, :tenant_id, 'Herbicida X', 'INSUMO', 'L', 0, 0.0, true)
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(PRODUTO_ID), "tenant_id": str(TENANT_ID)})

    await garantir_assinatura(session, TENANT_ID)
    await session.commit()


# ---------------------------------------------------------------------------
# OPR-MOV-01: Entrada de estoque
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_entrada_estoque(client, session, headers_operacional):
    """OPR-MOV-01: POST /estoque/movimentacoes/entrada cria entrada e retorna 201"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/estoque/movimentacoes/entrada",
        json={
            "produto_id": str(PRODUTO_ID),
            "deposito_id": str(DEPOSITO_A_ID),
            "quantidade": 100.0,
            "custo_unitario": 45.0,
            "motivo": "Compra direta",
        },
        headers=headers_operacional,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["tipo"] == "ENTRADA"
    assert data["quantidade"] == 100.0


# ---------------------------------------------------------------------------
# OPR-MOV-02: Saída de estoque
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_saida_estoque(client, session, headers_operacional):
    """OPR-MOV-02: POST /estoque/movimentacoes/saida diminui saldo"""
    await _garantir_suporte(session)

    # Garante saldo
    await client.post("/api/v1/estoque/movimentacoes/entrada", json={
        "produto_id": str(PRODUTO_ID),
        "deposito_id": str(DEPOSITO_A_ID),
        "quantidade": 200.0,
        "custo_unitario": 45.0,
    }, headers=headers_operacional)

    response = await client.post(
        "/api/v1/estoque/movimentacoes/saida",
        json={
            "produto_id": str(PRODUTO_ID),
            "deposito_id": str(DEPOSITO_A_ID),
            "quantidade": 50.0,
            "motivo": "Uso em operação agrícola",
        },
        headers=headers_operacional,
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["tipo"] == "SAIDA"


# ---------------------------------------------------------------------------
# OPR-MOV-03: Transferência entre depósitos
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_transferencia_entre_depositos(client, session, headers_operacional):
    """OPR-MOV-03: POST /estoque/movimentacoes/transferencia move saldo A→B"""
    await _garantir_suporte(session)

    await client.post("/api/v1/estoque/movimentacoes/entrada", json={
        "produto_id": str(PRODUTO_ID),
        "deposito_id": str(DEPOSITO_A_ID),
        "quantidade": 300.0,
        "custo_unitario": 45.0,
    }, headers=headers_operacional)

    response = await client.post(
        "/api/v1/estoque/movimentacoes/transferencia",
        json={
            "produto_id": str(PRODUTO_ID),
            "deposito_origem_id": str(DEPOSITO_A_ID),
            "deposito_destino_id": str(DEPOSITO_B_ID),
            "quantidade": 80.0,
            "motivo": "Redistribuição",
        },
        headers=headers_operacional,
    )

    assert response.status_code in (200, 201), response.text


# ---------------------------------------------------------------------------
# OPR-MOV-04: Ajuste de inventário
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ajuste_inventario(client, session, headers_operacional):
    """OPR-MOV-04: POST /estoque/movimentacoes/ajuste corrige saldo"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/estoque/movimentacoes/ajuste",
        json={
            "produto_id": str(PRODUTO_ID),
            "deposito_id": str(DEPOSITO_A_ID),
            "quantidade_nova": 95.0,
            "motivo": "Contagem física — diferença de 5L",
        },
        headers=headers_operacional,
    )

    assert response.status_code in (200, 201), response.text


# ---------------------------------------------------------------------------
# OPR-MOV-06: Saldo negativo retorna erro
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_saida_saldo_insuficiente_retorna_erro(client, session, headers_operacional):
    """OPR-MOV-06: Saída maior que saldo retorna 400/422"""
    await _garantir_suporte(session)

    produto_sem_saldo = uuid.uuid4()
    await session.execute(text("""
        INSERT INTO cadastros_produtos
            (id, tenant_id, nome, tipo, unidade_medida, estoque_minimo, preco_medio, ativo)
        VALUES (:id, :tenant_id, 'Produto Zerado', 'INSUMO', 'KG', 0, 0.0, true)
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(produto_sem_saldo), "tenant_id": str(TENANT_ID)})
    await session.commit()

    response = await client.post(
        "/api/v1/estoque/movimentacoes/saida",
        json={
            "produto_id": str(produto_sem_saldo),
            "deposito_id": str(DEPOSITO_A_ID),
            "quantidade": 9999.0,
            "motivo": "Tentativa de saldo negativo",
        },
        headers=headers_operacional,
    )

    assert response.status_code in (400, 422), (
        f"Esperava erro de saldo insuficiente, recebeu {response.status_code}: {response.text}"
    )


# ---------------------------------------------------------------------------
# OPR-MOV-07: Histórico de movimentações
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_historico_movimentacoes(client, session, headers_operacional):
    """OPR-MOV-07: GET /estoque/movimentacoes retorna histórico"""
    await _garantir_suporte(session)

    response = await client.get(
        f"/api/v1/estoque/movimentacoes?produto_id={PRODUTO_ID}",
        headers=headers_operacional,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# OPR-LOT-01: Criar lote de produto
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_criar_lote_produto(client, session, headers_operacional):
    """OPR-LOT-01: POST /estoque/lotes cria lote rastreável"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/estoque/lotes",
        json={
            "produto_id": str(PRODUTO_ID),
            "deposito_id": str(DEPOSITO_A_ID),
            "numero_lote": f"LOTE-{uuid.uuid4().hex[:6].upper()}",
            "quantidade_inicial": 50.0,
            "custo_unitario": 45.0,
            "data_fabricacao": str(date.today() - timedelta(days=30)),
            "data_validade": str(date.today() + timedelta(days=365)),
        },
        headers=headers_operacional,
    )

    assert response.status_code in (200, 201), response.text


# ---------------------------------------------------------------------------
# OPR-LOT-02: Lote com validade
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_lote_com_validade(client, session, headers_operacional):
    """OPR-LOT-02: Lote criado com data_validade pode ser consultado"""
    await _garantir_suporte(session)

    validade = date.today() + timedelta(days=180)

    r = await client.post(
        "/api/v1/estoque/lotes",
        json={
            "produto_id": str(PRODUTO_ID),
            "deposito_id": str(DEPOSITO_A_ID),
            "numero_lote": f"LOTE-VAL-{uuid.uuid4().hex[:4].upper()}",
            "quantidade_inicial": 30.0,
            "custo_unitario": 45.0,
            "data_validade": str(validade),
        },
        headers=headers_operacional,
    )
    assert r.status_code in (200, 201), r.text


# ---------------------------------------------------------------------------
# OPR-LOT-03: Alerta de validade próxima
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_alerta_validade_proxima(client, session, headers_operacional):
    """OPR-LOT-03: GET /estoque/lotes/alertas-validade retorna lotes vencendo"""
    await _garantir_suporte(session)

    response = await client.get(
        "/api/v1/estoque/lotes/alertas-validade?dias=30",
        headers=headers_operacional,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# OPR-DEP-01: Criar depósito
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_criar_deposito(client, session, headers_operacional):
    """OPR-DEP-01: POST /estoque/depositos cria novo depósito"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/estoque/depositos",
        json={
            "unidade_produtiva_id": str(FAZENDA_ID),
            "nome": f"Depósito Teste {uuid.uuid4().hex[:4]}",
            "tipo": "GERAL",
        },
        headers=headers_operacional,
    )

    assert response.status_code == 201, response.text
    assert "id" in response.json()


# ---------------------------------------------------------------------------
# Sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_estoque_sem_token_retorna_401(client):
    """Estoque sem token retorna 401"""
    response = await client.get("/api/v1/estoque/movimentacoes")
    assert response.status_code == 401
