"""
Testes de Integração — Desbloqueio de Login

Testes para endpoints de desbloqueio:
- Backoffice (admin SaaS) pode desbloquear qualquer usuário
- Gestor de tenant pode desbloquear usuários do seu tenant
"""
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta, timezone

from core.services.auth_service import hash_password
from tests.integration.helpers import garantir_assinatura


@pytest.fixture
async def usuario_bloqueado(session: AsyncSession):
    """Cria usuário bloqueado para teste."""
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), 'bloqueado@teste.com', 'bloqueadoteste', 'Usuário Bloqueado', :hash, true, false, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = true
        RETURNING id
    """), {"hash": hash_password("Senha@123")})

    # Limpa tentativas anteriores e cria nova bloqueada
    await session.execute(text(
        "DELETE FROM login_tentativas WHERE email = 'bloqueado@teste.com'"
    ))
    bloqueio_ate = datetime.now(timezone.utc) + timedelta(minutes=10)
    await session.execute(text("""
        INSERT INTO login_tentativas (id, email, tentativas_count, bloqueado, sucesso, data_bloqueio, data_desbloqueio, motivo_falha, created_at, updated_at)
        VALUES (gen_random_uuid(), 'bloqueado@teste.com', 5, true, false, NOW() - INTERVAL '5 minutes', :desbloqueio, 'SENHA_INVALIDA', NOW(), NOW())
    """), {"desbloqueio": bloqueio_ate})
    await session.commit()

    result = await session.execute(text("SELECT id FROM usuarios WHERE email = 'bloqueado@teste.com'"))
    row = result.fetchone()

    class _User:
        id = row[0]
        email = "bloqueado@teste.com"

    return _User()


@pytest.fixture
async def admin_backoffice(session: AsyncSession):
    """Cria usuário admin do backoffice."""
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), 'admin@agrosaas.com.br', 'adminbackoffice', 'Admin Backoffice', :hash, true, true, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = true, is_superuser = true
        RETURNING id
    """), {"hash": hash_password("Senha@123")})
    await session.commit()

    result = await session.execute(text("SELECT id FROM usuarios WHERE email = 'admin@agrosaas.com.br'"))
    row = result.fetchone()

    class _Admin:
        id = row[0]
        email = "admin@agrosaas.com.br"

    return _Admin()


