"""
Testes para dashboard financeiro de safra.

Valida:
1. Agregação de custo (operações + despesas)
2. Agregação de receita (romaneios + receitas)
3. Cálculo de ROI
4. Rastreabilidade (origem_id linkados)
5. Tenant isolation
"""
import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.exceptions import EntityNotFoundError
from agricola.dashboard.service import DashboardAgricolaService
from agricola.safras.models import Safra
from agricola.operacoes.models import OperacaoAgricola
from agricola.romaneios.models import RomaneioColheita
from agricola.operacoes.schemas import OperacaoAgricolaCreate
from agricola.romaneios.schemas import RomaneioColheitaCreate
from financeiro.models.despesa import Despesa
from financeiro.models.receita import Receita
from financeiro.models.plano_conta import PlanoConta


class TestDashboardFinanceiroSafra:
    """Testes de agregação financeira de safra."""

    @pytest.mark.asyncio
    async def test_resumo_financeiro_safra_valido(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Dashboard deve retornar agregação correta de custo + receita."""
        # Setup: Criar safra
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="COLHEITA",
            area_plantada_ha=100.0
        )
        session.add(safra)

        # Criar planos de conta
        plano_despesa = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            descricao="Custeio",
            categoria_rfb="CUSTEIO",
            natureza="ANALITICA",
            ativo=True
        )
        plano_receita = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            descricao="Receita Venda",
            categoria_rfb="RECEITA_ATIVIDADE",
            natureza="ANALITICA",
            ativo=True
        )
        session.add_all([plano_despesa, plano_receita])
        await session.commit()

        # Criar operação com custo
        operacao = OperacaoAgricola(
            id=uuid4(),
            tenant_id=tenant_id,
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="COLHEITA",
            descricao="Colheita",
            data_realizada=date.today(),
            area_aplicada_ha=100.0,
            custo_total=5000.0,  # R$ 5000
            fase_safra="COLHEITA"
        )
        session.add(operacao)
        await session.commit()

        # Criar despesa associada (webhook já a teria criado, simulamos)
        despesa = Despesa(
            id=uuid4(),
            tenant_id=tenant_id,
            fazenda_id=fazenda_id,
            plano_conta_id=plano_despesa.id,
            descricao="Colheita — MILHO 2025/26",
            valor_total=5000.0,
            data_emissao=date.today(),
            data_vencimento=date.today(),
            data_pagamento=date.today(),
            status="PAGO",
            origem_id=operacao.id,
            origem_tipo="OPERACAO_AGRICOLA"
        )
        session.add(despesa)
        await session.commit()

        # Criar romaneio com receita
        romaneio = RomaneioColheita(
            id=uuid4(),
            tenant_id=tenant_id,
            safra_id=safra.id,
            talhao_id=talhao_id,
            data_colheita=date.today(),
            peso_bruto_kg=60000.0,  # 60 toneladas
            tara_kg=0.0,
            umidade_pct=14.0,
            impureza_pct=1.0,
            preco_saca=100.0,  # R$ 100/saca
            peso_liquido_kg=60000.0,
            desconto_umidade_kg=0.0,
            desconto_impureza_kg=0.0,
            peso_liquido_padrao_kg=60000.0,
            sacas_60kg=1000.0,  # 1000 sacas
            receita_total=100000.0  # 1000 sacas × R$ 100
        )
        session.add(romaneio)
        await session.commit()

        # Criar receita associada (webhook já a teria criado, simulamos)
        receita = Receita(
            id=uuid4(),
            tenant_id=tenant_id,
            fazenda_id=fazenda_id,
            plano_conta_id=plano_receita.id,
            descricao="Venda de grãos — MILHO 2025/26",
            valor_total=100000.0,
            data_emissao=date.today(),
            data_vencimento=date.today(),
            data_recebimento=date.today(),
            status="RECEBIDO",
            origem_id=romaneio.id,
            origem_tipo="ROMANEIO_COLHEITA"
        )
        session.add(receita)
        await session.commit()

        # Act
        dashboard = DashboardAgricolaService(session, tenant_id)
        resumo = await dashboard.resumo_financeiro_safra(safra.id)

        # Assert
        assert resumo.id == safra.id
        assert resumo.cultura == "MILHO"
        assert resumo.ano_safra == "2025/26"
        assert resumo.area_plantada_ha == 100.0

        # Operações
        assert resumo.financeiro.total_operacoes == 1
        assert resumo.financeiro.custo_operacoes_total == 5000.0
        assert resumo.financeiro.custo_por_ha == 50.0  # 5000 / 100

        # Romaneios
        assert resumo.financeiro.total_romaneios == 1
        assert resumo.financeiro.total_sacas == 1000.0
        assert resumo.financeiro.produtividade_sc_ha == 10.0  # 1000 / 100

        # Financeiro
        assert resumo.financeiro.despesa_total == 5000.0
        assert resumo.financeiro.receita_total == 100000.0
        assert resumo.financeiro.lucro_bruto == 95000.0
        assert resumo.financeiro.roi_pct == 1900.0  # (95000 / 5000) × 100

    @pytest.mark.asyncio
    async def test_resumo_financeiro_safra_sem_operacoes(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Dashboard com safra sem operações deve retornar zeros."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="SOJA",
            status="PLANTIO",
            area_plantada_ha=50.0
        )
        session.add(safra)
        await session.commit()

        # Act
        dashboard = DashboardAgricolaService(session, tenant_id)
        resumo = await dashboard.resumo_financeiro_safra(safra.id)

        # Assert: Todos os valores zero/vazios
        assert resumo.financeiro.total_operacoes == 0
        assert resumo.financeiro.custo_operacoes_total == 0.0
        assert resumo.financeiro.total_romaneios == 0
        assert resumo.financeiro.total_sacas == 0.0
        assert resumo.financeiro.despesa_total == 0.0
        assert resumo.financeiro.receita_total == 0.0
        assert resumo.financeiro.lucro_bruto == 0.0
        assert resumo.financeiro.roi_pct is None  # Sem despesa = sem ROI

    @pytest.mark.asyncio
    async def test_resumo_financeiro_safra_nao_existe(
        self,
        session: AsyncSession,
        tenant_id: str
    ):
        """Dashboard deve falhar se safra não existe."""
        safra_id_fake = uuid4()

        dashboard = DashboardAgricolaService(session, tenant_id)

        with pytest.raises(EntityNotFoundError):
            await dashboard.resumo_financeiro_safra(safra_id_fake)

    @pytest.mark.asyncio
    async def test_tenant_isolation_dashboard(
        self,
        session: AsyncSession,
        tenant_id: str,
        outro_tenant_id: str,
        talhao_id: str
    ):
        """Dashboard de um tenant não deveria acessar safra de outro tenant."""
        # Setup: Safra de outro tenant
        safra_outro = Safra(
            id=uuid4(),
            tenant_id=outro_tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="COLHEITA",
            area_plantada_ha=50.0
        )
        session.add(safra_outro)
        await session.commit()

        # Act: Tentar acessar com tenant_id diferente
        dashboard = DashboardAgricolaService(session, tenant_id)

        with pytest.raises(EntityNotFoundError):
            await dashboard.resumo_financeiro_safra(safra_outro.id)

    @pytest.mark.asyncio
    async def test_resumo_produtividade_calculada(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Produtividade deve ser calculada corretamente (sacas/ha)."""
        # Setup: Safra com area 100 ha
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="SOJA",
            status="COLHEITA",
            area_plantada_ha=100.0
        )
        session.add(safra)

        plano = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            descricao="Receita",
            categoria_rfb="RECEITA_ATIVIDADE",
            natureza="ANALITICA",
            ativo=True
        )
        session.add(plano)
        await session.commit()

        # Criar romaneio: 2500 sacas em 100 ha = 25 sc/ha
        romaneio = RomaneioColheita(
            id=uuid4(),
            tenant_id=tenant_id,
            safra_id=safra.id,
            talhao_id=talhao_id,
            data_colheita=date.today(),
            peso_bruto_kg=150000.0,  # 150 toneladas
            tara_kg=0.0,
            umidade_pct=12.0,
            impureza_pct=1.0,
            preco_saca=100.0,
            peso_liquido_kg=150000.0,
            desconto_umidade_kg=0.0,
            desconto_impureza_kg=0.0,
            peso_liquido_padrao_kg=150000.0,
            sacas_60kg=2500.0,  # 2500 sacas
            receita_total=250000.0
        )
        session.add(romaneio)
        await session.commit()

        # Act
        dashboard = DashboardAgricolaService(session, tenant_id)
        resumo = await dashboard.resumo_financeiro_safra(safra.id)

        # Assert
        assert resumo.financeiro.total_sacas == 2500.0
        assert resumo.financeiro.produtividade_sc_ha == 25.0  # 2500 / 100

    @pytest.mark.asyncio
    async def test_resumo_roi_calculado(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """ROI deve ser (receita - despesa) / despesa × 100."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="COLHEITA",
            area_plantada_ha=100.0
        )
        session.add(safra)

        plano_despesa = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            descricao="Custeio",
            categoria_rfb="CUSTEIO",
            natureza="ANALITICA",
            ativo=True
        )
        plano_receita = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            descricao="Receita",
            categoria_rfb="RECEITA_ATIVIDADE",
            natureza="ANALITICA",
            ativo=True
        )
        session.add_all([plano_despesa, plano_receita])
        await session.commit()

        # Operação: custo = R$ 10.000
        operacao = OperacaoAgricola(
            id=uuid4(),
            tenant_id=tenant_id,
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="COLHEITA",
            descricao="Colheita",
            data_realizada=date.today(),
            area_aplicada_ha=100.0,
            custo_total=10000.0,
            fase_safra="COLHEITA"
        )
        session.add(operacao)

        # Despesa
        despesa = Despesa(
            id=uuid4(),
            tenant_id=tenant_id,
            fazenda_id=fazenda_id,
            plano_conta_id=plano_despesa.id,
            descricao="Colheita",
            valor_total=10000.0,
            data_emissao=date.today(),
            data_vencimento=date.today(),
            data_pagamento=date.today(),
            status="PAGO",
            origem_id=operacao.id,
            origem_tipo="OPERACAO_AGRICOLA"
        )
        session.add(despesa)

        # Romaneio: receita = R$ 30.000
        romaneio = RomaneioColheita(
            id=uuid4(),
            tenant_id=tenant_id,
            safra_id=safra.id,
            talhao_id=talhao_id,
            data_colheita=date.today(),
            peso_bruto_kg=60000.0,
            tara_kg=0.0,
            umidade_pct=14.0,
            impureza_pct=1.0,
            preco_saca=300.0,  # Preço alto
            peso_liquido_kg=60000.0,
            desconto_umidade_kg=0.0,
            desconto_impureza_kg=0.0,
            peso_liquido_padrao_kg=60000.0,
            sacas_60kg=1000.0,
            receita_total=300000.0  # 1000 × 300
        )
        session.add(romaneio)

        # Receita
        receita = Receita(
            id=uuid4(),
            tenant_id=tenant_id,
            fazenda_id=fazenda_id,
            plano_conta_id=plano_receita.id,
            descricao="Venda",
            valor_total=300000.0,
            data_emissao=date.today(),
            data_vencimento=date.today(),
            data_recebimento=date.today(),
            status="RECEBIDO",
            origem_id=romaneio.id,
            origem_tipo="ROMANEIO_COLHEITA"
        )
        session.add(receita)
        await session.commit()

        # Act
        dashboard = DashboardAgricolaService(session, tenant_id)
        resumo = await dashboard.resumo_financeiro_safra(safra.id)

        # Assert
        # ROI = (300000 - 10000) / 10000 × 100 = 2900%
        assert resumo.financeiro.despesa_total == 10000.0
        assert resumo.financeiro.receita_total == 300000.0
        assert resumo.financeiro.lucro_bruto == 290000.0
        assert resumo.financeiro.roi_pct == 2900.0
