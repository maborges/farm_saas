from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import BusinessRuleError
from core.base_service import BaseService

from agricola.previsoes.models import PrevisaoProdutividade
from agricola.previsoes.schemas import PrevisaoProdutividadeCreate

class PrevisaoService(BaseService[PrevisaoProdutividade]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(PrevisaoProdutividade, session, tenant_id)

    async def gerar_nova_previsao(self, safra_id: UUID, talhao_id: UUID) -> PrevisaoProdutividade:
        # Integração real fará fetch de Clima, NDVI, info do solo
        # e passará para modelo de Machine Learning via request ou lib
        
        # Mock calculation
        dados = {
            "safra_id": safra_id,
            "talhao_id": talhao_id,
            "data_previsao": date.today(),
            "produtividade_estimada_sc_ha": 65.5,
            "margem_erro_pct": 5.0,
            "fatores_peso": {"clima": 0.4, "solo": 0.3, "ndvi": 0.3},
            "indice_ndvi_medio": 0.72,
            "modelo_ia_versao": "rf_soja_v2",
        }
        
        schema = PrevisaoProdutividadeCreate(**dados)
        return await self.criar(schema)

    async def criar(self, dados: PrevisaoProdutividadeCreate) -> PrevisaoProdutividade:
        dados_dict = dados.model_dump()
        return await super().create(dados_dict)
