import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import List, Optional
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from financeiro.models.receita import Receita
from financeiro.models.plano_conta import PlanoConta
from financeiro.schemas.receita_schema import ReceitaCreate, ReceitaUpdate


class ReceitaService(BaseService[Receita]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(Receita, session, tenant_id)

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

    async def create_parcelado(self, obj_in: ReceitaCreate) -> list[Receita]:
        """
        Cria uma receita com suporte a parcelamento.

        Se total_parcelas > 1, cria N receitas com mesmo grupo_parcela_id.
        Retorna lista de receitas criadas (1 item se sem parcelamento).
        """
        await self._validar_plano_conta(obj_in.plano_conta_id)

        base_data = obj_in.model_dump(exclude={"total_parcelas"})
        total_parcelas = obj_in.total_parcelas or 1

        grupo_parcela_id = uuid.uuid4() if total_parcelas > 1 else None
        valores = self._calcular_parcelas(obj_in.valor_total, total_parcelas)

        receitas_criadas: list[Receita] = []

        for i, valor in enumerate(valores):
            numero_parcela = i + 1
            vencimento = obj_in.data_vencimento + relativedelta(months=i)

            receita_data = {
                **base_data,
                "tenant_id": self.tenant_id,
                "valor_total": valor,
                "data_vencimento": vencimento,
                "grupo_parcela_id": grupo_parcela_id,
                "numero_parcela": numero_parcela if total_parcelas > 1 else None,
                "total_parcelas": total_parcelas if total_parcelas > 1 else None,
            }

            db_receita = Receita(**receita_data)
            self.session.add(db_receita)
            await self.session.flush()
            await self.session.refresh(db_receita)
            receitas_criadas.append(db_receita)

        return receitas_criadas

    async def listar_com_filtros(
        self,
        fazenda_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        vencimento_de: Optional[date] = None,
        vencimento_ate: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Receita]:
        stmt = (
            select(Receita)
            .where(Receita.tenant_id == self.tenant_id, Receita.ativo == True)
            .order_by(Receita.data_vencimento)
            .offset(skip)
            .limit(limit)
        )
        if fazenda_id:
            stmt = stmt.where(Receita.fazenda_id == fazenda_id)
        if status:
            stmt = stmt.where(Receita.status == status)
        if vencimento_de:
            stmt = stmt.where(Receita.data_vencimento >= vencimento_de)
        if vencimento_ate:
            stmt = stmt.where(Receita.data_vencimento <= vencimento_ate)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def listar_vencendo(
        self,
        dias: int = 7,
        fazenda_id: Optional[uuid.UUID] = None,
    ) -> List[Receita]:
        """Retorna receitas a vencer nos próximos N dias."""
        hoje = date.today()
        ate = hoje + timedelta(days=dias)
        stmt = (
            select(Receita)
            .where(
                Receita.tenant_id == self.tenant_id,
                Receita.ativo == True,
                Receita.status.in_(["A_RECEBER", "RECEBIDO_PARCIAL"]),
                Receita.data_vencimento <= ate,
            )
            .order_by(Receita.data_vencimento)
        )
        if fazenda_id:
            stmt = stmt.where(Receita.fazenda_id == fazenda_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def atualizar(self, receita_id: uuid.UUID, data: ReceitaUpdate) -> Receita:
        receita = await self.get_or_fail(receita_id)
        updates = data.model_dump(exclude_unset=True)

        # Atualizar status automaticamente baseado em valor_recebido
        if "valor_recebido" in updates and updates["valor_recebido"] is not None:
            valor_recebido = updates["valor_recebido"]
            valor_total = updates.get("valor_total", receita.valor_total)
            if valor_recebido >= valor_total:
                updates.setdefault("status", "RECEBIDO")
                updates.setdefault("data_recebimento", date.today())
            else:
                updates.setdefault("status", "RECEBIDO_PARCIAL")

        for field, value in updates.items():
            setattr(receita, field, value)
        self.session.add(receita)
        await self.session.flush()
        await self.session.refresh(receita)
        return receita
