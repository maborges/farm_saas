"""
Testes unitários — máquina de estados AssinaturaTenant (Step 23).

Verifica:
- Transições válidas são permitidas.
- Transições inválidas levantam TransicaoInvalidaError.
- CANCELADA é terminal: nenhuma transição é permitida.
- SUSPENSA não pode ir direto para TRIAL.
"""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.services.assinatura_service import (
    transicionar_assinatura,
    TransicaoInvalidaError,
    _TRANSICOES,
)

pytestmark = pytest.mark.asyncio(loop_scope="function")


def _make_session(status_atual: str) -> AsyncMock:
    assinatura = MagicMock()
    assinatura.id = uuid.uuid4()
    assinatura.tenant_id = uuid.uuid4()
    assinatura.status = status_atual

    result = MagicMock()
    result.scalar_one_or_none.return_value = assinatura

    session = AsyncMock()
    session.execute.return_value = result
    return session


class TestTransicoesValidas:
    async def test_pendente_para_trial(self):
        session = _make_session("PENDENTE")
        await transicionar_assinatura(session, uuid.uuid4(), "TRIAL")
        session.execute.assert_called()

    async def test_trial_para_ativa(self):
        session = _make_session("TRIAL")
        await transicionar_assinatura(session, uuid.uuid4(), "ATIVA")
        session.execute.assert_called()

    async def test_ativa_para_pendente_pagamento(self):
        session = _make_session("ATIVA")
        await transicionar_assinatura(session, uuid.uuid4(), "PENDENTE_PAGAMENTO")
        session.execute.assert_called()

    async def test_ativa_para_suspensa(self):
        session = _make_session("ATIVA")
        await transicionar_assinatura(session, uuid.uuid4(), "SUSPENSA")
        session.execute.assert_called()

    async def test_suspensa_para_ativa(self):
        session = _make_session("SUSPENSA")
        await transicionar_assinatura(session, uuid.uuid4(), "ATIVA")
        session.execute.assert_called()

    async def test_pendente_pagamento_para_ativa(self):
        session = _make_session("PENDENTE_PAGAMENTO")
        await transicionar_assinatura(session, uuid.uuid4(), "ATIVA")
        session.execute.assert_called()


class TestTransicoesInvalidas:
    async def test_cancelada_e_terminal(self):
        session = _make_session("CANCELADA")
        with pytest.raises(TransicaoInvalidaError, match="terminal"):
            await transicionar_assinatura(session, uuid.uuid4(), "ATIVA")

    async def test_cancelada_nao_vai_para_trial(self):
        session = _make_session("CANCELADA")
        with pytest.raises(TransicaoInvalidaError):
            await transicionar_assinatura(session, uuid.uuid4(), "TRIAL")

    async def test_suspensa_nao_vai_para_trial(self):
        session = _make_session("SUSPENSA")
        with pytest.raises(TransicaoInvalidaError):
            await transicionar_assinatura(session, uuid.uuid4(), "TRIAL")

    async def test_trial_nao_vai_para_pendente_pagamento(self):
        session = _make_session("TRIAL")
        with pytest.raises(TransicaoInvalidaError):
            await transicionar_assinatura(session, uuid.uuid4(), "PENDENTE_PAGAMENTO")

    async def test_ativa_nao_vai_para_pendente(self):
        session = _make_session("ATIVA")
        with pytest.raises(TransicaoInvalidaError):
            await transicionar_assinatura(session, uuid.uuid4(), "PENDENTE")


class TestCoberturaCompleta:
    def test_todos_os_status_estao_mapeados(self):
        """Garante que nenhum status ficou sem mapeamento."""
        status_conhecidos = {
            "PENDENTE", "TRIAL", "ATIVA",
            "PENDENTE_PAGAMENTO", "SUSPENSA", "BLOQUEADA", "CANCELADA",
        }
        assert set(_TRANSICOES.keys()) == status_conhecidos

    def test_cancelada_tem_set_vazio(self):
        assert _TRANSICOES["CANCELADA"] == set()
