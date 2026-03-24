from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_service import BaseService

from agricola.cadastros.models import Cultura

class CulturaService(BaseService[Cultura]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(Cultura, session, tenant_id)
