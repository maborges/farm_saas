"""
Testes unitários para AnaliseSoloService.
Foco: cálculo automático de CTC/V%, classificações e recomendações.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal

from agricola.analises_solo.service import AnaliseSoloService
from agricola.analises_solo.models import AnaliseSolo
from agricola.analises_solo.schemas import AnaliseSoloCreate

pytestmark = pytest.mark.asyncio(loop_scope="function")

TENANT_ID = uuid.uuid4()


def make_service() -> AnaliseSoloService:
    session = AsyncMock()
    svc = AnaliseSoloService(session=session, tenant_id=TENANT_ID)
    svc.create = AsyncMock(side_effect=lambda d: _fake_analise(d))
    return svc


def _fake_analise(dados: dict) -> AnaliseSolo:
    a = AnaliseSolo()
    for k, v in dados.items():
        setattr(a, k, v)
    return a


class TestCTCAutoCalculo:
    """CTC e V% devem ser calculados automaticamente quando não fornecidos."""

    async def test_calcula_ctc_e_vpct(self):
        svc = make_service()
        dados = AnaliseSoloCreate(
            talhao_id=uuid.uuid4(),
            data_coleta="2025-01-15",
            calcio_ca=3.5,
            magnesio_mg=1.2,
            potassio_k=195.0,   # mg/dm³ → 195/391 ≈ 0.499 cmolc
            hidrogenio_al_hal=4.0,
        )
        analise = await svc.criar(dados)

        # K em cmolc = 195/391 ≈ 0.499
        k_cmol = 195.0 / 391
        sb = 3.5 + 1.2 + k_cmol
        ctc_esperada = round(sb + 4.0, 2)
        v_pct_esperada = round((sb / (sb + 4.0)) * 100, 2)

        assert abs(float(analise.ctc) - ctc_esperada) < 0.01
        assert abs(float(analise.v_pct) - v_pct_esperada) < 0.1

    async def test_nao_sobrescreve_ctc_ja_informado(self):
        svc = make_service()
        dados = AnaliseSoloCreate(
            talhao_id=uuid.uuid4(),
            data_coleta="2025-01-15",
            calcio_ca=3.5,
            magnesio_mg=1.2,
            potassio_k=195.0,
            hidrogenio_al_hal=4.0,
            ctc=9.99,  # informado pelo laboratório
        )
        analise = await svc.criar(dados)
        assert float(analise.ctc) == 9.99

    async def test_sem_bases_nao_calcula(self):
        """Se não há Ca, Mg, K, H+Al: não deve gerar CTC nem V%."""
        svc = make_service()
        dados = AnaliseSoloCreate(
            talhao_id=uuid.uuid4(),
            data_coleta="2025-01-15",
            ph_agua=6.2,
        )
        analise = await svc.criar(dados)
        # CTC calculada = 0, não deve ser gravada
        assert not analise.ctc or float(analise.ctc) == 0


class TestClassificacaoPH:
    """Testes síncronos do helper _fallback_nivel_ph."""
    def test_muito_acido(self):
        svc = make_service()
        r = svc._fallback_nivel_ph(4.0)
        assert r["nivel"] == "MUITO_BAIXO"

    def test_acido(self):
        svc = make_service()
        r = svc._fallback_nivel_ph(5.0)
        assert r["nivel"] == "BAIXO"

    def test_ideal(self):
        svc = make_service()
        r = svc._fallback_nivel_ph(6.0)
        assert r["nivel"] == "IDEAL"

    def test_alcalino(self):
        svc = make_service()
        r = svc._fallback_nivel_ph(7.0)
        assert r["nivel"] == "ALTO"

    def test_muito_alcalino(self):
        svc = make_service()
        r = svc._fallback_nivel_ph(8.0)
        assert r["nivel"] == "MUITO_ALTO"


def _make_service_sem_db() -> AnaliseSoloService:
    """Service com sessão e helpers mockados (sem banco)."""
    session = AsyncMock()
    # scalar_one_or_none() retorna None (sem talhão) — síncrono
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result

    svc = AnaliseSoloService(session=session, tenant_id=TENANT_ID)
    svc._get_cultura = AsyncMock(return_value=None)
    svc._get_parametros = AsyncMock(return_value=[])
    return svc


def _analise_completa(v_pct=45.0, ctc=8.5, p=8.0, k=120.0, ph=5.0) -> AnaliseSolo:
    from datetime import date
    a = AnaliseSolo()
    a.talhao_id = uuid.uuid4()
    a.v_pct = Decimal(str(v_pct))
    a.ctc = Decimal(str(ctc))
    a.fosforo_p = Decimal(str(p))
    a.potassio_k = Decimal(str(k))
    a.ph_agua = Decimal(str(ph))
    a.materia_organica_pct = Decimal("2.5")
    a.cultura_nome = None
    a.tipo_irrigacao = None
    a.cultura_anterior = None
    a.sistema_manejo = None
    a.data_coleta = date.today()
    a.validade_meses = 12
    return a


class TestRecomendacoes:
    async def test_calagem_necessaria_quando_v_atual_menor_que_meta(self):
        svc = _make_service_sem_db()
        analise = _analise_completa(v_pct=45.0, ctc=8.5)
        rec = await svc.gerar_recomendacoes(analise, cultura_nome="SOJA", v_meta=60.0)
        assert rec["calagem"]["necessaria"] is True
        assert rec["calagem"]["dose_t_ha"] > 0

    async def test_calagem_desnecessaria_quando_v_atual_maior_que_meta(self):
        svc = _make_service_sem_db()
        analise = _analise_completa(v_pct=70.0, ctc=8.5)
        rec = await svc.gerar_recomendacoes(analise, cultura_nome="SOJA", v_meta=60.0)
        assert rec["calagem"]["necessaria"] is False
        assert rec["calagem"]["dose_t_ha"] == 0.0

    async def test_fosforo_baixo_tem_recomendacao_alta(self):
        svc = _make_service_sem_db()
        analise = _analise_completa(p=5.0)  # < 6 = MUITO_BAIXO
        rec = await svc.gerar_recomendacoes(analise)
        assert rec["fosforo"]["nivel"] == "MUITO_BAIXO"
        assert rec["fosforo"]["rec_p2o5_kg_ha"] == 130

    async def test_potassio_alto_tem_recomendacao_menor(self):
        svc = _make_service_sem_db()
        analise = _analise_completa(k=200.0)  # > 150 = ALTO
        rec = await svc.gerar_recomendacoes(analise)
        assert rec["potassio"]["nivel"] == "ALTO"
        assert rec["potassio"]["rec_k2o_kg_ha"] == 45

    async def test_nitrogenio_soja_menor_que_milho(self):
        svc = _make_service_sem_db()
        analise = _analise_completa()
        rec_soja = await svc.gerar_recomendacoes(analise, cultura_nome="SOJA")
        rec_milho = await svc.gerar_recomendacoes(analise, cultura_nome="MILHO")
        assert rec_soja["nitrogenio"]["rec_n_kg_ha"] < rec_milho["nitrogenio"]["rec_n_kg_ha"]
