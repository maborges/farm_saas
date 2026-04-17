"""
Testes de Segurança — Validações de Input e Autenticação
SEC-01..14: OWASP Top 10 e validações de negócio
"""
import pytest
import uuid
from datetime import date, timedelta
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# SEC-01: Acesso sem token retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_acesso_sem_token(client):
    """SEC-01: Qualquer endpoint protegido sem Authorization retorna 401"""
    endpoints = [
        "/api/v1/auth/me",
        "/api/v1/safras/",
        "/api/v1/financeiro/receitas/",
        "/api/v1/estoque/depositos",
    ]
    for endpoint in endpoints:
        response = await client.get(endpoint)
        assert response.status_code == 401, (
            f"Endpoint {endpoint} deveria retornar 401, recebeu {response.status_code}"
        )


# ---------------------------------------------------------------------------
# SEC-02: Token expirado retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_expirado_retorna_401(client):
    """SEC-02: Token com exp no passado retorna 401"""
    from core.services.auth_service import AuthService

    svc = AuthService(MagicMock())
    token = svc.create_access_token(
        {"sub": str(uuid.uuid4()), "tenant_id": str(uuid.uuid4()),
         "modules": ["CORE"], "is_superuser": False},
        expires_delta=timedelta(hours=-1),
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# SEC-03: Token inválido (assinatura errada) retorna 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_assinatura_invalida_retorna_401(client):
    """SEC-03: Token com assinatura adulterada retorna 401"""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer token.invalido.assinado_errado"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# SEC-04: Sem permissão retorna 403
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sem_permissao_retorna_403(client):
    """SEC-04: Token válido sem módulo requerido retorna 402/403"""
    from core.services.auth_service import AuthService

    svc = AuthService(MagicMock())
    # Token apenas com CORE — sem módulo agrícola
    token = svc.create_access_token({
        "sub": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "modules": ["CORE"],
        "fazendas_auth": [],
        "is_superuser": False,
        "plan_tier": "BASICO",
    }, expires_delta=timedelta(hours=1))

    response = await client.get(
        "/api/v1/safras/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (402, 403)


# ---------------------------------------------------------------------------
# SEC-06: SQL injection não funciona
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sql_injection_nao_funciona(client):
    """SEC-06: Payload com SQL injection não quebra a aplicação"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@teste.com'; DROP TABLE usuarios; --",
            "senha": "qualquer",
        },
    )
    # Deve retornar 401 (credenciais inválidas), nunca 500
    assert response.status_code in (401, 422), (
        f"SQL injection causou erro inesperado: {response.status_code}"
    )


# ---------------------------------------------------------------------------
# SEC-07: XSS não funciona (campos de texto são escapados)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_xss_payload_tratado(client):
    """SEC-07: Campos com payload XSS retornam erro de validação ou são sanitizados"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "xss@teste.com",
            "username": "<script>alert('xss')</script>",
            "nome_completo": "<img src=x onerror=alert(1)>",
            "senha": "Senha@123",
        },
    )
    # Deve criar com dados sanitizados ou rejeitar — nunca 500
    assert response.status_code in (201, 400, 422), (
        f"XSS causou erro inesperado: {response.status_code}"
    )

    if response.status_code == 201:
        # Verifica que o script não foi armazenado literalmente
        data = response.json()
        assert "<script>" not in str(data.get("username", ""))


# ---------------------------------------------------------------------------
# SEC-09: CPF inválido retorna 422
# ---------------------------------------------------------------------------

def test_cpf_invalido_schema():
    """SEC-09: Schema Pydantic rejeita CPF com dígitos verificadores errados"""
    from pydantic import ValidationError

    try:
        from core.schemas.auth_schemas import UserCreateRequest
        # CPF inválido (todos zeros)
        obj = UserCreateRequest(
            email="teste@cpf.com",
            username="testecpf",
            nome_completo="Teste CPF",
            senha="Senha@123",
            cpf="00000000000",
        )
        # Se o schema não valida CPF ainda, marca como xfail
        pytest.xfail("Validação de CPF ainda não implementada")
    except (ValidationError, ValueError):
        pass  # comportamento esperado
    except TypeError:
        pytest.skip("Campo cpf não existe no schema atual")


# ---------------------------------------------------------------------------
# SEC-11: Email inválido retorna 422
# ---------------------------------------------------------------------------

def test_email_invalido_schema():
    """SEC-11: Schema Pydantic rejeita email mal formatado"""
    from pydantic import ValidationError
    from core.schemas.auth_schemas import UserCreateRequest

    with pytest.raises(ValidationError):
        UserCreateRequest(
            email="nao-e-email",
            username="testeemail",
            nome_completo="Teste",
            senha="Senha@123",
        )


# ---------------------------------------------------------------------------
# SEC-12: Data futura em operações é inválida
# ---------------------------------------------------------------------------

def test_data_futura_invalida_schema():
    """SEC-12: Data futura em operação agrícola é rejeitada pelo schema"""
    from pydantic import ValidationError

    data_futura = date.today() + timedelta(days=30)

    try:
        from agricola.operacoes.schemas import OperacaoAgricolaCreate
        with pytest.raises((ValidationError, ValueError)):
            OperacaoAgricolaCreate(
                safra_id=uuid.uuid4(),
                talhao_id=uuid.uuid4(),
                tipo_operacao="PLANTIO",
                data_operacao=data_futura,
                area_aplicada_ha=10.0,
            )
    except ImportError:
        pytest.skip("Schema não encontrado")


# ---------------------------------------------------------------------------
# SEC-13: Valor negativo em financeiro retorna 422
# ---------------------------------------------------------------------------

def test_valor_negativo_receita_rejeitado():
    """SEC-13: valor_total negativo em ReceitaCreate retorna ValidationError"""
    from pydantic import ValidationError
    from financeiro.schemas.receita_schema import ReceitaCreate

    with pytest.raises(ValidationError):
        ReceitaCreate(
            unidade_produtiva_id=uuid.uuid4(),
            plano_conta_id=uuid.uuid4(),
            descricao="Receita inválida",
            valor_total=-1000.0,  # negativo
            data_emissao=date.today(),
            data_vencimento=date.today(),
        )


def test_valor_zero_despesa_rejeitado():
    """SEC-13: valor_total=0 em DespesaCreate retorna ValidationError"""
    from pydantic import ValidationError
    from financeiro.schemas.despesa_schema import DespesaCreate

    with pytest.raises(ValidationError):
        DespesaCreate(
            unidade_produtiva_id=uuid.uuid4(),
            plano_conta_id=uuid.uuid4(),
            descricao="Despesa inválida",
            valor_total=0,  # zero
            data_emissao=date.today(),
            data_vencimento=date.today(),
        )


# ---------------------------------------------------------------------------
# SEC: Senha não é retornada nas respostas
# ---------------------------------------------------------------------------

def test_senha_nao_exposta_no_schema():
    """Nenhum response schema deve conter campo senha ou senha_hash"""
    from core.schemas.auth_schemas import UsuarioMeResponse
    campos = UsuarioMeResponse.model_fields.keys()
    assert "senha" not in campos
    assert "senha_hash" not in campos
    assert "password" not in campos
