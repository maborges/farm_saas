from core.base_service import BaseService
from core.models.fazenda import Fazenda
from core.schemas.fazenda_input import FazendaCreate
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class FazendaService(BaseService[Fazenda]):
    """
    Serviço que gerencia o ciclo de vida das fazendas do AgroSaaS.
    Herda do BaseService que assegura blindagem por tenant_id de forma automática.
    """
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        # Passamos a classe model `Fazenda` para o genérico do BaseService
        super().__init__(Fazenda, session, tenant_id)

    # Aqui podemos adicionar lógicas extras de Fazenda que não existem no CRUD Base
    # Exemplo: async def fetch_climatic_data_for_fazenda(self, fazenda_id): ...
    
    async def create_fazenda(self, dados: FazendaCreate) -> Fazenda:
        # Business logic: Antes de criar, poderíamos somar os hectares de todas as fazendas 
        # do tenant e ver se ele não estourou o limite de Hectares do Plano dele (Ex: Plano Starter = max 200 ha).
        return await super().create(dados)
