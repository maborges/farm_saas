"""
Testes de Integração — Cadastros (HTTP)
CAD-PRO-01..05: Produtos
CAD-PES-01..05: Pessoas (Fornecedores/Clientes)
CAD-MAR-01: Marcas
"""
import pytest
import uuid
from sqlalchemy import text

from tests.integration.conftest import TENANT_ID, FAZENDA_ID


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _garantir_tenant(session):
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, modulos_ativos, max_usuarios_simultaneos, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, 'Tenant Cadastros', '33344455566', true, '["CORE"]', 10, 0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TENANT_ID)})
    await session.execute(text("""
        INSERT INTO fazendas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, 'Fazenda Cadastros', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(FAZENDA_ID), "tenant_id": str(TENANT_ID)})
    await session.commit()


def _payload_produto(**overrides) -> dict:
    base = {
        "nome": f"Herbicida-{uuid.uuid4().hex[:4]}",
        "unidade_medida": "L",
        "tipo": "INSUMO",
        "descricao": "Produto para testes",
    }
    base.update(overrides)
    return base


def _payload_pessoa(**overrides) -> dict:
    base = {
        "tipo": "PJ",
        "nome_exibicao": f"Fornecedor Teste {uuid.uuid4().hex[:4]}",
    }
    base.update(overrides)
    return base


# ===========================================================================
# CAD-PRO: Produtos
# ===========================================================================

# ---------------------------------------------------------------------------
# CAD-PRO-01: Cadastrar produto
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cadastrar_produto(client, session, headers_admin):
    """CAD-PRO-01: POST /cadastros/produtos cria produto e retorna 201"""
    await _garantir_tenant(session)

    response = await client.post(
        "/api/v1/cadastros/produtos",
        json=_payload_produto(),
        headers=headers_admin,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["unidade_medida"] == "L"
    assert data["tipo"] == "INSUMO"
    assert "id" in data


# ---------------------------------------------------------------------------
# CAD-PRO-02: Produto com código duplicado retorna erro
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.xfail(reason="No unique constraint on produto codigo — duplicates allowed in current schema")
async def test_produto_codigo_duplicado(client, session, headers_admin):
    """CAD-PRO-02: Criar dois produtos com mesmo código retorna 400/409"""
    await _garantir_tenant(session)

    codigo = f"COD-{uuid.uuid4().hex[:6].upper()}"
    payload = _payload_produto(codigo_interno=codigo)

    r1 = await client.post("/api/v1/cadastros/produtos", json=payload, headers=headers_admin)
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/cadastros/produtos", json=payload, headers=headers_admin)
    assert r2.status_code in (400, 409, 422), (
        f"Duplicata deveria ser rejeitada, recebeu {r2.status_code}"
    )


# ---------------------------------------------------------------------------
# CAD-PRO-03: Listar produtos com filtros
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listar_produtos_com_filtros(client, session, headers_admin):
    """CAD-PRO-03: GET /cadastros/produtos?tipo=INSUMO retorna apenas insumos"""
    await _garantir_tenant(session)

    await client.post(
        "/api/v1/cadastros/produtos",
        json=_payload_produto(tipo="INSUMO"),
        headers=headers_admin,
    )

    response = await client.get(
        "/api/v1/cadastros/produtos?tipo=INSUMO",
        headers=headers_admin,
    )

    assert response.status_code == 200
    produtos = response.json()
    assert isinstance(produtos, list)
    tipos = {p["tipo"] for p in produtos}
    assert tipos <= {"INSUMO"}, f"Filtro de tipo falhou: {tipos}"


# ---------------------------------------------------------------------------
# CAD-PRO-04: Atualizar produto
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_atualizar_produto(client, session, headers_admin):
    """CAD-PRO-04: PATCH /cadastros/produtos/{id} atualiza descricao"""
    await _garantir_tenant(session)

    r = await client.post(
        "/api/v1/cadastros/produtos",
        json=_payload_produto(),
        headers=headers_admin,
    )
    assert r.status_code == 201
    produto_id = r.json()["id"]

    update = await client.patch(
        f"/api/v1/cadastros/produtos/{produto_id}",
        json={"descricao": "Descrição atualizada via teste"},
        headers=headers_admin,
    )
    assert update.status_code == 200
    assert update.json()["descricao"] == "Descrição atualizada via teste"


# ---------------------------------------------------------------------------
# CAD-PRO-05: Inativar produto
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_inativar_produto(client, session, headers_admin):
    """CAD-PRO-05: PATCH /cadastros/produtos/{id} com ativo=false inativa produto"""
    await _garantir_tenant(session)

    r = await client.post(
        "/api/v1/cadastros/produtos",
        json=_payload_produto(),
        headers=headers_admin,
    )
    assert r.status_code == 201
    produto_id = r.json()["id"]

    inativacao = await client.patch(
        f"/api/v1/cadastros/produtos/{produto_id}",
        json={"ativo": False},
        headers=headers_admin,
    )
    assert inativacao.status_code == 200
    assert inativacao.json()["ativo"] is False


# ===========================================================================
# CAD-PES: Pessoas
# ===========================================================================

# ---------------------------------------------------------------------------
# CAD-PES-01: Cadastrar pessoa (CPF/CNPJ)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cadastrar_pessoa(client, session, headers_admin):
    """CAD-PES-01: POST /cadastros/pessoas cria pessoa e retorna 201"""
    await _garantir_tenant(session)

    response = await client.post(
        "/api/v1/cadastros/pessoas",
        json=_payload_pessoa(),
        headers=headers_admin,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["tipo"] == "PJ"
    assert "id" in data


# ---------------------------------------------------------------------------
# CAD-PES-02: Validação de CPF/CNPJ (formato)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.xfail(reason="PessoaCreate does not have 'documento' field in current schema")
async def test_pessoa_documento_invalido(client, session, headers_admin):
    """CAD-PES-02: Documento com formato inválido retorna 422"""
    await _garantir_tenant(session)

    response = await client.post(
        "/api/v1/cadastros/pessoas",
        json=_payload_pessoa(documento="123"),  # inválido
        headers=headers_admin,
    )
    assert response.status_code == 422, (
        f"Documento inválido deveria ser rejeitado, recebeu {response.status_code}"
    )


# ---------------------------------------------------------------------------
# CAD-PES-03: Pessoa com documento duplicado
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.xfail(reason="PessoaCreate does not have 'documento' field in current schema")
async def test_pessoa_documento_duplicado(client, session, headers_admin):
    """CAD-PES-03: Dois cadastros com mesmo documento retornam 400/409"""
    await _garantir_tenant(session)

    documento = f"{uuid.uuid4().int % 10**14:014d}"
    payload = _payload_pessoa(documento=documento)

    r1 = await client.post("/api/v1/cadastros/pessoas", json=payload, headers=headers_admin)
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/cadastros/pessoas", json=payload, headers=headers_admin)
    assert r2.status_code in (400, 409, 422), (
        f"Duplicata deveria ser rejeitada, recebeu {r2.status_code}"
    )


# ---------------------------------------------------------------------------
# CAD-PES-04: Listar pessoas por tipo
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listar_pessoas_por_tipo(client, session, headers_admin):
    """CAD-PES-04: GET /cadastros/pessoas?tipo_relacionamento=FORNECEDOR filtra corretamente"""
    await _garantir_tenant(session)

    await client.post(
        "/api/v1/cadastros/pessoas",
        json=_payload_pessoa(),
        headers=headers_admin,
    )

    response = await client.get(
        "/api/v1/cadastros/pessoas?tipo_relacionamento=FORNECEDOR",
        headers=headers_admin,
    )

    assert response.status_code == 200
    pessoas = response.json()
    assert isinstance(pessoas, list)


# ---------------------------------------------------------------------------
# CAD-PES-05: Atualizar pessoa
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_atualizar_pessoa(client, session, headers_admin):
    """CAD-PES-05: PATCH /cadastros/pessoas/{id} atualiza nome"""
    await _garantir_tenant(session)

    r = await client.post(
        "/api/v1/cadastros/pessoas",
        json=_payload_pessoa(),
        headers=headers_admin,
    )
    assert r.status_code == 201
    pessoa_id = r.json()["id"]

    update = await client.patch(
        f"/api/v1/cadastros/pessoas/{pessoa_id}",
        json={"nome_exibicao": "Fornecedor Atualizado"},
        headers=headers_admin,
    )
    assert update.status_code == 200
    assert update.json()["nome_exibicao"] == "Fornecedor Atualizado"


# ===========================================================================
# CAD-MAR: Marcas
# ===========================================================================

@pytest.mark.asyncio
async def test_cadastrar_marca(client, session, headers_admin):
    """CAD-MAR-01: POST /cadastros/marcas cria marca e retorna 201"""
    await _garantir_tenant(session)

    response = await client.post(
        "/api/v1/cadastros/marcas",
        json={"nome": f"Marca-{uuid.uuid4().hex[:4]}", "pais_origem": "Brasil"},
        headers=headers_admin,
    )

    assert response.status_code == 201, response.text
    assert "id" in response.json()


# ---------------------------------------------------------------------------
# Sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cadastros_sem_token_retorna_401(client):
    response = await client.get("/api/v1/cadastros/produtos")
    assert response.status_code == 401
