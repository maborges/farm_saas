"""
Testes unitários — billing gates do Step 23.

Verifica que:
- PENDENTE_PAGAMENTO NÃO passa nos gates de módulo/tier/limite.
- ATIVA e TRIAL passam normalmente.
- _assinatura_ativa_filter() retorna o filtro correto.
"""
import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute
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


class TestRequireTier:
    async def test_bloqueia_tier_baixo_com_headers(self):
        from core.constants import PlanTier
        from core.dependencies import require_tier

        verificador = require_tier(PlanTier.PROFISSIONAL)

        with pytest.raises(HTTPException) as exc:
            await verificador(
                request=None,
                claims={
                    "tenant_id": "aaaaaaaa-0000-0000-0000-000000000010",
                    "plan_tier": "BASICO",
                },
                session=AsyncMock(),
            )

        assert exc.value.status_code == 402
        assert exc.value.headers == {
            "X-Tier-Required": "PROFISSIONAL",
            "X-Tier-Current": "BASICO",
        }

    async def test_permite_tier_profissional(self):
        from core.constants import PlanTier
        from core.dependencies import require_tier

        verificador = require_tier(PlanTier.PROFISSIONAL)

        result = await verificador(
            request=None,
            claims={
                "tenant_id": "aaaaaaaa-0000-0000-0000-000000000010",
                "plan_tier": "PROFISSIONAL",
            },
            session=AsyncMock(),
        )

        assert result == PlanTier.PROFISSIONAL


class TestBillingUpgradePermission:
    def test_solicitar_mudanca_plano_exige_tenant_billing_view(self):
        from core.routers.plan_changes import router as plan_changes_router

        solicitar_route = next(
            route
            for route in plan_changes_router.routes
            if isinstance(route, APIRoute) and route.path.endswith("/solicitar") and "POST" in route.methods
        )

        dependency_calls = [
            dep.call
            for dep in solicitar_route.dependant.dependencies
            if getattr(dep.call, "__closure__", None)
        ]

        assert any(
            any(cell.cell_contents == "tenant:billing:view" for cell in dep.__closure__)
            for dep in dependency_calls
        )
