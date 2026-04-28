"""Testes unitários — campos canônicos de InsumoOperacao (Step 83)."""
import uuid
import pytest
from agricola.operacoes.schemas import InsumoOperacaoCreate, InsumoOperacaoResponse


def test_insumo_create_aceita_lote_estoque_id():
    payload = InsumoOperacaoCreate(
        produto_id=uuid.uuid4(),
        dose_por_ha=1.0,
        unidade="L",
        lote_estoque_id=uuid.uuid4(),
    )
    assert payload.lote_estoque_id is not None


def test_insumo_create_lote_estoque_id_opcional():
    payload = InsumoOperacaoCreate(
        produto_id=uuid.uuid4(),
        dose_por_ha=1.0,
        unidade="L",
    )
    assert payload.lote_estoque_id is None


def test_insumo_create_aceita_unidade_medida_id():
    uid = uuid.uuid4()
    payload = InsumoOperacaoCreate(
        produto_id=uuid.uuid4(),
        dose_por_ha=1.0,
        unidade="L",
        unidade_medida_id=uid,
    )
    assert payload.unidade_medida_id == uid


def test_insumo_create_unidade_medida_id_opcional():
    payload = InsumoOperacaoCreate(
        produto_id=uuid.uuid4(),
        dose_por_ha=1.0,
        unidade="L",
    )
    assert payload.unidade_medida_id is None


def test_insumo_response_tem_produto_id():
    assert "produto_id" in InsumoOperacaoResponse.model_fields


def test_insumo_create_tem_produto_id():
    pid = uuid.uuid4()
    payload = InsumoOperacaoCreate(produto_id=pid, dose_por_ha=1.0, unidade="L")
    assert payload.produto_id == pid


def test_insumo_response_tem_lote_estoque_id():
    assert "lote_estoque_id" in InsumoOperacaoResponse.model_fields


def test_insumo_response_tem_unidade_medida_id():
    assert "unidade_medida_id" in InsumoOperacaoResponse.model_fields
