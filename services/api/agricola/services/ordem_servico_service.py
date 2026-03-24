from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from agricola.models.ordem_servico import OrdemServico
from agricola.models.safra import Safra
from agricola.schemas.ordem_servico_schema import OrdemServicoCreate, OrdemServicoUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from datetime import date

class OrdemServicoService(BaseService[OrdemServico]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(OrdemServico, session, tenant_id)
        
    async def create_ordem(self, obj_in: OrdemServicoCreate | dict) -> OrdemServico:
        # Puxa o dicionário
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        
        # 1 RNI (Regra de Negócio Inegociável): Valida se a safra atrelada à OS realmente existe e pertence à mesma Fazenda
        stmt = select(Safra).where(
            Safra.id == obj_data["safra_id"], 
            Safra.tenant_id == self.tenant_id,
            Safra.fazenda_id == obj_data["fazenda_id"]
        )
        result = await self.session.execute(stmt)
        safra = result.scalars().first()
        
        if not safra:
            raise BusinessRuleError("Safra não encontrada OU não pertence a esta fazenda informada.")

        # Cria a entidade
        db_obj = OrdemServico(**obj_data, tenant_id=self.tenant_id)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update_status(self, os_id: uuid.UUID, new_status: str) -> OrdemServico:
        # RNI sobre Carga de Status de OS
        os = await self.get(os_id)
        if not os:
            raise BusinessRuleError("OS não encontrada.")
            
        valid_statuses = ["PLANEJADA", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADA"]
        if new_status not in valid_statuses:
            raise BusinessRuleError(f"Status inválido. Permitidos: {', '.join(valid_statuses)}")
            
        if new_status == "CONCLUIDA" and not os.data_execucao:
             # Só pode concluir se marcou a data da execução
             os.data_execucao = date.today()

        os.status = new_status
        await self.session.flush()
        await self.session.refresh(os)
        return os
