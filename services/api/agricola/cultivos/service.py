import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from core.base_service import BaseService
from core.exceptions import BusinessRuleError, EntityNotFoundError
from agricola.safras.models import Safra
from agricola.cultivos.models import Cultivo, CultivoArea
from agricola.cultivos.schemas import (
    CultivoCreate,
    CultivoUpdate,
    CultivoResponse,
    CultivoAreaCreate,
)


class CultivoService(BaseService[Cultivo]):
    """Serviço para gerenciar cultivos dentro de safras."""

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(session, Cultivo, tenant_id)
        self.session = session
        self.tenant_id = tenant_id

    async def _get_safra(self, safra_id: uuid.UUID) -> Safra:
        """Valida que a safra existe e pertence ao tenant."""
        stmt = select(Safra).where(
            Safra.id == safra_id,
            Safra.tenant_id == self.tenant_id,
        )
        safra = (await self.session.execute(stmt)).scalars().first()
        if not safra:
            raise EntityNotFoundError(f"Safra {safra_id} não encontrada.")
        return safra

    async def criar_com_areas(
        self, safra_id: uuid.UUID, data: CultivoCreate
    ) -> Cultivo:
        """Cria um cultivo com suas CultivoAreas atomicamente."""
        await self._get_safra(safra_id)

        cultivo = Cultivo(
            tenant_id=self.tenant_id,
            safra_id=safra_id,
            cultura=data.cultura,
            cultivar_id=data.cultivar_id,
            cultivar_nome=data.cultivar_nome,
            commodity_id=data.commodity_id,
            sistema_plantio=data.sistema_plantio,
            populacao_prevista=data.populacao_prevista,
            espacamento_cm=data.espacamento_cm,
            data_plantio_prevista=data.data_plantio_prevista,
            produtividade_meta_sc_ha=data.produtividade_meta_sc_ha,
            preco_venda_previsto=data.preco_venda_previsto,
            observacoes=data.observacoes,
        )
        self.session.add(cultivo)
        await self.session.flush()

        # Adicionar áreas
        for area_data in data.areas:
            area = CultivoArea(
                tenant_id=self.tenant_id,
                cultivo_id=cultivo.id,
                area_id=area_data.area_id,
                area_ha=area_data.area_ha,
            )
            self.session.add(area)

        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(cultivo, ["areas"])
        return cultivo

    async def listar_por_safra(self, safra_id: uuid.UUID) -> list[Cultivo]:
        """Lista todos os cultivos de uma safra."""
        await self._get_safra(safra_id)
        stmt = select(Cultivo).where(
            Cultivo.tenant_id == self.tenant_id,
            Cultivo.safra_id == safra_id,
        ).order_by(Cultivo.cultura)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_area_total(self, cultivo_id: uuid.UUID) -> float:
        """Retorna a área total (em hectares) do cultivo."""
        stmt = select(func.sum(CultivoArea.area_ha)).where(
            CultivoArea.cultivo_id == cultivo_id,
            CultivoArea.tenant_id == self.tenant_id,
        )
        total = (await self.session.execute(stmt)).scalar() or 0.0
        return float(total)

    async def sincronizar_areas(
        self, cultivo_id: uuid.UUID, areas_data: list[CultivoAreaCreate]
    ) -> Cultivo:
        """Atualiza as CultivoAreas de um cultivo (DELETE + INSERT)."""
        cultivo = await self.get_or_fail(cultivo_id)

        # Remover áreas antigas
        delete_stmt = select(CultivoArea).where(
            CultivoArea.cultivo_id == cultivo_id,
            CultivoArea.tenant_id == self.tenant_id,
        )
        old_areas = list((await self.session.execute(delete_stmt)).scalars().all())
        for area in old_areas:
            await self.session.delete(area)

        # Adicionar novas áreas
        for area_data in areas_data:
            area = CultivoArea(
                tenant_id=self.tenant_id,
                cultivo_id=cultivo_id,
                area_id=area_data.area_id,
                area_ha=area_data.area_ha,
            )
            self.session.add(area)

        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(cultivo, ["areas"])
        return cultivo
