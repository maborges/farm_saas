"""
Testes Unitários — Autenticação e Autorização
CORE-AUTH-01 a 08: Lógica pura do AuthService (sem HTTP)
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta
from jose import jwt

from core.services.auth_service import AuthService, hash_password
from core.schemas.auth_schemas import LoginRequest, UserCreateRequest
from core.config import settings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_mock_user(
    email="fazendeiro@teste.com",
    senha="Senha@123",
    ativo=True,
    is_superuser=False,
):
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = email
    user.username = "fazendeiro"
    user.nome_completo = "Fazendeiro Teste"
    user.senha_hash = hash_password(senha)
    user.ativo = ativo
    user.is_superuser = is_superuser
    user.foto_perfil_url = None
    return user


@pytest.fixture
def mock_session():
    session = AsyncMock()
    return session


@pytest.fixture
def auth_service(mock_session):
    return AuthService(mock_session)


# ---------------------------------------------------------------------------
# CORE-AUTH-01: Login com credenciais válidas
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_credenciais_validas(auth_service, mock_session):
    """CORE-AUTH-01: Login com credenciais válidas retorna usuário e token JWT"""
    user = make_mock_user()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user
    result_mock.scalars.return_value.all.return_value = []  # sem tenants
    mock_session.execute.return_value = result_mock

    login_data = LoginRequest(email="fazendeiro@teste.com", senha="Senha@123")
    returned_user, token = await auth_service.authenticate_user(login_data)

    assert returned_user.id == user.id
    assert token is not None
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert payload["sub"] == str(user.id)


# ---------------------------------------------------------------------------
# CORE-AUTH-02: Login com email inválido
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_email_invalido(auth_service, mock_session):
    """CORE-AUTH-02: Login com email inexistente retorna 401"""
    from fastapi import HTTPException

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock

    login_data = LoginRequest(email="naoexiste@teste.com", senha="qualquer")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.authenticate_user(login_data)

    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# CORE-AUTH-03: Login com senha inválida
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_senha_invalida(auth_service, mock_session):
    """CORE-AUTH-03: Login com senha errada retorna 401"""
    from fastapi import HTTPException

    user = make_mock_user(senha="SenhaCorreta@123")

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = result_mock

    login_data = LoginRequest(email="fazendeiro@teste.com", senha="SenhaErrada@999")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.authenticate_user(login_data)

    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# CORE-AUTH-04: JWT gerado com claims corretos
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_claims_corretos(auth_service, mock_session):
    """CORE-AUTH-04: Token JWT contém sub, tenant_id, modules, exp"""
    user = make_mock_user()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user
    result_mock.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = result_mock

    login_data = LoginRequest(email="fazendeiro@teste.com", senha="Senha@123")
    _, token = await auth_service.authenticate_user(login_data)

    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert "sub" in payload
    assert "modules" in payload
    assert "exp" in payload
    assert "CORE" in payload["modules"]


# ---------------------------------------------------------------------------
# CORE-AUTH-05: Usuário inativo bloqueado
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_usuario_inativo(auth_service, mock_session):
    """CORE-AUTH-05: Usuário inativo retorna 403"""
    from fastapi import HTTPException

    user = make_mock_user(ativo=False)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = result_mock

    login_data = LoginRequest(email="fazendeiro@teste.com", senha="Senha@123")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.authenticate_user(login_data)

    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# CORE-AUTH-06: Senha hasheada com bcrypt
# ---------------------------------------------------------------------------

def test_senha_hash_bcrypt():
    """CORE-AUTH-06: Senha é armazenada como hash bcrypt (nunca plain text)"""
    senha = "MinhaSenha@123"
    hashed = hash_password(senha)

    assert hashed != senha
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    from passlib.context import CryptContext
    ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    assert ctx.verify(senha, hashed)


# ---------------------------------------------------------------------------
# CORE-AUTH-07: Registro de novo usuário
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_registro_novo_usuario(auth_service, mock_session):
    """CORE-AUTH-07: Registro com dados válidos cria usuário"""
    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = None  # sem duplicata
    mock_session.execute.return_value = result_mock
    mock_session.commit = AsyncMock()

    user_data = UserCreateRequest(
        email="novo@fazenda.com",
        username="novo_fazendeiro",
        nome_completo="Novo Fazendeiro",
        senha="Senha@456",
    )

    # Captura o objeto adicionado à session
    added_objects = []
    mock_session.add.side_effect = lambda obj: added_objects.append(obj)

    from core.models.auth import Usuario
    with patch.object(Usuario, "__init__", lambda self, **kw: self.__dict__.update(kw)):
        await auth_service.register_user(user_data)

    mock_session.commit.assert_called_once()


# ---------------------------------------------------------------------------
# CORE-AUTH-08: Registro com email duplicado retorna erro
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_registro_email_duplicado(auth_service, mock_session):
    """CORE-AUTH-08: Registro com email já cadastrado retorna 400"""
    from fastapi import HTTPException

    existing_user = make_mock_user()
    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = existing_user
    mock_session.execute.return_value = result_mock

    user_data = UserCreateRequest(
        email="fazendeiro@teste.com",
        username="outro_user",
        nome_completo="Outro",
        senha="Senha@789",
    )

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(user_data)

    assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# CORE-AUTH helper: create_access_token com expiração customizada
# ---------------------------------------------------------------------------

def test_token_expiracao_customizada():
    """create_access_token respeita expires_delta"""
    from core.services.auth_service import AuthService
    from unittest.mock import MagicMock
    svc = AuthService(MagicMock())

    token = svc.create_access_token({"sub": "test"}, expires_delta=timedelta(minutes=5))
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    from datetime import datetime, timezone
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    diff_minutes = (exp - now).total_seconds() / 60

    assert 4 <= diff_minutes <= 6
