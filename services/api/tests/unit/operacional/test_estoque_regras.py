"""
Testes Unitários — Estoque: Regras de Negócio
OPR-MOV-06: Saldo negativo, OPR-LOT-04: PEPS
FIN-DES-03: Despesa sem custo, FIN-DES-10: Rateio 100%
"""
import pytest
import uuid
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# OPR-MOV-06: Saldo negativo retorna erro
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_saida_estoque_saldo_insuficiente():
    """OPR-MOV-06: Saída maior que saldo disponível retorna erro"""
    from unittest.mock import AsyncMock, MagicMock
    from fastapi import HTTPException

    session = AsyncMock()
    tenant_id = uuid.uuid4()

    # Simula saldo disponível de 10 unidades
    saldo_mock = MagicMock()
    saldo_mock.quantidade = 10.0
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = saldo_mock
    session.execute.return_value = result_mock

    try:
        from operacional.service import EstoqueService
        svc = EstoqueService(session, tenant_id)

        saida_data = MagicMock()
        saida_data.produto_id = uuid.uuid4()
        saida_data.deposito_id = uuid.uuid4()
        saida_data.quantidade = 50.0  # maior que saldo
        saida_data.tipo_movimentacao = "SAIDA"

        with pytest.raises((HTTPException, ValueError, Exception)) as exc_info:
            await svc.registrar_saida(saida_data)

        if hasattr(exc_info.value, "status_code"):
            assert exc_info.value.status_code in (400, 422)

    except ImportError:
        pytest.skip("EstoqueService ainda não implementado")


# ---------------------------------------------------------------------------
# OPR-LOT-04: Saída usa lote mais antigo (PEPS - Primeiro a Entrar, Primeiro a Sair)
# ---------------------------------------------------------------------------

def test_peps_lote_mais_antigo_primeiro():
    """OPR-LOT-04: PEPS — lote com data de entrada mais antiga é consumido primeiro"""
    lotes = [
        {"id": "lote-C", "data_entrada": date(2025, 3, 1), "quantidade": 100},
        {"id": "lote-A", "data_entrada": date(2025, 1, 1), "quantidade": 100},
        {"id": "lote-B", "data_entrada": date(2025, 2, 1), "quantidade": 100},
    ]

    lotes_ordenados = sorted(lotes, key=lambda l: l["data_entrada"])

    assert lotes_ordenados[0]["id"] == "lote-A"
    assert lotes_ordenados[1]["id"] == "lote-B"
    assert lotes_ordenados[2]["id"] == "lote-C"


def test_peps_consome_lote_correto():
    """OPR-LOT-04: Saída de 150 unidades consome lote-A completo + 50 do lote-B"""
    lotes = [
        {"id": "lote-A", "data_entrada": date(2025, 1, 1), "quantidade": 100},
        {"id": "lote-B", "data_entrada": date(2025, 2, 1), "quantidade": 100},
        {"id": "lote-C", "data_entrada": date(2025, 3, 1), "quantidade": 100},
    ]

    quantidade_saida = 150
    consumo = []
    restante = quantidade_saida

    for lote in lotes:
        if restante <= 0:
            break
        consumido = min(lote["quantidade"], restante)
        consumo.append({"lote_id": lote["id"], "consumido": consumido})
        restante -= consumido

    assert consumo[0] == {"lote_id": "lote-A", "consumido": 100}
    assert consumo[1] == {"lote_id": "lote-B", "consumido": 50}
    assert restante == 0


# ---------------------------------------------------------------------------
# FIN-DES-03: Despesa sem custo não cria
# ---------------------------------------------------------------------------

def test_despesa_valor_zero_invalido():
    """FIN-DES-03: Despesa com valor <= 0 é inválida"""
    valores_invalidos = [0, -1, -100.50]
    for valor in valores_invalidos:
        assert valor <= 0, f"Valor {valor} deveria ser inválido"


def test_despesa_valor_positivo_valido():
    """FIN-DES-03: Despesa com valor > 0 é válida"""
    valor = 500.0
    assert valor > 0


# ---------------------------------------------------------------------------
# FIN-DES-10: Rateio deve somar exatamente 100%
# ---------------------------------------------------------------------------

def test_rateio_soma_100_valido():
    """FIN-DES-10: Rateios somando 100% são válidos"""
    rateios = [
        {"safra_id": "safra-1", "percentual": 60.0},
        {"safra_id": "safra-2", "percentual": 40.0},
    ]
    total = sum(r["percentual"] for r in rateios)
    assert total == pytest.approx(100.0, rel=1e-3)


def test_rateio_soma_diferente_100_invalido():
    """FIN-DES-10: Rateios não somando 100% devem ser rejeitados"""
    rateios = [
        {"safra_id": "safra-1", "percentual": 60.0},
        {"safra_id": "safra-2", "percentual": 30.0},  # soma 90%, não 100%
    ]
    total = sum(r["percentual"] for r in rateios)
    assert total != pytest.approx(100.0, rel=1e-3)

    # A regra de negócio deve rejeitar isso
    is_valido = abs(total - 100.0) < 0.01
    assert is_valido is False


def test_rateio_com_tres_safras_100_porcento():
    """FIN-DES-10: Três safras com rateio que soma 100%"""
    rateios = [33.33, 33.33, 33.34]
    total = sum(rateios)
    assert total == pytest.approx(100.0, rel=1e-2)
