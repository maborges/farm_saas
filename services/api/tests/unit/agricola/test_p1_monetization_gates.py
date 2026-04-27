import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute
from unittest.mock import AsyncMock

from core.constants import PlanTier


pytestmark = pytest.mark.asyncio(loop_scope="function")


def _route(router, path: str, methods: set[str]) -> APIRoute:
    for route in router.routes:
        if isinstance(route, APIRoute) and route.path == path and route.methods == methods:
            return route
    raise AssertionError(f"Rota não encontrada: {methods} {path}")


def _tier_dependencies(route: APIRoute):
    return [
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") == "_dependency"
        and dep.call.__closure__
        and any(cell.cell_contents == PlanTier.PROFISSIONAL for cell in dep.call.__closure__)
    ]


@pytest.mark.parametrize(
    ("router_path", "path", "methods"),
    [
        ("agricola.analises_solo.router", "/analises-solo/{id}/recomendacoes", {"GET"}),
        ("agricola.analises_solo.router", "/analises-solo/{id}/inteligencia", {"GET"}),
        ("agricola.analises_solo.router", "/analises-solo/{id}/gerar-tarefas", {"POST"}),
        ("agricola.previsoes.router", "/previsoes/gerar", {"POST"}),
        ("agricola.previsoes.router", "/previsoes/", {"GET"}),
        ("agricola.dashboard.router", "/agricola/dashboard/verificar-alertas", {"POST"}),
        ("core.routers.reports", "/reports/agricola/summary", {"GET"}),
        ("core.routers.reports", "/reports/agricola/talhoes", {"GET"}),
        ("core.routers.reports", "/reports/agricola/profitability", {"GET"}),
    ],
)
async def test_p1_endpoints_exigem_tier_profissional(router_path, path, methods):
    module = __import__(router_path, fromlist=["router"])
    route = _route(module.router, path, methods)
    dependencies = _tier_dependencies(route)

    assert len(dependencies) == 1

    with pytest.raises(HTTPException) as exc:
        await dependencies[0](
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


@pytest.mark.parametrize(
    ("router_path", "path", "methods"),
    [
        ("agricola.analises_solo.router", "/analises-solo/", {"GET"}),
        ("agricola.analises_solo.router", "/analises-solo/{id}", {"GET"}),
        ("agricola.analises_solo.router", "/analises-solo/", {"POST"}),
        ("agricola.analises_solo.router", "/analises-solo/{id}", {"PATCH"}),
        ("agricola.analises_solo.router", "/analises-solo/{id}", {"DELETE"}),
        ("agricola.dashboard.router", "/agricola/dashboard/", {"GET"}),
    ],
)
async def test_p1_nao_bloqueia_endpoints_operacionais_a1(router_path, path, methods):
    module = __import__(router_path, fromlist=["router"])
    route = _route(module.router, path, methods)

    assert _tier_dependencies(route) == []
