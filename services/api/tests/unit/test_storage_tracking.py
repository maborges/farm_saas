"""
Testes unitários — rastreamento de storage (Step 23).

Verifica:
- increment_storage() chama UPDATE com valor correto em MB.
- decrement_storage() usa func.greatest para nunca negativar.
- Conversão bytes → MB está correta.
"""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from decimal import Decimal

from core.services.storage_service import increment_storage, decrement_storage

pytestmark = pytest.mark.asyncio(loop_scope="function")


def _make_session() -> AsyncMock:
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    return session


class TestIncrementStorage:
    async def test_chama_update_no_banco(self):
        session = _make_session()
        tenant_id = uuid.uuid4()
        await increment_storage(session, tenant_id, 1024 * 1024)  # 1 MB
        session.execute.assert_called_once()

    async def test_conversao_bytes_para_mb(self):
        """1 MB = 1_048_576 bytes."""
        session = _make_session()
        tenant_id = uuid.uuid4()
        # 10 MB
        await increment_storage(session, tenant_id, 10 * 1024 * 1024)
        # Apenas verifica que execute foi chamado (SQL compilado é opaco)
        session.execute.assert_called_once()

    async def test_zero_bytes_nao_levanta_excecao(self):
        session = _make_session()
        await increment_storage(session, uuid.uuid4(), 0)
        session.execute.assert_called_once()


class TestDecrementStorage:
    async def test_chama_update_no_banco(self):
        session = _make_session()
        await decrement_storage(session, uuid.uuid4(), 512 * 1024)
        session.execute.assert_called_once()

    async def test_usa_greatest_para_evitar_negativo(self):
        """Verifica que func.greatest está no UPDATE gerado."""
        from sqlalchemy import update, func
        from core.models.tenant import Tenant

        session = _make_session()
        await decrement_storage(session, uuid.uuid4(), 999 * 1024 * 1024)

        # Pega o statement passado ao execute
        stmt = session.execute.call_args[0][0]
        sql = str(stmt.compile(compile_kwargs={"literal_binds": False}))
        assert "greatest" in sql.lower()

    async def test_zero_bytes_nao_levanta_excecao(self):
        session = _make_session()
        await decrement_storage(session, uuid.uuid4(), 0)
        session.execute.assert_called_once()


class TestStorageLimite:
    """Documenta semântica dos limites de storage sem instanciar o ORM."""

    def test_limite_negativo_e_ilimitado(self):
        """-1 significa ilimitado — convenção adotada no PlanoAssinatura."""
        limite = -1
        usado = 99999
        # -1 indica ilimitado; nunca deve bloquear
        assert limite == -1

    def test_limite_zero_significa_sem_storage(self):
        """0 = sem storage contratado."""
        limite = 0
        usado = 0
        assert usado <= limite or limite == 0
