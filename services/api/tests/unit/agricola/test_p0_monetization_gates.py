import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute
from unittest.mock import AsyncMock

from core.constants import PlanTier


pytestmark = pytest.mark.asyncio(loop_scope="function")


def _tier_dependencies(router):
    dependencies = []
    for route in router.routes:
        if isinstance(route, APIRoute):
            dependencies.extend(
                dep.call
                for dep in route.dependant.dependencies
                if getattr(dep.call, "__name__", "") == "_dependency"
                and dep.call.__closure__
                and any(cell.cell_contents == PlanTier.PROFISSIONAL for cell in dep.call.__closure__)
            )
    return dependencies


def _module_dependencies(router, module_id: str):
    dependencies = []
    for route in router.routes:
        if isinstance(route, APIRoute):
            dependencies.extend(
                dep.call
                for dep in route.dependant.dependencies
                if getattr(dep.call, "__name__", "") == "_dependency"
                and dep.call.__closure__
                and any(cell.cell_contents == module_id for cell in dep.call.__closure__)
            )
    return dependencies


@pytest.mark.parametrize(
    ("router_path", "module_id"),
    [
        ("agricola.templates.router", "A1_PLANEJAMENTO"),
        ("agricola.amostragem_solo.routers.amostras", "A4_PRECISAO"),
        ("agricola.amostragem_solo.routers.mapas_fertilidade", "A4_PRECISAO"),
        ("agricola.amostragem_solo.routers.prescricoes_vra", "A4_PRECISAO"),
        ("agricola.ndvi_avancado.routers.ndvi", "A4_PRECISAO"),
        ("agricola.ndvi_avancado.routers.irrigacao", "A4_PRECISAO"),
        ("agricola.ndvi_avancado.routers.meteorologia", "A4_PRECISAO"),
    ],
)
async def test_p0_routers_exigem_modulo_e_tier_profissional(router_path, module_id):
    module = __import__(router_path, fromlist=["router"])
    dependencies = _tier_dependencies(module.router)
    module_dependencies = _module_dependencies(module.router, module_id)

    api_routes = [route for route in module.router.routes if isinstance(route, APIRoute)]
    assert api_routes
    assert len(dependencies) == len(api_routes)
    assert len(module_dependencies) == len(api_routes)

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
