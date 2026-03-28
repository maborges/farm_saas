"""
Testes unitários para a máquina de estados do ciclo de vida da safra.
Foco: validação de transições permitidas e bloqueadas.
"""
import pytest
from agricola.safras.models import SAFRA_FASES_ORDEM, SAFRA_TRANSICOES
from core.exceptions import BusinessRuleError


def pode_transicionar(de: str, para: str) -> bool:
    """Replica a validação do SafraService.avancar_fase()."""
    permitidas = SAFRA_TRANSICOES.get(de, [])
    return para in permitidas


class TestTransicoesPermitidas:
    def test_planejada_para_preparo_solo(self):
        assert pode_transicionar("PLANEJADA", "PREPARO_SOLO") is True

    def test_preparo_solo_para_plantio(self):
        assert pode_transicionar("PREPARO_SOLO", "PLANTIO") is True

    def test_plantio_para_desenvolvimento(self):
        assert pode_transicionar("PLANTIO", "DESENVOLVIMENTO") is True

    def test_desenvolvimento_para_colheita(self):
        assert pode_transicionar("DESENVOLVIMENTO", "COLHEITA") is True

    def test_colheita_para_pos_colheita(self):
        assert pode_transicionar("COLHEITA", "POS_COLHEITA") is True


class TestTransicoesNaoPermitidas:
    def test_nao_pode_pular_fases(self):
        """Planejada não pode ir direto para Colheita."""
        assert pode_transicionar("PLANEJADA", "COLHEITA") is False

    def test_nao_pode_voltar(self):
        """Não pode regredir de fase (COLHEITA → PLANTIO)."""
        assert pode_transicionar("COLHEITA", "PLANTIO") is False

    def test_nao_pode_pular_preparo_solo(self):
        assert pode_transicionar("PLANEJADA", "PLANTIO") is False

    def test_nao_pode_transicionar_para_si_mesmo(self):
        for fase in SAFRA_FASES_ORDEM:
            assert pode_transicionar(fase, fase) is False, f"Fase {fase} permite transição para si mesma"


class TestOrdemFases:
    def test_planejada_e_primeira(self):
        assert SAFRA_FASES_ORDEM[0] == "PLANEJADA"

    def test_pos_colheita_e_ultima_fase_agricola(self):
        fases_sem_encerramento = [f for f in SAFRA_FASES_ORDEM if f not in ("ENCERRADA", "CANCELADA")]
        assert fases_sem_encerramento[-1] == "POS_COLHEITA"

    def test_todas_fases_tem_transicao_definida(self):
        """Toda fase ativa deve ter uma entrada em SAFRA_TRANSICOES."""
        fases_ativas = [f for f in SAFRA_FASES_ORDEM if f not in ("ENCERRADA", "CANCELADA")]
        for fase in fases_ativas:
            assert fase in SAFRA_TRANSICOES, f"Fase {fase} sem transições definidas"
