"""
Testes para webhook: Romaneio → Receita Automática.

Valida:
1. Romaneio com receita_total > 0 cria Receita automaticamente
2. Romaneio sem receita_total não cria Receita
3. Rastreabilidade via origem_id + origem_tipo
4. Tenant isolation
"""
import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.exceptions import EntityNotFoundError
from agricola.romaneios.service import RomaneioService
from agricola.romaneios.schemas import RomaneioColheitaCreate
from agricola.safras.models import Safra
from financeiro.models.receita import Receita
from financeiro.models.plano_conta import PlanoConta


class TestRomaneioReceitaWebhook:
    """Testes de automação de receita ao criar romaneio."""

    @pytest.mark.asyncio
    async def test_romaneio_com_receita_cria_receita_automatica(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Romaneio com receita_total > 0 deve criar Receita automaticamente."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="COLHEITA",
            area_plantada_ha=50.0
        )
        session.add(safra)
        await session.commit()

        # Criar plano de conta para receita (necessário para criar Receita)
        plano = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            codigo="4.01",
            nome="Receita de Venda de Grãos",
            tipo="RECEITA",
            categoria_rfb="RECEITA_ATIVIDADE",
            natureza="ANALITICA",
            ativo=True
        )
        session.add(plano)
        await session.commit()

        # Act: Criar romaneio com receita_total
        service = RomaneioService(session, tenant_id)

        romaneio_create = RomaneioColheitaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            data_colheita=date.today(),
            peso_bruto_kg=30000.0,  # 30 toneladas
            tara_kg=0.0,
            umidade_pct=14.0,
            impureza_pct=1.0,
            preco_saca=200.0  # ← Isso gera receita_total
        )

        romaneio = await service.criar(romaneio_create)

        # Assert: Receita deve ter sido criada
        receita_stmt = select(Receita).where(
            Receita.origem_id == romaneio.id,
            Receita.origem_tipo == "ROMANEIO_COLHEITA"
        )
        receita = (await session.execute(receita_stmt)).scalars().first()

        assert receita is not None, "Receita não foi criada automaticamente"
        assert receita.valor_total == romaneio.receita_total
        assert receita.status == "RECEBIDO"
        assert receita.origem_tipo == "ROMANEIO_COLHEITA"

    @pytest.mark.asyncio
    async def test_romaneio_sem_preco_nao_cria_receita(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Romaneio sem preco_saca não deve criar Receita."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="COLHEITA",
            area_plantada_ha=50.0
        )
        session.add(safra)
        await session.commit()

        # Act: Criar romaneio SEM preco (receita_total = 0 ou None)
        service = RomaneioService(session, tenant_id)

        romaneio_create = RomaneioColheitaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            data_colheita=date.today(),
            peso_bruto_kg=30000.0,
            tara_kg=0.0,
            umidade_pct=14.0,
            impureza_pct=1.0,
            preco_saca=None  # ← Sem preço
        )

        romaneio = await service.criar(romaneio_create)

        # Assert: Receita NÃO deve ter sido criada
        receita_stmt = select(Receita).where(
            Receita.origem_id == romaneio.id
        )
        receita = (await session.execute(receita_stmt)).scalars().first()

        assert receita is None, "Receita não deveria ter sido criada (sem preco)"

    @pytest.mark.asyncio
    async def test_rastreabilidade_romaneio_receita(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Receita deve ter origem_id linkado ao romaneio para rastreabilidade."""
        # Setup
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
            codigo="4.01",
            nome="Receita Soja",
            tipo="RECEITA",
            categoria_rfb="RECEITA_ATIVIDADE",
            natureza="ANALITICA",
            ativo=True
        )
        session.add(plano)
        await session.commit()

        # Act
        service = RomaneioService(session, tenant_id)

        romaneio_create = RomaneioColheitaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            data_colheita=date.today(),
            peso_bruto_kg=60000.0,  # 60 toneladas
            tara_kg=500.0,
            umidade_pct=14.0,
            impureza_pct=2.0,
            preco_saca=450.0
        )

        romaneio = await service.criar(romaneio_create)

        # Assert: Buscar receita por origem_id
        receita_stmt = select(Receita).where(
            Receita.origem_id == romaneio.id,
            Receita.origem_tipo == "ROMANEIO_COLHEITA"
        )
        receita = (await session.execute(receita_stmt)).scalars().first()

        assert receita is not None
        assert receita.origem_id == romaneio.id
        assert receita.descricao is not None  # Descrição gerada automaticamente
        assert "Soja" in receita.descricao or "grãos" in receita.descricao.lower()

    @pytest.mark.asyncio
    async def test_tenant_isolation_romaneio_receita(
        self,
        session: AsyncSession,
        tenant_id: str,
        outro_tenant_id: str,
        talhao_id: str
    ):
        """Receita de um tenant não deveria ser criada para romaneio de outro tenant."""
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

        # Act: Tentar criar romaneio com tenant_id diferente
        service = RomaneioService(session, tenant_id)  # ← tenant_id diferente

        romaneio_create = RomaneioColheitaCreate(
            safra_id=safra_outro.id,  # ← Safra de outro tenant
            talhao_id=talhao_id,
            data_colheita=date.today(),
            peso_bruto_kg=30000.0,
            tara_kg=0.0,
            umidade_pct=14.0,
            impureza_pct=1.0,
            preco_saca=200.0
        )

        # Assert: EntityNotFoundError pois safra é de outro tenant
        with pytest.raises(EntityNotFoundError):
            await service.criar(romaneio_create)

    @pytest.mark.asyncio
    async def test_receita_valor_calculado_corretamente(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Receita deve usar o valor_total calculado do romaneio (sacas × preço)."""
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

        plano = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            codigo="4.01",
            nome="Receita Milho",
            tipo="RECEITA",
            categoria_rfb="RECEITA_ATIVIDADE",
            natureza="ANALITICA",
            ativo=True
        )
        session.add(plano)
        await session.commit()

        # Act
        service = RomaneioService(session, tenant_id)

        # Romaneio: 30000 kg bruto - 0 kg tara = 30000 kg líquido
        # Com padrão MILHO: 60 kg/saca → ~500 sacas
        # Preço: R$ 50/saca → receita_total ≈ R$ 25.000

        romaneio_create = RomaneioColheitaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            data_colheita=date.today(),
            peso_bruto_kg=30000.0,  # 30 toneladas
            tara_kg=0.0,
            umidade_pct=14.0,  # padrão para milho
            impureza_pct=1.0,  # padrão para milho
            preco_saca=50.0
        )

        romaneio = await service.criar(romaneio_create)

        # Assert: Receita deve ter valor = romaneio.receita_total
        receita_stmt = select(Receita).where(
            Receita.origem_id == romaneio.id
        )
        receita = (await session.execute(receita_stmt)).scalars().first()

        assert receita is not None
        assert abs(receita.valor_total - romaneio.receita_total) < 0.01  # Float comparison
        assert receita.valor_total > 0

    @pytest.mark.asyncio
    async def test_romaneio_campos_derivados_antes_receita(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """
        Romaneio deve ter todos os campos derivados (sacas, receita, produtividade)
        calculados antes de criar Receita.
        """
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="SOJA",
            status="COLHEITA",
            area_plantada_ha=50.0  # ← Necessário para calcular produtividade
        )
        session.add(safra)

        plano = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            codigo="4.01",
            nome="Receita Soja",
            tipo="RECEITA",
            categoria_rfb="RECEITA_ATIVIDADE",
            natureza="ANALITICA",
            ativo=True
        )
        session.add(plano)
        await session.commit()

        # Act
        service = RomaneioService(session, tenant_id)

        romaneio_create = RomaneioColheitaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            data_colheita=date.today(),
            peso_bruto_kg=45000.0,  # 45 toneladas
            tara_kg=300.0,
            umidade_pct=12.0,  # Soja: 12% (abaixo padrão 14%)
            impureza_pct=0.5,  # Soja: 0.5% (abaixo padrão 1%)
            preco_saca=100.0
        )

        romaneio = await service.criar(romaneio_create)

        # Assert: Campos derivados devem estar calculados
        assert romaneio.peso_liquido_kg > 0
        assert romaneio.sacas_60kg > 0
        assert romaneio.receita_total > 0
        assert romaneio.produtividade_sc_ha is not None
        assert romaneio.produtividade_sc_ha > 0

        # E Receita deve ter esse valor
        receita_stmt = select(Receita).where(
            Receita.origem_id == romaneio.id
        )
        receita = (await session.execute(receita_stmt)).scalars().first()

        assert receita.valor_total == romaneio.receita_total
