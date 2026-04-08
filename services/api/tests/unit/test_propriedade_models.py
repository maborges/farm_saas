"""Testes unitários para os modelos da Sprint 00 - C-01."""
import pytest
from core.cadastros.propriedades.propriedade_models import (
    Propriedade,
    ExploracaoRural,
    DocumentoExploracao,
    NaturezaVinculo,
    TipoDocumentoExploracao,
)


class TestNomeTabelas:
    """Verifica se os nomes das tabelas estão corretos."""

    def test_propriedade_tablename(self):
        assert Propriedade.__tablename__ == "cadastros_propriedades"

    def test_exploracao_rural_tablename(self):
        assert ExploracaoRural.__tablename__ == "cadastros_exploracoes_rurais"

    def test_documento_exploracao_tablename(self):
        assert DocumentoExploracao.__tablename__ == "cadastros_documentos_exploracao"


class TestEnumNaturezaVinculo:
    """Verifica se os enums de NaturezaVinculo estão corretos."""

    def test_propria(self):
        assert NaturezaVinculo.PROPRIA.value == "propria"

    def test_arrendamento(self):
        assert NaturezaVinculo.ARRENDAMENTO.value == "arrendamento"

    def test_parceria(self):
        assert NaturezaVinculo.PARCERIA.value == "parceria"

    def test_comodato(self):
        assert NaturezaVinculo.COMODATO.value == "comodato"

    def test_posse(self):
        assert NaturezaVinculo.POSSE.value == "posse"


class TestEnumTipoDocumentoExploracao:
    """Verifica se os enums de TipoDocumentoExploracao estão corretos."""

    def test_contrato_arrendamento(self):
        assert TipoDocumentoExploracao.CONTRATO_ARRENDAMENTO.value == "contrato_arrendamento"

    def test_contrato_parceria(self):
        assert TipoDocumentoExploracao.CONTRATO_PARCERIA.value == "contrato_parceria"

    def test_contrato_comodato(self):
        assert TipoDocumentoExploracao.CONTRATO_COMODATO.value == "contrato_comodato"

    def test_escritura(self):
        assert TipoDocumentoExploracao.ESCRITURA.value == "escritura"

    def test_matricula(self):
        assert TipoDocumentoExploracao.MATRICULA.value == "matricula"

    def test_ccir(self):
        assert TipoDocumentoExploracao.CCIR.value == "ccir"

    def test_itr(self):
        assert TipoDocumentoExploracao.ITR.value == "itr"

    def test_car(self):
        assert TipoDocumentoExploracao.CAR.value == "car"

    def test_outro(self):
        assert TipoDocumentoExploracao.OUTRO.value == "outro"


class TestImports:
    """Verifica se os imports funcionam sem erro."""

    def test_import_modelos(self):
        from core.cadastros.propriedades.propriedade_models import (
            Propriedade,
            ExploracaoRural,
            DocumentoExploracao,
        )
        assert Propriedade is not None
        assert ExploracaoRural is not None
        assert DocumentoExploracao is not None

    def test_import_enums(self):
        from core.cadastros.propriedades.propriedade_models import (
            NaturezaVinculo,
            TipoDocumentoExploracao,
        )
        assert NaturezaVinculo is not None
        assert TipoDocumentoExploracao is not None
