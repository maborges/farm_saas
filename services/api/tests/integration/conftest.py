"""
Fixtures compartilhadas para testes de integração (HTTP)
Gera tokens JWT e cliente HTTP para todos os módulos.
"""
import sys
import uuid
import pytest
from pathlib import Path
from datetime import timedelta
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.auth_service import AuthService
from unittest.mock import MagicMock


# IDs fixos para facilitar rastreabilidade nos testes
TENANT_ID = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
FAZENDA_ID = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000002")
TALHAO_ID = uuid.UUID("cccccccc-0000-0000-0000-000000000003")
PRODUTO_ID = uuid.UUID("dddddddd-0000-0000-0000-000000000004")
USER_ID    = uuid.UUID("eeeeeeee-0000-0000-0000-000000000005")


def _gerar_token(tenant_id: uuid.UUID, modules: list[str], role: str = "admin") -> str:
    svc = AuthService(MagicMock())
    claims = {
        "sub": str(USER_ID),
        "tenant_id": str(tenant_id),
        "modules": modules,
        "fazendas_auth": [{"id": str(FAZENDA_ID), "role": role}],
        "is_superuser": False,
        "plan_tier": "PROFISSIONAL",
    }
    return svc.create_access_token(claims, expires_delta=timedelta(hours=1))


@pytest.fixture(scope="module")
def token_agricola():
    return _gerar_token(TENANT_ID, ["CORE", "A1", "A1_PLANEJAMENTO"])


@pytest.fixture(scope="module")
def token_financeiro():
    return _gerar_token(TENANT_ID, ["CORE", "F1", "F1_FINANCEIRO"])


@pytest.fixture(scope="module")
def token_operacional():
    return _gerar_token(TENANT_ID, ["CORE", "O1", "O2", "O3"])


@pytest.fixture(scope="module")
def token_admin():
    return _gerar_token(TENANT_ID, [
        "CORE", "A1", "A1_PLANEJAMENTO", "F1", "F1_FINANCEIRO",
        "O1", "O2", "O3", "P1", "RH1",
    ])


@pytest.fixture
async def client():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
def headers_agricola(token_agricola):
    return {"Authorization": f"Bearer {token_agricola}",
            "X-Tenant-ID": str(TENANT_ID),
            "X-Fazenda-ID": str(FAZENDA_ID)}


@pytest.fixture
def headers_financeiro(token_financeiro):
    return {"Authorization": f"Bearer {token_financeiro}",
            "X-Tenant-ID": str(TENANT_ID),
            "X-Fazenda-ID": str(FAZENDA_ID)}


@pytest.fixture
def headers_operacional(token_operacional):
    return {"Authorization": f"Bearer {token_operacional}",
            "X-Tenant-ID": str(TENANT_ID),
            "X-Fazenda-ID": str(FAZENDA_ID)}


@pytest.fixture
def headers_admin(token_admin):
    return {"Authorization": f"Bearer {token_admin}",
            "X-Tenant-ID": str(TENANT_ID)}