@pytest.fixture
async def tenant_com_gestor(session: AsyncSession):
    """Cria tenant com gestor e usuário comum."""
    tenant_id = uuid.uuid4()
    await session.execute(text("""
        INSERT INTO tenants (id, nome, documento, ativo, storage_usado_mb, storage_limite_mb, idioma_padrao, created_at, updated_at)
        VALUES (:id, 'Tenant Desbloqueio Teste', '99999999000199', true, 0, 10240, 'pt-BR', NOW(), NOW())
        ON CONFLICT (documento) DO UPDATE SET nome = EXCLUDED.nome
        RETURNING id
    """), {"id": str(tenant_id)})
    # Recupera o id real (pode diferir se houve conflito de documento)
    result = await session.execute(text("SELECT id FROM tenants WHERE documento = '99999999000199'"))
    tenant_id = result.fetchone()[0]

    # Upsert gestor
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), 'gestor@tenant.com.br', 'gestorteste', 'Gestor do Tenant', :hash, true, false, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = true
    """), {"hash": hash_password("Senha@123")})

    # Upsert usuário comum
    await session.execute(text("""
        INSERT INTO usuarios (id, email, username, nome_completo, senha_hash, ativo, is_superuser, created_at, updated_at)
        VALUES (gen_random_uuid(), 'usuario@tenant.com.br', 'usuarioteste', 'Usuário Comum', :hash, true, false, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET senha_hash = EXCLUDED.senha_hash, ativo = true
    """), {"hash": hash_password("Senha@123")})

    await garantir_assinatura(session, tenant_id)
    await session.commit()

    gestor_row = await session.execute(text("SELECT id FROM usuarios WHERE email = 'gestor@tenant.com.br'"))
    gestor_id = gestor_row.fetchone()[0]

    comum_row = await session.execute(text("SELECT id FROM usuarios WHERE email = 'usuario@tenant.com.br'"))
    comum_id = comum_row.fetchone()[0]

    # Vincula gestor ao tenant como owner
    await session.execute(text("""
        INSERT INTO tenant_usuarios (id, tenant_id, usuario_id, is_owner, status, created_at)
        SELECT gen_random_uuid(), :tid, :uid, true, 'ATIVO', NOW()
        WHERE NOT EXISTS (SELECT 1 FROM tenant_usuarios WHERE tenant_id = :tid AND usuario_id = :uid)
    """), {"tid": str(tenant_id), "uid": str(gestor_id)})

    # Vincula usuário comum ao tenant
    await session.execute(text("""
        INSERT INTO tenant_usuarios (id, tenant_id, usuario_id, is_owner, status, created_at)
        SELECT gen_random_uuid(), :tid, :uid, false, 'ATIVO', NOW()
        WHERE NOT EXISTS (SELECT 1 FROM tenant_usuarios WHERE tenant_id = :tid AND usuario_id = :uid)
    """), {"tid": str(tenant_id), "uid": str(comum_id)})

    await session.commit()

    class _Gestor:
        id = gestor_id
        email = "gestor@tenant.com.br"

    class _Comum:
        id = comum_id
        email = "usuario@tenant.com.br"

    return {
        "tenant_id": tenant_id,
        "gestor": _Gestor(),
        "usuario_comum": _Comum(),
    }


class TestDesbloqueioBackoffice:
    """Testes para desbloqueio via backoffice (admin SaaS)."""

    @pytest.mark.asyncio
    async def test_backoffice_desbloqueia_usuario(self, client: AsyncClient, session, usuario_bloqueado, admin_backoffice):
        """Backoffice consegue desbloquear usuário bloqueado."""
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@agrosaas.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]

        response = await client.post(
            "/api/v1/backoffice/login/desbloquear",
            json={"email": "bloqueado@teste.com"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["sucesso"] is True

    @pytest.mark.asyncio
    async def test_backoffice_ver_tentativas(self, client: AsyncClient, session, usuario_bloqueado, admin_backoffice):
        """Backoffice consegue ver tentativas de login de usuário."""
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@agrosaas.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/backoffice/login/tentativas/bloqueado@teste.com",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == "bloqueado@teste.com"
        assert data["bloqueado"] is True

    @pytest.mark.asyncio
    async def test_backoffice_listar_bloqueados(self, client: AsyncClient, session, usuario_bloqueado, admin_backoffice):
        """Backoffice consegue listar usuários bloqueados."""
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@agrosaas.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/backoffice/login/bloqueados",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["total"] >= 1
        emails = [b["email"] for b in data["bloqueados"]]
        assert "bloqueado@teste.com" in emails


class TestDesbloqueioGestorTenant:
    """Testes para desbloqueio via gestor de tenant."""

    @pytest.mark.asyncio
    async def test_gestor_desbloqueia_usuario_do_tenant(self, client: AsyncClient, session, tenant_com_gestor):
        """Gestor consegue desbloquear usuário do seu tenant."""
        await session.execute(text(
            "DELETE FROM login_tentativas WHERE email = 'usuario@tenant.com.br'"
        ))
        bloqueio_ate = datetime.now(timezone.utc) + timedelta(minutes=10)
        await session.execute(text("""
            INSERT INTO login_tentativas (id, email, tentativas_count, bloqueado, sucesso, data_bloqueio, data_desbloqueio, created_at, updated_at)
            VALUES (gen_random_uuid(), 'usuario@tenant.com.br', 5, true, false, NOW() - INTERVAL '5 minutes', :ate, NOW(), NOW())
        """), {"ate": bloqueio_ate})
        await session.commit()

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "gestor@tenant.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]

        response = await client.post(
            f"/api/v1/auth/tenant/usuarios/{tenant_com_gestor['usuario_comum'].id}/desbloquear-login",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["sucesso"] is True

    @pytest.mark.asyncio
    async def test_gestor_nao_desbloqueia_usuario_de_outro_tenant(self, client: AsyncClient, session, tenant_com_gestor, usuario_bloqueado):
        """Gestor NÃO consegue desbloquear usuário de outro tenant."""
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "gestor@tenant.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]

        response = await client.post(
            f"/api/v1/auth/tenant/usuarios/{usuario_bloqueado.id}/desbloquear-login",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_operador_nao_desbloqueia_usuario(self, client: AsyncClient, session, tenant_com_gestor):
        """Operador (sem permissão) NÃO consegue desbloquear usuário."""
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "usuario@tenant.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]

        response = await client.post(
            f"/api/v1/auth/tenant/usuarios/{tenant_com_gestor['gestor'].id}/desbloquear-login",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_gestor_ver_tentativas_usuario(self, client: AsyncClient, session, tenant_com_gestor):
        """Gestor consegue ver tentativas de login de usuário do tenant."""
        await session.execute(text(
            "DELETE FROM login_tentativas WHERE email = 'usuario@tenant.com.br'"
        ))
        await session.execute(text("""
            INSERT INTO login_tentativas (id, email, tentativas_count, bloqueado, sucesso, motivo_falha, created_at, updated_at)
            VALUES (gen_random_uuid(), 'usuario@tenant.com.br', 3, false, false, 'SENHA_INVALIDA', NOW(), NOW())
        """))
        await session.commit()

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "gestor@tenant.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]

        response = await client.get(
            f"/api/v1/auth/tenant/usuarios/{tenant_com_gestor['usuario_comum'].id}/login-tentativas",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == "usuario@tenant.com.br"
        assert data["tentativas_count"] == 3
