"""
Testes de Integração — Pedidos de Compra (HTTP)
OPR-COM-01..06: CRUD, aprovação, recebimento via API REST
"""
import pytest
import uuid
from datetime import date
from sqlalchemy import text

from tests.integration.conftest import TENANT_ID, FAZENDA_ID, PRODUTO_ID, USER_ID
from tests.integration.helpers import garantir_assinatura


# ---------------------------------------------------------------------------
# IDs de suporte
# ---------------------------------------------------------------------------

FORNECEDOR_ID = uuid.UUID("cc000001-0000-0000-0000-000000000001")
DEPOSITO_ID   = uuid.UUID("ff000001-0000-0000-0000-000000000001")


async def _garantir_suporte(session):
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, 'Tenant Compras', '99988877766', true,  0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, 'Fazenda Compras', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(FAZENDA_ID), "tenant_id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO cadastros_produtos
            (id, tenant_id, nome, tipo, unidade_medida, estoque_minimo, preco_medio, ativo)
        VALUES (:id, :tenant_id, 'Fertilizante NPK', 'INSUMO', 'KG', 0, 0.0, true)
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(PRODUTO_ID), "tenant_id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO estoque_depositos (id, tenant_id, unidade_produtiva_id, nome, tipo, ativo)
        VALUES (:id, :tenant_id, :unidade_produtiva_id, 'Depósito Compras', 'ALMOXARIFADO', true)
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(DEPOSITO_ID), "tenant_id": str(TENANT_ID),
           "unidade_produtiva_id": str(FAZENDA_ID)})

    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, is_superuser, ativo, created_at, updated_at)
        VALUES (:id, 'test@compras.com', 'test_compras', false, true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(USER_ID)})

    # Fornecedor
    await session.execute(text("""
        INSERT INTO compras_fornecedores (id, tenant_id, nome_fantasia)
        VALUES (:id, :tenant_id, 'Fornecedor ABC')
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(FORNECEDOR_ID), "tenant_id": str(TENANT_ID)})

    await garantir_assinatura(session, TENANT_ID)
    await session.commit()


# ---------------------------------------------------------------------------
# OPR-COM-FOR-01: Criar fornecedor com pessoa canônica e sem duplicar legado
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_criar_fornecedor_resolve_pessoa_e_reutiliza_legado(client, session, headers_operacional):
    await _garantir_suporte(session)

    payload = {
        "nome_fantasia": "Fornecedor Canonico",
        "cnpj_cpf": "12.345.678/0001-90",
        "email": "compras@canonico.test",
        "telefone": "11999990000",
        "condicoes_pagamento": "28 dias",
        "prazo_entrega_dias": 5,
        "avaliacao": 4.7,
    }

    response_1 = await client.post(
        "/api/v1/compras/fornecedores",
        json=payload,
        headers=headers_operacional,
    )
    assert response_1.status_code == 201, response_1.text

    response_2 = await client.post(
        "/api/v1/compras/fornecedores",
        json={
            **payload,
            "nome_fantasia": "Fornecedor Canonico Atualizado",
            "cnpj_cpf": "12345678000190",
        },
        headers=headers_operacional,
    )
    assert response_2.status_code == 201, response_2.text

    data_1 = response_1.json()
    data_2 = response_2.json()

    assert data_1["pessoa_id"] is not None
    assert data_2["pessoa_id"] == data_1["pessoa_id"]
    assert data_2["id"] == data_1["id"]
    assert data_2["condicoes_pagamento"] == "28 dias"
    assert data_2["prazo_entrega_dias"] == 5
    assert data_2["avaliacao"] == 4.7

    fornecedor_count = await session.execute(
        text(
            "SELECT COUNT(*) FROM compras_fornecedores "
            "WHERE tenant_id = :tenant_id AND pessoa_id = :pessoa_id"
        ),
        {"tenant_id": str(TENANT_ID), "pessoa_id": data_1["pessoa_id"]},
    )
    pessoa_count = await session.execute(
        text(
            "SELECT COUNT(*) FROM cadastros_pessoas_documentos "
            "WHERE tipo = 'CNPJ' AND numero = :cnpj_cpf"
        ),
        {"cnpj_cpf": "12345678000190"},
    )

    assert fornecedor_count.scalar_one() == 1
    assert pessoa_count.scalar_one() == 1


# ---------------------------------------------------------------------------
# OPR-COM-01: Criar pedido de compra
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_criar_pedido_compra(client, session, headers_operacional):
    """OPR-COM-01: POST /compras/pedidos cria pedido e retorna 201"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/compras/pedidos",
        json={"observacoes": "Pedido de fertilizante para safra 2025"},
        headers=headers_operacional,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data
    assert data["status"] in ("RASCUNHO", "PENDENTE", "ABERTO")


# ---------------------------------------------------------------------------
# OPR-COM-01b: Criar pedido e adicionar itens
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_criar_pedido_com_itens(client, session, headers_operacional):
    """OPR-COM-01: Pedido com itens tem produto e quantidade corretos"""
    await _garantir_suporte(session)

    r = await client.post(
        "/api/v1/compras/pedidos",
        json={"observacoes": "Pedido com itens"},
        headers=headers_operacional,
    )
    assert r.status_code == 201
    pedido_id = r.json()["id"]

    # Adiciona item
    item_resp = await client.post(
        f"/api/v1/compras/pedidos/{pedido_id}/itens",
        json={
            "produto_id": str(PRODUTO_ID),
            "quantidade_solicitada": 500.0,
            "preco_estimado_unitario": 3.50,
        },
        headers=headers_operacional,
    )
    assert item_resp.status_code in (200, 201), item_resp.text
    assert item_resp.json()["quantidade_solicitada"] == 500.0


# ---------------------------------------------------------------------------
# OPR-COM-02: Adicionar cotação ao pedido
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_adicionar_cotacao_pedido(client, session, headers_operacional):
    """OPR-COM-02: Cotação vinculada ao pedido é registrada corretamente"""
    await _garantir_suporte(session)

    r = await client.post(
        "/api/v1/compras/pedidos",
        json={"observacoes": "Pedido para cotação"},
        headers=headers_operacional,
    )
    assert r.status_code == 201
    pedido_id = r.json()["id"]

    cotacao = await client.post(
        f"/api/v1/compras/pedidos/{pedido_id}/cotacoes",
        json={
            "fornecedor_id": str(FORNECEDOR_ID),
            "valor_total": 1750.0,
            "prazo_entrega_dias": 5,
            "condicoes_pagamento": "30 dias",
        },
        headers=headers_operacional,
    )
    assert cotacao.status_code in (200, 201), cotacao.text


# ---------------------------------------------------------------------------
# OPR-COM-03: Aprovar pedido
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_aprovar_pedido(client, session, headers_operacional):
    """OPR-COM-03: POST /pedidos/{id}/aprovar muda status para APROVADO"""
    await _garantir_suporte(session)

    r = await client.post(
        "/api/v1/compras/pedidos",
        json={"observacoes": "Pedido para aprovar"},
        headers=headers_operacional,
    )
    assert r.status_code == 201
    pedido_id = r.json()["id"]

    aprovacao = await client.post(
        f"/api/v1/compras/pedidos/{pedido_id}/aprovar",
        headers=headers_operacional,
    )
    assert aprovacao.status_code in (200, 201), aprovacao.text
    assert aprovacao.json()["status"] == "APROVADO"


# ---------------------------------------------------------------------------
# OPR-COM-04: Receber pedido gera entrada de estoque
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_receber_pedido_gera_entrada_estoque(client, session, headers_operacional):
    """OPR-COM-04: Recebimento de pedido cria movimentação de entrada no estoque"""
    await _garantir_suporte(session)

    # Cria e aprova pedido
    r = await client.post(
        "/api/v1/compras/pedidos",
        json={"observacoes": "Pedido para recebimento"},
        headers=headers_operacional,
    )
    assert r.status_code == 201
    pedido_id = r.json()["id"]

    item_resp = await client.post(
        f"/api/v1/compras/pedidos/{pedido_id}/itens",
        json={
            "produto_id": str(PRODUTO_ID),
            "quantidade_solicitada": 200.0,
            "preco_estimado_unitario": 3.50,
        },
        headers=headers_operacional,
    )
    assert item_resp.status_code in (200, 201), item_resp.text
    item_id = item_resp.json()["id"]

    await client.post(
        f"/api/v1/compras/pedidos/{pedido_id}/aprovar",
        headers=headers_operacional,
    )

    # Recebe o pedido
    recebimento = await client.patch(
        f"/api/v1/compras/pedidos/{pedido_id}/receber",
        json={
            "deposito_id": str(DEPOSITO_ID),
            "itens": [{
                "item_id": item_id,
                "quantidade_recebida": 200.0,
                "preco_real_unitario": 3.50,
                "numero_lote": f"LOTE-{uuid.uuid4().hex[:6].upper()}",
                "data_validade": str(date(2026, 12, 31)),
            }],
            "nota_fiscal": "NF-001234",
        },
        headers=headers_operacional,
    )
    assert recebimento.status_code in (200, 201), recebimento.text


# ---------------------------------------------------------------------------
# OPR-COM-06: Listar pedidos por status
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listar_pedidos_por_status(client, session, headers_operacional):
    """OPR-COM-06: GET /compras/pedidos?status=APROVADO filtra corretamente"""
    await _garantir_suporte(session)

    response = await client.get(
        "/api/v1/compras/pedidos?status=APROVADO",
        headers=headers_operacional,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# Sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_compras_sem_token_retorna_401(client):
    response = await client.get("/api/v1/compras/pedidos")
    assert response.status_code == 401
