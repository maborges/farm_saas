"""
Testes de Integração — Pecuária (HTTP)
PEC-LOT-01..04: Lotes bovinos
PEC-EVT-01..03: Eventos de manejo (pesagem, vacinação)
"""
import pytest
import uuid
from datetime import date
from sqlalchemy import text

from tests.integration.conftest import TENANT_ID, FAZENDA_ID
from tests.integration.helpers import garantir_assinatura


# ---------------------------------------------------------------------------
# IDs de suporte
# ---------------------------------------------------------------------------

LOTE_ID = uuid.UUID("ee000001-0000-0000-0000-000000000001")


async def _garantir_suporte(session):
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, 'Tenant Pecuária', '44455566677', true,  0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(TENANT_ID)})

    await session.execute(text("""
        INSERT INTO unidades_produtivas (id, tenant_id, nome, ativo, created_at, updated_at)
        VALUES (:id, :tenant_id, 'Fazenda Pecuária', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """), {"id": str(FAZENDA_ID), "tenant_id": str(TENANT_ID)})

    await garantir_assinatura(session, TENANT_ID)
    await session.commit()


@pytest.fixture(scope="module")
def token_pecuaria():
    from datetime import timedelta
    from unittest.mock import MagicMock
    from core.services.auth_service import AuthService
    svc = AuthService(MagicMock())
    return svc.create_access_token({
        "sub": str(uuid.uuid4()),
        "tenant_id": str(TENANT_ID),
        "modules": ["CORE", "P1_REBANHO"],
        "fazendas_auth": [{"id": str(FAZENDA_ID), "role": "admin"}],
        "is_superuser": False,
        "plan_tier": "PROFISSIONAL",
    }, expires_delta=timedelta(hours=1))


@pytest.fixture
def headers_pecuaria(token_pecuaria):
    return {"Authorization": f"Bearer {token_pecuaria}",
            "X-Tenant-ID": str(TENANT_ID)}


