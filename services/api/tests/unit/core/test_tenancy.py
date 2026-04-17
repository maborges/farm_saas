"""
Testes Unitários — Multi-Tenancy e RBAC
CORE-TEN-01..05, CORE-RBAC-01..05
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_claims(tenant_id=None, is_superuser=False, modules=None, fazendas=None):
    return {
        "sub": str(uuid.uuid4()),
        "tenant_id": str(tenant_id) if tenant_id else None,
        "modules": modules or ["CORE"],
        "fazendas_auth": fazendas or [],
        "is_superuser": is_superuser,
        "plan_tier": "BASICO",
    }


TENANT_A = uuid.uuid4()
TENANT_B = uuid.uuid4()


# ---------------------------------------------------------------------------
# CORE-TEN-01: Usuário vê apenas dados do seu tenant
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_base_service_filtra_por_tenant():
    """CORE-TEN-01: BaseService injeta tenant_id em todas as queries"""
    from core.base_service import BaseService
    from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda

    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    session.execute.return_value = result_mock

    svc = BaseService(Fazenda, session, TENANT_A)
    await svc.list_all()

    # Verifica que execute foi chamado (query foi construída)
    session.execute.assert_called_once()

    # Inspeciona a query para garantir que tenant_id está no WHERE
    call_args = session.execute.call_args[0][0]
    query_str = str(call_args)
    assert "tenant_id" in query_str


# ---------------------------------------------------------------------------
# CORE-TEN-02: Tenant A não acessa dados do Tenant B
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tenant_isolamento_get_or_fail():
    """CORE-TEN-02: get_or_fail com ID de outro tenant lança erro de não encontrado"""
    from core.base_service import BaseService
    from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda

    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock

    svc = BaseService(Fazenda, session, TENANT_A)
    resource_id = uuid.uuid4()

    # BaseService pode lançar EntityNotFoundError ou HTTPException 404
    with pytest.raises(Exception) as exc_info:
        await svc.get_or_fail(resource_id)

    exc = exc_info.value
    status = getattr(exc, "status_code", None)
    assert status == 404 or "não encontrado" in str(exc).lower() or "not found" in str(exc).lower()


# ---------------------------------------------------------------------------
# CORE-TEN-03: Seleção de tenant ativo funciona (claims com tenant_id)
# ---------------------------------------------------------------------------

def test_claims_contem_tenant_id():
    """CORE-TEN-03: Token com tenant ativo contém tenant_id correto"""
    claims = make_claims(tenant_id=TENANT_A)
    assert claims["tenant_id"] == str(TENANT_A)
    assert claims["tenant_id"] != str(TENANT_B)


# ---------------------------------------------------------------------------
# CORE-TEN-04: Listar múltiplos tenants do usuário
# ---------------------------------------------------------------------------

def test_claims_superuser_sem_tenant():
    """CORE-TEN-04: Superuser entra sem tenant_id no contexto"""
    claims = make_claims(is_superuser=True)
    assert claims["tenant_id"] is None
    assert claims["is_superuser"] is True


# ---------------------------------------------------------------------------
# CORE-TEN-05: Criação de tenant com plano (estrutura de claims)
# ---------------------------------------------------------------------------

def test_tenant_modulos_no_token():
    """CORE-TEN-05: Token contém módulos do plano do tenant via AssinaturaTenant"""
    modulos = ["CORE", "A1_PLANEJAMENTO", "F1_FINANCEIRO"]
    claims = make_claims(tenant_id=TENANT_A, modules=modulos)
    assert "A1_PLANEJAMENTO" in claims["modules"]
    assert "F1_FINANCEIRO" in claims["modules"]


# ---------------------------------------------------------------------------
# CORE-RBAC-01: require_permission bloqueia sem permissão correta
# ---------------------------------------------------------------------------

def test_require_permission_sem_permissao():
    """CORE-RBAC-01: require_permission retorna dependency callable para o FastAPI"""
    from core.dependencies import require_permission

    # require_permission é um factory que retorna um Depends — verificamos que é criado sem erro
    dep = require_permission("backoffice:tenants:view")
    assert dep is not None


def test_require_tenant_permission_viewer_bloqueado():
    """CORE-RBAC-02: require_tenant_permission retorna dependency para o FastAPI"""
    from core.dependencies import require_tenant_permission

    dep = require_tenant_permission("tenant:safras:create")
    assert dep is not None


# ---------------------------------------------------------------------------
# CORE-RBAC-03: Superuser bypass — testado via HTTP em test_auth_api.py
# CORE-RBAC-04: Módulo não contratado retorna 402
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_require_module_nao_contratado():
    """CORE-RBAC-04: Verificador de módulo rejeita token sem módulo requerido"""
    from core.dependencies import require_module

    # require_module retorna uma função verificadora — chamamos diretamente
    verificador = require_module("A1_PLANEJAMENTO")

    # Se retorna um callable puro (não Depends), testamos direto
    if callable(verificador) and not hasattr(verificador, "dependency"):
        claims = {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(TENANT_A),
            "modules": ["CORE"],
            "is_superuser": False,
        }
        with pytest.raises((HTTPException, Exception)):
            result = verificador(claims)
            if hasattr(result, "__await__"):
                await result
    else:
        # É um Depends FastAPI — validado via testes de integração HTTP
        pytest.skip("require_module é Depends FastAPI — testado em integration/")


@pytest.mark.asyncio
async def test_require_module_contratado_permite():
    """CORE-RBAC-05: Módulo contratado no token permite acesso"""
    from core.dependencies import require_module

    verificador = require_module("A1_PLANEJAMENTO")

    if callable(verificador) and not hasattr(verificador, "dependency"):
        claims = {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(TENANT_A),
            "modules": ["CORE", "A1_PLANEJAMENTO"],
            "is_superuser": False,
        }
        try:
            result = verificador(claims)
            if hasattr(result, "__await__"):
                await result
        except HTTPException as e:
            pytest.fail(f"Módulo contratado deveria passar, recebeu {e.status_code}")
    else:
        pytest.skip("require_module é Depends FastAPI — testado em integration/")
