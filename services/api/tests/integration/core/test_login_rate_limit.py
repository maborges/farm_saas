"""
Testes de Integração — Login Rate Limiting

CORE-AUTH-06: Rate limiting de login via API
- 5 tentativas falhas em 15 minutos → bloqueio (HTTP 423)
- Bloqueio dura 15 minutos
- Login bem-sucedido reseta contador
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from core.models.auth import Usuario, TentativaLogin
from core.services.auth_service import hash_password


@pytest.fixture
async def usuario_teste(session: AsyncSession):
    """Cria usuário de teste."""
    from sqlalchemy import text
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), :email, :username, :nome, :hash, true, false, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = true
    """), {
        "email": "rate.limit@teste.com",
        "username": "ratelimit",
        "nome": "Rate Limit Teste",
        "hash": hash_password("Senha@123"),
    })
    await session.commit()
    from sqlalchemy import select as sel
    await session.execute(text("DELETE FROM login_tentativas WHERE email = 'rate.limit@teste.com'"))
    await session.commit()
    return (await session.execute(sel(Usuario).where(Usuario.email == "rate.limit@teste.com"))).scalar_one()


@pytest.mark.asyncio
async def test_login_sucesso_reseta_contador(client: AsyncClient, session: AsyncSession, usuario_teste):
    """Login bem-sucedido reseta contador de tentativas."""
    # Primeiro, cria algumas tentativas falhas
    for i in range(3):
        await client.post("/api/v1/auth/login", json={
            "email": "rate.limit@teste.com",
            "senha": "senha_errada"
        })
    
    # Login bem-sucedido
    response = await client.post("/api/v1/auth/login", json={
        "email": "rate.limit@teste.com",
        "senha": "Senha@123"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Verifica se contador foi resetado
    stmt = select(TentativaLogin).where(TentativaLogin.email == "rate.limit@teste.com")
    result = await session.execute(stmt)
    tentativa = result.scalar_one_or_none()
    
    assert tentativa is not None
    assert tentativa.tentativas_count == 0
    assert tentativa.sucesso is True


@pytest.mark.asyncio
async def test_login_cinco_falhas_bloqueia(client: AsyncClient, session: AsyncSession):
    """5 tentativas falhas bloqueiam a conta."""
    email = "bloqueio@teste.com"
    await session.execute(text("DELETE FROM login_tentativas WHERE email = :e"), {"e": email})
    await session.commit()
    
    # Cria usuário
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), :email, :username, :nome, :hash, :ativo, false, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = EXCLUDED.ativo
    """), {"email": email, "username": "bloqueioteste", "nome": "Bloqueio Teste", "hash": hash_password("Senha@123"), "ativo": True})
    await session.commit()
    
    # 5 tentativas falhas
    for i in range(5):
        response = await client.post("/api/v1/auth/login", json={
            "email": email,
            "senha": "senha_errada"
        })
        assert response.status_code == 401
    
    # Sexta tentativa deve retornar 423 (bloqueado)
    response = await client.post("/api/v1/auth/login", json={
        "email": email,
        "senha": "senha_errada"
    })
    
    assert response.status_code == 423
    assert "bloqueada" in response.json()["detail"].lower()
    assert "Retry-After" in response.headers


@pytest.mark.asyncio
async def test_login_conta_bloqueada_mensagem_informativa(client: AsyncClient, session: AsyncSession):
    """Conta bloqueada exibe mensagem com tempo restante."""
    email = "bloqueado2@teste.com"
    await session.execute(text("DELETE FROM login_tentativas WHERE email = :e"), {"e": email})
    await session.commit()
    
    # Cria usuário
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), :email, :username, :nome, :hash, :ativo, false, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = EXCLUDED.ativo
    """), {"email": email, "username": "bloqueado2teste", "nome": "Bloqueado 2 Teste", "hash": hash_password("Senha@123"), "ativo": True})
    
    # Cria registro de bloqueio manualmente
    from datetime import datetime, timedelta, timezone
    tentativa = TentativaLogin(
        email=email,
        tentativas_count=5,
        bloqueado=True,
        data_bloqueio=datetime.now(timezone.utc) - timedelta(minutes=5),
        data_desbloqueio=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    session.add(tentativa)
    await session.commit()
    
    # Tenta login
    response = await client.post("/api/v1/auth/login", json={
        "email": email,
        "senha": "Senha@123"
    })
    
    assert response.status_code == 423
    detail = response.json()["detail"]
    assert "bloqueada" in detail.lower()
    assert "minuto" in detail.lower()


@pytest.mark.asyncio
async def test_login_usuario_inativo_registra_tentativa(client: AsyncClient, session: AsyncSession):
    """Login de usuário inativo registra tentativa e retorna 403."""
    email = "inativo@teste.com"
    await session.execute(text("DELETE FROM login_tentativas WHERE email = :e"), {"e": email})
    await session.commit()
    
    # Cria usuário
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), :email, :username, :nome, :hash, :ativo, false, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = EXCLUDED.ativo
    """), {"email": email, "username": "inativoteste", "nome": "Inativo Teste", "hash": hash_password("Senha@123"), "ativo": False})
    await session.commit()
    
    # Tenta login
    response = await client.post("/api/v1/auth/login", json={
        "email": email,
        "senha": "Senha@123"
    })
    
    assert response.status_code == 403
    assert "inativo" in response.json()["detail"].lower()
    
    # Verifica se registrou tentativa
    stmt = select(TentativaLogin).where(TentativaLogin.email == email)
    result = await session.execute(stmt)
    tentativa = result.scalar_one_or_none()
    
    assert tentativa is not None
    assert tentativa.motivo_falha == "USUARIO_INATIVO"


@pytest.mark.asyncio
async def test_login_usuario_nao_encontrado_registra_tentativa(client: AsyncClient, session: AsyncSession):
    """Login com usuário não encontrado registra tentativa."""
    email = "naoexiste@teste.com"
    await session.execute(text("DELETE FROM login_tentativas WHERE email = :e"), {"e": email})
    await session.commit()
    
    # Tenta login com usuário que não existe
    response = await client.post("/api/v1/auth/login", json={
        "email": email,
        "senha": "qualquer_senha"
    })
    
    assert response.status_code == 401
    
    # Verifica se registrou tentativa
    stmt = select(TentativaLogin).where(TentativaLogin.email == email)
    result = await session.execute(stmt)
    tentativa = result.scalar_one_or_none()
    
    assert tentativa is not None
    assert tentativa.motivo_falha == "USUARIO_NAO_ENCONTRADO"
    assert tentativa.tentativas_count == 1


@pytest.mark.asyncio
async def test_login_ip_e_user_agent_registrados(client: AsyncClient, session: AsyncSession):
    """IP e User Agent são registrados nas tentativas."""
    email = "auditoria@teste.com"
    await session.execute(text("DELETE FROM login_tentativas WHERE email = :e"), {"e": email})
    await session.commit()
    
    # Cria usuário
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), :email, :username, :nome, :hash, :ativo, false, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = EXCLUDED.ativo
    """), {"email": email, "username": "auditoriateste", "nome": "Auditoria Teste", "hash": hash_password("Senha@123"), "ativo": True})
    await session.commit()
    
    # Tenta login com headers customizados
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "senha_errada"},
        headers={"User-Agent": "TestClient/1.0"}
    )
    
    assert response.status_code == 401
    
    # Verifica se IP e User Agent foram registrados
    stmt = select(TentativaLogin).where(TentativaLogin.email == email)
    result = await session.execute(stmt)
    tentativa = result.scalar_one_or_none()
    
    assert tentativa is not None
    assert tentativa.ip_address is not None  # IP do cliente de teste
    assert tentativa.user_agent == "TestClient/1.0"


@pytest.mark.asyncio
async def test_login_tentativas_restantes_api(client: AsyncClient, session: AsyncSession):
    """Testa fluxo completo de tentativas."""
    email = "fluxo@teste.com"
    await session.execute(text("DELETE FROM login_tentativas WHERE email = :e"), {"e": email})
    await session.commit()
    
    # Cria usuário
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), :email, :username, :nome, :hash, :ativo, false, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = EXCLUDED.ativo
    """), {"email": email, "username": "fluxoteste", "nome": "Fluxo Teste", "hash": hash_password("Senha@123"), "ativo": True})
    await session.commit()
    
    # 3 tentativas falhas
    for i in range(3):
        response = await client.post("/api/v1/auth/login", json={
            "email": email,
            "senha": "errada"
        })
        assert response.status_code == 401
    
    # Login bem-sucedido
    response = await client.post("/api/v1/auth/login", json={
        "email": email,
        "senha": "Senha@123"
    })
    assert response.status_code == 200
    
    # Após sucesso, pode tentar novamente sem bloqueio
    response = await client.post("/api/v1/auth/login", json={
        "email": email,
        "senha": "errada"
    })
    # Deve ser 401 (senha errada) e não 423 (bloqueado)
    assert response.status_code == 401