def _payload_lote(**overrides) -> dict:
    base = {
        "unidade_produtiva_id": str(FAZENDA_ID),
        "identificacao": f"Lote-{uuid.uuid4().hex[:4].upper()}",
        "categoria": "Novilhas",
        "raca": "Nelore",
        "quantidade_cabecas": 50,
        "peso_medio_kg": 280.0,
        "data_formacao": str(date.today()),
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# PEC-LOT-01: Criar lote de animais
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_criar_lote_bovino(client, session, headers_pecuaria):
    """PEC-LOT-01: POST /lotes-bovinos cria lote e retorna 201"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/lotes-bovinos/",
        json=_payload_lote(),
        headers=headers_pecuaria,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["categoria"] == "Novilhas"
    assert data["quantidade_cabecas"] == 50
    assert "id" in data


# ---------------------------------------------------------------------------
# PEC-LOT-02: Listar lotes com filtros
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listar_lotes_com_filtros(client, session, headers_pecuaria):
    """PEC-LOT-02: GET /lotes-bovinos?categoria=Novilhas filtra corretamente"""
    await _garantir_suporte(session)

    # Garante ao menos um lote Novilhas
    await client.post(
        "/api/v1/lotes-bovinos/",
        json=_payload_lote(categoria="Novilhas"),
        headers=headers_pecuaria,
    )

    response = await client.get(
        "/api/v1/lotes-bovinos/?categoria=Novilhas",
        headers=headers_pecuaria,
    )

    assert response.status_code == 200
    lotes = response.json()
    assert isinstance(lotes, list)
    categorias = {l["categoria"] for l in lotes}
    assert categorias <= {"Novilhas"}, f"Filtro falhou: {categorias}"


# ---------------------------------------------------------------------------
# PEC-LOT-04: Lote com categoria inválida retorna erro
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_lote_quantidade_invalida_retorna_422(client, session, headers_pecuaria):
    """PEC-LOT-04: Lote com quantidade_cabecas=0 retorna 422"""
    await _garantir_suporte(session)

    response = await client.post(
        "/api/v1/lotes-bovinos/",
        json=_payload_lote(quantidade_cabecas=0),
        headers=headers_pecuaria,
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# PEC-EVT-01: Registrar evento de pesagem
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_registrar_evento_pesagem(client, session, headers_pecuaria):
    """PEC-EVT-01: POST /pecuaria/manejos registra pesagem do lote"""
    await _garantir_suporte(session)

    # Cria lote
    r = await client.post(
        "/api/v1/lotes-bovinos/",
        json=_payload_lote(),
        headers=headers_pecuaria,
    )
    assert r.status_code == 201
    lote_id = r.json()["id"]

    response = await client.post(
        "/api/v1/pecuaria/manejos/",
        json={
            "lote_id": lote_id,
            "tipo_evento": "PESAGEM",
            "data_evento": str(date.today()),
            "quantidade_cabecas": 50,
            "peso_total_kg": 15000.0,
            "observacoes": "Pesagem mensal",
        },
        headers=headers_pecuaria,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["tipo_evento"] == "PESAGEM"
    assert data["lote_id"] == lote_id


# ---------------------------------------------------------------------------
# PEC-EVT-01b: Registrar evento de vacinação
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_registrar_evento_vacinacao(client, session, headers_pecuaria):
    """PEC-EVT-01: POST /pecuaria/manejos registra vacinação do lote"""
    await _garantir_suporte(session)

    r = await client.post(
        "/api/v1/lotes-bovinos/",
        json=_payload_lote(),
        headers=headers_pecuaria,
    )
    assert r.status_code == 201
    lote_id = r.json()["id"]

    response = await client.post(
        "/api/v1/pecuaria/manejos/",
        json={
            "lote_id": lote_id,
            "tipo_evento": "VACINACAO",
            "data_evento": str(date.today()),
            "quantidade_cabecas": 50,
            "custo_total": 750.0,
            "observacoes": "Vacina Aftosa",
        },
        headers=headers_pecuaria,
    )

    assert response.status_code == 201, response.text
    assert response.json()["tipo_evento"] == "VACINACAO"


# ---------------------------------------------------------------------------
# PEC-EVT-02: Eventos são append-only (não editáveis)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_eventos_append_only(client, session, headers_pecuaria):
    """PEC-EVT-02: Eventos de manejo não podem ser editados (PUT/PATCH retorna 405)"""
    await _garantir_suporte(session)

    r = await client.post(
        "/api/v1/lotes-bovinos/",
        json=_payload_lote(),
        headers=headers_pecuaria,
    )
    assert r.status_code == 201
    lote_id = r.json()["id"]

    evt = await client.post(
        "/api/v1/pecuaria/manejos/",
        json={
            "lote_id": lote_id,
            "tipo_evento": "PESAGEM",
            "data_evento": str(date.today()),
            "peso_total_kg": 12000.0,
        },
        headers=headers_pecuaria,
    )
    assert evt.status_code == 201
    evento_id = evt.json()["id"]

    # Tenta editar — deve ser bloqueado
    patch = await client.patch(
        f"/api/v1/pecuaria/manejos/{evento_id}",
        json={"observacoes": "Tentativa de edição"},
        headers=headers_pecuaria,
    )
    assert patch.status_code in (405, 404, 422), (
        f"Eventos deveriam ser imutáveis, recebeu {patch.status_code}"
    )


# ---------------------------------------------------------------------------
# PEC-EVT-03: Listar eventos por lote
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listar_eventos_por_lote(client, session, headers_pecuaria):
    """PEC-EVT-03: GET /pecuaria/manejos?lote_id={id} retorna eventos do lote"""
    await _garantir_suporte(session)

    r = await client.post(
        "/api/v1/lotes-bovinos/",
        json=_payload_lote(),
        headers=headers_pecuaria,
    )
    assert r.status_code == 201
    lote_id = r.json()["id"]

    # Cria 2 eventos
    for tipo in ["PESAGEM", "VACINACAO"]:
        await client.post(
            "/api/v1/pecuaria/manejos/",
            json={"lote_id": lote_id, "tipo_evento": tipo,
                  "data_evento": str(date.today())},
            headers=headers_pecuaria,
        )

    response = await client.get(
        f"/api/v1/pecuaria/manejos/?lote_id={lote_id}",
        headers=headers_pecuaria,
    )

    assert response.status_code == 200
    eventos = response.json()
    assert len(eventos) >= 2
    lotes_ids = {e["lote_id"] for e in eventos}
    assert lotes_ids == {lote_id}


# ---------------------------------------------------------------------------
# Sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pecuaria_sem_token_retorna_401(client):
    response = await client.get("/api/v1/lotes-bovinos/")
    assert response.status_code == 401
