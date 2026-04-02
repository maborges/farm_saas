"""
Template para testes de integração - Módulo Agrícola

Este arquivo serve como template para criar novos testes de integração.
Copie e adapte para suas necessidades.
"""
import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Import models e schemas
from agricola.safras.models import Safra
from agricola.operacoes.models import OperacaoAgricola
from agricola.operacoes.schemas import OperacaoAgricolaCreate
from agricola.operacoes.service import OperacaoService
from core.exceptions import BusinessRuleError, EntityNotFoundError


class TestOperacoesAgricolasIntegration:
    """
    Template de testes de integração para Operações Agrícolas.
    
    Este template testa:
    1. Criação de operação
    2. Validações de regra de negócio
    3. Isolamento de tenant
    4. Integração com outros módulos
    """

    @pytest.mark.asyncio
    async def test_criar_operacao_sucesso(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """
        Teste básico de criação de operação.
        
        Arrange: Criar safra em fase adequada
        Act: Criar operação com dados válidos
        Assert: Operação criada com todos os campos
        """
        # Arrange
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="SOJA",
            status="PLANTIO",  # Fase que permite PLANTIO
            area_plantada_ha=100.0
        )
        session.add(safra)
        await session.commit()

        # Act
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="PLANTIO",
            descricao="Plantio de soja",
            data_realizada=date(2025, 11, 15),
            area_aplicada_ha=100.0,
            custo_total=10000.0,
            insumos=[]
        )

        operacao = await service.criar(operacao_create)

        # Assert
        assert operacao.id is not None
        assert operacao.tipo == "PLANTIO"
        # Custo total é recalculado baseado nos insumos (0 quando sem insumos)
        assert operacao.custo_total == 0.0
        assert operacao.area_aplicada_ha == 100.0

    @pytest.mark.asyncio
    async def test_operacao_fase_invalida(
        self,
        session: AsyncSession,
        tenant_id: str,
        talhao_id: str
    ):
        """
        Testa validação: operação não permitida na fase atual.
        
        Arrange: Criar safra em fase COLHEITA
        Act: Tentar criar operação de PLANTIO
        Assert: BusinessRuleError é levantada
        """
        # Arrange
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="SOJA",
            status="COLHEITA",  # Fase que NÃO permite PLANTIO
            area_plantada_ha=100.0
        )
        session.add(safra)
        await session.commit()

        # Act & Assert
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="PLANTIO",  # Não permitido em COLHEITA
            descricao="Plantio inválido",
            data_realizada=date.today(),
            area_aplicada_ha=100.0,
            custo_total=0.0,
            insumos=[]
        )

        with pytest.raises(BusinessRuleError) as exc_info:
            await service.criar(operacao_create)

        assert "não é permitido" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_isolamento_tenant_operacao(
        self,
        session: AsyncSession,
        tenant_id: str,
        outro_tenant_id: str,
        talhao_id: str
    ):
        """
        Testa isolamento de tenant.
        
        Arrange: Criar safra no Tenant B
        Act: Tentar criar operação no Tenant A usando safra do Tenant B
        Assert: EntityNotFoundError
        """
        # Arrange
        safra_outro = Safra(
            id=uuid4(),
            tenant_id=outro_tenant_id,  # Safra de outro tenant
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="SOJA",
            status="PLANTIO",
            area_plantada_ha=100.0
        )
        session.add(safra_outro)
        await session.commit()

        # Act & Assert
        service = OperacaoService(session, tenant_id)  # Service do Tenant A

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra_outro.id,  # Safra do Tenant B
            talhao_id=talhao_id,
            tipo="PLANTIO",
            descricao="Operação inválida",
            data_realizada=date.today(),
            area_aplicada_ha=100.0,
            custo_total=0.0,
            insumos=[]
        )

        with pytest.raises(EntityNotFoundError):
            await service.criar(operacao_create)

    @pytest.mark.asyncio
    async def test_operacao_com_insumos(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """
        Testa criação de operação com insumos.
        
        Arrange: Criar safra e produto (insumo)
        Act: Criar operação com lista de insumos
        Assert: Operação e insumos criados corretamente
        """
        # Arrange
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
        await session.commit()

        # TODO: Adicionar criação de produto e estoque

        # Act
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="PULVERIZACAO",
            descricao="Pulverização fungicida",
            data_realizada=date.today(),
            area_aplicada_ha=50.0,
            custo_total=2500.0,
            insumos=[
                # TODO: Adicionar insumos
            ]
        )

        operacao = await service.criar(operacao_create)

        # Assert
        assert operacao.id is not None
        # TODO: Validar insumos criados

    @pytest.mark.asyncio
    async def test_operacao_data_futura(
        self,
        session: AsyncSession,
        tenant_id: str,
        talhao_id: str
    ):
        """
        Testa validação: operação com data futura.
        
        Arrange: Criar safra
        Act: Tentar criar operação com data futura
        Assert: Validação de data (se implementada)
        """
        # Arrange
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="SOJA",
            status="PLANTIO",
            area_plantada_ha=100.0
        )
        session.add(safra)
        await session.commit()

        # Act
        service = OperacaoService(session, tenant_id)

        from datetime import timedelta
        data_futura = date.today() + timedelta(days=30)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="PLANTIO",
            descricao="Plantio futuro",
            data_realizada=data_futura,  # Data no futuro
            area_aplicada_ha=100.0,
            custo_total=0.0,
            insumos=[]
        )

        # TODO: Implementar validação de data futura
        # with pytest.raises(BusinessRuleError):
        #     await service.criar(operacao_create)


# MARKERS para rodar testes específicos:
# pytest -m agricola
# pytest -m integration
# pytest tests/agricola/test_operacoes_integration.py
