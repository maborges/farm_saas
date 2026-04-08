"""
Testes de Integração — Desbloqueio de Login

Testes para endpoints de desbloqueio:
- Backoffice (admin SaaS) pode desbloquear qualquer usuário
- Gestor de tenant pode desbloquear usuários do seu tenant
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from core.models.auth import Usuario, TentativaLogin, TenantUsuario
from core.services.auth_service import hash_password


@pytest.fixture
async def usuario_bloqueado(session: AsyncSession):
    """Cria usuário bloqueado para teste."""
    usuario = Usuario(
        email="bloqueado@teste.com",
        username="bloqueadoteste",
        nome_completo="Usuário Bloqueado",
        senha_hash=hash_password("Senha@123"),
        ativo=True
    )
    session.add(usuario)
    await session.commit()
    
    # Cria registro de bloqueio
    tentativa = TentativaLogin(
        email="bloqueado@teste.com",
        tentativas_count=5,
        bloqueado=True,
        data_bloqueio=datetime.now(timezone.utc) - timedelta(minutes=5),
        data_desbloqueio=datetime.now(timezone.utc) + timedelta(minutes=10),
        motivo_falha="SENHA_INVALIDA"
    )
    session.add(tentativa)
    await session.commit()
    
    return usuario


@pytest.fixture
async def admin_backoffice(session: AsyncSession):
    """Cria usuário admin do backoffice."""
    usuario = Usuario(
        email="admin@agrosaas.com.br",
        username="adminbackoffice",
        nome_completo="Admin Backoffice",
        senha_hash=hash_password("Senha@123"),
        ativo=True,
        is_superuser=True
    )
    session.add(usuario)
    await session.commit()
    return usuario


@pytest.fixture
async def tenant_com_gestor(session: AsyncSession):
    """Cria tenant com gestor e usuário comum."""
    from core.models.tenant import Tenant
    from core.models.auth import PerfilAcesso
    
    # Cria tenant
    tenant = Tenant(nome="Tenant Teste", cnpj="00.000.000/0001-00")
    session.add(tenant)
    await session.commit()
    
    # Cria perfil de gestor
    perfil_gestor = PerfilAcesso(
        tenant_id=tenant.id,
        nome="Gestor",
        permissoes={"core": {"usuarios": "write"}, "backoffice": "write"}
    )
    session.add(perfil_gestor)
    
    # Cria perfil de operador
    perfil_operador = PerfilAcesso(
        tenant_id=tenant.id,
        nome="Operador",
        permissoes={"core": {"usuarios": "read"}}
    )
    session.add(perfil_operador)
    await session.commit()
    
    # Cria gestor
    gestor = Usuario(
        email="gestor@tenant.com.br",
        username="gestorteste",
        nome_completo="Gestor do Tenant",
        senha_hash=hash_password("Senha@123"),
        ativo=True
    )
    session.add(gestor)
    await session.commit()
    
    # Vincula gestor ao tenant
    tenant_usuario_gestor = TenantUsuario(
        tenant_id=tenant.id,
        usuario_id=gestor.id,
        perfil_id=perfil_gestor.id,
        is_owner=True,
        status="ATIVO"
    )
    session.add(tenant_usuario_gestor)
    
    # Cria usuário comum
    usuario_comum = Usuario(
        email="usuario@tenant.com.br",
        username="usuarioteste",
        nome_completo="Usuário Comum",
        senha_hash=hash_password("Senha@123"),
        ativo=True
    )
    session.add(usuario_comum)
    await session.commit()
    
    # Vincula usuário comum ao tenant
    tenant_usuario_comum = TenantUsuario(
        tenant_id=tenant.id,
        usuario_id=usuario_comum.id,
        perfil_id=perfil_operador.id,
        is_owner=False,
        status="ATIVO"
    )
    session.add(tenant_usuario_comum)
    await session.commit()
    
    return {
        "tenant": tenant,
        "gestor": gestor,
        "usuario_comum": usuario_comum,
        "perfil_gestor": perfil_gestor,
        "perfil_operador": perfil_operador
    }


class TestDesbloqueioBackoffice:
    """Testes para desbloqueio via backoffice (admin SaaS)."""

    @pytest.mark.asyncio
    async def test_backoffice_desbloqueia_usuario(self, client: AsyncClient, usuario_bloqueado, admin_backoffice):
        """Backoffice consegue desbloquear usuário bloqueado."""
        # Login do admin
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@agrosaas.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Desbloqueia usuário
        response = await client.post(
            "/api/v1/backoffice/login/desbloquear",
            json={"email": "bloqueado@teste.com"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sucesso"] is True
        assert "desbloqueado" in data["mensagem"].lower()
        
        # Verifica no banco que foi desbloqueado
        from sqlalchemy import select
        stmt = select(TentativaLogin).where(TentativaLogin.email == "bloqueado@teste.com")
        result = await client.app.state.db.execute(stmt)
        tentativa = result.scalar_one_or_none()
        assert tentativa is not None
        assert tentativa.bloqueado is False

    @pytest.mark.asyncio
    async def test_backoffice_ver_tentativas(self, client: AsyncClient, usuario_bloqueado, admin_backoffice):
        """Backoffice consegue ver tentativas de login de usuário."""
        # Login do admin
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@agrosaas.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Ver tentativas
        response = await client.get(
            "/api/v1/backoffice/login/tentativas/bloqueado@teste.com",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "bloqueado@teste.com"
        assert data["bloqueado"] is True
        assert data["tentativas_count"] == 5

    @pytest.mark.asyncio
    async def test_backoffice_listar_bloqueados(self, client: AsyncClient, usuario_bloqueado, admin_backoffice):
        """Backoffice consegue listar usuários bloqueados."""
        # Login do admin
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@agrosaas.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Listar bloqueados
        response = await client.get(
            "/api/v1/backoffice/login/bloqueados",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["bloqueados"]) >= 1
        emails = [b["email"] for b in data["bloqueados"]]
        assert "bloqueado@teste.com" in emails


class TestDesbloqueioGestorTenant:
    """Testes para desbloqueio via gestor de tenant."""

    @pytest.mark.asyncio
    async def test_gestor_desbloqueia_usuario_do_tenant(self, client: AsyncClient, tenant_com_gestor):
        """Gestor consegue desbloquear usuário do seu tenant."""
        # Cria bloqueio para o usuário comum
        tentativa = TentativaLogin(
            email="usuario@tenant.com.br",
            tentativas_count=5,
            bloqueado=True,
            data_bloqueio=datetime.now(timezone.utc) - timedelta(minutes=5),
            data_desbloqueio=datetime.now(timezone.utc) + timedelta(minutes=10)
        )
        client.app.state.db.add(tentativa)
        await client.app.state.db.commit()
        
        # Login do gestor
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "gestor@tenant.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Desbloqueia usuário
        response = await client.post(
            f"/api/v1/auth/tenant/usuarios/{tenant_com_gestor['usuario_comum'].id}/desbloquear-login",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sucesso"] is True
        assert "desbloqueado" in data["mensagem"].lower()

    @pytest.mark.asyncio
    async def test_gestor_nao_desbloqueia_usuario_de_outro_tenant(self, client: AsyncClient, tenant_com_gestor, usuario_bloqueado):
        """Gestor NÃO consegue desbloquear usuário de outro tenant."""
        # Login do gestor
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "gestor@tenant.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Tenta desbloquear usuário de outro tenant
        response = await client.post(
            f"/api/v1/auth/tenant/usuarios/{usuario_bloqueado.id}/desbloquear-login",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Deve retornar 403 ou 404
        assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_operador_nao_desbloqueia_usuario(self, client: AsyncClient, tenant_com_gestor):
        """Operador (sem permissão de escrita) NÃO consegue desbloquear usuário."""
        # Cria bloqueio para o gestor
        tentativa = TentativaLogin(
            email="gestor@tenant.com.br",
            tentativas_count=5,
            bloqueado=True,
            data_bloqueio=datetime.now(timezone.utc) - timedelta(minutes=5),
            data_desbloqueio=datetime.now(timezone.utc) + timedelta(minutes=10)
        )
        client.app.state.db.add(tentativa)
        await client.app.state.db.commit()
        
        # Login do operador (perfil com apenas leitura)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "usuario@tenant.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Tenta desbloquear gestor
        response = await client.post(
            f"/api/v1/auth/tenant/usuarios/{tenant_com_gestor['gestor'].id}/desbloquear-login",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Deve retornar 403 (sem permissão)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_gestor_ver_tentativas_usuario(self, client: AsyncClient, tenant_com_gestor):
        """Gestor consegue ver tentativas de login de usuário do tenant."""
        # Cria bloqueio
        tentativa = TentativaLogin(
            email="usuario@tenant.com.br",
            tentativas_count=3,
            bloqueado=False,
            motivo_falha="SENHA_INVALIDA"
        )
        client.app.state.db.add(tentativa)
        await client.app.state.db.commit()
        
        # Login do gestor
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "gestor@tenant.com.br",
            "senha": "Senha@123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Ver tentativas
        response = await client.get(
            f"/api/v1/auth/tenant/usuarios/{tenant_com_gestor['usuario_comum'].id}/login-tentativas",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "usuario@tenant.com.br"
        assert data["tentativas_count"] == 3
