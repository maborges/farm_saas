"""
Testes Unitários de Segurança — Validação de Input (sem HTTP)
SEC-09, SEC-11, SEC-12, SEC-13: Pydantic schemas rejeitam dados inválidos
"""
import pytest
import uuid
from datetime import date, timedelta
from pydantic import ValidationError


# ---------------------------------------------------------------------------
# SEC-11: Email inválido retorna 422
# ---------------------------------------------------------------------------

def test_email_invalido_schema():
    """SEC-11: Schema rejeita email mal formatado"""
    from core.schemas.auth_schemas import UserCreateRequest

    with pytest.raises(ValidationError):
        UserCreateRequest(
            email="nao-e-email",
            username="testeemail",
            nome_completo="Teste",
            senha="Senha@123",
        )


def test_email_sem_dominio_rejeitado():
    """SEC-11: Email sem domínio é inválido"""
    from core.schemas.auth_schemas import UserCreateRequest

    with pytest.raises(ValidationError):
        UserCreateRequest(
            email="usuario@",
            username="testeemail2",
            nome_completo="Teste",
            senha="Senha@123",
        )


# ---------------------------------------------------------------------------
# SEC-12: Data futura em operações é inválida
# ---------------------------------------------------------------------------

def test_data_futura_operacao_agricola():
    """SEC-12: Data futura em operação agrícola é rejeitada"""
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
# SEC-13: Valores negativos/zero em financeiro
# ---------------------------------------------------------------------------

def test_valor_negativo_receita_rejeitado():
    """SEC-13: valor_total negativo em ReceitaCreate retorna ValidationError"""
    from financeiro.schemas.receita_schema import ReceitaCreate

    with pytest.raises(ValidationError):
        ReceitaCreate(
            fazenda_id=uuid.uuid4(),
            plano_conta_id=uuid.uuid4(),
            descricao="Receita inválida",
            valor_total=-1000.0,
            data_emissao=date.today(),
            data_vencimento=date.today(),
        )


def test_valor_zero_despesa_rejeitado():
    """SEC-13: valor_total=0 em DespesaCreate retorna ValidationError"""
    from financeiro.schemas.despesa_schema import DespesaCreate

    with pytest.raises(ValidationError):
        DespesaCreate(
            fazenda_id=uuid.uuid4(),
            plano_conta_id=uuid.uuid4(),
            descricao="Despesa inválida",
            valor_total=0,
            data_emissao=date.today(),
            data_vencimento=date.today(),
        )


def test_valor_negativo_despesa_rejeitado():
    """SEC-13: valor_total negativo em DespesaCreate retorna ValidationError"""
    from financeiro.schemas.despesa_schema import DespesaCreate

    with pytest.raises(ValidationError):
        DespesaCreate(
            fazenda_id=uuid.uuid4(),
            plano_conta_id=uuid.uuid4(),
            descricao="Despesa negativa",
            valor_total=-500.0,
            data_emissao=date.today(),
            data_vencimento=date.today(),
        )


# ---------------------------------------------------------------------------
# SEC: Senha não é exposta nos response schemas
# ---------------------------------------------------------------------------

def test_senha_nao_exposta_response():
    """Nenhum response schema deve conter campo senha ou senha_hash"""
    from core.schemas.auth_schemas import UsuarioMeResponse

    campos = set(UsuarioMeResponse.model_fields.keys())
    assert "senha" not in campos
    assert "senha_hash" not in campos
    assert "password" not in campos
    assert "secret" not in campos


# ---------------------------------------------------------------------------
# SEC: Quantidade negativa em lote bovino rejeitada
# ---------------------------------------------------------------------------

def test_quantidade_negativa_lote_bovino():
    """SEC-13: quantidade_cabecas <= 0 em LoteBovinoCreate é inválido"""
    from pecuaria.schemas.lote_schema import LoteBovinoCreate

    with pytest.raises(ValidationError):
        LoteBovinoCreate(
            fazenda_id=uuid.uuid4(),
            identificacao="Lote X",
            categoria="Novilhas",
            raca="Nelore",
            quantidade_cabecas=0,   # inválido
            peso_medio_kg=200.0,
        )


# ---------------------------------------------------------------------------
# SEC: Parcelamento fora do range rejeitado
# ---------------------------------------------------------------------------

def test_parcelas_acima_limite_rejeitado():
    """total_parcelas > 360 é inválido (limite máximo)"""
    from financeiro.schemas.receita_schema import ReceitaCreate

    with pytest.raises(ValidationError):
        ReceitaCreate(
            fazenda_id=uuid.uuid4(),
            plano_conta_id=uuid.uuid4(),
            descricao="Parcelamento absurdo",
            valor_total=1000.0,
            data_emissao=date.today(),
            data_vencimento=date.today(),
            total_parcelas=999,  # acima do limite de 360
        )
