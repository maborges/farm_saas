from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.exceptions import BusinessRuleError

from agricola.cultivos.models import Cultivo  # noqa: F401 - registers relationship target
from agricola.safras.models import Safra, SafraTalhao
from agricola.operacoes.models import OperacaoAgricola
from agricola.production_units.models import ProductionUnit
from agricola.custos.models import CostAllocation
from agricola.custos.schemas import ReumoCustosSafraResponse, CustoBreakdown

class CustosService:
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def get_resumo_safra(self, safra_id: UUID) -> ReumoCustosSafraResponse:
        # Busca a Safra para ter a area
        stmt_safra = select(Safra).filter_by(id=safra_id, tenant_id=self.tenant_id)
        result_safra = await self.session.execute(stmt_safra)
        safra = result_safra.scalar_one_or_none()
        
        if not safra:
            raise BusinessRuleError("Safra não encontrada.")
            
        area_pu = (await self.session.execute(
            select(func.coalesce(func.sum(ProductionUnit.area_ha), 0)).where(
                ProductionUnit.tenant_id == self.tenant_id,
                ProductionUnit.safra_id == safra_id,
                ProductionUnit.status != "CANCELADA",
            )
        )).scalar_one()
        area_talhoes = (await self.session.execute(
            select(func.coalesce(func.sum(SafraTalhao.area_ha), 0)).where(
                SafraTalhao.tenant_id == self.tenant_id,
                SafraTalhao.safra_id == safra_id,
            )
        )).scalar_one()
        area_ha = float(area_pu or area_talhoes or 1.0)
        
        breakdowns = []
        custo_total = 0.0

        stmt_alloc = (
            select(
                CostAllocation.cost_category.label("categoria"),
                func.sum(CostAllocation.amount).label("total"),
            )
            .join(ProductionUnit, ProductionUnit.id == CostAllocation.production_unit_id)
            .where(
                CostAllocation.tenant_id == self.tenant_id,
                ProductionUnit.safra_id == safra_id,
            )
            .group_by(CostAllocation.cost_category)
        )
        items = (await self.session.execute(stmt_alloc)).all()

        if not items:
            stmt_ops = select(
                OperacaoAgricola.tipo.label("categoria"),
                func.sum(OperacaoAgricola.custo_total).label("total"),
            ).filter_by(
                safra_id=safra_id,
                tenant_id=self.tenant_id,
            ).group_by(OperacaoAgricola.tipo)
            items = (await self.session.execute(stmt_ops)).all()

        for row in items:
            valor = float(row.total or 0)
            custo_total += valor
            breakdowns.append({
                "categoria": row.categoria,
                "valor_total": valor,
                "valor_por_ha": valor / float(area_ha),
                "percentual": 0 # calculado no proximo step
            })
            
        # Atualiza percentuais
        for b in breakdowns:
            if custo_total > 0:
                b["percentual"] = round((b["valor_total"] / custo_total) * 100, 2)
            
        orcamento = None
        desvio = None
        custo_previsto_ha = getattr(safra, "custo_previsto_ha", None)
        if custo_previsto_ha:
            orcamento = float(custo_previsto_ha * area_ha)
            if orcamento > 0:
                desvio = round(((custo_total - orcamento) / orcamento) * 100, 2)
                
        return ReumoCustosSafraResponse(
            safra_id=safra_id,
            area_total_ha=float(area_ha),
            custo_total_realizado=custo_total,
            custo_realizado_por_ha=custo_total / float(area_ha),
            orcamento_previsto_total=orcamento,
            desvio_orcamento_pct=desvio,
            breakdown=breakdowns
        )
