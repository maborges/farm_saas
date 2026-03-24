import json
from uuid import UUID
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, mapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.exceptions import BusinessRuleError
from core.base_service import BaseService

from agricola.talhoes.models import Talhao
from agricola.talhoes.schemas import TalhaoCreate, TalhaoUpdate

class TalhaoService(BaseService[Talhao]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(Talhao, session, tenant_id)

    async def criar(self, dados: TalhaoCreate) -> Talhao:
        """
        Cria talhão com geometria PostGIS.
        Se geometria_geojson fornecida, converte para WKT e salva.
        area_ha é calculada automaticamente pelo trigger do banco.
        """
        dados_dict = dados.model_dump(exclude={"geometria_geojson"})

        if dados.geometria_geojson:
            geom_shapely = shape(dados.geometria_geojson)
            if not geom_shapely.is_valid:
                raise BusinessRuleError("Geometria do talhão é inválida")
            
            from core.database import DB_URL
            if "postgresql" in DB_URL:
                dados_dict["geometria"] = from_shape(geom_shapely, srid=4326)
            else:
                # Fallback SQLite: salva o dict GeoJSON direto
                dados_dict["geometria"] = dados.geometria_geojson
                # Calcula centroide para facilitar zoom-to-marker se desejado
                c = geom_shapely.centroid
                dados_dict["centroide"] = {"lat": c.y, "lng": c.x}

        return await super().create(dados_dict)

    async def atualizar(self, obj_id: UUID, dados: TalhaoUpdate) -> Talhao:
        dados_dict = dados.model_dump(exclude_unset=True, exclude={"geometria_geojson"})
        
        if dados.geometria_geojson:
            geom_shapely = shape(dados.geometria_geojson)
            if not geom_shapely.is_valid:
                raise BusinessRuleError("Geometria do talhão é inválida")
            
            from core.database import DB_URL
            if "postgresql" in DB_URL:
                dados_dict["geometria"] = from_shape(geom_shapely, srid=4326)
            else:
                dados_dict["geometria"] = dados.geometria_geojson
            
        return await super().update(obj_id, dados_dict)

    async def serializar_com_geojson(self, talhao: Talhao) -> dict:
        """Converte geometria PostGIS para GeoJSON para o frontend."""
        resultado = {col.name: getattr(talhao, col.name) for col in talhao.__table__.columns}
        
        # Add property explicitly if needed
        resultado["area_efetiva_ha"] = talhao.area_efetiva_ha
        
        if talhao.geometria is not None:
            if isinstance(talhao.geometria, dict):
                # SQLite fallback
                resultado["geometria_geojson"] = talhao.geometria
            else:
                # PostGIS Geometry
                geom = to_shape(talhao.geometria)
                resultado["geometria_geojson"] = mapping(geom)
                
        if talhao.centroide is not None:
            if isinstance(talhao.centroide, dict):
                resultado["centroide_lat"] = talhao.centroide.get("lat")
                resultado["centroide_lng"] = talhao.centroide.get("lng")
            else:
                ponto = to_shape(talhao.centroide)
                resultado["centroide_lat"] = ponto.y
                resultado["centroide_lng"] = ponto.x
            
        return resultado

    async def calcular_sobreposicao(self, talhao_id: UUID, outro_talhao_id: UUID) -> float:
        """Retorna percentual de sobreposição entre dois talhões (deve ser 0 em produção)."""
        stmt = text("""
            SELECT ST_Area(
                ST_Intersection(a.geometria::geography, b.geometria::geography)
            ) / NULLIF(ST_Area(a.geometria::geography), 0) * 100 AS pct
            FROM talhoes a, talhoes b
            WHERE a.id = :id1 AND b.id = :id2
              AND a.tenant_id = :tid AND b.tenant_id = :tid
        """)
        result = await self.session.execute(stmt, {"id1": talhao_id, "id2": outro_talhao_id, "tid": self.tenant_id})
        val = result.scalar()
        return float(val) if val else 0.0
