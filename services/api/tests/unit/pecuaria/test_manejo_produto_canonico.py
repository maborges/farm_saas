"""Testes unitários — campo produto_id em ManejoLote (Step 83)."""
import uuid
import pytest
from pecuaria.schemas.manejo_schema import ManejoLoteCreate, ManejoLoteResponse


def test_manejo_create_aceita_produto_id():
    payload = ManejoLoteCreate(
        lote_id=uuid.uuid4(),
        tipo_evento="VACINACAO",
        produto_id=uuid.uuid4(),
    )
    assert payload.produto_id is not None


def test_manejo_create_produto_id_opcional():
    payload = ManejoLoteCreate(
        lote_id=uuid.uuid4(),
        tipo_evento="PESAGEM",
    )
    assert payload.produto_id is None


def test_manejo_create_medicacao_com_produto():
    pid = uuid.uuid4()
    payload = ManejoLoteCreate(
        lote_id=uuid.uuid4(),
        tipo_evento="MEDICACAO",
        produto_id=pid,
        custo_total=150.0,
    )
    assert payload.produto_id == pid
    assert payload.custo_total == 150.0


def test_manejo_response_tem_produto_id():
    assert "produto_id" in ManejoLoteResponse.model_fields


def test_manejo_response_produto_id_opcional():
    field = ManejoLoteResponse.model_fields["produto_id"]
    assert field.is_required() is False


def test_manejo_create_pesagem_sem_produto():
    payload = ManejoLoteCreate(
        lote_id=uuid.uuid4(),
        tipo_evento="PESAGEM",
        peso_total_kg=5000.0,
        quantidade_cabecas=50,
    )
    assert payload.produto_id is None
