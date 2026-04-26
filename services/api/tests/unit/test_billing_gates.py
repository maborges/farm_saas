"""
Testes unitários — billing gates do Step 23.

Verifica que:
- PENDENTE_PAGAMENTO NÃO passa nos gates de módulo/tier/limite.
- ATIVA e TRIAL passam normalmente.
- _assinatura_ativa_filter() retorna o filtro correto.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import select

pytestmark = pytest.mark.asyncio(loop_scope="function")


def _make_assinatura(status: str):
    """Cria mock de AssinaturaTenant com o status informado."""
    a = MagicMock()
    a.status = status
    a.plano = MagicMock()
    a.plano.modulos_inclusos = ["CORE", "A1_PLANEJAMENTO", "AGRICOLA"]
    a.plano.tier = "ESSENCIAL"
    return a


class TestAssinaturaAtivaFilter:
    """_assinatura_ativa_filter deve incluir apenas ATIVA e TRIAL."""

    def test_filter_inclui_ativa_e_trial(self):
        from core.dependencies import _assinatura_ativa_filter
        from core.models.billing import AssinaturaTenant

        filtro = _assinatura_ativa_filter()
        # O filtro gerado deve conter ATIVA e TRIAL
        sql = str(filtro.compile(compile_kwargs={"literal_binds": True}))
        assert "ATIVA" in sql
        assert "TRIAL" in sql

    def test_filter_exclui_pendente_pagamento(self):
        from core.dependencies import _assinatura_ativa_filter

        filtro = _assinatura_ativa_filter()
        sql = str(filtro.compile(compile_kwargs={"literal_binds": True}))
        assert "PENDENTE_PAGAMENTO" not in sql

    def test_filter_exclui_suspensa(self):
        from core.dependencies import _assinatura_ativa_filter

        filtro = _assinatura_ativa_filter()
        sql = str(filtro.compile(compile_kwargs={"literal_binds": True}))
        assert "SUSPENSA" not in sql

    def test_filter_exclui_cancelada(self):
        from core.dependencies import _assinatura_ativa_filter

        filtro = _assinatura_ativa_filter()
        sql = str(filtro.compile(compile_kwargs={"literal_binds": True}))
        assert "CANCELADA" not in sql
