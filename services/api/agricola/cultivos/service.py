import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from decimal import Decimal

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
from core.cadastros.propriedades.models import AreaRural


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

    async def _validar_ocupacao_talhao(
        self, safra_id: uuid.UUID, areas_data: list[CultivoAreaCreate], consorciado: bool
    ) -> None:
        """Valida que a ocupação de cada talhão não ultrapassa sua capacidade.

        Regra: Para cada talhão, a soma das áreas de cultivos não-consorciados
        não pode ultrapassar a área total do talhão. Cultivos consorciados podem
        compartilhar a mesma área.
        """
        if not areas_data or consorciado:
            return

        for area_data in areas_data:
            # Get talhao info
            talhao_stmt = select(AreaRural).where(
                AreaRural.id == area_data.area_id,
                AreaRural.tenant_id == self.tenant_id,
            )
            talhao = (await self.session.execute(talhao_stmt)).scalars().first()
            if not talhao or not talhao.area_hectares:
                continue

            # Sum all non-consorciado cultivo areas for this talhao in same safra
            sum_stmt = select(func.sum(CultivoArea.area_ha)).where(
                and_(
                    CultivoArea.area_id == area_data.area_id,
                    CultivoArea.tenant_id == self.tenant_id,
                    Cultivo.safra_id == safra_id,
                    Cultivo.consorciado == False,
                )
            ).select_from(CultivoArea).join(Cultivo)

            total_area = (await self.session.execute(sum_stmt)).scalar() or 0.0
            total_area = float(total_area) + float(area_data.area_ha)

            if total_area > float(talhao.area_hectares):
                raise BusinessRuleError(
                    f"Talhão '{talhao.nome}' tem capacidade de {talhao.area_hectares} ha, "
                    f"mas seria ocupado com {total_area:.2f} ha. "
                    f"Marque como 'consorciado' se cultivos devem compartilhar espaço."
                )

    async def criar_com_areas(
        self, safra_id: uuid.UUID, data: CultivoCreate
    ) -> Cultivo:
        """Cria um cultivo com suas CultivoAreas atomicamente."""
        await self._get_safra(safra_id)

        # Validar ocupação de talhões
        await self._validar_ocupacao_talhao(safra_id, data.areas, data.consorciado)

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
            consorciado=data.consorciado,
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
