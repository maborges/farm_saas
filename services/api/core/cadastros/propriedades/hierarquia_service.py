import uuid
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.exceptions import EntityNotFoundError
from .propriedade_models import Propriedade, ExploracaoRural
from .models import AreaRural
from .schemas import AreaRuralTreeResponse, AreaRuralCreate, AreaRuralResponse
from .service import AreaRuralService


class HierarquiaService(BaseService[Propriedade]):

    async def obter_propriedade(self, propriedade_id: uuid.UUID) -> Propriedade:
        obj = (await self.session.execute(
            select(Propriedade).where(Propriedade.id == propriedade_id, Propriedade.tenant_id == self.tenant_id)
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Propriedade não encontrada")
        return obj

    async def listar_exploracoes_ativas(self, propriedade_id: uuid.UUID) -> list[ExploracaoRural]:
        return list((await self.session.execute(
            select(ExploracaoRural).where(
                and_(
                    ExploracaoRural.propriedade_id == propriedade_id,
                    ExploracaoRural.tenant_id == self.tenant_id,
                    ExploracaoRural.ativo == True,
                )
            )
        )).scalars().all())

    async def verificar_vinculo(self, propriedade_id: uuid.UUID, unidade_produtiva_id: uuid.UUID) -> bool:
        obj = (await self.session.execute(
            select(ExploracaoRural).where(
                and_(
                    ExploracaoRural.propriedade_id == propriedade_id,
                    ExploracaoRural.unidade_produtiva_id == unidade_produtiva_id,
                    ExploracaoRural.tenant_id == self.tenant_id,
                )
            )
        )).scalar_one_or_none()
        return obj is not None

    async def construir_arvore_areas(self, area_id: uuid.UUID) -> AreaRuralTreeResponse:
        area = (await self.session.execute(
            select(AreaRural).where(
                and_(AreaRural.id == area_id, AreaRural.tenant_id == self.tenant_id, AreaRural.ativo == True)
            )
        )).scalar_one_or_none()
        if not area:
            raise HTTPException(404, f"Área {area_id} não encontrada")

        filhos = list((await self.session.execute(
            select(AreaRural).where(
                and_(AreaRural.parent_id == area_id, AreaRural.tenant_id == self.tenant_id, AreaRural.ativo == True)
            )
        )).scalars().all())

        filhos_arvore = [await self.construir_arvore_areas(f.id) for f in filhos]

        return AreaRuralTreeResponse(
            id=area.id,
            tenant_id=area.tenant_id,
            unidade_produtiva_id=area.unidade_produtiva_id,
            parent_id=area.parent_id,
            tipo=area.tipo,
            nome=area.nome,
            codigo=area.codigo,
            descricao=area.descricao,
            area_hectares=area.area_hectares,
            area_hectares_manual=area.area_hectares_manual,
            geometria=area.geometria,
            centroide_lat=area.centroide_lat,
            centroide_lng=area.centroide_lng,
            dados_extras=area.dados_extras,
            ativo=area.ativo,
            created_at=area.created_at,
            updated_at=area.updated_at,
            filhos=filhos_arvore,
        )

    async def obter_hierarquia_completa(self, propriedade_id: uuid.UUID) -> dict:
        propriedade = await self.obter_propriedade(propriedade_id)
        exploracoes = await self.listar_exploracoes_ativas(propriedade_id)

        areas_svc = AreaRuralService(AreaRural, self.session, self.tenant_id)
        fazendas = []
        for expl in exploracoes:
            raizes = await areas_svc.listar_raizes(unidade_produtiva_id=expl.unidade_produtiva_id)
            arvore_areas = [await self.construir_arvore_areas(r.id) for r in raizes]
            fazendas.append({
                "unidade_produtiva_id": expl.unidade_produtiva_id,
                "exploracao_id": expl.id,
                "natureza": expl.natureza,
                "data_inicio": expl.data_inicio,
                "data_fim": expl.data_fim,
                "areas": arvore_areas,
            })

        return {"propriedade": propriedade, "fazendas": fazendas}

    async def listar_areas_por_fazenda(
        self, propriedade_id: uuid.UUID, unidade_produtiva_id: uuid.UUID,
        tipo: Optional[str] = None,
    ) -> list[AreaRuralTreeResponse]:
        if not await self.verificar_vinculo(propriedade_id, unidade_produtiva_id):
            raise HTTPException(400, "Fazenda não vinculada a esta propriedade")

        areas_svc = AreaRuralService(AreaRural, self.session, self.tenant_id)
        if tipo:
            raizes = await areas_svc.listar(unidade_produtiva_id=unidade_produtiva_id, tipo=tipo, parent_id=None)
        else:
            raizes = await areas_svc.listar_raizes(unidade_produtiva_id=unidade_produtiva_id)

        return [await self.construir_arvore_areas(r.id) for r in raizes]

    async def criar_area_rural(
        self, propriedade_id: uuid.UUID, unidade_produtiva_id: uuid.UUID, data: AreaRuralCreate
    ) -> AreaRural:
        if not await self.verificar_vinculo(propriedade_id, unidade_produtiva_id):
            raise HTTPException(400, "Fazenda não vinculada a esta propriedade")
        areas_svc = AreaRuralService(AreaRural, self.session, self.tenant_id)
        area_data = data.model_dump()
        area_data["unidade_produtiva_id"] = unidade_produtiva_id
        return await areas_svc.criar_area(area_data)
