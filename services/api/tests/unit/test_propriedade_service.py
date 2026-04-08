"""Testes unitários para o service de Propriedades - C-04."""
import pytest
import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from core.cadastros.propriedades.propriedade_service import (
    ExploracaoRuralService,
    PropriedadeService,
    DocumentoExploracaoService,
)
from core.cadastros.propriedades.propriedade_schemas import ExploracaoCreate
from core.cadastros.propriedades.propriedade_models import (
    ExploracaoRural,
    Propriedade,
    NaturezaVinculo,
)
from core.exceptions import BusinessRuleError, EntityNotFoundError


class TestExploracaoRuralServiceValidacoes:
    """Testes para as validações do ExploracaoRuralService."""

    @pytest.fixture
    def mock_session(self):
        """Mock da sessão SQLAlchemy."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.flush = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Instância do service com mock."""
        tenant_id = uuid.uuid4()
        return ExploracaoRuralService(mock_session, tenant_id)

    @pytest.mark.asyncio
    async def test_validar_data_fim_anterior_gera_erro(self, service):
        """data_fim <= data_inicio deve gerar BusinessRuleError."""
        with pytest.raises(BusinessRuleError) as exc_info:
            await service._validar_data_fim(
                data_inicio=date(2024, 1, 10),
                data_fim=date(2024, 1, 1),
            )
        assert "data_fim deve ser posterior" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validar_data_fim_igual_gera_erro(self, service):
        """data_fim == data_inicio deve gerar BusinessRuleError."""
        with pytest.raises(BusinessRuleError) as exc_info:
            await service._validar_data_fim(
                data_inicio=date(2024, 1, 1),
                data_fim=date(2024, 1, 1),
            )
        assert "data_fim deve ser posterior" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validar_data_fim_none_sucesso(self, service):
        """data_fim None não deve gerar erro."""
        # Não deve levantar exceção
        await service._validar_data_fim(
            data_inicio=date(2024, 1, 1),
            data_fim=None,
        )

    @pytest.mark.asyncio
    async def test_validar_data_fim_posterior_sucesso(self, service):
        """data_fim > data_inicio deve ter sucesso."""
        await service._validar_data_fim(
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 12, 31),
        )

    @pytest.mark.asyncio
    async def test_validar_sobreposicao_sem_conflito(self, service, mock_session):
        """Sem explorações existentes, não deve haver conflito."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        # Não deve levantar exceção
        await service._validar_sobreposicao(
            fazenda_id=uuid.uuid4(),
            propriedade_id=uuid.uuid4(),
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 12, 31),
        )

    @pytest.mark.asyncio
    async def test_validar_sobreposicao_com_conflito(self, service, mock_session):
        """Exploração existente com período sobreposto deve gerar erro."""
        # Mock de uma exploração existente
        expl_existente = MagicMock()
        expl_existente.data_inicio = date(2024, 1, 1)
        expl_existente.data_fim = date(2024, 12, 31)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [expl_existente]
        mock_session.execute.return_value = mock_result

        comeca_antes_termina_depois = date(2024, 6, 1)  # Dentro do período existente
        
        with pytest.raises(BusinessRuleError) as exc_info:
            await service._validar_sobreposicao(
                fazenda_id=uuid.uuid4(),
                propriedade_id=uuid.uuid4(),
                data_inicio=comeca_antes_termina_depois,
                data_fim=date(2025, 1, 1),
            )
        assert "período sobreposto" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validar_sobreposicao_sem_conflito_fora_periodo(self, service, mock_session):
        """Exploração existente fora do período não deve gerar conflito."""
        expl_existente = MagicMock()
        expl_existente.data_inicio = date(2023, 1, 1)
        expl_existente.data_fim = date(2023, 12, 31)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [expl_existente]
        mock_session.execute.return_value = mock_result

        # Nova exploração começa depois que a existente termina
        await service._validar_sobreposicao(
            fazenda_id=uuid.uuid4(),
            propriedade_id=uuid.uuid4(),
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 12, 31),
        )


class TestExploracaoRuralServiceCRUD:
    """Testes para o CRUD do ExploracaoRuralService."""

    @pytest.fixture
    def mock_session(self):
        """Mock da sessão SQLAlchemy."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.flush = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Instância do service com mock."""
        tenant_id = uuid.uuid4()
        return ExploracaoRuralService(mock_session, tenant_id)

    @pytest.mark.asyncio
    async def test_criar_exploracao_sucesso(self, service, mock_session):
        """Criar exploração válida deve funcionar."""
        propriedade_id = uuid.uuid4()
        fazenda_id = uuid.uuid4()
        
        # Mock: propriedade existe
        mock_propriedade = MagicMock()
        mock_propriedade.id = propriedade_id
        
        # Mock: sem sobreposições
        mock_result_execute = MagicMock()
        mock_result_execute.scalars.return_value.all.return_value = []
        mock_result_execute.scalar_one_or_none.return_value = mock_propriedade
        
        mock_session.execute.side_effect = [
            mock_result_execute,  # Para validar propriedade
            mock_result_execute,  # Para validar sobreposição
        ]

        data = ExploracaoCreate(
            fazenda_id=fazenda_id,
            natureza="propria",
            data_inicio=date(2024, 1, 1),
        )

        resultado = await service.criar(propriedade_id, data)
        
        assert resultado is not None
        assert resultado.tenant_id == service.tenant_id
        assert resultado.propriedade_id == propriedade_id
        assert resultado.fazenda_id == fazenda_id
        assert resultado.natureza == "propria"
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_exploracao_propriedade_nao_existe(self, service, mock_session):
        """Criar com propriedade inexistente deve gerar EntityNotFoundError."""
        propriedade_id = uuid.uuid4()
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        data = ExploracaoCreate(
            fazenda_id=uuid.uuid4(),
            natureza="propria",
            data_inicio=date(2024, 1, 1),
        )

        with pytest.raises(EntityNotFoundError) as exc_info:
            await service.criar(propriedade_id, data)
        assert "Propriedade não encontrada" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_listar_por_propriedade(self, service, mock_session):
        """listar_por_propriedade deve retornar explorações ordenadas."""
        propriedade_id = uuid.uuid4()
        
        mock_exploracoes = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_exploracoes
        mock_session.execute.return_value = mock_result

        resultado = await service.listar_por_propriedade(propriedade_id)
        
        assert resultado == mock_exploracoes

    @pytest.mark.asyncio
    async def test_listar_vigentes_por_fazenda(self, service, mock_session):
        """listar_vigentes_por_fazenda deve retornar apenas explorações vigentes."""
        fazenda_id = uuid.uuid4()
        
        mock_exploracoes = [MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_exploracoes
        mock_session.execute.return_value = mock_result

        resultado = await service.listar_vigentes_por_fazenda(fazenda_id)
        
        assert resultado == mock_exploracoes

    @pytest.mark.asyncio
    async def test_obter_exploracao_existente(self, service, mock_session):
        """obter deve retornar exploração quando existe."""
        exploracao_id = uuid.uuid4()
        
        mock_exploracao = MagicMock()
        mock_exploracao.id = exploracao_id
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_exploracao
        mock_session.execute.return_value = mock_result

        resultado = await service.obter(exploracao_id)
        
        assert resultado == mock_exploracao

    @pytest.mark.asyncio
    async def test_obter_exploracao_nao_existente(self, service, mock_session):
        """obter deve retornar None quando não existe."""
        exploracao_id = uuid.uuid4()
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        resultado = await service.obter(exploracao_id)
        
        assert resultado is None

    @pytest.mark.asyncio
    async def test_remover_exploracao(self, service, mock_session):
        """remover deve setar ativo=False."""
        exploracao_id = uuid.uuid4()
        
        mock_exploracao = MagicMock()
        mock_exploracao.ativo = True
        
        # Mock para obter
        mock_result_obter = MagicMock()
        mock_result_obter.scalar_one_or_none.return_value = mock_exploracao
        
        # Mock para outras chamadas
        mock_result_execute = MagicMock()
        mock_result_execute.scalar_one_or_none.return_value = mock_exploracao
        
        mock_session.execute.side_effect = [mock_result_obter, mock_result_execute]

        await service.remover(exploracao_id)
        
        assert mock_exploracao.ativo is False
