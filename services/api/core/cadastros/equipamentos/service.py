import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.exceptions import EntityNotFoundError
from .models import Equipamento
from .schemas import EquipamentoCreate, EquipamentoUpdate


class EquipamentoService(BaseService[Equipamento]):

    async def listar(self, tipo: Optional[str] = None, status: Optional[str] = None) -> list[Equipamento]:
        stmt = select(Equipamento).where(Equipamento.tenant_id == self.tenant_id)
        if tipo:
            stmt = stmt.where(Equipamento.tipo == tipo)
        if status:
            stmt = stmt.where(Equipamento.status == status)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar(self, data: EquipamentoCreate) -> Equipamento:
        eq = Equipamento(tenant_id=self.tenant_id, **data.model_dump())
        self.session.add(eq)
        await self.session.flush()
        await self.session.refresh(eq)
        return eq

    async def obter(self, eq_id: uuid.UUID) -> Equipamento:
        stmt = select(Equipamento).where(Equipamento.id == eq_id, Equipamento.tenant_id == self.tenant_id)
        obj = (await self.session.execute(stmt)).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Equipamento não encontrado")
        return obj

    async def atualizar(self, eq_id: uuid.UUID, data: EquipamentoUpdate) -> Equipamento:
        obj = await self.obter(eq_id)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def desativar(self, eq_id: uuid.UUID) -> None:
        obj = await self.obter(eq_id)
        obj.status = "INATIVO"
