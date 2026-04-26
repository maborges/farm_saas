import uuid
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.exceptions import EntityNotFoundError
from .models import ProdutoColhido
from .schemas import ProdutoColhidoCreate, ProdutoColhidoUpdate


class ProdutoColhidoService(BaseService[ProdutoColhido]):

    async def listar(
        self,
        safra_id: Optional[uuid.UUID] = None,
        commodity_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> list[ProdutoColhido]:
        stmt = select(ProdutoColhido).where(ProdutoColhido.tenant_id == self.tenant_id)
        if safra_id:
            stmt = stmt.where(ProdutoColhido.safra_id == safra_id)
        if commodity_id:
            stmt = stmt.where(ProdutoColhido.commodity_id == commodity_id)
        if status:
            stmt = stmt.where(ProdutoColhido.status == status)
        result = await self.session.execute(stmt.order_by(ProdutoColhido.data_entrada.desc()))
        return list(result.scalars().all())

    async def criar(self, data: ProdutoColhidoCreate) -> ProdutoColhido:
        obj = ProdutoColhido(tenant_id=self.tenant_id, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def obter(self, produto_id: uuid.UUID) -> ProdutoColhido:
        stmt = select(ProdutoColhido).where(
            ProdutoColhido.id == produto_id,
            ProdutoColhido.tenant_id == self.tenant_id,
        )
        obj = (await self.session.execute(stmt)).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Produto colhido não encontrado")
        return obj

    async def atualizar(self, produto_id: uuid.UUID, data: ProdutoColhidoUpdate) -> ProdutoColhido:
        obj = await self.obter(produto_id)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def remover(self, produto_id: uuid.UUID) -> None:
        obj = await self.obter(produto_id)
        await self.session.delete(obj)

    async def resumo_estoque(
        self,
        status: Optional[str] = None,
        commodity_id: Optional[uuid.UUID] = None,
    ) -> dict:
        stmt = select(
            ProdutoColhido.commodity_id,
            ProdutoColhido.unidade,
            ProdutoColhido.armazem_id,
            ProdutoColhido.status,
            func.sum(ProdutoColhido.quantidade).label("total_quantidade"),
            func.sum(ProdutoColhido.peso_liquido_kg).label("total_peso_kg"),
            func.count(ProdutoColhido.id).label("num_lotes"),
        ).where(ProdutoColhido.tenant_id == self.tenant_id)

        if status:
            stmt = stmt.where(ProdutoColhido.status == status)
        if commodity_id:
            stmt = stmt.where(ProdutoColhido.commodity_id == commodity_id)

        stmt = stmt.group_by(
            ProdutoColhido.commodity_id,
            ProdutoColhido.unidade,
            ProdutoColhido.armazem_id,
            ProdutoColhido.status,
        )

        rows = (await self.session.execute(stmt)).all()

        commodity_ids = list({r.commodity_id for r in rows}) if rows else []
        commodity_map = {}
        if commodity_ids:
            from core.cadastros.commodities.models import Commodity
            c_stmt = select(Commodity).where(Commodity.id.in_(commodity_ids))
            commodities = (await self.session.execute(c_stmt)).scalars().all()
            commodity_map = {c.id: c for c in commodities}

        itens = []
        total_geral_kg = 0.0
        total_lotes = 0

        for r in rows:
            qty = float(r.total_quantidade)
            peso = float(r.total_peso_kg)
            total_geral_kg += peso
            total_lotes += int(r.num_lotes)
            c = commodity_map.get(r.commodity_id)
            itens.append({
                "commodity_id": r.commodity_id,
                "commodity_nome": c.nome if c else None,
                "commodity_codigo": c.codigo if c else None,
                "commodity_tipo": c.tipo if c else None,
                "unidade": r.unidade,
                "armazem_id": r.armazem_id,
                "status": r.status,
                "total_quantidade": round(qty, 3),
                "total_peso_kg": round(peso, 3),
                "num_lotes": int(r.num_lotes),
            })

        return {
            "itens": itens,
            "total_geral_kg": round(total_geral_kg, 3),
            "total_lotes": total_lotes,
        }
