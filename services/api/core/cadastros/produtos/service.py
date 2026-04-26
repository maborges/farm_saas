import uuid
from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.exceptions import EntityNotFoundError, BusinessRuleError
from .models import Marca, ModeloProduto, CategoriaProduto, Produto, ProdutoAgricola, ProdutoEstoque, ProdutoEPI, ProdutoCultura, SoloParametroCultura


_PRODUTO_LOADS = [
    selectinload(Produto.marca_rel),
    selectinload(Produto.modelo_rel),
    selectinload(Produto.categoria),
    selectinload(Produto.detalhe_agricola),
    selectinload(Produto.detalhe_estoque),
    selectinload(Produto.detalhe_epi),
]


class ProdutoService(BaseService[Produto]):

    # ── Marcas ────────────────────────────────────────────────────────────────

    async def listar_marcas(self, ativo: Optional[bool] = None) -> list[Marca]:
        stmt = select(Marca).where(
            or_(Marca.tenant_id.is_(None), Marca.tenant_id == self.tenant_id)
        ).order_by(Marca.nome)
        if ativo is not None:
            stmt = stmt.where(Marca.ativo == ativo)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_marca(self, data) -> Marca:
        obj = Marca(tenant_id=self.tenant_id, sistema=False, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def _get_marca(self, marca_id: uuid.UUID, editavel: bool = False) -> Marca:
        conds = [Marca.id == marca_id, Marca.tenant_id == self.tenant_id]
        if editavel:
            conds.append(Marca.sistema == False)
        obj = (await self.session.execute(select(Marca).where(*conds))).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Marca não encontrada" + (" ou não editável" if editavel else ""))
        return obj

    async def atualizar_marca(self, marca_id: uuid.UUID, data) -> Marca:
        obj = await self._get_marca(marca_id, editavel=True)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def remover_marca(self, marca_id: uuid.UUID) -> None:
        obj = await self._get_marca(marca_id, editavel=True)
        if (await self.session.execute(select(ModeloProduto).where(ModeloProduto.marca_id == marca_id))).scalar_one_or_none():
            raise BusinessRuleError("Não é possível excluir marca com modelos vinculados. Desative os modelos primeiro.")
        obj.ativo = False

    # ── Modelos ───────────────────────────────────────────────────────────────

    async def listar_modelos(
        self, marca_id: Optional[uuid.UUID] = None,
        tipo_produto: Optional[str] = None, ativo: Optional[bool] = None,
    ) -> list[ModeloProduto]:
        stmt = (
            select(ModeloProduto)
            .where(or_(ModeloProduto.tenant_id.is_(None), ModeloProduto.tenant_id == self.tenant_id))
            .options(selectinload(ModeloProduto.marca))
            .order_by(ModeloProduto.nome)
        )
        if marca_id:
            stmt = stmt.where(ModeloProduto.marca_id == marca_id)
        if tipo_produto:
            stmt = stmt.where(
                (ModeloProduto.tipo_produto == tipo_produto) | (ModeloProduto.tipo_produto.is_(None))
            )
        if ativo is not None:
            stmt = stmt.where(ModeloProduto.ativo == ativo)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_modelo(self, data) -> ModeloProduto:
        marca = (await self.session.execute(
            select(Marca).where(Marca.id == data.marca_id, or_(Marca.tenant_id.is_(None), Marca.tenant_id == self.tenant_id))
        )).scalar_one_or_none()
        if not marca:
            raise EntityNotFoundError("Marca não encontrada")
        obj = ModeloProduto(tenant_id=self.tenant_id, sistema=False, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        res = (await self.session.execute(
            select(ModeloProduto).where(ModeloProduto.id == obj.id).options(selectinload(ModeloProduto.marca))
        )).scalar_one()
        return res

    async def _get_modelo(self, modelo_id: uuid.UUID, editavel: bool = False) -> ModeloProduto:
        conds = [ModeloProduto.id == modelo_id, ModeloProduto.tenant_id == self.tenant_id]
        if editavel:
            conds.append(ModeloProduto.sistema == False)
        obj = (await self.session.execute(
            select(ModeloProduto).where(*conds).options(selectinload(ModeloProduto.marca))
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Modelo não encontrado" + (" ou não editável" if editavel else ""))
        return obj

    async def atualizar_modelo(self, modelo_id: uuid.UUID, data) -> ModeloProduto:
        obj = await self._get_modelo(modelo_id, editavel=True)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def remover_modelo(self, modelo_id: uuid.UUID) -> None:
        obj = await self._get_modelo(modelo_id, editavel=True)
        obj.ativo = False

    # ── Categorias ────────────────────────────────────────────────────────────

    async def listar_categorias(self, parent_id: Optional[uuid.UUID] = None, ativo: Optional[bool] = None) -> list[CategoriaProduto]:
        stmt = (
            select(CategoriaProduto)
            .where(or_(CategoriaProduto.tenant_id.is_(None), CategoriaProduto.tenant_id == self.tenant_id))
            .order_by(CategoriaProduto.ordem, CategoriaProduto.nome)
        )
        if parent_id is not None:
            stmt = stmt.where(CategoriaProduto.parent_id == parent_id)
        if ativo is not None:
            stmt = stmt.where(CategoriaProduto.ativo == ativo)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_categoria(self, data) -> CategoriaProduto:
        obj = CategoriaProduto(tenant_id=self.tenant_id, sistema=False, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def _get_categoria(self, cat_id: uuid.UUID, editavel: bool = False) -> CategoriaProduto:
        conds = [CategoriaProduto.id == cat_id, CategoriaProduto.tenant_id == self.tenant_id]
        if editavel:
            conds.append(CategoriaProduto.sistema == False)
        obj = (await self.session.execute(select(CategoriaProduto).where(*conds))).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Categoria não encontrada" + (" ou não editável" if editavel else ""))
        return obj

    async def atualizar_categoria(self, cat_id: uuid.UUID, data) -> CategoriaProduto:
        obj = await self._get_categoria(cat_id, editavel=True)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def remover_categoria(self, cat_id: uuid.UUID) -> None:
        obj = await self._get_categoria(cat_id, editavel=True)
        obj.ativo = False

    # ── Produtos ──────────────────────────────────────────────────────────────

    async def listar_produtos(
        self, tipo: Optional[str] = None, categoria_id: Optional[uuid.UUID] = None,
        marca_id: Optional[uuid.UUID] = None, ativo: Optional[bool] = None, q: Optional[str] = None,
    ) -> list[Produto]:
        stmt = select(Produto).where(Produto.tenant_id == self.tenant_id).options(*_PRODUTO_LOADS).order_by(Produto.nome)
        if tipo:
            stmt = stmt.where(Produto.tipo == tipo)
        if categoria_id:
            stmt = stmt.where(Produto.categoria_id == categoria_id)
        if marca_id:
            stmt = stmt.where(Produto.marca_id == marca_id)
        if ativo is not None:
            stmt = stmt.where(Produto.ativo == ativo)
        if q:
            stmt = stmt.where(or_(Produto.nome.ilike(f"%{q}%"), Produto.codigo_interno.ilike(f"%{q}%")))
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_produto(self, data) -> Produto:
        payload = data.model_dump(exclude={"detalhe_agricola", "detalhe_estoque", "detalhe_epi"})
        produto = Produto(tenant_id=self.tenant_id, **payload)
        if data.detalhe_agricola:
            produto.detalhe_agricola = ProdutoAgricola(**data.detalhe_agricola.model_dump())
        if data.detalhe_estoque:
            produto.detalhe_estoque = ProdutoEstoque(**data.detalhe_estoque.model_dump())
        if data.detalhe_epi:
            produto.detalhe_epi = ProdutoEPI(**data.detalhe_epi.model_dump())
        self.session.add(produto)
        await self.session.flush()
        res = (await self.session.execute(
            select(Produto).where(Produto.id == produto.id).options(*_PRODUTO_LOADS)
        )).scalar_one()
        return res

    async def _get_produto(self, produto_id: uuid.UUID) -> Produto:
        obj = (await self.session.execute(
            select(Produto).where(Produto.id == produto_id, Produto.tenant_id == self.tenant_id).options(*_PRODUTO_LOADS)
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Produto não encontrado")
        return obj

    async def atualizar_produto(self, produto_id: uuid.UUID, data) -> Produto:
        obj = await self._get_produto(produto_id)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        res = (await self.session.execute(
            select(Produto).where(Produto.id == produto_id).options(*_PRODUTO_LOADS)
        )).scalar_one()
        return res

    async def remover_produto(self, produto_id: uuid.UUID) -> None:
        obj = await self._get_produto(produto_id)
        obj.ativo = False

    # ── Culturas ──────────────────────────────────────────────────────────────

    async def listar_culturas(self, grupo: Optional[str] = None, ativa: Optional[bool] = None, q: Optional[str] = None) -> list[ProdutoCultura]:
        stmt = select(ProdutoCultura).where(
            or_(ProdutoCultura.tenant_id.is_(None), ProdutoCultura.tenant_id == self.tenant_id)
        ).order_by(ProdutoCultura.nome)
        if grupo:
            stmt = stmt.where(ProdutoCultura.grupo == grupo)
        if ativa is not None:
            stmt = stmt.where(ProdutoCultura.ativa == ativa)
        if q:
            stmt = stmt.where(or_(ProdutoCultura.nome.ilike(f"%{q}%"), ProdutoCultura.nome_cientifico.ilike(f"%{q}%")))
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_cultura(self, data) -> ProdutoCultura:
        obj = ProdutoCultura(tenant_id=self.tenant_id, sistema=False, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def _get_cultura(self, cultura_id: uuid.UUID, editavel: bool = False) -> ProdutoCultura:
        conds = [ProdutoCultura.id == cultura_id, ProdutoCultura.tenant_id == self.tenant_id]
        if editavel:
            conds.append(ProdutoCultura.sistema == False)
        obj = (await self.session.execute(select(ProdutoCultura).where(*conds))).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Cultura não encontrada" + (" ou não editável" if editavel else ""))
        return obj

    async def atualizar_cultura(self, cultura_id: uuid.UUID, data) -> ProdutoCultura:
        obj = await self._get_cultura(cultura_id, editavel=True)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def remover_cultura(self, cultura_id: uuid.UUID) -> None:
        obj = await self._get_cultura(cultura_id, editavel=True)
        obj.ativa = False

    # ── Solo Parâmetros ───────────────────────────────────────────────────────

    async def listar_parametros_solo(self, cultura_id: uuid.UUID) -> list[SoloParametroCultura]:
        stmt = select(SoloParametroCultura).where(
            SoloParametroCultura.cultura_id == cultura_id,
            or_(SoloParametroCultura.tenant_id.is_(None), SoloParametroCultura.tenant_id == self.tenant_id),
        ).order_by(SoloParametroCultura.parametro, SoloParametroCultura.faixa_min)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_parametro_solo(self, cultura_id: uuid.UUID, data) -> SoloParametroCultura:
        if not await self.session.get(ProdutoCultura, cultura_id):
            raise EntityNotFoundError("Cultura não encontrada")
        obj = SoloParametroCultura(cultura_id=cultura_id, tenant_id=self.tenant_id, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def _get_parametro_solo(self, param_id: uuid.UUID, cultura_id: uuid.UUID) -> SoloParametroCultura:
        obj = (await self.session.execute(
            select(SoloParametroCultura).where(
                SoloParametroCultura.id == param_id,
                SoloParametroCultura.cultura_id == cultura_id,
                SoloParametroCultura.tenant_id == self.tenant_id,
            )
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Parâmetro não encontrado ou não editável")
        return obj

    async def atualizar_parametro_solo(self, param_id: uuid.UUID, cultura_id: uuid.UUID, data) -> SoloParametroCultura:
        obj = await self._get_parametro_solo(param_id, cultura_id)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def remover_parametro_solo(self, param_id: uuid.UUID, cultura_id: uuid.UUID) -> None:
        obj = await self._get_parametro_solo(param_id, cultura_id)
        await self.session.delete(obj)
