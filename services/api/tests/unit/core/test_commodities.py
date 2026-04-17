"""
COM-01 a COM-20: Testes unitários de schemas e validações de commodities.
"""
import pytest
from pydantic import ValidationError
import uuid

from core.cadastros.commodities.schemas import (
    CommodityCreate, CommodityUpdate,
    CommodityClassificacaoCreate, CommodityClassificacaoUpdate,
    CotacaoCommodityCreate, CotacaoCommodityUpdate,
)
from core.cadastros.commodities.models import UNIDADES_PESO_FIXO, UNIDADES_SEM_PESO_FIXO


# ===========================================================================
# COM-01 a COM-06: Validação de CommodityCreate
# ===========================================================================

class TestCommodityCreate:
    """Validação do schema de criação de commodity."""

    # COM-01: Criação válida com unidade fixa e peso
    def test_agricola_valido(self):
        c = CommodityCreate(
            nome="Soja",
            codigo="SOJA",
            tipo="AGRICOLA",
            unidade_padrao="SACA_60KG",
            peso_unidade=60.0,
        )
        assert c.nome == "Soja"
        assert c.codigo == "SOJA"
        assert c.peso_unidade == 60.0

    # COM-02: Código normalizado para maiúsculas
    def test_codigo_normalizado(self):
        c = CommodityCreate(
            nome="Milho",
            codigo="milho",
            tipo="AGRICOLA",
            unidade_padrao="SACA_60KG",
            peso_unidade=60.0,
        )
        assert c.codigo == "MILHO"

    # COM-03: Código vazio rejeitado
    def test_codigo_vazio_rejeitado(self):
        with pytest.raises(ValidationError):
            CommodityCreate(
                nome="Teste",
                codigo="",
                tipo="AGRICOLA",
                unidade_padrao="SACA_60KG",
                peso_unidade=60.0,
            )

    # COM-04: Código com espaços rejeitado
    def test_codigo_com_espacos_rejeitado(self):
        with pytest.raises(ValidationError):
            CommodityCreate(
                nome="Teste",
                codigo="CODIGO COM ESPACO",
                tipo="AGRICOLA",
                unidade_padrao="SACA_60KG",
                peso_unidade=60.0,
            )

    # COM-05: peso_unidade obrigatório para unidades fixas
    @pytest.mark.parametrize("unidade", sorted(UNIDADES_PESO_FIXO))
    def test_peso_obrigatorio_unidades_fixas(self, unidade):
        with pytest.raises(ValidationError) as exc_info:
            CommodityCreate(
                nome="Teste",
                codigo="TESTE",
                tipo="AGRICOLA",
                unidade_padrao=unidade,
                peso_unidade=None,
            )
        assert "obrigatório" in str(exc_info.value).lower() or "peso" in str(exc_info.value).lower()

    # COM-06: peso_unidade proibido para unidades variáveis
    @pytest.mark.parametrize("unidade", sorted(UNIDADES_SEM_PESO_FIXO))
    def test_peso_proibido_unidades_variaveis(self, unidade):
        with pytest.raises(ValidationError) as exc_info:
            CommodityCreate(
                nome="Teste",
                codigo="TESTE",
                tipo="PECUARIA",
                unidade_padrao=unidade,
                peso_unidade=50.0,
            )
        assert "não deve" in str(exc_info.value).lower() or "peso" in str(exc_info.value).lower()

    # COM-07: Campos opcionais
    def test_campos_opcionais(self):
        c = CommodityCreate(
            nome="Soja Premium",
            codigo="SOJA_PREMIUM",
            tipo="AGRICOLA",
            unidade_padrao="SACA_60KG",
            peso_unidade=60.0,
            descricao="Soja de alta qualidade",
            umidade_padrao_pct=14.0,
            impureza_padrao_pct=1.0,
            possui_cotacao=True,
            bolsa_referencia="CBOT",
            codigo_bolsa="ZS",
        )
        assert c.descricao == "Soja de alta qualidade"
        assert c.umidade_padrao_pct == 14.0
        assert c.impureza_padrao_pct == 1.0
        assert c.possui_cotacao is True


# ===========================================================================
# COM-08 a COM-10: Validação de CommodityUpdate
# ===========================================================================

