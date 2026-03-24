import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.base_service import BaseService
from core.cadastros.models import ProdutoCatalogo, ProdutoAgricolaDetalhe, ProdutoEstoqueDetalhe
from core.cadastros.schemas import ProdutoCatalogoCreate, ProdutoCatalogoUpdate, ProdutoCatalogoResponse
from core.exceptions import EntityNotFoundError


class CatalogoProdutoService(BaseService[ProdutoCatalogo]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(ProdutoCatalogo, session, tenant_id)

    async def listar(self, tipo: Optional[str] = None, apenas_ativos: bool = True) -> list[ProdutoCatalogo]:
        stmt = select(ProdutoCatalogo).where(ProdutoCatalogo.tenant_id == self.tenant_id)
        if tipo:
            stmt = stmt.where(ProdutoCatalogo.tipo == tipo)
        if apenas_ativos:
            stmt = stmt.where(ProdutoCatalogo.ativo == True)
        stmt = stmt.order_by(ProdutoCatalogo.nome)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def criar(self, data: ProdutoCatalogoCreate) -> ProdutoCatalogo:
        produto = ProdutoCatalogo(
            tenant_id=self.tenant_id,
            nome=data.nome,
            tipo=data.tipo,
            unidade_medida=data.unidade_medida,
            codigo_interno=data.codigo_interno,
            sku=data.sku,
            descricao=data.descricao,
            estoque_minimo=data.estoque_minimo,
            preco_medio=data.preco_medio,
            ativo=data.ativo,
        )
        self.session.add(produto)
        await self.session.flush()

        if data.detalhe_agricola:
            det = ProdutoAgricolaDetalhe(produto_id=produto.id, **data.detalhe_agricola.model_dump())
            self.session.add(det)

        if data.detalhe_estoque:
            det = ProdutoEstoqueDetalhe(produto_id=produto.id, **data.detalhe_estoque.model_dump())
            self.session.add(det)

        await self.session.flush()
        return produto

    async def atualizar(self, produto_id: uuid.UUID, data: ProdutoCatalogoUpdate) -> ProdutoCatalogo:
        produto = await self._get_or_fail(produto_id)
        for field, value in data.model_dump(exclude_none=True, exclude={"detalhe_agricola", "detalhe_estoque"}).items():
            setattr(produto, field, value)

        if data.detalhe_agricola is not None:
            await self._upsert_extension(
                ProdutoAgricolaDetalhe,
                produto_id,
                data.detalhe_agricola.model_dump(),
            )

        if data.detalhe_estoque is not None:
            await self._upsert_extension(
                ProdutoEstoqueDetalhe,
                produto_id,
                data.detalhe_estoque.model_dump(),
            )

        await self.session.flush()
        return produto

    async def _get_or_fail(self, produto_id: uuid.UUID) -> ProdutoCatalogo:
        stmt = select(ProdutoCatalogo).where(
            ProdutoCatalogo.id == produto_id,
            ProdutoCatalogo.tenant_id == self.tenant_id,
        )
        result = await self.session.execute(stmt)
        produto = result.scalar_one_or_none()
        if not produto:
            raise EntityNotFoundError("Produto não encontrado")
        return produto

    async def _upsert_extension(self, model_cls, produto_id: uuid.UUID, data: dict) -> None:
        stmt = select(model_cls).where(model_cls.produto_id == produto_id)
        result = await self.session.execute(stmt)
        ext = result.scalar_one_or_none()
        if ext:
            for k, v in data.items():
                setattr(ext, k, v)
        else:
            self.session.add(model_cls(produto_id=produto_id, **data))

    async def obter(self, produto_id: uuid.UUID) -> ProdutoCatalogo:
        return await self._get_or_fail(produto_id)

    async def build_response(self, produto: ProdutoCatalogo) -> ProdutoCatalogoResponse:
        """Enrich response with extension tables."""
        agricola = None
        estoque_det = None

        stmt_ag = select(ProdutoAgricolaDetalhe).where(ProdutoAgricolaDetalhe.produto_id == produto.id)
        r_ag = await self.session.execute(stmt_ag)
        ag = r_ag.scalar_one_or_none()
        if ag:
            from core.cadastros.schemas import ProdutoAgricolaDetalheSchema
            agricola = ProdutoAgricolaDetalheSchema.model_validate(ag)

        stmt_est = select(ProdutoEstoqueDetalhe).where(ProdutoEstoqueDetalhe.produto_id == produto.id)
        r_est = await self.session.execute(stmt_est)
        est = r_est.scalar_one_or_none()
        if est:
            from core.cadastros.schemas import ProdutoEstoqueDetalheSchema
            estoque_det = ProdutoEstoqueDetalheSchema.model_validate(est)

        return ProdutoCatalogoResponse(
            id=produto.id,
            tenant_id=produto.tenant_id,
            nome=produto.nome,
            tipo=produto.tipo,
            unidade_medida=produto.unidade_medida,
            codigo_interno=produto.codigo_interno,
            sku=produto.sku,
            descricao=produto.descricao,
            estoque_minimo=produto.estoque_minimo,
            preco_medio=produto.preco_medio,
            ativo=produto.ativo,
            created_at=produto.created_at,
            updated_at=produto.updated_at,
            detalhe_agricola=agricola,
            detalhe_estoque=estoque_det,
        )
