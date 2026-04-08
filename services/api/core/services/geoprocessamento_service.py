"""
Serviço de Upload e Processamento de Arquivos Geoespaciais.

Responsabilidades:
- Upload de shapefile/KML
- Conversão para GeoJSON
- Cálculo de área do polígono (hectares)
- Validação de geometria
"""
import io
import zipfile
import json
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

try:
    import fiona
    from shapely.geometry import shape, mapping
    from shapely.ops import transform
    from functools import partial
    import pyproj
    GEOSPATIAL_LIBS_AVAILABLE = True
except ImportError:
    GEOSPATIAL_LIBS_AVAILABLE = False
    logger.warning("Fiona/Shapely não disponíveis. Funcionalidades geoespaciais limitadas.")


class GeoprocessamentoService:
    """
    Serviço para processamento de arquivos geoespaciais.
    
    Funcionalidades:
    - Processar shapefile (zip com .shp, .dbf, .shx, .prj)
    - Processar KML/KMZ
    - Converter para GeoJSON
    - Calcular área em hectares
    - Validar geometria
    """
    
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id
    
    # ==========================================================================
    # PROCESSAMENTO DE SHAPEFILE
    # ==========================================================================
    
    async def processar_shapefile(
        self,
        arquivo_zip: bytes,
        nome_camada: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa shapefile (arquivo ZIP com .shp, .dbf, .shx, .prj).
        
        Args:
            arquivo_zip: Conteúdo binário do ZIP
            nome_camada: Nome da camada para extrair (se múltiplas)
            
        Returns:
            Dict com:
            - geometria: GeoJSON da geometria
            - area_ha: Área calculada em hectares
            - propriedades: Atributos da feature
            - srs: Sistema de referência espacial
        """
        if not GEOSPATIAL_LIBS_AVAILABLE:
            raise RuntimeError(
                "Bibliotecas geoespaciais não disponíveis. "
                "Instale: pip install fiona shapely pyproj"
            )
        
        try:
            # Extrair ZIP em memória
            with zipfile.ZipFile(io.BytesIO(arquivo_zip)) as zf:
                # Listar arquivos no ZIP
                arquivos = zf.namelist()
                logger.info(f"Shapefile contém: {arquivos}")
                
                # Validar arquivos obrigatórios
                shp_files = [f for f in arquivos if f.endswith('.shp')]
                if not shp_files:
                    raise ValueError("Shapefile inválido: arquivo .shp não encontrado")
                
                # Extrair para diretório temporário em memória
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    zf.extractall(tmpdir)
                    
                    # Encontrar arquivo .shp principal
                    shp_path = os.path.join(tmpdir, shp_files[0])
                    
                    # Abrir com Fiona
                    with fiona.open(shp_path, 'r') as dataset:
                        # Obter CRS
                        crs = dataset.crs
                        logger.info(f"CRS do shapefile: {crs}")
                        
                        # Ler todas as features
                        features = []
                        area_total_ha = 0.0
                        
                        for feature in dataset:
                            # Converter para GeoJSON
                            geojson_feature = {
                                "type": "Feature",
                                "geometry": feature.geometry,
                                "properties": feature.properties,
                            }
                            
                            # Calcular área
                            area_ha = await self._calcular_area_feature(feature, crs)
                            area_total_ha += area_ha
                            
                            features.append(geojson_feature)
                        
                        # Se múltiplas features, criar FeatureCollection
                        if len(features) == 1:
                            geometria = features[0]["geometry"]
                            propriedades = features[0]["properties"]
                        else:
                            geometria = {
                                "type": "FeatureCollection",
                                "features": features,
                            }
                            propriedades = {"total_features": len(features)}
                        
                        return {
                            "geometria": geometria,
                            "area_ha": round(area_total_ha, 4),
                            "propriedades": propriedades,
                            "crs": str(crs) if crs else "WGS84",
                            "total_features": len(features),
                        }
        
        except Exception as e:
            logger.error(f"Erro ao processar shapefile: {e}")
            raise ValueError(f"Erro ao processar shapefile: {str(e)}")
    
    # ==========================================================================
    # PROCESSAMENTO DE KML/KMZ
    # ==========================================================================
    
    async def processar_kml(
        self,
        arquivo: bytes,
        is_kmz: bool = False
    ) -> Dict[str, Any]:
        """
        Processa arquivo KML ou KMZ.
        
        Args:
            arquivo: Conteúdo binário do KML/KMZ
            is_kmz: True se for KMZ (KML compactado)
            
        Returns:
            Dict com geometria, área e propriedades
        """
        if not GEOSPATIAL_LIBS_AVAILABLE:
            raise RuntimeError("Bibliotecas geoespaciais não disponíveis")
        
        try:
            import xml.etree.ElementTree as ET
            from xml.etree.ElementTree import ParseError
            
            # Extrair KML se for KMZ
            if is_kmz:
                with zipfile.ZipFile(io.BytesIO(arquivo)) as zf:
                    # Extrair primeiro arquivo .kml
                    kml_files = [f for f in zf.namelist() if f.endswith('.kml')]
                    if not kml_files:
                        raise ValueError("KMZ inválido: arquivo .kml não encontrado")
                    
                    kml_content = zf.read(kml_files[0])
            else:
                kml_content = arquivo
            
            # Parse XML
            try:
                root = ET.fromstring(kml_content)
            except ParseError as e:
                raise ValueError(f"KML inválido: {str(e)}")
            
            # Extrair coordenadas de Placemarks
            coordenadas_todas = []
            nomes = []
            
            # Namespace KML
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            
            for placemark in root.findall('.//kml:Placemark', ns):
                # Extrair nome
                nome_elem = placemark.find('kml:name', ns)
                if nome_elem is not None and nome_elem.text:
                    nomes.append(nome_elem.text)
                
                # Extrair coordenadas (Polygon ou LineString)
                for polygon in placemark.findall('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns):
                    if polygon.text:
                        coords_text = polygon.text.strip()
                        coords = self._parse_kml_coordinates(coords_text)
                        coordenadas_todas.append(coords)
                
                # LineString
                for linestring in placemark.findall('.//kml:LineString/kml:coordinates', ns):
                    if linestring.text:
                        coords_text = linestring.text.strip()
                        coords = self._parse_kml_coordinates(coords_text)
                        coordenadas_todas.append(coords)
            
            if not coordenadas_todas:
                raise ValueError("Nenhuma geometria encontrada no KML")
            
            # Converter para GeoJSON Polygon (se apenas 1) ou MultiPolygon
            if len(coordenadas_todas) == 1:
                geometria = {
                    "type": "Polygon",
                    "coordinates": [coordenadas_todas[0]],
                }
            else:
                geometria = {
                    "type": "MultiPolygon",
                    "coordinates": [[coords] for coords in coordenadas_todas],
                }
            
            # Calcular área
            area_ha = await self._calcular_area_geojson(geometria)
            
            return {
                "geometria": geometria,
                "area_ha": round(area_ha, 4),
                "propriedades": {
                    "nomes": nomes,
                    "total_poligonos": len(coordenadas_todas),
                },
                "crs": "WGS84",
            }
        
        except Exception as e:
            logger.error(f"Erro ao processar KML: {e}")
            raise ValueError(f"Erro ao processar KML: {str(e)}")
    
    def _parse_kml_coordinates(self, coords_text: str) -> List[List[float]]:
        """
        Parse coordenadas KML para lista de [lon, lat].
        
        KML formato: "lon,lat,alt lon,lat,alt ..."
        """
        coordenadas = []
        for coord in coords_text.split():
            partes = coord.strip().split(',')
            if len(partes) >= 2:
                lon = float(partes[0])
                lat = float(partes[1])
                coordenadas.append([lon, lat])
        
        # Fechar polígono (primeiro = último)
        if coordenadas and coordenadas[0] != coordenadas[-1]:
            coordenadas.append(coordenadas[0].copy())
        
        return coordenadas
    
    # ==========================================================================
    # CÁLCULO DE ÁREA
    # ==========================================================================
    
    async def _calcular_area_feature(
        self,
        feature: Any,
        crs: Any
    ) -> float:
        """Calcula área de uma feature em hectares."""
        from shapely.geometry import shape
        
        # Converter geometria para Shapely
        geom = shape(feature.geometry)
        
        # Calcular área
        return await self._calcular_area_shapely(geom, crs)
    
    async def _calcular_area_shapely(
        self,
        geom: Any,
        crs: Any
    ) -> float:
        """
        Calcula área de geometria Shapely em hectares.
        
        Se CRS for projetado (ex: UTM), calcula direto e converte.
        Se CRS for geográfico (WGS84), transforma para projeção adequada.
        """
        from shapely.ops import transform
        import pyproj
        
        # Verificar se CRS é geográfico (lat/lon)
        if crs and crs.get('proj') == 'longlat' or (crs and 'EPSG:4326' in str(crs)):
            # Transformar para projeção UTM adequada
            # Obter centróide para determinar zona UTM
            centroid = geom.centroid
            lon, lat = centroid.x, centroid.y
            
            # Calcular zona UTM
            zona_utm = int((lon + 180) / 6) + 1
            
            # Criar projeção UTM (hemisfério sul para Brasil)
            if lat < 0:
                # Hemisfério sul
                crs_proj = f"+proj=utm +zone={zona_utm} +south +datum=WGS84 +units=m +no_defs"
            else:
                crs_proj = f"+proj=utm +zone={zona_utm} +datum=WGS84 +units=m +no_defs"
            
            # Transformar geometria
            project = partial(
                pyproj.transform,
                pyproj.Proj(init='EPSG:4326'),
                pyproj.Proj(crs_proj)
            )
            geom_proj = transform(project, geom)
            
            # Calcular área em m² e converter para hectares
            area_m2 = geom_proj.area
            area_ha = area_m2 / 10000.0
            
        else:
            # CRS já é projetado (ex: UTM)
            area_m2 = geom.area
            area_ha = area_m2 / 10000.0
        
        return area_ha
    
    async def _calcular_area_geojson(self, geometria: Dict) -> float:
        """Calcula área de GeoJSON em hectares."""
        if not GEOSPATIAL_LIBS_AVAILABLE:
            # Fallback: cálculo aproximado para polígonos simples
            return self._calcular_area_aproximada(geometria)
        
        from shapely.geometry import shape
        
        geom = shape(geometria)
        # Assumir WGS84
        return await self._calcular_area_shapely(geom, {'proj': 'longlat'})
    
    def _calcular_area_aproximada(self, geometria: Dict) -> float:
        """
        Cálculo aproximado de área (fallback sem shapely).
        
        Usa fórmula do shoelace para polígonos simples.
        """
        if geometria.get('type') == 'Polygon':
            coords = geometria['coordinates'][0]
        elif geometria.get('type') == 'MultiPolygon':
            # Somar área de todos os polígonos
            area_total = 0.0
            for polygon_coords in geometria['coordinates']:
                area_total += self._calcular_area_aproximada({
                    'type': 'Polygon',
                    'coordinates': [polygon_coords[0]]
                })
            return area_total
        else:
            return 0.0
        
        # Fórmula do shoelace
        n = len(coords)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        
        area = abs(area) / 2.0
        
        # Converter de graus² para hectares (aproximado, válido perto do equador)
        # 1 grau² ≈ 12.324 km² ≈ 1,232,400 hectares
        area_ha = area * 12324.0
        
        return area_ha
    
    # ==========================================================================
    # VALIDAÇÃO DE GEOMETRIA
    # ==========================================================================
    
    async def validar_geometria(self, geometria: Dict) -> Dict[str, Any]:
        """
        Valida geometria GeoJSON.
        
        Returns:
            Dict com:
            - valida: bool
            - erros: lista de erros
            - area_ha: área calculada
            - bounds: limites da geometria
        """
        erros = []
        
        # Validar estrutura básica
        if not geometria:
            return {
                "valida": False,
                "erros": ["Geometria vazia"],
                "area_ha": 0.0,
            }
        
        tipo = geometria.get('type')
        if tipo not in ['Point', 'LineString', 'Polygon', 'MultiPolygon', 'MultiPoint', 'Feature', 'FeatureCollection']:
            erros.append(f"Tipo de geometria inválido: {tipo}")
        
        # Calcular área se for polígono
        area_ha = 0.0
        if tipo in ['Polygon', 'MultiPolygon', 'Feature', 'FeatureCollection']:
            try:
                area_ha = await self._calcular_area_geojson(geometria)
                if area_ha <= 0:
                    erros.append("Área calculada é zero ou negativa")
            except Exception as e:
                erros.append(f"Erro ao calcular área: {str(e)}")
        
        # Obter bounds
        bounds = None
        if GEOSPATIAL_LIBS_AVAILABLE:
            try:
                from shapely.geometry import shape
                geom = shape(geometria)
                bounds = {
                    "min_lon": geom.bounds[0],
                    "min_lat": geom.bounds[1],
                    "max_lon": geom.bounds[2],
                    "max_lat": geom.bounds[3],
                }
            except Exception:
                pass
        
        return {
            "valida": len(erros) == 0,
            "erros": erros,
            "area_ha": round(area_ha, 4),
            "bounds": bounds,
        }


# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def calcular_area_poligono_simples(coords: List[List[float]]) -> float:
    """
    Calcula área de polígono simples usando fórmula do shoelace.
    
    Args:
        coords: Lista de [lon, lat]
        
    Returns:
        Área aproximada em hectares
    """
    n = len(coords)
    if n < 3:
        return 0.0
    
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    
    area = abs(area) / 2.0
    
    # Converter graus² para hectares (aproximado)
    area_ha = area * 12324.0
    
    return round(area_ha, 4)