class TestCommodityUpdate:
    """Validação do schema de atualização de commodity."""

    # COM-08: Partial update válido
    def test_partial_update(self):
        u = CommodityUpdate(nome="Soja Melhorada")
        assert u.nome == "Soja Melhorada"
        assert u.tipo is None

    # COM-09: Código normalizado no update
    def test_codigo_normalizado_update(self):
        u = CommodityUpdate(codigo="novo_codigo")
        assert u.codigo == "NOVO_CODIGO"

    # COM-10: peso_unidade proibido para unidade variável no update
    def test_peso_proibido_update(self):
        with pytest.raises(ValidationError):
            CommodityUpdate(unidade_padrao="CABECA", peso_unidade=30.0)


# ===========================================================================
# COM-11 a COM-13: CommodityClassificacao schemas
# ===========================================================================

class TestCommodityClassificacaoCreate:
    """Validação do schema de classificação."""

    # COM-11: Criação mínima
    def test_minimo(self):
        cls = CommodityClassificacaoCreate(classe="TIPO_1")
        assert cls.classe == "TIPO_1"
        assert cls.ativo is True

    # COM-12: Criação completa
    def test_completo(self):
        cls = CommodityClassificacaoCreate(
            classe="PREMIUM",
            descricao="Café especial SCAA > 84",
            umidade_max_pct=12.0,
            impureza_max_pct=0.5,
            avariados_max_pct=1.0,
            ardidos_max_pct=0.5,
            desconto_umidade_por_ponto=0.1,
            desconto_impureza_por_ponto=0.15,
        )
        assert cls.classe == "PREMIUM"
        assert cls.umidade_max_pct == 12.0

    # COM-13: Parâmetros extras
    def test_parametros_extras(self):
        cls = CommodityClassificacaoCreate(
            classe="TIPO_1",
            parametros_extras={"scaa_min": 80, "defeitos_max": 6},
        )
        assert cls.parametros_extras["scaa_min"] == 80


# ===========================================================================
# COM-14 a COM-16: CotacaoCommodity schemas
# ===========================================================================

class TestCotacaoCommodityCreate:
    """Validação do schema de cotação."""

    # COM-14: Criação mínima
    def test_minimo(self):
        from datetime import datetime, timezone
        c = CotacaoCommodityCreate(
            data=datetime(2026, 4, 12, tzinfo=timezone.utc),
            preco=150.50,
        )
        assert c.preco == 150.50
        assert c.moeda == "BRL"

    # COM-15: Criação com fonte
    def test_com_fonte(self):
        from datetime import datetime, timezone
        c = CotacaoCommodityCreate(
            data=datetime(2026, 4, 12, tzinfo=timezone.utc),
            preco=150.50,
            fonte="CEPEA",
        )
        assert c.fonte == "CEPEA"

    # COM-16: Moeda customizada
    def test_moeda_custom(self):
        from datetime import datetime, timezone
        c = CotacaoCommodityCreate(
            data=datetime(2026, 4, 12, tzinfo=timezone.utc),
            preco=25.0,
            moeda="USD",
        )
        assert c.moeda == "USD"


# ===========================================================================
# COM-17 a COM-20: Regras de negócio e constantes
# ===========================================================================

class TestCommodityRegras:
    """Testes de regras de negócio e constantes do modelo."""

    # COM-17: Unidades fixas são as esperadas
    def test_unidades_fixas_esperadas(self):
        assert "SACA_60KG" in UNIDADES_PESO_FIXO
        assert "TONELADA" in UNIDADES_PESO_FIXO
        assert "KG" in UNIDADES_PESO_FIXO
        assert "ARROBA" in UNIDADES_PESO_FIXO

    # COM-18: Unidades variáveis são as esperadas
    def test_unidades_variaveis_esperadas(self):
        assert "CABECA" in UNIDADES_SEM_PESO_FIXO
        assert "LITRO" in UNIDADES_SEM_PESO_FIXO
        assert "M3" in UNIDADES_SEM_PESO_FIXO
        assert "UNIDADE" in UNIDADES_SEM_PESO_FIXO

    # COM-19: Conjuntos não se sobrepõem
    def test_sem_sobreposicao(self):
        assert UNIDADES_PESO_FIXO.isdisjoint(UNIDADES_SEM_PESO_FIXO)

    # COM-20: Todos os enums cobertos
    def test_todas_unidades_cobertas(self):
        from core.cadastros.commodities.models import UnidadeCommodity
        enum_values = {u.value for u in UnidadeCommodity}
        todas = UNIDADES_PESO_FIXO | UNIDADES_SEM_PESO_FIXO
        assert enum_values == todas, f"Faltam: {enum_values - todas}"
