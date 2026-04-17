import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from pecuaria.models.lote import LoteBovino
from pecuaria.models.piquete import Piquete
from pecuaria.schemas.lote_schema import LoteBovinoCreate

class LoteBovinoService(BaseService[LoteBovino]):
    def __init__(self, tenant_id: uuid.UUID):
        # NOTE: Ideally this expects session as well in __init__(self, model, session, tenant_id)
        # but let's see how it was called in router
        super().__init__(LoteBovino, None, tenant_id) # Session is passed in the methods there?


    async def create_lote(self, db: AsyncSession, *, obj_in: LoteBovinoCreate) -> LoteBovino:
        obj_data = obj_in.model_dump()
        
        # 1. Regra de Negócio Pecuária: Se especificou piquete, verifica se ele pertence a esta fazenda e tenant
        if obj_data.get("piquete_id"):
            stmt_piquete = select(Piquete).where(
                Piquete.id == obj_data["piquete_id"],
                Piquete.unidade_produtiva_id == obj_data["unidade_produtiva_id"],
                Piquete.tenant_id == self.tenant_id,
                Piquete.ativo == True
            )
            piquete = (await db.execute(stmt_piquete)).scalars().first()
            if not piquete:
                raise BusinessRuleError("O Piquete selecionado não existe ou não pertence a esta fazenda.")
        
        # 2. Mapeia piquete_id → area_id (nome do campo no modelo)
        if "piquete_id" in obj_data:
            obj_data["area_id"] = obj_data.pop("piquete_id")

        # 3. Persiste Lote Principal
        db_lote = LoteBovino(**obj_data, tenant_id=self.tenant_id)
        db.add(db_lote)
        await db.flush()
        await db.refresh(db_lote)
        
        return db_lote
