from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from core.base_service import BaseService
from agricola.prescricoes.models import PrescricaoVRA

class PrescricaoService(BaseService[PrescricaoVRA]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(PrescricaoVRA, session, tenant_id)
