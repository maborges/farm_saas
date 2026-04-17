"""
FIN-COM-01 a FIN-COM-12: Testes unitários de ComercializacaoCommodity.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
import uuid

from financeiro.comercializacao.schemas import (
    ComercializacaoCreate, ComercializacaoUpdate,
    STATUS_VALIDOS,
)
from financeiro.comercializacao.router import TRANSICOES


# ===========================================================================
# FIN-COM-01 a FIN-COM-06: Validação de ComercializacaoCreate
# ===========================================================================

class TestComercializacaoCreate:
    """Validação do schema de criação de comercialização."""

    # FIN-COM-01: Criação válida mínima
    def test_minimo(self):
        c = ComercializacaoCreate(
            commodity_id=uuid.uuid4(),
            comprador_id=uuid.uuid4(),
            quantidade=100.0,
            unidade="SACA_60KG",
            preco_unitario=150.0,
        )
        assert c.quantidade == 100.0
        assert c.moeda == "BRL"

    # FIN-COM-02: Quantidade positiva obrigatória
    def test_quantidade_positiva(self):
        with pytest.raises(ValidationError):
            ComercializacaoCreate(
                commodity_id=uuid.uuid4(),
                comprador_id=uuid.uuid4(),
                quantidade=0,
                unidade="SACA_60KG",
                preco_unitario=150.0,
            )

    # FIN-COM-03: Quantidade negativa rejeitada
    def test_quantidade_negativa(self):
        with pytest.raises(ValidationError):
            ComercializacaoCreate(
                commodity_id=uuid.uuid4(),
                comprador_id=uuid.uuid4(),
                quantidade=-50.0,
                unidade="SACA_60KG",
                preco_unitario=150.0,
            )

    # FIN-COM-04: Preço unitário positivo obrigatório
    def test_preco_positivo(self):
        with pytest.raises(ValidationError):
            ComercializacaoCreate(
                commodity_id=uuid.uuid4(),
                comprador_id=uuid.uuid4(),
                quantidade=100.0,
                unidade="SACA_60KG",
                preco_unitario=0,
            )

    # FIN-COM-05: Preço negativo rejeitado
    def test_preco_negativo(self):
        with pytest.raises(ValidationError):
            ComercializacaoCreate(
                commodity_id=uuid.uuid4(),
                comprador_id=uuid.uuid4(),
                quantidade=100.0,
                unidade="SACA_60KG",
                preco_unitario=-10.0,
            )

    # FIN-COM-06: Campos opcionais
    def test_campos_opcionais(self):
        c = ComercializacaoCreate(
            commodity_id=uuid.uuid4(),
            comprador_id=uuid.uuid4(),
            quantidade=500.0,
            unidade="SACA_60KG",
            preco_unitario=155.50,
            moeda="BRL",
            numero_contrato="CTR-2026-001",
            forma_pagamento="BOLETO",
            data_entrega_prevista=None,
            local_entrega="Armazém Central",
            frete_por_conta="COMPRADOR",
        )
        assert c.numero_contrato == "CTR-2026-001"
        assert c.forma_pagamento == "BOLETO"


# ===========================================================================
# FIN-COM-07 a FIN-COM-09: Validação de ComercializacaoUpdate
# ===========================================================================

class TestComercializacaoUpdate:
    """Validação do schema de atualização."""

    # FIN-COM-07: Partial update válido
    def test_partial_update(self):
        u = ComercializacaoUpdate(status="CONFIRMADO")
        assert u.status == "CONFIRMADO"
        assert u.preco_unitario is None

    # FIN-COM-08: Status inválido rejeitado
    @pytest.mark.parametrize("status_invalido", ["PAGO", "ENTREGA", "INVALIDO", ""])
    def test_status_invalido_rejeitado(self, status_invalido):
        with pytest.raises(ValidationError) as exc_info:
            ComercializacaoUpdate(status=status_invalido)
        assert "deve ser um de" in str(exc_info.value).lower()

    # FIN-COM-09: Status válido aceito
    @pytest.mark.parametrize("status_valido", sorted(STATUS_VALIDOS))
    def test_status_valido_aceito(self, status_valido):
        u = ComercializacaoUpdate(status=status_valido)
        assert u.status == status_valido


# ===========================================================================
# FIN-COM-10 a FIN-COM-12: Regras de transição de status
# ===========================================================================

class TestTransicoesStatus:
    """Testes das regras de transição de status."""

    # FIN-COM-10: Transições permitidas do RASCUNHO
    def test_transicoes_rascunho(self):
        permitidas = TRANSICOES["RASCUNHO"]
        assert "CONFIRMADO" in permitidas
        assert "CANCELADO" in permitidas
        assert "FINALIZADO" not in permitidas

    # FIN-COM-11: Transições permitidas do CONFIRMADO
    def test_transicoes_confirmado(self):
        permitidas = TRANSICOES["CONFIRMADO"]
        assert "EM_TRANSITO" in permitidas
        assert "CANCELADO" in permitidas
        assert "FINALIZADO" not in permitidas

    # FIN-COM-12: FINALIZADO e CANCELADO são terminais
    def test_estados_terminais(self):
        assert TRANSICOES["FINALIZADO"] == []
        assert TRANSICOES["CANCELADO"] == []
