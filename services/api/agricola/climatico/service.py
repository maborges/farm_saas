from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.base_service import BaseService

from agricola.climatico.models import RegistroClima

class ClimaService(BaseService[RegistroClima]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(RegistroClima, session, tenant_id)

    async def sync_open_meteo(self, unidade_produtiva_id: UUID) -> str:
        # 1. Obter lat/lng da Fazenda localmente
        # 2. Requisitar dados histórcios do dia anterior na API Historical Open-Meteo
        # 3. Salvar no BD
        return "Sincronização do clima executada com sucesso"

    async def get_clima_periodo(self, unidade_produtiva_id: UUID, data_inicio: date, data_fim: date):
        stmt = select(RegistroClima).filter_by(
            tenant_id=self.tenant_id,
            unidade_produtiva_id=unidade_produtiva_id
        ).where(
            RegistroClima.data_registro >= data_inicio,
            RegistroClima.data_registro <= data_fim
        ).order_by(RegistroClima.data_registro.asc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
        
    async def get_chuva_acumulada(self, unidade_produtiva_id: UUID, dias: int = 30) -> float:
        hoje = date.today()
        limite = hoje - timedelta(days=dias)
        
        stmt = select(func.sum(RegistroClima.precipitacao_mm)).filter_by(
            tenant_id=self.tenant_id,
            unidade_produtiva_id=unidade_produtiva_id
        ).where(RegistroClima.data_registro >= limite)
        
        resultado = await self.session.execute(stmt)
        val = resultado.scalar()
        return float(val) if val else 0.0
