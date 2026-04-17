"""
AGR-PC-01 a AGR-PC-10: Testes unitários de ProdutoColhido schemas.
"""
import pytest
from pydantic import ValidationError
from datetime import date
import uuid

from agricola.colheita.schemas import ProdutoColhidoCreate, ProdutoColhidoUpdate


# ===========================================================================
# AGR-PC-01 a AGR-PC-05: Validação de ProdutoColhidoCreate
# ===========================================================================

class TestProdutoColhidoCreate:
    """Validação do schema de criação de produto colhido."""

    # AGR-PC-01: Criação válida mínima
    def test_minimo(self):
        p = ProdutoColhidoCreate(
            safra_id=uuid.uuid4(),
            talhao_id=uuid.uuid4(),
            commodity_id=uuid.uuid4(),
            quantidade=100.0,
            unidade="SACA_60KG",
            peso_liquido_kg=6000.0,
            data_entrada=date(2026, 4, 12),
        )
        assert p.quantidade == 100.0
        assert p.status == "ARMAZENADO"

    # AGR-PC-02: Quantidade positiva obrigatória
    def test_quantidade_positiva(self):
        with pytest.raises(ValidationError):
            ProdutoColhidoCreate(
                safra_id=uuid.uuid4(),
                talhao_id=uuid.uuid4(),
                commodity_id=uuid.uuid4(),
                quantidade=0,
                unidade="SACA_60KG",
                peso_liquido_kg=6000.0,
                data_entrada=date(2026, 4, 12),
            )

    # AGR-PC-03: Quantidade negativa rejeitada
    def test_quantidade_negativa(self):
        with pytest.raises(ValidationError):
            ProdutoColhidoCreate(
                safra_id=uuid.uuid4(),
                talhao_id=uuid.uuid4(),
                commodity_id=uuid.uuid4(),
                quantidade=-10.0,
                unidade="SACA_60KG",
                peso_liquido_kg=6000.0,
                data_entrada=date(2026, 4, 12),
            )

    # AGR-PC-04: Peso líquido positivo obrigatório
    def test_peso_liquido_positivo(self):
        with pytest.raises(ValidationError):
            ProdutoColhidoCreate(
                safra_id=uuid.uuid4(),
                talhao_id=uuid.uuid4(),
                commodity_id=uuid.uuid4(),
                quantidade=100.0,
                unidade="SACA_60KG",
                peso_liquido_kg=0,
                data_entrada=date(2026, 4, 12),
            )

    # AGR-PC-05: Campos de qualidade opcionais
    def test_campos_qualidade(self):
        p = ProdutoColhidoCreate(
            safra_id=uuid.uuid4(),
            talhao_id=uuid.uuid4(),
            commodity_id=uuid.uuid4(),
            quantidade=500.0,
            unidade="SACA_60KG",
            peso_liquido_kg=30000.0,
            data_entrada=date(2026, 4, 12),
            umidade_pct=14.5,
            impureza_pct=1.2,
            avariados_pct=2.0,
            ardidos_pct=0.5,
            quebrados_pct=1.0,
        )
        assert p.umidade_pct == 14.5
        assert p.impureza_pct == 1.2


# ===========================================================================
# AGR-PC-06 a AGR-PC-10: ProdutoColhidoUpdate e regras
# ===========================================================================

class TestProdutoColhidoUpdate:
    """Validação do schema de atualização."""

    # AGR-PC-06: Partial update válido
    def test_partial_update(self):
        u = ProdutoColhidoUpdate(status="RESERVADO")
        assert u.status == "RESERVADO"
        assert u.armazem_id is None

    # AGR-PC-07: Update de múltiplos campos
    def test_multi_update(self):
        u = ProdutoColhidoUpdate(
            status="EM_TRANSITO",
            destino="TERCEIRO",
            data_saida_prevista=date(2026, 4, 20),
            observacoes="Enviado para beneficiamento",
        )
        assert u.status == "EM_TRANSITO"
        assert u.destino == "TERCEIRO"

    # AGR-PC-08: Status padrão é ARMAZENADO
    def test_status_padrao(self):
        p = ProdutoColhidoCreate(
            safra_id=uuid.uuid4(),
            talhao_id=uuid.uuid4(),
            commodity_id=uuid.uuid4(),
            quantidade=100.0,
            unidade="SACA_60KG",
            peso_liquido_kg=6000.0,
            data_entrada=date(2026, 4, 12),
        )
        assert p.status == "ARMAZENADO"

    # AGR-PC-09: Classificação opcional
    def test_classificacao_opcional(self):
        p = ProdutoColhidoCreate(
            safra_id=uuid.uuid4(),
            talhao_id=uuid.uuid4(),
            commodity_id=uuid.uuid4(),
            classificacao_id=uuid.uuid4(),
            quantidade=100.0,
            unidade="SACA_60KG",
            peso_liquido_kg=6000.0,
            data_entrada=date(2026, 4, 12),
        )
        assert p.classificacao_id is not None

    # AGR-PC-10: Romaneio opcional (entrada manual)
    def test_romaneio_opcional(self):
        p = ProdutoColhidoCreate(
            safra_id=uuid.uuid4(),
            talhao_id=uuid.uuid4(),
            commodity_id=uuid.uuid4(),
            romaneio_id=None,
            quantidade=100.0,
            unidade="SACA_60KG",
            peso_liquido_kg=6000.0,
            data_entrada=date(2026, 4, 12),
        )
        assert p.romaneio_id is None
