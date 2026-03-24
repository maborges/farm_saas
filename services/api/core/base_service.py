from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, delete
from pydantic import BaseModel
import uuid
from core.exceptions import EntityNotFoundError, TenantViolationError

# O tipo T representará o Model SQLAlchemy (ex: Animal, Fazenda)
T = TypeVar('T')

class BaseService(Generic[T]):
    """
    O coração do Monolito Modular: o BaseService atua como um Repository Pattern.
    NENHUM acesso ao banco fora desse pattern é permitido nas camadas superiores para garantir que 
    o filtro `tenant_id` **sempre** seja injetado programaticamente (Defense in Depth / Camada 2).
    """

    def __init__(self, model: Type[T], session: AsyncSession, tenant_id: uuid.UUID):
        self.model = model
        self.session = session
        self.tenant_id = tenant_id

    async def _enforce_tenant(self, obj: Any):
        """Impede que alguém edite/salve objeto que pertence a outro tenant no meio do processo."""
        if hasattr(obj, "tenant_id") and obj.tenant_id != self.tenant_id:
            raise TenantViolationError(f"Tentativa de vazamento de dados interceptada no Service.")

    async def get(self, id: Any) -> Optional[T]:
        """Busca um id cravando cláusula do tenant atrelada sempre."""
        stmt = select(self.model).where(
            and_(
                self.model.id == id,
                self.model.tenant_id == self.tenant_id
            )
        )
        result = await self.session.execute(stmt)
        res = result.scalar_one_or_none()
        return res

    async def get_or_fail(self, id: Any) -> T:
        obj = await self.get(id)
        if not obj:
            raise EntityNotFoundError(f"{self.model.__name__} com ID {id} não encontrado neste tenant.")
        return obj

    async def list_all(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        """Sempre injeta o `tenant_id == self.tenant_id` por baixo dos panos na query"""
        stmt = select(self.model).where(
            self.model.tenant_id == self.tenant_id
        )
        
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                stmt = stmt.where(getattr(self.model, field) == value)

        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: BaseModel | dict) -> T:
        """Aceita um schema pydantic validado, cria e crava o Tenant cravando na marra"""
        obj_data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
        
        # Garante a assinatura do dono local
        obj_data["tenant_id"] = self.tenant_id
        
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        # O commit principal geralmente é feito no Router, mas por segurança flushes ocorrem
        await self.session.flush()
        return db_obj

    async def update(self, id: Any, obj_in: BaseModel | dict) -> T:
        db_obj = await self.get_or_fail(id)
        
        obj_data = obj_in.model_dump(exclude_unset=True) if isinstance(obj_in, BaseModel) else obj_in
        
        # Prevenindo injeção de troca de tenant via JSON Payload
        if "tenant_id" in obj_data:
            del obj_data["tenant_id"]
            
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
            
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def hard_delete(self, id: Any) -> None:
        db_obj = await self.get_or_fail(id)
        await self.session.delete(db_obj)
        await self.session.flush()
