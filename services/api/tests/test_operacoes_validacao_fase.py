"""
Testes para validação de operações agrícolas.

Valida:
1. Operação só permitida em fases específicas (RN)
2. Data não pode ser futura
3. Tenant isolation
"""
import pytest
from uuid import uuid4
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BusinessRuleError, EntityNotFoundError
from agricola.operacoes.service import OperacaoService
from agricola.safras.models import Safra
from agricola.operacoes.models import OperacaoAgricola
from agricola.models import OperacaoTipoFase
from agricola.operacoes.schemas import OperacaoAgricolaCreate, InsumoOperacaoCreate


class TestOperacaoValidacaoFase:
    """Testes de validação de fase da safra."""

    @pytest.mark.asyncio
    async def test_operacao_plantio_em_fase_colheita_deve_falhar(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Operação PLANTIO não deve ser permitida em fase COLHEITA."""
        # Setup: Criar safra em fase COLHEITA
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="COLHEITA",  # ← COLHEITA
            area_plantada_ha=50.0
        )
        session.add(safra)
        await session.commit()

        # Act & Assert: Tentar criar operação PLANTIO deve falhar
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="PLANTIO",  # ← Tipo PLANTIO
            subtipo="Manual",
            descricao="Teste plantio em COLHEITA",
            data_realizada=date.today(),
            area_aplicada_ha=10.0,
            insumos=[]
        )

        with pytest.raises(BusinessRuleError) as exc_info:
            await service.criar(operacao_create)

        assert "PLANTIO" in str(exc_info.value)
        assert "COLHEITA" in str(exc_info.value)
        assert "não é permitida" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_operacao_colheita_em_fase_colheita_deve_suceder(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Operação COLHEITA deve ser permitida em fase COLHEITA."""
        # Setup: Criar safra em fase COLHEITA
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="COLHEITA",  # ← COLHEITA
            area_plantada_ha=50.0
        )
        session.add(safra)
        await session.commit()

        # Act: Criar operação COLHEITA
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="COLHEITA",  # ← Tipo permitido em COLHEITA
            descricao="Colheita mecanizada",
            data_realizada=date.today(),
            area_aplicada_ha=50.0,
            insumos=[]
        )

        operacao = await service.criar(operacao_create)

        # Assert
        assert operacao.id is not None
        assert operacao.tipo == "COLHEITA"
        assert operacao.fase_safra == "COLHEITA"

    @pytest.mark.asyncio
    async def test_operacao_com_data_futura_deve_falhar(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Operação com data futura deve ser rejeitada."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="DESENVOLVIMENTO",
            area_plantada_ha=50.0
        )
        session.add(safra)
        await session.commit()

        # Act & Assert
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="PULVERIZAÇÃO",
            descricao="Pulverização futura",
            data_realizada=date.today() + timedelta(days=5),  # ← Data futura
            area_aplicada_ha=10.0,
            insumos=[]
        )

        with pytest.raises(BusinessRuleError) as exc_info:
            await service.criar(operacao_create)

        assert "futura" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_operacao_tipo_nao_cadastrado_deve_falhar(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Operação com tipo não cadastrado na lookup table deve falhar."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="DESENVOLVIMENTO",
            area_plantada_ha=50.0
        )
        session.add(safra)
        await session.commit()

        # Act & Assert
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="TIPO_INEXISTENTE",  # ← Tipo não existe em lookup
            descricao="Teste tipo inválido",
            data_realizada=date.today(),
            area_aplicada_ha=10.0,
            insumos=[]
        )

        with pytest.raises(BusinessRuleError) as exc_info:
            await service.criar(operacao_create)

        assert "TIPO_INEXISTENTE" in str(exc_info.value)
        assert "cadastrado" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tenant_isolation_operacao_safra_outro_tenant(
        self,
        session: AsyncSession,
        tenant_id: str,
        outro_tenant_id: str,
        talhao_id: str
    ):
        """Operação não deve ser criada para safra de outro tenant."""
        # Setup: Safra de outro tenant
        safra_outro = Safra(
            id=uuid4(),
            tenant_id=outro_tenant_id,  # ← Outro tenant
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="DESENVOLVIMENTO",
            area_plantada_ha=50.0
        )
        session.add(safra_outro)
        await session.commit()

        # Act & Assert: Serviço de tenant_id não deveria encontrar safra
        service = OperacaoService(session, tenant_id)  # ← tenant_id diferente

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra_outro.id,
            talhao_id=talhao_id,
            tipo="ADUBAÇÃO",
            descricao="Teste tenant isolation",
            data_realizada=date.today(),
            area_aplicada_ha=10.0,
            insumos=[]
        )

        with pytest.raises(EntityNotFoundError):
            await service.criar(operacao_create)

    @pytest.mark.asyncio
    async def test_operacao_snapshot_fase_safra(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
        talhao_id: str
    ):
        """Operação deve registrar snapshot da fase_safra no momento da criação."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="DESENVOLVIMENTO",  # ← Status atual
            area_plantada_ha=50.0
        )
        session.add(safra)
        await session.commit()

        # Act
        service = OperacaoService(session, tenant_id)

        operacao_create = OperacaoAgricolaCreate(
            safra_id=safra.id,
            talhao_id=talhao_id,
            tipo="ADUBAÇÃO",
            descricao="Adubação de cobertura",
            data_realizada=date.today(),
            area_aplicada_ha=10.0,
            insumos=[]
        )

        operacao = await service.criar(operacao_create)

        # Assert: fase_safra deve ter o valor do status no momento da criação
        assert operacao.fase_safra == "DESENVOLVIMENTO"

    @pytest.mark.asyncio
    async def test_operacao_lookup_table_multiplas_fases(
        self,
        session: AsyncSession,
        tenant_id: str,
        talhao_id: str
    ):
        """Operação PULVERIZAÇÃO deve ser permitida em múltiplas fases."""
        # PULVERIZAÇÃO → [DESENVOLVIMENTO, COLHEITA]

        # Test 1: DESENVOLVIMENTO
        safra_dev = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="DESENVOLVIMENTO",
            area_plantada_ha=50.0
        )
        session.add(safra_dev)
        await session.commit()

        service = OperacaoService(session, tenant_id)
        op_dev = await service.criar(OperacaoAgricolaCreate(
            safra_id=safra_dev.id,
            talhao_id=talhao_id,
            tipo="PULVERIZAÇÃO",
            descricao="Pulverização em DESENVOLVIMENTO",
            data_realizada=date.today(),
            area_aplicada_ha=10.0,
            insumos=[]
        ))
        assert op_dev.fase_safra == "DESENVOLVIMENTO"

        # Test 2: COLHEITA
        safra_colh = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            ano_safra="2025/26",
            cultura="MILHO",
            status="COLHEITA",
            area_plantada_ha=50.0
        )
        session.add(safra_colh)
        await session.commit()

        op_colh = await service.criar(OperacaoAgricolaCreate(
            safra_id=safra_colh.id,
            talhao_id=talhao_id,
            tipo="PULVERIZAÇÃO",
            descricao="Pulverização em COLHEITA",
            data_realizada=date.today(),
            area_aplicada_ha=10.0,
            insumos=[]
        ))
        assert op_colh.fase_safra == "COLHEITA"
