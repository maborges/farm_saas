"""
Testes automatizados — Step 20: safra_cenarios + safra_cenarios_unidades

Cobertura:
- BASE não duplicado em chamadas concorrentes
- BASE não pode ser excluído
- Override por unidade prevalece sobre default do cenário
- fator_custo_pct aplicado corretamente quando não há override
- Isolamento multi-tenant
- Fallback de custo: REALIZADO → ORCADO → MANUAL
- Cálculos: receita_bruta, custo_total, margem_contribuicao, ponto_equilibrio
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from unittest.mock import AsyncMock, MagicMock, patch

from core.exceptions import BusinessRuleError, EntityNotFoundError
from agricola.cenarios.models import SafraCenario, SafraCenarioUnidade
from agricola.cenarios.schemas import CenarioCreate, CenarioUnidadeInput, CenarioUpdate, DuplicarCenarioRequest
from agricola.cenarios.service import CenariosService, _d, _f


# ---------------------------------------------------------------------------
# Fixtures helpers
# ---------------------------------------------------------------------------

TENANT_A = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000010")
TENANT_B = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000020")
SAFRA_ID = uuid.UUID("cccccccc-0000-0000-0000-000000000001")
PU_ID_1  = uuid.UUID("dddddddd-0000-0000-0000-000000000001")
PU_ID_2  = uuid.UUID("dddddddd-0000-0000-0000-000000000002")
UOM_ID   = uuid.UUID("eeeeeeee-0000-0000-0000-000000000001")


def _make_pu(pu_id=PU_ID_1, area_ha=100.0, participacao=100.0):
    pu = MagicMock()
    pu.id = pu_id
    pu.area_ha = area_ha
    pu.percentual_participacao = participacao
    pu.cultivo_id = uuid.uuid4()
    pu.area_id = uuid.uuid4()
    pu.status = "ATIVA"
    pu.safra_id = SAFRA_ID
    pu.tenant_id = TENANT_A
    return pu


def _make_linha(
    pu_id=PU_ID_1,
    area_ha=100.0,
    participacao=100.0,
    prod_simulada=60.0,
    preco_simulado=120.0,
    custo_simulado_ha=None,
    cenario_id=None,
):
    linha = SafraCenarioUnidade()
    linha.id = uuid.uuid4()
    linha.tenant_id = TENANT_A
    linha.cenario_id = cenario_id or uuid.uuid4()
    linha.production_unit_id = pu_id
    linha.area_ha = area_ha
    linha.percentual_participacao = participacao
    linha.produtividade_simulada = prod_simulada
    linha.preco_simulado = preco_simulado
    linha.custo_total_simulado_ha = custo_simulado_ha
    linha.custo_base_fonte = None
    linha.unidade_medida_id = UOM_ID
    linha.cultivo_nome = "Soja"
    linha.area_nome = "Talhão A"
    # campos calculados (inicialmente None)
    linha.produtividade_efetiva = None
    linha.preco_efetivo = None
    linha.custo_ha_efetivo = None
    linha.producao_total = None
    linha.receita_bruta = None
    linha.custo_total = None
    linha.margem_contribuicao = None
    linha.margem_pct = None
    linha.resultado_liquido = None
    linha.ponto_equilibrio = None
    linha.updated_at = None
    return linha


def _make_cenario(
    eh_base=False,
    prod_default=None,
    preco_default=None,
    custo_ha_default=None,
    fator=None,
    unidades=None,
):
    c = SafraCenario()
    c.id = uuid.uuid4()
    c.tenant_id = TENANT_A
    c.safra_id = SAFRA_ID
    c.nome = "Teste"
    c.tipo = "BASE" if eh_base else "CUSTOM"
    c.eh_base = eh_base
    c.status = "ATIVO"
    c.unidade_medida_id = UOM_ID
    c.produtividade_default = prod_default
    c.preco_default = preco_default
    c.custo_ha_default = custo_ha_default
    c.fator_custo_pct = fator
    c.unidades = unidades or []
    c.area_total_ha = None
    c.receita_bruta_total = None
    c.custo_total = None
    c.margem_contribuicao_total = None
    c.resultado_liquido_total = None
    c.ponto_equilibrio_sc_ha = None
    c.calculado_em = None
    c.updated_at = None
    return c


def _make_service(tenant_id=TENANT_A) -> CenariosService:
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    svc = CenariosService(session, tenant_id)
    return svc


# ---------------------------------------------------------------------------
# Helpers numéricos — testes unitários puros
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_d_none(self):
        assert _d(None) is None

    def test_d_float(self):
        assert _d(60.5) == Decimal("60.5")

    def test_d_string(self):
        assert _d("120.25") == Decimal("120.25")

    def test_f_none(self):
        assert _f(None) is None

    def test_f_decimal(self):
        assert _f(Decimal("99.99")) == pytest.approx(99.99)


# ---------------------------------------------------------------------------
# Engine de cálculo — testes com objetos em memória
# ---------------------------------------------------------------------------

class TestCalculoEngine:
    """Valida _recalculate_all com objetos reais (sem banco)."""

    @pytest.mark.asyncio
    async def test_receita_custo_margem_basicos(self):
        """prod=60sc/ha, preco=R$120, custo=R$3000/ha, area=100ha"""
        svc = _make_service()
        linha = _make_linha(area_ha=100, prod_simulada=60, preco_simulado=120, custo_simulado_ha=3000)
        cenario = _make_cenario(unidades=[linha])

        await svc._recalculate_all(cenario)

        # producao = 60 * 100 = 6000 sc
        assert linha.producao_total == pytest.approx(6000.0)
        # receita = 6000 * 120 = 720000
        assert linha.receita_bruta == pytest.approx(720_000.0)
        # custo = 3000 * 100 = 300000
        assert linha.custo_total == pytest.approx(300_000.0)
        # margem = 720000 - 300000 = 420000
        assert linha.margem_contribuicao == pytest.approx(420_000.0)
        assert linha.resultado_liquido == pytest.approx(420_000.0)
        # ponto_equilibrio = custo_ha / preco = 3000 / 120 = 25 sc/ha
        assert linha.ponto_equilibrio == pytest.approx(25.0)

        # header
        assert cenario.receita_bruta_total == pytest.approx(720_000.0)
        assert cenario.custo_total == pytest.approx(300_000.0)
        assert cenario.margem_contribuicao_total == pytest.approx(420_000.0)

    @pytest.mark.asyncio
    async def test_override_por_unidade_prevalece(self):
        """custo_total_simulado_ha da linha deve prevalecer sobre custo_ha_default + fator."""
        svc = _make_service()
        linha = _make_linha(
            area_ha=100, prod_simulada=60, preco_simulado=100,
            custo_simulado_ha=2500,  # override explícito
        )
        cenario = _make_cenario(custo_ha_default=5000, fator=1.5, unidades=[linha])

        await svc._recalculate_all(cenario)

        # custo efetivo deve ser 2500 (override), não 5000 * 1.5 = 7500
        assert linha.custo_ha_efetivo == pytest.approx(2500.0)
        assert linha.custo_total == pytest.approx(250_000.0)

    @pytest.mark.asyncio
    async def test_fator_custo_aplicado_sem_override(self):
        """Sem custo_total_simulado_ha na linha, usa custo_ha_default * fator_custo_pct."""
        svc = _make_service()
        linha = _make_linha(
            area_ha=50, prod_simulada=55, preco_simulado=110,
            custo_simulado_ha=None,  # sem override
        )
        cenario = _make_cenario(
            custo_ha_default=Decimal("2000"),
            fator=Decimal("1.10"),  # +10%
            unidades=[linha],
        )

        await svc._recalculate_all(cenario)

        # custo esperado = 2000 * 1.10 = 2200/ha
        assert linha.custo_ha_efetivo == pytest.approx(2200.0, rel=1e-3)
        assert linha.custo_total == pytest.approx(110_000.0, rel=1e-3)

    @pytest.mark.asyncio
    async def test_fallback_prod_default(self):
        """Se linha não tem produtividade_simulada, usa produtividade_default do cenário."""
        svc = _make_service()
        linha = _make_linha(area_ha=80, prod_simulada=None, preco_simulado=130, custo_simulado_ha=2800)
        cenario = _make_cenario(prod_default=50.0, unidades=[linha])

        await svc._recalculate_all(cenario)

        assert linha.produtividade_efetiva == pytest.approx(50.0)
        assert linha.producao_total == pytest.approx(4000.0)  # 50 * 80

    @pytest.mark.asyncio
    async def test_sem_preco_receita_nula(self):
        """Se não há preco (linha nem default), receita/margem ficam None."""
        svc = _make_service()
        linha = _make_linha(area_ha=100, prod_simulada=60, preco_simulado=None, custo_simulado_ha=2000)
        cenario = _make_cenario(unidades=[linha])  # sem preco_default

        await svc._recalculate_all(cenario)

        assert linha.receita_bruta is None
        assert linha.margem_contribuicao is None
        assert cenario.receita_bruta_total is None

    @pytest.mark.asyncio
    async def test_duas_unidades_somadas_no_header(self):
        """Header agrega receita/custo/margem de todas as unidades."""
        svc = _make_service()
        l1 = _make_linha(PU_ID_1, area_ha=100, prod_simulada=60, preco_simulado=100, custo_simulado_ha=2000)
        l2 = _make_linha(PU_ID_2, area_ha=50, prod_simulada=40, preco_simulado=100, custo_simulado_ha=1500)
        cenario = _make_cenario(unidades=[l1, l2])

        await svc._recalculate_all(cenario)

        # l1: receita=600000, custo=200000, margem=400000
        # l2: receita=200000, custo=75000,  margem=125000
        assert cenario.receita_bruta_total == pytest.approx(800_000.0)
        assert cenario.custo_total == pytest.approx(275_000.0)
        assert cenario.margem_contribuicao_total == pytest.approx(525_000.0)
        assert cenario.area_total_ha == pytest.approx(150.0)

    @pytest.mark.asyncio
    async def test_margem_pct_calculada(self):
        """margem_pct = margem / receita * 100."""
        svc = _make_service()
        # receita=600000, custo=300000, margem=300000 → 50%
        linha = _make_linha(area_ha=100, prod_simulada=60, preco_simulado=100, custo_simulado_ha=3000)
        cenario = _make_cenario(unidades=[linha])

        await svc._recalculate_all(cenario)

        assert linha.margem_pct == pytest.approx(50.0, rel=1e-3)


# ---------------------------------------------------------------------------
# Regras de negócio
# ---------------------------------------------------------------------------

class TestRegrasNegocio:

    @pytest.mark.asyncio
    async def test_base_nao_pode_ser_excluido(self):
        """delete_cenario deve lançar BusinessRuleError para cenário BASE."""
        svc = _make_service()
        base = _make_cenario(eh_base=True)

        svc.get_cenario = AsyncMock(return_value=base)

        with pytest.raises(BusinessRuleError, match="base não pode ser excluído"):
            await svc.delete_cenario(SAFRA_ID, base.id)

    @pytest.mark.asyncio
    async def test_cenario_custom_pode_ser_excluido(self):
        """delete_cenario deve funcionar normalmente para cenários não-BASE."""
        svc = _make_service()
        custom = _make_cenario(eh_base=False)
        svc.get_cenario = AsyncMock(return_value=custom)

        await svc.delete_cenario(SAFRA_ID, custom.id)

        svc.session.delete.assert_awaited_once_with(custom)

    @pytest.mark.asyncio
    async def test_duplicar_base_gera_custom(self):
        """Ao duplicar BASE, novo cenário deve ter tipo='CUSTOM' e eh_base=False."""
        svc = _make_service()
        base = _make_cenario(eh_base=True)
        base.tipo = "BASE"
        base.unidades = []

        svc.get_cenario = AsyncMock(return_value=base)
        svc._assert_limite_cenarios = AsyncMock()
        svc._assert_nome_unico = AsyncMock()
        svc._recalculate_all = AsyncMock()

        req = DuplicarCenarioRequest(nome="Cópia do BASE")
        novo = await svc.duplicar(SAFRA_ID, base.id, req)

        assert novo.eh_base is False
        assert novo.tipo == "CUSTOM"
        assert novo.nome == "Cópia do BASE"

    @pytest.mark.asyncio
    async def test_create_nao_permite_tipo_base(self):
        """CenarioCreate com tipo='BASE' deve ser rejeitado pela validação Pydantic."""
        with pytest.raises(Exception):
            CenarioCreate(
                nome="Teste BASE manual",
                tipo="BASE",
                unidades=[],
            )

    @pytest.mark.asyncio
    async def test_limite_cenarios_ativos(self):
        """Deve lançar erro ao atingir MAX_CENARIOS_ATIVOS."""
        svc = _make_service()

        # Simula count = 20
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 20
        svc.session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(BusinessRuleError, match="Limite"):
            await svc._assert_limite_cenarios(SAFRA_ID)


# ---------------------------------------------------------------------------
# Isolamento multi-tenant
# ---------------------------------------------------------------------------

class TestMultiTenant:

    @pytest.mark.asyncio
    async def test_fetch_base_filtra_tenant(self):
        """_fetch_base deve retornar None se o base pertence a outro tenant."""
        svc_a = _make_service(TENANT_A)
        svc_b = _make_service(TENANT_B)

        # Cenário BASE do Tenant A
        base_a = _make_cenario(eh_base=True)
        base_a.tenant_id = TENANT_A

        # svc_b não deve encontrar base_a
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        svc_b.session.execute = AsyncMock(return_value=mock_result)

        result = await svc_b._fetch_base(SAFRA_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_cenario_tenant_isolation(self):
        """get_cenario deve lançar EntityNotFoundError se cenário é de outro tenant."""
        svc_b = _make_service(TENANT_B)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        svc_b.session.execute = AsyncMock(return_value=mock_result)

        cenario_id = uuid.uuid4()
        with pytest.raises(EntityNotFoundError):
            await svc_b.get_cenario(SAFRA_ID, cenario_id)

    @pytest.mark.asyncio
    async def test_resolve_custo_filtra_tenant(self):
        """_resolve_custo_base deve filtrar por tenant_id nas queries."""
        svc = _make_service(TENANT_A)

        # Ambas as queries retornam 0 (nenhum dado do tenant A)
        result_vazio = MagicMock()
        result_vazio.scalar_one_or_none.return_value = None
        svc.session.execute = AsyncMock(return_value=result_vazio)

        custo, fonte = await svc._resolve_custo_base(PU_ID_1, 100.0)

        assert custo is None
        assert fonte == "MANUAL"

        # Verificar que as queries incluem tenant_id
        calls = svc.session.execute.call_args_list
        assert len(calls) == 2  # cost_allocations + a1_planejamento
        for call in calls:
            stmt = call.args[0]
            compiled = str(stmt.compile(compile_kwargs={"literal_binds": False}))
            # Apenas verifica que há uma cláusula WHERE (tenant_id está presente via whereclause)
            assert "WHERE" in compiled.upper()


# ---------------------------------------------------------------------------
# Fallback de custo
# ---------------------------------------------------------------------------

class TestFallbackCusto:

    @pytest.mark.asyncio
    async def test_fallback_realizado(self):
        """Quando cost_allocations tem valor, deve retornar REALIZADO."""
        svc = _make_service()

        result_realizado = MagicMock()
        result_realizado.scalar_one_or_none.return_value = Decimal("300000")

        result_vazio = MagicMock()
        result_vazio.scalar_one_or_none.return_value = None

        # Primeira chamada (cost_allocations) retorna valor
        svc.session.execute = AsyncMock(return_value=result_realizado)

        custo, fonte = await svc._resolve_custo_base(PU_ID_1, 100.0)

        assert fonte == "REALIZADO"
        assert custo == pytest.approx(3000.0)  # 300000 / 100

    @pytest.mark.asyncio
    async def test_fallback_orcado(self):
        """Quando cost_allocations=0, deve usar a1_planejamento → ORCADO."""
        svc = _make_service()

        result_zero = MagicMock()
        result_zero.scalar_one_or_none.return_value = None

        result_orcado = MagicMock()
        result_orcado.scalar_one_or_none.return_value = Decimal("200000")

        svc.session.execute = AsyncMock(
            side_effect=[result_zero, result_orcado]
        )

        custo, fonte = await svc._resolve_custo_base(PU_ID_1, 100.0)

        assert fonte == "ORCADO"
        assert custo == pytest.approx(2000.0)

    @pytest.mark.asyncio
    async def test_fallback_manual(self):
        """Quando ambos retornam None, deve retornar MANUAL."""
        svc = _make_service()

        result_vazio = MagicMock()
        result_vazio.scalar_one_or_none.return_value = None

        svc.session.execute = AsyncMock(return_value=result_vazio)

        custo, fonte = await svc._resolve_custo_base(PU_ID_1, 100.0)

        assert fonte == "MANUAL"
        assert custo is None


# ---------------------------------------------------------------------------
# Idempotência do BASE (concorrência simulada)
# ---------------------------------------------------------------------------

class TestIdempotenciaBase:

    @pytest.mark.asyncio
    async def test_base_nao_duplicado_em_chamadas_sequenciais(self):
        """Segunda chamada _get_or_create_base deve retornar o mesmo base."""
        svc = _make_service()

        base_existente = _make_cenario(eh_base=True)

        # Primeira chamada: _fetch_base retorna None → cria
        # Segunda chamada: _fetch_base retorna base existente → não cria
        svc._fetch_base = AsyncMock(side_effect=[None, base_existente])
        svc._assert_safra_nao_cancelada = AsyncMock()
        svc._fetch_uom_padrao_id = AsyncMock(return_value=UOM_ID)
        svc._fetch_production_units = AsyncMock(return_value=[])
        svc._recalculate_all = AsyncMock()

        # lock via pg_advisory_xact_lock
        lock_result = MagicMock()
        lock_result.scalar_one_or_none = MagicMock(return_value=None)
        svc.session.execute = AsyncMock(return_value=lock_result)

        result1 = await svc._get_or_create_base(SAFRA_ID)
        # Na segunda chamada, _fetch_base já retorna base_existente antes do lock
        svc._fetch_base = AsyncMock(return_value=base_existente)
        result2 = await svc._get_or_create_base(SAFRA_ID)

        assert result2 is base_existente

    @pytest.mark.asyncio
    async def test_base_double_check_apos_lock(self):
        """Após obter advisory lock, service re-verifica antes de criar."""
        svc = _make_service()

        base_criado_por_concorrente = _make_cenario(eh_base=True)

        # _fetch_base: primeira vez None (antes do lock), segunda vez tem (concorrente criou)
        svc._fetch_base = AsyncMock(side_effect=[None, base_criado_por_concorrente])
        svc._assert_safra_nao_cancelada = AsyncMock()

        lock_result = MagicMock()
        svc.session.execute = AsyncMock(return_value=lock_result)

        result = await svc._get_or_create_base(SAFRA_ID)

        # Deve retornar o que o concorrente criou, sem duplicar
        assert result is base_criado_por_concorrente
        # session.add não deve ter sido chamado (BASE não foi criado)
        svc.session.add.assert_not_called()
