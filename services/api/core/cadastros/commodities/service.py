import uuid
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.exceptions import EntityNotFoundError, EntityAlreadyExistsError
from .models import Commodity, CommodityClassificacao, CotacaoCommodity
from .conversao import ConversaoUnidade
from .schemas import CommodityClassificacaoResponse, CotacaoCommodityResponse, CommodityDetalhadaResponse


class CommodityService(BaseService[Commodity]):

    def _tenant_or_sistema(self):
        return or_(Commodity.tenant_id == self.tenant_id, Commodity.sistema == True)

    # ── Commodity ─────────────────────────────────────────────────────────────

    async def listar(
        self, tipo: Optional[str] = None,
        apenas_ativos: bool = True, incluir_sistema: bool = True,
    ) -> list[Commodity]:
        stmt = select(Commodity)
        if incluir_sistema:
            stmt = stmt.where(or_(Commodity.tenant_id == self.tenant_id, Commodity.sistema == True))
        else:
            stmt = stmt.where(Commodity.tenant_id == self.tenant_id)
        if apenas_ativos:
            stmt = stmt.where(Commodity.ativo == True)
        if tipo:
            stmt = stmt.where(Commodity.tipo == tipo)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar(self, data) -> Commodity:
        existente = (await self.session.execute(
            select(Commodity).where(Commodity.tenant_id == self.tenant_id, Commodity.nome == data.nome, Commodity.ativo == True)
        )).scalar_one_or_none()
        if existente:
            raise EntityAlreadyExistsError(f"Já existe uma commodity ativa com o nome '{data.nome}'")
        obj = Commodity(tenant_id=self.tenant_id, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def obter(
        self, commodity_id: uuid.UUID,
        incluir_classificacoes: bool = True, incluir_cotacao: bool = True,
    ) -> CommodityDetalhadaResponse:
        obj = (await self.session.execute(
            select(Commodity).where(Commodity.id == commodity_id, self._tenant_or_sistema())
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Commodity não encontrada")

        data = CommodityDetalhadaResponse.model_validate(obj)

        if incluir_classificacoes:
            cls_result = await self.session.execute(
                select(CommodityClassificacao).where(
                    CommodityClassificacao.commodity_id == commodity_id,
                    CommodityClassificacao.ativo == True,
                )
            )
            data.classificacoes = [CommodityClassificacaoResponse.model_validate(c) for c in cls_result.scalars().all()]

        if incluir_cotacao:
            ultima = (await self.session.execute(
                select(CotacaoCommodity).where(CotacaoCommodity.commodity_id == commodity_id)
                .order_by(CotacaoCommodity.data.desc()).limit(1)
            )).scalar_one_or_none()
            if ultima:
                data.ultima_cotacao = CotacaoCommodityResponse.model_validate(ultima)

        return data

    async def _get_commodity(self, commodity_id: uuid.UUID, permitir_escrita: bool = False) -> Commodity:
        obj = (await self.session.execute(
            select(Commodity).where(Commodity.id == commodity_id, self._tenant_or_sistema())
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Commodity não encontrada")
        if permitir_escrita and obj.sistema:
            raise HTTPException(403, "Commodity do sistema — apenas administrador do SaaS pode alterar")
        return obj

    async def atualizar(self, commodity_id: uuid.UUID, data) -> Commodity:
        obj = await self._get_commodity(commodity_id, permitir_escrita=True)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def remover(self, commodity_id: uuid.UUID) -> None:
        obj = await self._get_commodity(commodity_id, permitir_escrita=True)
        obj.ativo = False

    # ── Classificações ────────────────────────────────────────────────────────

    async def listar_classificacoes(self, commodity_id: uuid.UUID, apenas_ativas: bool = True) -> list[CommodityClassificacao]:
        await self._get_commodity(commodity_id)
        stmt = select(CommodityClassificacao).where(CommodityClassificacao.commodity_id == commodity_id)
        if apenas_ativas:
            stmt = stmt.where(CommodityClassificacao.ativo == True)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_classificacao(self, commodity_id: uuid.UUID, data) -> CommodityClassificacao:
        await self._get_commodity(commodity_id, permitir_escrita=True)
        obj = CommodityClassificacao(commodity_id=commodity_id, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def _get_classificacao(self, commodity_id: uuid.UUID, classificacao_id: uuid.UUID, escrita: bool = False) -> CommodityClassificacao:
        await self._get_commodity(commodity_id, permitir_escrita=escrita)
        obj = (await self.session.execute(
            select(CommodityClassificacao).where(
                CommodityClassificacao.id == classificacao_id,
                CommodityClassificacao.commodity_id == commodity_id,
            )
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Classificação não encontrada")
        return obj

    async def atualizar_classificacao(self, commodity_id: uuid.UUID, classificacao_id: uuid.UUID, data) -> CommodityClassificacao:
        obj = await self._get_classificacao(commodity_id, classificacao_id, escrita=True)
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def remover_classificacao(self, commodity_id: uuid.UUID, classificacao_id: uuid.UUID) -> None:
        obj = await self._get_classificacao(commodity_id, classificacao_id, escrita=True)
        obj.ativo = False

    # ── Cotações ──────────────────────────────────────────────────────────────

    async def listar_cotacoes(
        self, commodity_id: uuid.UUID,
        data_inicio: Optional[str] = None, data_fim: Optional[str] = None, fonte: Optional[str] = None,
    ) -> list[CotacaoCommodity]:
        await self._get_commodity(commodity_id)
        stmt = select(CotacaoCommodity).where(CotacaoCommodity.commodity_id == commodity_id)
        if data_inicio:
            stmt = stmt.where(CotacaoCommodity.data >= data_inicio)
        if data_fim:
            stmt = stmt.where(CotacaoCommodity.data <= data_fim)
        if fonte:
            stmt = stmt.where(CotacaoCommodity.fonte == fonte)
        return list((await self.session.execute(stmt.order_by(CotacaoCommodity.data.desc()))).scalars().all())

    async def criar_cotacao(self, commodity_id: uuid.UUID, data) -> CotacaoCommodity:
        await self._get_commodity(commodity_id, permitir_escrita=True)
        obj = CotacaoCommodity(commodity_id=commodity_id, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def ultima_cotacao(self, commodity_id: uuid.UUID, fonte: Optional[str] = None) -> CotacaoCommodity:
        await self._get_commodity(commodity_id)
        stmt = select(CotacaoCommodity).where(CotacaoCommodity.commodity_id == commodity_id)
        if fonte:
            stmt = stmt.where(CotacaoCommodity.fonte == fonte)
        obj = (await self.session.execute(stmt.order_by(CotacaoCommodity.data.desc()).limit(1))).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Nenhuma cotação encontrada para esta commodity")
        return obj

    async def remover_cotacao(self, commodity_id: uuid.UUID, cotacao_id: uuid.UUID) -> None:
        await self._get_commodity(commodity_id, permitir_escrita=True)
        obj = (await self.session.execute(
            select(CotacaoCommodity).where(CotacaoCommodity.id == cotacao_id, CotacaoCommodity.commodity_id == commodity_id)
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Cotação não encontrada")
        await self.session.delete(obj)

    # ── Conversões ────────────────────────────────────────────────────────────

    async def listar_conversoes(self, commodity_id: uuid.UUID) -> list[dict]:
        await self._get_commodity(commodity_id)
        itens = (await self.session.execute(
            select(ConversaoUnidade).where(ConversaoUnidade.commodity_id == commodity_id, ConversaoUnidade.ativo == True)
            .order_by(ConversaoUnidade.unidade_origem, ConversaoUnidade.unidade_destino)
        )).scalars().all()
        return [{"unidade_origem": i.unidade_origem, "unidade_destino": i.unidade_destino, "fator": i.fator, "descricao": i.descricao, "exemplo": f"1 {i.unidade_origem} = {i.fator} {i.unidade_destino}"} for i in itens]

    async def criar_conversao(self, commodity_id: uuid.UUID, data: dict) -> dict:
        await self._get_commodity(commodity_id, permitir_escrita=True)
        obj = ConversaoUnidade(
            commodity_id=commodity_id,
            unidade_origem=data["unidade_origem"],
            unidade_destino=data["unidade_destino"],
            fator=data["fator"],
            descricao=data.get("descricao"),
        )
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return {"unidade_origem": obj.unidade_origem, "unidade_destino": obj.unidade_destino, "fator": obj.fator, "descricao": obj.descricao, "exemplo": f"1 {obj.unidade_origem} = {obj.fator} {obj.unidade_destino}"}

    async def calcular_conversao(self, commodity_id: uuid.UUID, quantidade: float, origem: str, destino: str) -> dict:
        await self._get_commodity(commodity_id)
        conv = (await self.session.execute(
            select(ConversaoUnidade).where(
                ConversaoUnidade.commodity_id == commodity_id,
                ConversaoUnidade.unidade_origem == origem,
                ConversaoUnidade.unidade_destino == destino,
                ConversaoUnidade.ativo == True,
            )
        )).scalar_one_or_none()

        if not conv:
            comm = await self.session.get(Commodity, commodity_id)
            if comm and comm.peso_unidade and origem == comm.unidade_padrao and destino == "KG":
                return {"quantidade_origem": quantidade, "unidade_origem": origem, "quantidade_destino": quantidade * comm.peso_unidade, "unidade_destino": destino, "origem": "peso_unidade_commodity"}
            raise HTTPException(404, f"Conversão {origem} → {destino} não encontrada para esta commodity")

        return {"quantidade_origem": quantidade, "unidade_origem": origem, "quantidade_destino": round(conv.converter(quantidade), 6), "unidade_destino": destino, "fator_usado": conv.fator, "origem": "tabela_conversao"}
