from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.exceptions import BusinessRuleError

from agricola.safras.models import Safra
from agricola.operacoes.models import OperacaoAgricola
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
            
        area_ha = safra.area_plantada_ha or 1.0 # fallback prevention division by zero
        
        # Consolida custos das operações
        stmt_ops = select(
            OperacaoAgricola.tipo, 
            func.sum(OperacaoAgricola.custo_total).label("total")
        ).filter_by(
            safra_id=safra_id, 
            tenant_id=self.tenant_id
        ).group_by(OperacaoAgricola.tipo)
        
        result_ops = await self.session.execute(stmt_ops)
        
        breakdowns = []
        custo_total = 0.0
        
        items = result_ops.all()
        
        for row in items:
            valor = float(row.total or 0)
            custo_total += valor
            breakdowns.append({
                "categoria": row.tipo,
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
        if safra.custo_previsto_ha:
            orcamento = float(safra.custo_previsto_ha * area_ha)
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
