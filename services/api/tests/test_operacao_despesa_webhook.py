"""
Testes para webhook: Operação → Despesa Automática.

Valida:
1. Operação com custo_total > 0 cria Despesa automaticamente
2. Operação sem custo não cria Despesa
3. Rastreabilidade via origem_id + origem_tipo
4. Tenant isolation
5. Integração com PlanoConta (categoria CUSTEIO)
"""
import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.exceptions import EntityNotFoundError
from agricola.operacoes.service import OperacaoService
from agricola.operacoes.schemas import OperacaoAgricolaCreate
from agricola.safras.models import Safra
from agricola.talhoes.models import Talhao
from financeiro.models.despesa import Despesa
from financeiro.models.plano_conta import PlanoConta


class TestOperacaoDespesaWebhook:
    """Testes de automação de despesa ao criar operação."""

    @pytest.mark.asyncio
    async def test_operacao_com_custo_cria_despesa_automatica(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Operação com custo_total > 0 deve criar Despesa automaticamente."""
        # Setup: Criar safra
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

        # Criar plano de conta para despesa (necessário)
        plano = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            descricao="Custeio - Operações Agrícolas",
            categoria_rfb="CUSTEIO",
            natureza="ANALITICA",
            ativo=True
        )
        session.add(plano)
        await session.commit()

        # Act: Criar operação com custo
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="COLHEITA",
            descricao="Colheita mecanizada",
            data_realizada=date.today(),
            area_aplicada_ha=50.0,
            custo_total=5000.0,  # ← Custo > 0
            insumos=[]
        )

        operacao = await service.criar(operacao_create)

        # Assert: Despesa deve ter sido criada
        despesa_stmt = select(Despesa).where(
            Despesa.origem_id == operacao.id,
            Despesa.origem_tipo == "OPERACAO_AGRICOLA"
        )
        despesa = (await session.execute(despesa_stmt)).scalars().first()

        assert despesa is not None, "Despesa não foi criada automaticamente"
        assert despesa.valor_total == operacao.custo_total
        assert despesa.status == "PAGO"
        assert despesa.origem_tipo == "OPERACAO_AGRICOLA"

    @pytest.mark.asyncio
    async def test_operacao_sem_custo_nao_cria_despesa(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Operação com custo_total = 0 não deve criar Despesa."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="PLANTIO",
            area_plantada_ha=50.0
        )
        session.add(safra)
        await session.commit()

        # Act: Criar operação COM insumos (mas simulate zero custo)
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="PLANTIO",
            descricao="Plantio manual",
            data_realizada=date.today(),
            area_aplicada_ha=10.0,
            custo_total=0.0,  # ← Sem custo
            insumos=[]
        )

        operacao = await service.criar(operacao_create)

        # Assert: Despesa NÃO deve ter sido criada
        despesa_stmt = select(Despesa).where(
            Despesa.origem_id == operacao.id
        )
        despesa = (await session.execute(despesa_stmt)).scalars().first()

        assert despesa is None, "Despesa não deveria ter sido criada (custo = 0)"

    @pytest.mark.asyncio
    async def test_rastreabilidade_operacao_despesa(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Despesa deve ter origem_id linkado à operação para rastreabilidade."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="SOJA",
            status="DESENVOLVIMENTO",
            area_plantada_ha=100.0
        )
        session.add(safra)

        plano = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            descricao="Custeio",
            categoria_rfb="CUSTEIO",
            natureza="ANALITICA",
            ativo=True
        )
        session.add(plano)
        await session.commit()

        # Act
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="ADUBAÇÃO",
            descricao="Adubação de cobertura",
            data_realizada=date.today(),
            area_aplicada_ha=50.0,
            custo_total=2500.0,
            insumos=[]
        )

        operacao = await service.criar(operacao_create)

        # Assert: Buscar despesa por origem_id
        despesa_stmt = select(Despesa).where(
            Despesa.origem_id == operacao.id,
            Despesa.origem_tipo == "OPERACAO_AGRICOLA"
        )
        despesa = (await session.execute(despesa_stmt)).scalars().first()

        assert despesa is not None
        assert despesa.origem_id == operacao.id
        assert despesa.origem_tipo == "OPERACAO_AGRICOLA"
        assert "Adubação" in despesa.descricao or "ADUBAÇÃO" in despesa.descricao

    @pytest.mark.asyncio
    async def test_tenant_isolation_operacao_despesa(
        self,
        session: AsyncSession,
        tenant_id: str,
        outro_tenant_id: str,
        talhao_id: str
    ):
        """Despesa de um tenant não deveria ser criada para operação de outro tenant."""
        # Setup: Safra de outro tenant
        safra_outro = Safra(
            id=uuid4(),
            tenant_id=outro_tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="DESENVOLVIMENTO",
            area_plantada_ha=50.0
        )
        session.add(safra_outro)
        await session.commit()

        # Act: Tentar criar operação com tenant_id diferente
        service = OperacaoService(session, tenant_id)  # ← tenant_id diferente

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra_outro.id,  # ← Safra de outro tenant
            talhao_id=talhao_id,
            tipo="PULVERIZAÇÃO",
            descricao="Pulverização",
            data_realizada=date.today(),
            area_aplicada_ha=10.0,
            custo_total=1000.0,
            insumos=[]
        )

        # Assert: EntityNotFoundError pois safra é de outro tenant
        with pytest.raises(EntityNotFoundError):
            await service.criar(operacao_create)

    @pytest.mark.asyncio
    async def test_despesa_descricao_inclui_tipo_e_safra(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Despesa deve ter descricção com tipo de operação e safra."""
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

        plano = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            descricao="Custeio",
            categoria_rfb="CUSTEIO",
            natureza="ANALITICA",
            ativo=True
        )
        session.add(plano)
        await session.commit()

        # Act
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="COLHEITA",
            descricao="Colheita da safra",
            data_realizada=date.today(),
            area_aplicada_ha=50.0,
            custo_total=5000.0,
            insumos=[]
        )

        operacao = await service.criar(operacao_create)

        # Assert: Despesa tem descricção informativa
        despesa_stmt = select(Despesa).where(
            Despesa.origem_id == operacao.id
        )
        despesa = (await session.execute(despesa_stmt)).scalars().first()

        assert despesa is not None
        assert "COLHEITA" in despesa.descricao  # Tipo de operação
        assert "MILHO" in despesa.descricao or "2025/26" in despesa.descricao  # Safra info

    @pytest.mark.asyncio
    async def test_despesa_data_operacao(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Despesa deve usar data_realizada da operação como data de emissão/vencimento."""
        # Setup
        data_op = date(2025, 6, 15)

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

        plano = PlanoConta(
            id=uuid4(),
            tenant_id=tenant_id,
            descricao="Custeio",
            categoria_rfb="CUSTEIO",
            natureza="ANALITICA",
            ativo=True
        )
        session.add(plano)
        await session.commit()

        # Act
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="COLHEITA",
            descricao="Colheita",
            data_realizada=data_op,  # ← Data específica
            area_aplicada_ha=50.0,
            custo_total=5000.0,
            insumos=[]
        )

        operacao = await service.criar(operacao_create)

        # Assert: Despesa tem mesma data
        despesa_stmt = select(Despesa).where(
            Despesa.origem_id == operacao.id
        )
        despesa = (await session.execute(despesa_stmt)).scalars().first()

        assert despesa.data_emissao == data_op
        assert despesa.data_vencimento == data_op
        assert despesa.data_pagamento == data_op

    @pytest.mark.asyncio
    async def test_operacao_tipo_invalido_nao_cria_despesa(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """
        Se operação falha por tipo inválido (RN), despesa não deve ser criada.
        Testa integração entre validação de RN e webhook.
        """
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

        # Act: Tentar criar operação PLANTIO em fase COLHEITA (vai falhar)
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="PLANTIO",  # ← Tipo NÃO permitido em COLHEITA
            descricao="Plantio em COLHEITA (deve falhar)",
            data_realizada=date.today(),
            area_aplicada_ha=10.0,
            custo_total=1000.0,  # ← Tem custo, mas vai falhar
            insumos=[]
        )

        # Assert: Operação falha, e também nenhuma despesa é criada
        from core.exceptions import BusinessRuleError

        with pytest.raises(BusinessRuleError):
            await service.criar(operacao_create)

        # Verificar que nenhuma despesa foi criada (mesmo com custo)
        despesa_stmt = select(Despesa).where(
            Despesa.descricao.contains("Plantio em COLHEITA")
        )
        despesa = (await session.execute(despesa_stmt)).scalars().first()

        assert despesa is None, "Despesa não deveria ter sido criada (operação falhou)"
