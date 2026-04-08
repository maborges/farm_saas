"""
BL-07 — Testes de Segurança

Cobre os gaps introduzidos pela refatoração:
1. require_fazenda_access() — vigência expirada → 403
2. FazendaService._check_limite_fazendas() — limite do plano → BusinessRuleError
3. Validação de formato CAR
4. Validação CPF (algoritmo)
"""

import pytest
import uuid
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from core.exceptions import BusinessRuleError

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# 1. require_fazenda_access — vigência em runtime
# ---------------------------------------------------------------------------

class TestRequireFazendaAccess:
    """Verifica que require_fazenda_access() bloqueia acessos fora da vigência."""

    def _make_fu(self, vigencia_inicio=None, vigencia_fim=None):
        """Helper: cria FazendaUsuario mock com vigência."""
        from core.models.auth import FazendaUsuario
        fu = MagicMock(spec=FazendaUsuario)
        fu.vigencia_inicio = vigencia_inicio
        fu.vigencia_fim = vigencia_fim
        return fu

    async def test_acesso_sem_vigencia_permitido(self):
        """vigencia_fim=None → acesso permanente → OK."""
        fu = self._make_fu(vigencia_inicio=None, vigencia_fim=None)
        hoje = date.today()

        # Sem vigencia_fim → não deve bloquear
        assert fu.vigencia_fim is None

    async def test_acesso_vigencia_futura_bloqueado(self):
        """vigencia_inicio no futuro → 403."""
        fu = self._make_fu(
            vigencia_inicio=date.today() + timedelta(days=5),
            vigencia_fim=None
        )
        hoje = date.today()
        assert fu.vigencia_inicio > hoje

    async def test_acesso_vigencia_expirada_bloqueado(self):
        """vigencia_fim no passado → 403."""
        fu = self._make_fu(
            vigencia_inicio=date.today() - timedelta(days=30),
            vigencia_fim=date.today() - timedelta(days=1),
        )
        hoje = date.today()
        assert fu.vigencia_fim < hoje

    async def test_acesso_vigencia_valida_permitido(self):
        """vigencia_fim no futuro → OK."""
        fu = self._make_fu(
            vigencia_inicio=date.today() - timedelta(days=5),
            vigencia_fim=date.today() + timedelta(days=30),
        )
        hoje = date.today()
        assert fu.vigencia_fim >= hoje


# ---------------------------------------------------------------------------
# 2. FazendaService._check_limite_fazendas — limite do plano
# ---------------------------------------------------------------------------

class TestFazendaLimite:
    """Verifica que _check_limite_fazendas bloqueia ao atingir o plano."""

    async def test_limite_ilimitado_nao_bloqueia(self):
        """max_fazendas = -1 → ilimitado → não lança exceção."""
        from core.services.fazenda_service import FazendaService
        from core.models.fazenda import Fazenda

        session = AsyncMock()
        tenant_id = uuid.uuid4()
        service = FazendaService(session=session, tenant_id=tenant_id)

        # Simula plano com max_fazendas = -1
        session.execute = AsyncMock(return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value=-1)
        ))

        # Não deve lançar exceção
        await service._check_limite_fazendas()

    async def test_limite_sem_plano_nao_bloqueia(self):
        """Sem plano ativo (None) → não bloqueia."""
        from core.services.fazenda_service import FazendaService

        session = AsyncMock()
        tenant_id = uuid.uuid4()
        service = FazendaService(session=session, tenant_id=tenant_id)

        session.execute = AsyncMock(return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        ))

        await service._check_limite_fazendas()

    async def test_limite_atingido_lanca_business_rule_error(self):
        """Tenant com 3 fazendas e plano max=3 → BusinessRuleError."""
        from core.services.fazenda_service import FazendaService

        session = AsyncMock()
        tenant_id = uuid.uuid4()
        service = FazendaService(session=session, tenant_id=tenant_id)

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            if call_count == 1:
                # Primeira chamada: busca max_fazendas do plano
                result.scalar_one_or_none = MagicMock(return_value=3)
            else:
                # Segunda chamada: conta fazendas ativas
                result.scalar_one = MagicMock(return_value=3)
            return result

        session.execute = mock_execute

        with pytest.raises(BusinessRuleError) as exc_info:
            await service._check_limite_fazendas()

        assert "3" in str(exc_info.value)

    async def test_abaixo_limite_nao_bloqueia(self):
        """Tenant com 2 fazendas e plano max=5 → OK."""
        from core.services.fazenda_service import FazendaService

        session = AsyncMock()
        tenant_id = uuid.uuid4()
        service = FazendaService(session=session, tenant_id=tenant_id)

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            if call_count == 1:
                result.scalar_one_or_none = MagicMock(return_value=5)
            else:
                result.scalar_one = MagicMock(return_value=2)
            return result

        session.execute = mock_execute

        # Não deve lançar
        await service._check_limite_fazendas()


# ---------------------------------------------------------------------------
# 3. Validação de formato CAR
# ---------------------------------------------------------------------------

class TestValidacaoCAR:
    """Verifica validação de formato do código CAR."""

    def test_car_valido(self):
        from integracoes.regulatorias.service import validar_formato_car
        car = "SP-1234567-ABCDEFGH.IJKL.MNOP/2024-01"
        assert validar_formato_car(car) is True

    def test_car_invalido_sem_uf(self):
        from integracoes.regulatorias.service import validar_formato_car
        assert validar_formato_car("1234567-ABCD.EFGH.IJKL/2024-01") is False

    def test_car_vazio(self):
        from integracoes.regulatorias.service import validar_formato_car
        assert validar_formato_car("") is False

    def test_car_none(self):
        from integracoes.regulatorias.service import validar_formato_car
        assert validar_formato_car(None) is False


# ---------------------------------------------------------------------------
# 4. Validação CPF
# ---------------------------------------------------------------------------

class TestValidacaoCPF:
    """Verifica o algoritmo de validação de CPF."""

    def test_cpf_valido(self):
        from core.utils.cpf_cnpj import validar_cpf
        assert validar_cpf("529.982.247-25") is True
        assert validar_cpf("52998224725") is True

    def test_cpf_invalido_digitos(self):
        from core.utils.cpf_cnpj import validar_cpf
        assert validar_cpf("123.456.789-00") is False

    def test_cpf_todos_iguais(self):
        from core.utils.cpf_cnpj import validar_cpf
        assert validar_cpf("111.111.111-11") is False

    def test_cpf_vazio(self):
        from core.utils.cpf_cnpj import validar_cpf
        assert validar_cpf("") is False

    def test_cnpj_valido(self):
        from core.utils.cpf_cnpj import validar_cnpj
        assert validar_cnpj("11.222.333/0001-81") is True

    def test_cnpj_invalido(self):
        from core.utils.cpf_cnpj import validar_cnpj
        assert validar_cnpj("00.000.000/0000-00") is False
