import pytest
import uuid
from core.services.unidade_produtiva_service import UnidadeProdutivaService as FazendaService
from core.schemas.fazenda_input import FazendaCreate
from core.exceptions import EntityNotFoundError

pytestmark = pytest.mark.asyncio

class TestTenantIsolation:
    """
    Bateria de testes provando que a arquitetura 'BaseService' e 'RLS'
    bloqueia totalmente transações vazadas entre Clientes do SaaS.
    """

    async def test_fazenda_criada_pertence_ao_tenant_ativo(self, session_a):
        from tests.conftest import TENANT_A_ID

        service = FazendaService(session=session_a, tenant_id=TENANT_A_ID)

        dados_input = FazendaCreate(
            nome="Fazenda Santa Cruz do José",
            area_total_ha=500.0,
            ativo=True
        )

        fazenda = await service.create_fazenda(dados_input)

        assert fazenda.id is not None
        assert fazenda.tenant_id == TENANT_A_ID
        assert fazenda.nome == "Fazenda Santa Cruz do José"

    async def test_tenant_b_nao_consegue_ver_nem_alterar_fazenda_do_tenant_a(self, session_a, session_b):
        from tests.conftest import TENANT_A_ID, TENANT_B_ID

        service_a = FazendaService(session=session_a, tenant_id=TENANT_A_ID)
        fazenda_a = await service_a.create_fazenda(FazendaCreate(nome="Mato Grosso Sul", area_total_ha=100))

        service_b = FazendaService(session=session_b, tenant_id=TENANT_B_ID)

        fazendas_do_b = await service_b.list_all()
        assert len(fazendas_do_b) == 0

        with pytest.raises(EntityNotFoundError):
            await service_b.get_or_fail(fazenda_a.id)

        with pytest.raises(EntityNotFoundError):
            await service_b.update(fazenda_a.id, {"nome": "Tomei Posse", "tenant_id": str(TENANT_B_ID)})
