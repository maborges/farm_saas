"""
Testes de Integração — Auth API (HTTP)
CORE-AUTH-09, CORE-AUTH-10: Endpoints reais com banco de dados
"""
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from core.services.auth_service import hash_password


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _criar_usuario(session: AsyncSession, email: str, senha: str) -> uuid.UUID:
    """Insere usuário direto no banco para setup dos testes de integração."""
    from sqlalchemy import text
    user_id = uuid.uuid4()
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (:id, :email, :username, :nome_completo, :senha_hash, true, false, NOW(), NOW())
        ON CONFLICT (email) DO NOTHING
    """), {
        "id": str(user_id),
        "email": email,
        "username": email.split("@")[0],
        "nome_completo": "Usuário Teste Integração",
        "senha_hash": hash_password(senha),
    })
    await session.commit()
    return user_id


@pytest.fixture
async def client():
    """Cliente HTTP assíncrono apontando para a app FastAPI."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# CORE-AUTH-09: Acesso sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_acesso_sem_token_retorna_401(client):
    """CORE-AUTH-09: Endpoint protegido sem Authorization header retorna 401"""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# CORE-AUTH-10: Token expirado retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_expirado_retorna_401(client):
    """CORE-AUTH-10: Requisição com token expirado retorna 401"""
    from datetime import timedelta
    from core.services.auth_service import AuthService
    from unittest.mock import MagicMock

    # Gera token já expirado (expirou 1 hora atrás)
    svc = AuthService(MagicMock())
    token = svc.create_access_token(
        {"sub": str(uuid.uuid4()), "tenant_id": None, "modules": ["CORE"]},
        expires_delta=timedelta(hours=-1),
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# CORE-AUTH-11: Login completo via API retorna token válido
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_via_api(client, session):
    """Login via POST /auth/login retorna access_token"""
    email = f"integracao_{uuid.uuid4().hex[:6]}@teste.com"
    senha = "Integracao@123"
    await _criar_usuario(session, email, senha)

    response = await client.post("/api/v1/auth/login", json={"email": email, "senha": senha})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert len(data["access_token"]) > 20


# ---------------------------------------------------------------------------
# CORE-AUTH-12: Login com credenciais erradas via API retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_credenciais_erradas_via_api(client):
    """Login com email/senha incorretos via API retorna 401"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "naoexiste@never.com", "senha": "qualquer"},
    )
    assert response.status_code == 401
