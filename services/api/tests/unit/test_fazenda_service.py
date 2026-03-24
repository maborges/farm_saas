import pytest
import uuid
from core.services.fazenda_service import FazendaService
from core.schemas.fazenda_input import FazendaCreate
from core.exceptions import EntityNotFoundError, TenantViolationError

pytestmark = pytest.mark.asyncio

class TestTenantIsolation:
    """
    Bateria de testes provando que a arquitetura 'BaseService' e 'RLS'
    bloqueia totalmente transações vazadas entre Clientes do SaaS.
    """

    async def test_fazenda_criada_pertence_ao_tenant_ativo(self, session_a, conftest_tenant_a_id=None):
        # Utilizaremos o import dinâmico na fixture pra importar o ID certo:
        from tests.conftest import TENANT_A_ID
        
        # 1. Serviço logado como "Tenant José" (A)
        service = FazendaService(session=session_a, tenant_id=TENANT_A_ID)
        
        # 2. Tentativa de Criação Orgânica
        dados_input = FazendaCreate(
            nome="Fazenda Santa Cruz do José",
            area_total_ha=500.0,
            ativo=True
        )
        
        fazenda = await service.create_fazenda(dados_input)
        
        # 3. Asserção que a Herança do Monolito empurrou o TenantId Corretamente na raça
        assert fazenda.id is not None
        assert fazenda.tenant_id == TENANT_A_ID
        assert fazenda.nome == "Fazenda Santa Cruz do José"

    async def test_tenant_b_nao_consegue_ver_nem_alterar_fazenda_do_tenant_a(self, session_a, session_b):
        from tests.conftest import TENANT_A_ID, TENANT_B_ID
        
        # Configurar ambiente com 1 Fazenda gerada pro T_A
        service_a = FazendaService(session=session_a, tenant_id=TENANT_A_ID)
        fazenda_a = await service_a.create_fazenda(FazendaCreate(nome="Mato Grosso Sul", area_total_ha=100))
        
        # -- GUERRA DE ISOLAMENTO --
        
        # 1. Tenant B loga no sistema (Possui outro Tenant_ID)
        service_b = FazendaService(session=session_b, tenant_id=TENANT_B_ID)
        
        # 2. Tenant B tenta chamar list()
        fazendas_do_b = await service_b.list_all()
        # RESULTADO: A lista tem que vir vazia! A fazenda de A não é dele.
        assert len(fazendas_do_b) == 0
        
        # 3. Tenant B adivinhou a URL /fazendas/{fazenda_a.id} e tenta dar um GET forçado!
        with pytest.raises(EntityNotFoundError) as exc_info:
            await service_b.get_or_fail(fazenda_a.id)
        
        assert "não encontrado neste tenant" in str(exc_info.value)
        
        # 4. Tenant B tenta hackear passando manualmente um JSON malicioso no UPDATE 
        # (Tentando roubar a fazenda dizendo que o tenant_id = B)
        
        # Como Update obriga a ler a entidade primeiro e validá-la, 
        # vai esbarrar de cara no GET e no enforcing blindado!
        with pytest.raises(EntityNotFoundError):
            await service_b.update(fazenda_a.id, {"nome": "Tomei Posse", "tenant_id": str(TENANT_B_ID)})
