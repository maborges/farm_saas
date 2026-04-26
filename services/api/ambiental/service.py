import uuid
from datetime import date, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.exceptions import EntityNotFoundError
from .models import RegistroCAR, AlertaAmbiental, OutorgaHidrica, StatusCAR, StatusAlerta


class AmbientalService(BaseService[RegistroCAR]):

    # ── Dashboard ─────────────────────────────────────────────────────────────

    async def dashboard(self) -> dict:
        cars = list((await self.session.execute(
            select(RegistroCAR).where(RegistroCAR.tenant_id == self.tenant_id)
        )).scalars().all())
        alertas = list((await self.session.execute(
            select(AlertaAmbiental).where(AlertaAmbiental.tenant_id == self.tenant_id)
        )).scalars().all())
        outorgas = list((await self.session.execute(
            select(OutorgaHidrica).where(
                OutorgaHidrica.tenant_id == self.tenant_id,
                OutorgaHidrica.ativo == True,
            )
        )).scalars().all())
        hoje = date.today()
        prazo = hoje + timedelta(days=90)
        return {
            "total_cars": len(cars),
            "cars_ativos": sum(1 for c in cars if c.status == StatusCAR.ATIVO),
            "cars_pendentes": sum(1 for c in cars if c.status == StatusCAR.PENDENTE),
            "total_alertas_abertos": sum(1 for a in alertas if a.status in (StatusAlerta.NOVO, StatusAlerta.EM_ANALISE)),
            "alertas_criticos": sum(1 for a in alertas if a.severidade == "CRITICA" and a.status != StatusAlerta.RESOLVIDO),
            "total_outorgas": len(outorgas),
            "outorgas_vencendo": sum(1 for o in outorgas if o.data_vencimento and hoje <= o.data_vencimento <= prazo),
        }

    # ── CAR ───────────────────────────────────────────────────────────────────

    async def listar_cars(self, status_filter: Optional[str] = None) -> list[RegistroCAR]:
        stmt = select(RegistroCAR).where(RegistroCAR.tenant_id == self.tenant_id).order_by(RegistroCAR.created_at.desc())
        if status_filter:
            stmt = stmt.where(RegistroCAR.status == status_filter)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_car(self, dados: dict) -> RegistroCAR:
        car = RegistroCAR(tenant_id=self.tenant_id, **dados)
        self.session.add(car)
        await self.session.flush()
        await self.session.refresh(car)
        return car

    async def _get_car(self, car_id: uuid.UUID) -> RegistroCAR:
        obj = (await self.session.execute(
            select(RegistroCAR).where(RegistroCAR.id == car_id, RegistroCAR.tenant_id == self.tenant_id)
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("CAR não encontrado.")
        return obj

    async def atualizar_car(self, car_id: uuid.UUID, dados: dict) -> RegistroCAR:
        car = await self._get_car(car_id)
        for k, v in dados.items():
            setattr(car, k, v)
        await self.session.flush()
        await self.session.refresh(car)
        return car

    async def excluir_car(self, car_id: uuid.UUID) -> None:
        car = await self._get_car(car_id)
        await self.session.delete(car)

    # ── Alertas ───────────────────────────────────────────────────────────────

    async def listar_alertas(
        self, status_filter: Optional[str] = None,
        severidade: Optional[str] = None, tipo: Optional[str] = None,
    ) -> list[AlertaAmbiental]:
        stmt = select(AlertaAmbiental).where(AlertaAmbiental.tenant_id == self.tenant_id).order_by(AlertaAmbiental.data_deteccao.desc())
        if status_filter:
            stmt = stmt.where(AlertaAmbiental.status == status_filter)
        if severidade:
            stmt = stmt.where(AlertaAmbiental.severidade == severidade)
        if tipo:
            stmt = stmt.where(AlertaAmbiental.tipo == tipo)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_alerta(self, dados: dict) -> AlertaAmbiental:
        if "data_deteccao" not in dados:
            dados["data_deteccao"] = date.today()
        alerta = AlertaAmbiental(tenant_id=self.tenant_id, **dados)
        self.session.add(alerta)
        await self.session.flush()
        await self.session.refresh(alerta)
        return alerta

    async def atualizar_alerta(self, alerta_id: uuid.UUID, dados: dict) -> AlertaAmbiental:
        obj = (await self.session.execute(
            select(AlertaAmbiental).where(AlertaAmbiental.id == alerta_id, AlertaAmbiental.tenant_id == self.tenant_id)
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Alerta não encontrado.")
        for k, v in dados.items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    # ── Outorgas ──────────────────────────────────────────────────────────────

    async def listar_outorgas(self, status_filter: Optional[str] = None) -> list[OutorgaHidrica]:
        stmt = (
            select(OutorgaHidrica)
            .where(OutorgaHidrica.tenant_id == self.tenant_id, OutorgaHidrica.ativo == True)
            .order_by(OutorgaHidrica.data_vencimento.asc())
        )
        if status_filter:
            stmt = stmt.where(OutorgaHidrica.status == status_filter)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_outorga(self, dados: dict) -> OutorgaHidrica:
        outorga = OutorgaHidrica(tenant_id=self.tenant_id, **dados)
        self.session.add(outorga)
        await self.session.flush()
        await self.session.refresh(outorga)
        return outorga

    async def atualizar_outorga(self, outorga_id: uuid.UUID, dados: dict) -> OutorgaHidrica:
        obj = (await self.session.execute(
            select(OutorgaHidrica).where(OutorgaHidrica.id == outorga_id, OutorgaHidrica.tenant_id == self.tenant_id)
        )).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Outorga não encontrada.")
        for k, v in dados.items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj
