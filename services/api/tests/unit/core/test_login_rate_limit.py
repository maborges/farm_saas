"""
Testes Unitários — Login Rate Limiting Service

CORE-AUTH-06: Rate limiting de login
- 5 tentativas falhas em 15 minutos → bloqueio
- Bloqueio dura 15 minutos
- Login bem-sucedido reseta contador
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from core.services.login_rate_limit_service import LoginRateLimitService
from core.models.auth import TentativaLogin


@pytest.fixture
def mock_session():
    """Mock de sessão SQLAlchemy async."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def rate_limit_service(mock_session):
    return LoginRateLimitService(mock_session)


class TestVerificarBloqueio:
    """Testes para verificar_bloqueio()."""

    @pytest.mark.asyncio
    async def test_sem_registro_nao_bloqueado(self, rate_limit_service, mock_session):
        """Usuário sem tentativas anteriores não está bloqueado."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        bloqueado, data_desbloqueio = await rate_limit_service.verificar_bloqueio("teste@email.com")
        
        assert bloqueado is False
        assert data_desbloqueio is None

    @pytest.mark.asyncio
    async def test_registro_existente_nao_bloqueado(self, rate_limit_service, mock_session):
        """Registro com menos de 5 tentativas não bloqueia."""
        tentativa = TentativaLogin(
            email="teste@email.com",
            tentativas_count=3,
            bloqueado=False,
            created_at=datetime.now(timezone.utc)
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = tentativa
        mock_session.execute.return_value = mock_result
        
        bloqueado, data_desbloqueio = await rate_limit_service.verificar_bloqueio("teste@email.com")
        
        assert bloqueado is False
        assert data_desbloqueio is None

    @pytest.mark.asyncio
    async def test_bloqueado_com_desbloqueio_futuro(self, rate_limit_service, mock_session):
        """Usuário bloqueado com desbloqueio futuro permanece bloqueado."""
        tentativa = TentativaLogin(
            email="teste@email.com",
            tentativas_count=5,
            bloqueado=True,
            data_bloqueio=datetime.now(timezone.utc) - timedelta(minutes=5),
            data_desbloqueio=datetime.now(timezone.utc) + timedelta(minutes=10),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=20)
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = tentativa
        mock_session.execute.return_value = mock_result
        
        bloqueado, data_desbloqueio = await rate_limit_service.verificar_bloqueio("teste@email.com")
        
        assert bloqueado is True
        assert data_desbloqueio is not None

    @pytest.mark.asyncio
    async def test_bloqueado_com_desbloqueio_passado_auto_desbloqueia(self, rate_limit_service, mock_session):
        """Bloqueio com tempo expirado desbloqueia automaticamente."""
        tentativa = TentativaLogin(
            email="teste@email.com",
            tentativas_count=5,
            bloqueado=True,
            data_bloqueio=datetime.now(timezone.utc) - timedelta(minutes=20),
            data_desbloqueio=datetime.now(timezone.utc) - timedelta(minutes=5),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=30)
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = tentativa
        mock_session.execute.return_value = mock_result
        
        bloqueado, data_desbloqueio = await rate_limit_service.verificar_bloqueio("teste@email.com")
        
        assert bloqueado is False
        assert data_desbloqueio is None
        # Verifica se commit foi chamado para atualizar o desbloqueio
        mock_session.commit.assert_called_once()


class TestRegistrarTentativaFalha:
    """Testes para registrar_tentativa_falha()."""

    @pytest.mark.asyncio
    async def test_primeira_tentativa_falha(self, rate_limit_service, mock_session):
        """Primeira tentativa falha cria novo registro."""
        # Simula que não existe registro
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        bloqueado, data_desbloqueio = await rate_limit_service.registrar_tentativa_falha(
            email="teste@email.com",
            motivo="SENHA_INVALIDA",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        assert bloqueado is False
        assert data_desbloqueio is None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_quinta_tentativa_bloqueia(self, rate_limit_service, mock_session):
        """Quinta tentativa falha causa bloqueio automático."""
        tentativa_existente = TentativaLogin(
            email="teste@email.com",
            tentativas_count=4,
            bloqueado=False,
            created_at=datetime.now(timezone.utc)
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = tentativa_existente
        mock_session.execute.return_value = mock_result
        
        bloqueado, data_desbloqueio = await rate_limit_service.registrar_tentativa_falha(
            email="teste@email.com",
            motivo="SENHA_INVALIDA"
        )
        
        assert bloqueado is True
        assert data_desbloqueio is not None
        assert tentativa_existente.tentativas_count == 5
        assert tentativa_existente.bloqueado is True
        assert tentativa_existente.data_bloqueio is not None
        assert tentativa_existente.data_desbloqueio is not None

    @pytest.mark.asyncio
    async def test_tentativa_fora_janela_reseta_contador(self, rate_limit_service, mock_session):
        """Tentativa fora da janela de 15 minutos reseta contador."""
        tentativa_antiga = TentativaLogin(
            email="teste@email.com",
            tentativas_count=5,
            bloqueado=False,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=30)  # Fora da janela
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = tentativa_antiga
        mock_session.execute.return_value = mock_result
        
        bloqueado, data_desbloqueio = await rate_limit_service.registrar_tentativa_falha(
            email="teste@email.com",
            motivo="SENHA_INVALIDA"
        )
        
        # Deve criar novo registro com contador=1
        assert bloqueado is False
        mock_session.add.assert_called_once()


class TestRegistrarTentativaSucesso:
    """Testes para registrar_tentativa_sucesso()."""

    @pytest.mark.asyncio
    async def test_sucesso_reseta_contador(self, rate_limit_service, mock_session):
        """Login bem-sucedido reseta contador de tentativas."""
        tentativa = TentativaLogin(
            email="teste@email.com",
            tentativas_count=4,
            bloqueado=False,
            created_at=datetime.now(timezone.utc)
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = tentativa
        mock_session.execute.return_value = mock_result
        
        await rate_limit_service.registrar_tentativa_sucesso("teste@email.com")
        
        assert tentativa.tentativas_count == 0
        assert tentativa.sucesso is True
        mock_session.commit.assert_called_once()


class TestGetTentativasRestantes:
    """Testes para get_tentativas_restantes()."""

    @pytest.mark.asyncio
    async def test_sem_registro_tem_5_tentativas(self, rate_limit_service, mock_session):
        """Usuário sem registros tem 5 tentativas disponíveis."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        restantes = await rate_limit_service.get_tentativas_restantes("teste@email.com")
        
        assert restantes == 5

    @pytest.mark.asyncio
    async def test_com_2_tentativas_tem_3_restantes(self, rate_limit_service, mock_session):
        """Usuário com 2 tentativas tem 3 restantes."""
        tentativa = TentativaLogin(
            email="teste@email.com",
            tentativas_count=2,
            bloqueado=False,
            created_at=datetime.now(timezone.utc)
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = tentativa
        mock_session.execute.return_value = mock_result
        
        restantes = await rate_limit_service.get_tentativas_restantes("teste@email.com")
        
        assert restantes == 3

    @pytest.mark.asyncio
    async def test_bloqueado_tem_0_tentativas(self, rate_limit_service, mock_session):
        """Usuário bloqueado tem 0 tentativas restantes."""
        # Patch em verificar_bloqueio para retornar bloqueado
        with patch.object(rate_limit_service, 'verificar_bloqueio', return_value=(True, None)):
            restantes = await rate_limit_service.get_tentativas_restantes("teste@email.com")
            assert restantes == 0


class TestDesbloqueioManual:
    """Testes para desbloquear_manual()."""

    @pytest.mark.asyncio
    async def test_desbloqueio_manual_reseta_contador(self, rate_limit_service, mock_session):
        """Desbloqueio manual reseta todas as flags."""
        tentativa = TentativaLogin(
            email="teste@email.com",
            tentativas_count=5,
            bloqueado=True,
            data_bloqueio=datetime.now(timezone.utc),
            data_desbloqueio=datetime.now(timezone.utc) + timedelta(minutes=15),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=20)
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = tentativa
        mock_session.execute.return_value = mock_result
        
        await rate_limit_service.desbloquear_manual("teste@email.com")
        
        assert tentativa.bloqueado is False
        assert tentativa.data_bloqueio is None
        assert tentativa.data_desbloqueio is None
        assert tentativa.tentativas_count == 0
        mock_session.commit.assert_called_once()
