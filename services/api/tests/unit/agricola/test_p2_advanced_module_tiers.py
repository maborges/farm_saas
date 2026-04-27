import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute
from unittest.mock import AsyncMock

from core.constants import PlanTier


pytestmark = pytest.mark.asyncio(loop_scope="function")


def _route(router, path: str, methods: set[str]) -> APIRoute:
    expected_path = f"{router.prefix}{path}"
    for route in router.routes:
        if isinstance(route, APIRoute) and route.path == expected_path and route.methods == methods:
            return route
    raise AssertionError(f"Rota não encontrada: {methods} {expected_path}")


def _dependencies(route: APIRoute):
    return [
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__closure__", None)
    ]


def _has_dependency(route: APIRoute, value) -> bool:
    for dep in _dependencies(route):
        if any(cell.cell_contents == value for cell in dep.__closure__):
            return True
    return False


def _tier_dependency(route: APIRoute, tier: PlanTier):
    for dep in _dependencies(route):
        if any(cell.cell_contents == tier for cell in dep.__closure__):
            return dep
    raise AssertionError(f"Dependência de tier não encontrada: {tier}")


@pytest.mark.parametrize(
    ("router_path", "path", "methods", "module_id", "minimum_tier"),
    [
        ("agricola.agronomo.router", "/chat", {"POST"}, "A2_CAMPO", PlanTier.PROFISSIONAL),
        ("agricola.agronomo.router", "/conversas", {"GET"}, "A2_CAMPO", PlanTier.PROFISSIONAL),
        ("agricola.agronomo.router", "/rat", {"GET"}, "A2_CAMPO", PlanTier.PROFISSIONAL),
        ("agricola.agronomo.router", "/rat", {"POST"}, "A2_CAMPO", PlanTier.PROFISSIONAL),
        ("ia_diagnostico.routers.pragas_doencas", "/", {"GET"}, "EXT_IA", PlanTier.PROFISSIONAL),
        ("ia_diagnostico.routers.tratamentos", "/", {"GET"}, "EXT_IA", PlanTier.PROFISSIONAL),
        ("ia_diagnostico.routers.diagnosticos", "/", {"GET"}, "EXT_IA", PlanTier.PROFISSIONAL),
        ("agricola.beneficiamento.router", "/", {"GET"}, "A5_COLHEITA", PlanTier.PROFISSIONAL),
        ("agricola.beneficiamento.router", "/kpis", {"GET"}, "A5_COLHEITA", PlanTier.PROFISSIONAL),
        ("agricola.rastreabilidade.router", "/lotes", {"GET"}, "A5_COLHEITA", PlanTier.ENTERPRISE),
        ("agricola.rastreabilidade.router", "/lotes", {"POST"}, "A5_COLHEITA", PlanTier.ENTERPRISE),
        ("agricola.rastreabilidade.router", "/lotes/{lote_id}/cadeia", {"GET"}, "A5_COLHEITA", PlanTier.ENTERPRISE),
        ("agricola.amostragem_solo.routers.prescricoes_vra", "/", {"GET"}, "A4_PRECISAO", PlanTier.ENTERPRISE),
        ("agricola.amostragem_solo.routers.prescricoes_vra", "/", {"POST"}, "A4_PRECISAO", PlanTier.ENTERPRISE),
    ],
)
async def test_p2_advanced_endpoints_exigem_tier_e_modulo(router_path, path, methods, module_id, minimum_tier):
    module = __import__(router_path, fromlist=["router"])
    route = _route(module.router, path, methods)

    assert _has_dependency(route, module_id)
    tier_dep = _tier_dependency(route, minimum_tier)

    with pytest.raises(HTTPException) as exc:
        await tier_dep(
            request=None,
            claims={
                "tenant_id": "aaaaaaaa-0000-0000-0000-000000000010",
                "plan_tier": "BASICO",
            },
            session=AsyncMock(),
        )

    assert exc.value.status_code == 402
    assert exc.value.headers["X-Tier-Required"] == minimum_tier.value
    assert exc.value.headers["X-Tier-Current"] == "BASICO"


@pytest.mark.parametrize(
    ("router_path", "path", "methods"),
    [
        ("agricola.caderno.router", "/timeline", {"GET"}),
        ("agricola.caderno.router", "/entradas", {"POST"}),
        ("agricola.caderno.router", "/visitas", {"POST"}),
    ],
)
async def test_p2_caderno_basico_nao_exige_tier_premium(router_path, path, methods):
    module = __import__(router_path, fromlist=["router"])
    route = _route(module.router, path, methods)

    assert not _has_dependency(route, PlanTier.ENTERPRISE)


@pytest.mark.parametrize(
    ("router_path", "path", "methods"),
    [
        ("agricola.caderno.router", "/exportar", {"POST"}),
        ("agricola.caderno.router", "/exportacoes", {"GET"}),
        ("agricola.caderno.router", "/exportacoes/{exportacao_id}/download", {"GET"}),
        ("agricola.caderno.router", "/exportacoes/{exportacao_id}/assinar", {"POST"}),
        ("agricola.caderno.router", "/exportacoes/assinar-ultima", {"POST"}),
    ],
)
async def test_p2_caderno_exportacao_exige_premium(router_path, path, methods):
    module = __import__(router_path, fromlist=["router"])
    route = _route(module.router, path, methods)
    tier_dep = _tier_dependency(route, PlanTier.ENTERPRISE)

    with pytest.raises(HTTPException) as exc:
        await tier_dep(
            request=None,
            claims={
                "tenant_id": "aaaaaaaa-0000-0000-0000-000000000010",
                "plan_tier": "PROFISSIONAL",
            },
            session=AsyncMock(),
        )

    assert exc.value.status_code == 402
    assert exc.value.headers["X-Tier-Required"] == "ENTERPRISE"
    assert exc.value.headers["X-Tier-Current"] == "PROFISSIONAL"
