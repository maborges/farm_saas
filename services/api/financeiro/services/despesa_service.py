import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import List, Optional
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from financeiro.models.despesa import Despesa
from financeiro.models.rateio import Rateio
from financeiro.models.plano_conta import PlanoConta
from financeiro.schemas.despesa_schema import DespesaCreate, DespesaUpdate


class DespesaService(BaseService[Despesa]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(Despesa, session, tenant_id)

    async def _validar_plano_conta(self, plano_conta_id: uuid.UUID) -> PlanoConta:
        stmt = select(PlanoConta).where(
            PlanoConta.id == plano_conta_id,
            PlanoConta.tenant_id == self.tenant_id,
        )
        plano = (await self.session.execute(stmt)).scalars().first()
        if not plano:
            raise BusinessRuleError("Plano de contas não localizado ou inacessível.")
        return plano

    def _calcular_parcelas(self, valor_total: float, total_parcelas: int) -> list[float]:
        """
        Divide o valor total em parcelas com centavos corretos.
        A diferença de arredondamento vai para a última parcela.
        """
        valor_dec = Decimal(str(valor_total))
        parcela_base = (valor_dec / total_parcelas).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        parcelas = [float(parcela_base)] * total_parcelas
        diferenca = float(valor_dec - parcela_base * total_parcelas)
        if diferenca != 0:
            parcelas[-1] = round(parcelas[-1] + diferenca, 2)
        return parcelas

    async def create_with_rateio(self, obj_in: DespesaCreate) -> list[Despesa]:
        """
        Cria uma despesa com suporte a parcelamento e rateio.

        Se total_parcelas > 1, cria N despesas com mesmo grupo_parcela_id.
        Retorna lista de despesas criadas (1 item se sem parcelamento).
        """
        await self._validar_plano_conta(obj_in.plano_conta_id)

        base_data = obj_in.model_dump(exclude={"rateios", "total_parcelas"})
        total_parcelas = obj_in.total_parcelas or 1

        grupo_parcela_id = uuid.uuid4() if total_parcelas > 1 else None
        valores = self._calcular_parcelas(obj_in.valor_total, total_parcelas)

        despesas_criadas: list[Despesa] = []

        for i, valor in enumerate(valores):
            numero_parcela = i + 1
            vencimento = obj_in.data_vencimento + relativedelta(months=i)

            despesa_data = {
                **base_data,
                "tenant_id": self.tenant_id,
                "valor_total": valor,
                "data_vencimento": vencimento,
                "grupo_parcela_id": grupo_parcela_id,
                "numero_parcela": numero_parcela if total_parcelas > 1 else None,
                "total_parcelas": total_parcelas if total_parcelas > 1 else None,
            }

            db_despesa = Despesa(**despesa_data)
            self.session.add(db_despesa)
            await self.session.flush()

            # Rateios apenas na 1ª parcela (ou parcela única)
            if i == 0 and obj_in.rateios:
                for rateio_req in obj_in.rateios:
                    rateio_dict = rateio_req.model_dump()
                    rateio_dict["tenant_id"] = self.tenant_id
                    rateio_dict["despesa_id"] = db_despesa.id
                    self.session.add(Rateio(**rateio_dict))

            await self.session.flush()
            await self.session.refresh(db_despesa)
            despesas_criadas.append(db_despesa)

        return despesas_criadas

    async def listar_com_filtros(
        self,
        fazenda_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        vencimento_de: Optional[date] = None,
        vencimento_ate: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Despesa]:
        stmt = (
            select(Despesa)
            .where(Despesa.tenant_id == self.tenant_id, Despesa.ativo == True)
            .order_by(Despesa.data_vencimento)
            .offset(skip)
            .limit(limit)
        )
        if fazenda_id:
            stmt = stmt.where(Despesa.fazenda_id == fazenda_id)
        if status:
            stmt = stmt.where(Despesa.status == status)
        if vencimento_de:
            stmt = stmt.where(Despesa.data_vencimento >= vencimento_de)
        if vencimento_ate:
            stmt = stmt.where(Despesa.data_vencimento <= vencimento_ate)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def listar_vencendo(
        self,
        dias: int = 7,
        fazenda_id: Optional[uuid.UUID] = None,
    ) -> List[Despesa]:
        """Retorna despesas a vencer nos próximos N dias (inclui vencidas)."""
        hoje = date.today()
        ate = hoje + timedelta(days=dias)
        stmt = (
            select(Despesa)
            .where(
                Despesa.tenant_id == self.tenant_id,
                Despesa.ativo == True,
                Despesa.status.in_(["A_PAGAR", "PAGO_PARCIAL", "ATRASADO"]),
                Despesa.data_vencimento <= ate,
            )
            .order_by(Despesa.data_vencimento)
        )
        if fazenda_id:
            stmt = stmt.where(Despesa.fazenda_id == fazenda_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def atualizar(self, despesa_id: uuid.UUID, data: DespesaUpdate) -> Despesa:
        despesa = await self.get_or_fail(despesa_id)
        updates = data.model_dump(exclude_unset=True)

        # Atualizar status automaticamente baseado em valor_pago
        if "valor_pago" in updates and updates["valor_pago"] is not None:
            valor_pago = updates["valor_pago"]
            valor_total = updates.get("valor_total", despesa.valor_total)
            if valor_pago >= valor_total:
                updates.setdefault("status", "PAGO")
                updates.setdefault("data_pagamento", date.today())
            else:
                updates.setdefault("status", "PAGO_PARCIAL")

        for field, value in updates.items():
            setattr(despesa, field, value)
        self.session.add(despesa)
        await self.session.flush()
        await self.session.refresh(despesa)
        return despesa
