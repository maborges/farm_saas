import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from pecuaria.models.piquete import Piquete
from pecuaria.schemas.piquete_schema import PiqueteCreate


class PiqueteService(BaseService[Piquete]):
    """
    Service de CRUD para Piquetes/Pastagens da fazenda.

    Args:
        tenant_id: ID do tenant para isolamento de dados.
    """

    def __init__(self, tenant_id: uuid.UUID):
        super().__init__(Piquete, None, tenant_id)

    async def listar_por_fazenda(
        self, db: AsyncSession, *, unidade_produtiva_id: uuid.UUID
    ) -> list[Piquete]:
        """Lista piquetes ativos de uma fazenda específica."""
        stmt = (
            select(self.model)
            .where(
                self.model.tenant_id == self.tenant_id,
                self.model.unidade_produtiva_id == unidade_produtiva_id,
                self.model.ativo == True,
            )
            .order_by(self.model.nome)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def criar_piquete(
        self, db: AsyncSession, *, obj_in: PiqueteCreate
    ) -> Piquete:
        """Cria um novo piquete vinculado ao tenant."""
        obj_data = obj_in.model_dump()
        db_piquete = Piquete(**obj_data, tenant_id=self.tenant_id)
        db.add(db_piquete)
        await db.flush()
        await db.refresh(db_piquete)
        return db_piquete
