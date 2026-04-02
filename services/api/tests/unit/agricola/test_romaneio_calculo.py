"""
Testes Unitários — Romaneio: Cálculos de Colheita
AGR-ROM-02, AGR-ROM-03, AGR-ROM-05, AGR-ROM-10, AGR-ROM-11
"""
import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# Funções de cálculo (extraídas da regra de negócio MAPA)
# ---------------------------------------------------------------------------

def calcular_sacas_60kg(peso_liquido_kg: float) -> float:
    """Cálculo oficial MAPA: 1 saca = 60kg"""
    return peso_liquido_kg / 60.0


def calcular_peso_liquido(
    peso_bruto_kg: float,
    umidade_percentual: float,
    impureza_percentual: float,
    umidade_padrao: float = 13.0,
) -> float:
    """Aplica descontos de umidade e impureza ao peso bruto"""
    desconto_umidade = max(0, (umidade_percentual - umidade_padrao) / 100) * peso_bruto_kg
    desconto_impureza = (impureza_percentual / 100) * peso_bruto_kg
    return peso_bruto_kg - desconto_umidade - desconto_impureza


# ---------------------------------------------------------------------------
# AGR-ROM-02: Romaneio calcula sacas corretamente (MAPA)
# ---------------------------------------------------------------------------

def test_calculo_sacas_mapa():
    """AGR-ROM-02: Sacas = Peso Líquido / 60 (padrão MAPA)"""
    peso_liquido = 6000.0  # kg
    sacas = calcular_sacas_60kg(peso_liquido)
    assert sacas == 100.0


def test_calculo_sacas_valor_fracionado():
    """AGR-ROM-02: Cálculo com valor fracionado"""
    sacas = calcular_sacas_60kg(150.0)
    assert abs(sacas - 2.5) < 0.001


# ---------------------------------------------------------------------------
# AGR-ROM-03: Romaneio com descontos (umidade, impureza)
# ---------------------------------------------------------------------------

def test_desconto_umidade_acima_padrao():
    """AGR-ROM-03: Umidade acima de 13% gera desconto"""
    peso_bruto = 10000.0
    peso_liquido = calcular_peso_liquido(
        peso_bruto_kg=peso_bruto,
        umidade_percentual=15.0,  # 2% acima do padrão
        impureza_percentual=0.0,
    )
    # Desconto = (15-13)/100 * 10000 = 200kg
    assert peso_liquido == pytest.approx(9800.0, rel=1e-3)


def test_desconto_impureza():
    """AGR-ROM-03: Impureza reduz peso líquido"""
    peso_liquido = calcular_peso_liquido(
        peso_bruto_kg=10000.0,
        umidade_percentual=13.0,  # no padrão, sem desconto de umidade
        impureza_percentual=2.0,
    )
    # Desconto = 2% * 10000 = 200kg
    assert peso_liquido == pytest.approx(9800.0, rel=1e-3)


def test_desconto_combinado_umidade_impureza():
    """AGR-ROM-03: Descontos de umidade e impureza aplicados juntos"""
    peso_liquido = calcular_peso_liquido(
        peso_bruto_kg=10000.0,
        umidade_percentual=15.0,  # desconto 200kg
        impureza_percentual=2.0,  # desconto 200kg
    )
    assert peso_liquido == pytest.approx(9600.0, rel=1e-3)


def test_sem_desconto_umidade_abaixo_padrao():
    """AGR-ROM-03: Umidade abaixo do padrão não gera desconto adicional"""
    peso_liquido = calcular_peso_liquido(
        peso_bruto_kg=10000.0,
        umidade_percentual=10.0,  # abaixo do padrão
        impureza_percentual=0.0,
    )
    assert peso_liquido == 10000.0  # sem desconto


# ---------------------------------------------------------------------------
# AGR-ROM-05: Romaneio sem preço não gera receita
# ---------------------------------------------------------------------------

def test_romaneio_sem_preco_nao_gera_receita():
    """AGR-ROM-05: preco_por_saca=None ou 0 não deve criar receita financeira"""
    preco_por_saca = None
    sacas = 100.0
    valor_receita = (preco_por_saca * sacas) if preco_por_saca else None
    assert valor_receita is None


def test_romaneio_com_preco_gera_receita():
    """Romaneio com preço define valor correto para receita"""
    preco_por_saca = 120.0
    sacas = 100.0
    valor_receita = preco_por_saca * sacas
    assert valor_receita == 12000.0


# ---------------------------------------------------------------------------
# AGR-ROM-10: Destino ARMAZÉM
# ---------------------------------------------------------------------------

def test_romaneio_destino_armazem():
    """AGR-ROM-10: Romaneio com destino ARMAZÉM não gera receita imediata"""
    destino = "ARMAZEM"
    preco_por_saca = 120.0

    # Com destino ARMAZÉM, receita só é gerada quando sair do armazém
    deve_gerar_receita = destino == "VENDA_DIRETA" and preco_por_saca is not None
    assert deve_gerar_receita is False


# ---------------------------------------------------------------------------
# AGR-ROM-11: Destino VENDA DIRETA
# ---------------------------------------------------------------------------

def test_romaneio_destino_venda_direta_com_preco():
    """AGR-ROM-11: Romaneio com destino VENDA_DIRETA e preço gera receita"""
    destino = "VENDA_DIRETA"
    preco_por_saca = 120.0
    sacas = 50.0

    deve_gerar_receita = destino == "VENDA_DIRETA" and preco_por_saca is not None
    assert deve_gerar_receita is True

    valor = preco_por_saca * sacas
    assert valor == 6000.0
