from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_service import BaseService

from agricola.ndvi.models import ImagemNDVI
from agricola.ndvi.schemas import NDVICreate

class NDVIService(BaseService[ImagemNDVI]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(ImagemNDVI, session, tenant_id)

    async def sync_sentinel2_data(self, talhao_id: UUID) -> str:
        # 1. Busca poligono do talhao
        # 2. Faz req Copernicus Data Space API (Sentinel-2) com base na bbox do poligono
        # 3. Filtra nuvens < 20%
        # 4. Baixa banda B04 e B08, calcula NDVI
        # 5. Salva color map no MinIO/S3 e registra no BD
        
        # Mock logic
        return "Sincronização agendada com sucesso"

    async def get_serie_temporal(self, talhao_id: UUID) -> list[dict]:
        # Lista as medias das imagens capturadas ao longo do tempo para o grafico do frontend
        imagens = await self.list_all(talhao_id=talhao_id)
        serie = [
            {"data": img.data_captura.isoformat(), "ndvi": float(img.indice_medio) if img.indice_medio else 0}
            for img in imagens
        ]
        # Ordena cronologicamente
        serie.sort(key=lambda x: x["data"])
        return serie
