"""
Testes unitários para lógica de NDE no MonitoramentoService.
Foco: detecção de NDE atingido baseada em nível de infestação vs. NDE.
"""
import pytest
import uuid
from decimal import Decimal

pytestmark = pytest.mark.asyncio


class TestNDEDetection:
    """Testa a lógica de cálculo do campo atingiu_nde."""

    def _atingiu_nde(self, nivel_infestacao, nde_cultura) -> bool:
        """Replica exatamente a lógica do service.criar()."""
        return bool(
            nde_cultura
            and nivel_infestacao
            and float(nivel_infestacao) >= float(nde_cultura)
        )

    def test_nivel_acima_do_nde_retorna_true(self):
        assert self._atingiu_nde(3.0, 2.0) is True

    def test_nivel_igual_ao_nde_retorna_true(self):
        assert self._atingiu_nde(2.0, 2.0) is True

    def test_nivel_abaixo_do_nde_retorna_false(self):
        assert self._atingiu_nde(1.5, 2.0) is False

    def test_sem_nivel_retorna_false(self):
        assert self._atingiu_nde(None, 2.0) is False

    def test_sem_nde_retorna_false(self):
        assert self._atingiu_nde(5.0, None) is False

    def test_ambos_none_retorna_false(self):
        assert self._atingiu_nde(None, None) is False

    def test_com_decimal_precision(self):
        """Garante que Decimal do banco não quebra a comparação."""
        assert self._atingiu_nde(Decimal("2.0001"), Decimal("2.0")) is True
        assert self._atingiu_nde(Decimal("1.9999"), Decimal("2.0")) is False


class TestCatalogoAutoFill:
    """Verifica que campos do catálogo são usados como fallback."""

    def _aplicar_catalogo(self, dados: dict, catalogo: dict) -> dict:
        """Replica a lógica de auto-fill do service.criar()."""
        resultado = dados.copy()
        resultado["nde_cultura"] = dados.get("nde_cultura") or catalogo.get("nde_padrao")
        resultado["nome_popular"] = dados.get("nome_popular") or catalogo.get("nome_popular")
        resultado["nome_cientifico"] = dados.get("nome_cientifico") or catalogo.get("nome_cientifico")
        resultado["tipo"] = dados.get("tipo") or catalogo.get("tipo")
        resultado["unidade_medida"] = dados.get("unidade_medida") or catalogo.get("unidade_medida")
        return resultado

    def test_usa_nde_do_catalogo_quando_nao_informado(self):
        dados = {"nde_cultura": None, "nome_popular": None}
        catalogo = {"nde_padrao": 5.0, "nome_popular": "Ferrugem Asiática", "tipo": "DOENCA", "nome_cientifico": None, "unidade_medida": "%"}
        r = self._aplicar_catalogo(dados, catalogo)
        assert r["nde_cultura"] == 5.0
        assert r["nome_popular"] == "Ferrugem Asiática"

    def test_mantem_valor_informado_quando_presente(self):
        dados = {"nde_cultura": 3.0, "nome_popular": "Ferrugem (customizado)"}
        catalogo = {"nde_padrao": 5.0, "nome_popular": "Ferrugem Asiática", "tipo": "DOENCA", "nome_cientifico": None, "unidade_medida": "%"}
        r = self._aplicar_catalogo(dados, catalogo)
        assert r["nde_cultura"] == 3.0
        assert r["nome_popular"] == "Ferrugem (customizado)"
